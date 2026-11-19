#!/usr/bin/env python3
"""Bit-identical intra-cell durability for the heavy draw stages (permutation, placebo).

WHY THIS EXISTS
---------------
The durable campaign runners only checkpoint at CELL granularity (a whole
arm x venue x fold inference battery). On this box a single 20k permutation cell
costs ~3.2 h, and the runtime environment is torn down between agent sessions, so
an in-flight cell is discarded on every environment loss. Observed cost before
this module existed: `cost_base/okx/2024` was restarted from zero at least twice
(11:20Z, 17:24Z, 23:41Z) with no progress retained.

This module checkpoints *already evaluated draw subsets* into
`research_state/c25_draw_ckpts/` as contiguous chunks. On resume the completed
chunks are re-used and only the remaining subsets are evaluated.

BIT-IDENTITY (why this cannot change a verdict)
-----------------------------------------------
- The subset list is generated exactly as before (same seed, same code path via
  `c20.permutation_draw_subsets`), before any draw is evaluated.
- Every subset is evaluated independently by the same function
  (`c20._run_draw` -> `run_memo_portfolio`) with the same config.
- Chunks are composed in the original order, so the final `results` list -- and
  therefore every summary statistic and p-value -- is element-for-element
  identical to a monolithic run. Draw counts/floors are untouched.
- Chunk files are ignored (and recomputed) when the prereg sha, stage, arm,
  venue, fold, seed, total draw count or chunk size differ.

Fail-safe: a process killed mid-chunk loses at most one chunk of work (~5 min at
the default 500 draws), never the whole cell.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple

DrawMany = Callable[[Sequence[Sequence[Any]]], List[Dict[str, Any]]]


def resume_enabled() -> bool:
    return os.environ.get("C25_DRAW_RESUME", "1") != "0"


def chunk_size() -> int:
    try:
        return max(1, int(os.environ.get("C25_DRAW_CHUNK", "500")))
    except ValueError:
        return 500


def _meta(campaign: str, stage: str, arm: str, venue: str, fold: str, tag: str,
          draws_total: int, prereg_sha256: str, seed: int) -> Dict[str, Any]:
    return {
        "campaign": campaign,
        "stage": stage,
        "arm": arm,
        "venue": venue,
        "fold": fold,
        "tag": tag,
        "draws_total": int(draws_total),
        "chunk_size": chunk_size(),
        "prereg_sha256": prereg_sha256,
        "seed": int(seed),
    }


def _path(state_dir: Path, campaign: str, stage: str, arm: str, venue: str, fold: str,
          tag: str, idx: int) -> Path:
    return (Path(state_dir) / "c25_draw_ckpts" /
            f"{campaign.lower()}_partial_{stage}_{arm}_{venue}_{fold}_{tag}_chunk{idx:05d}.json")


def make_c20_draw_many(candles_active: Dict[str, Any], memo: Dict[Any, Any], cfg: Any,
                       jobs: int) -> DrawMany:
    """Draw executor backed by the real portfolio engine (same workers as c20)."""
    import scripts.run_c20_cross_venue_campaign as c20

    def draw_many(subsets: Sequence[Sequence[Any]]) -> List[Dict[str, Any]]:
        subsets = list(subsets)
        if jobs > 1 and "fork" in c20.mp.get_all_start_methods():
            ctx = c20.mp.get_context("fork")
            with ctx.Pool(processes=jobs, initializer=c20._init_worker,
                          initargs=(candles_active, memo, cfg)) as pool:
                return pool.map(c20._run_draw, subsets, chunksize=1)
        c20._init_worker(candles_active, memo, cfg)
        return [c20._run_draw(sub) for sub in subsets]

    return draw_many


def run_chunked(*, state_dir: Path, campaign: str, tag: str, stage: str, arm: str,
                venue: str, fold: str, subsets: Sequence[Sequence[Any]], jobs: int,
                prereg_sha256: str, seed: int, draw_many: DrawMany) -> List[Dict[str, Any]]:
    """Evaluate `subsets` in checkpointed chunks; returns results in original order."""
    subsets = list(subsets)
    size = chunk_size()
    meta = _meta(campaign, stage, arm, venue, fold, tag, len(subsets), prereg_sha256, seed)
    results: List[Dict[str, Any]] = []

    if resume_enabled():
        idx = 0
        while True:
            p = _path(state_dir, campaign, stage, arm, venue, fold, tag, idx)
            if not p.exists():
                break
            try:
                payload = json.loads(p.read_text())
            except Exception:
                break
            if payload.get("meta") != meta:
                break
            chunk = payload.get("results") or []
            if not chunk or len(chunk) > size:
                break
            results.extend(chunk)
            idx += 1
        # Contiguity guard: never resume from a misaligned offset.
        if results and (len(results) % size) != 0:
            results = []

    start = len(results)
    for offset in range(start, len(subsets), size):
        chunk = subsets[offset:offset + size]
        if not chunk:
            break
        out = draw_many(chunk)
        results.extend(out)
        if resume_enabled():
            d = Path(state_dir) / "c25_draw_ckpts"
            d.mkdir(parents=True, exist_ok=True)
            p = _path(state_dir, campaign, stage, arm, venue, fold, tag, offset // size)
            tmp = p.with_suffix(".json.tmp")
            tmp.write_text(json.dumps({"meta": meta, "results": out}) + "\n")
            tmp.replace(p)
    return results


def clear_partials(state_dir: Path, campaign: str, tag: str, stage: Optional[str] = None,
                   arm: Optional[str] = None, venue: Optional[str] = None,
                   fold: Optional[str] = None) -> int:
    """Remove chunk files for a campaign/tag (used after the cell artifact is written)."""
    d = Path(state_dir) / "c25_draw_ckpts"
    if not d.exists():
        return 0
    parts = [campaign.lower(), "partial"]
    parts.append(stage if stage else "*")
    parts.append(arm if arm else "*")
    parts.append(venue if venue else "*")
    parts.append(fold if fold else "*")
    pat = "_".join(parts) + f"_{tag}_chunk*.json"
    removed = 0
    for p in d.glob(pat):
        try:
            p.unlink()
            removed += 1
        except OSError:
            pass
    return removed
