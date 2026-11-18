#!/usr/bin/env python3
"""C23 acceptance gate — the no-avoidance check for the Bitget out-of-sample campaign.

Prints exactly one authoritative line:
  C23 ACCEPTANCE: PASS      -> prereg + viable-acquisition evidence + full battery present & consistent
  C23 ACCEPTANCE: PENDING   -> prerequisites OK but the heavy battery is incomplete (lists what is missing)
  C23 ACCEPTANCE: FAIL      -> prereg/probe missing, acquisition not viable, config drift, or inconsistent artifacts

Exit codes: PASS/PENDING -> 0, FAIL -> 1.

PENDING is NOT "done": per the handoff no-avoidance rule, a PENDING result means the session
must execute the heavy Bitget battery (fetch the archive, run the 4-fold 20k/20k/2k battery,
emit the required artifacts) until this gate prints PASS.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]
STATE = REPO_ROOT / "research_state"
TS = "20261118T202301Z"

VALID_TOKENS = {"STABLE_POSITIVE_SUBSET", "NO_GO", "UNDERPOWERED"}
FOLD_IDS = ["2023", "2024", "2025", "2026YTD"]

# Frozen spec-literal config the C23 prereg must match (drift detection).
FROZEN_CONFIG = {
    "rsi_period": 21,
    "rsi_threshold": 20.0,
    "target_pct": 9.0,
    "rebound_short_target_pct": 9.0,
    "rebound_short_time_exit_bars": 48,
    "enable_rebound_short": True,
    "enable_eth_hedge": True,
    "min_daily_volume_usd": 5_000_000.0,
    "gross_cap_pct": 120.0,
    "entry_spec_literal_next_open": True,
}

BATTERY_ARTIFACTS = [
    f"c23_bitget_fold_campaign_{TS}.json",
    f"c23_bitget_fold_episode_edge_{TS}.json",
    f"c23_bitget_fold_placebo_{TS}.json",
    f"c23_bitget_fold_census_{TS}.json",
    f"c23_decision_verdict_bitget_stability_{TS}.json",
    f"c23_pooled_stability_synthesis_{TS}.json",
    f"c23_decision_verdict_CONSOLIDATED_{TS}.json",
]


def _load(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:  # noqa: BLE001
        return None


def _sha256(path: Path) -> Optional[str]:
    try:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                h.update(chunk)
        return h.hexdigest()
    except Exception:  # noqa: BLE001
        return None


def _token_of(obj: Optional[Dict[str, Any]]) -> Optional[str]:
    if not isinstance(obj, dict):
        return None
    for key in ("final_verdict_token", "verdict_token", "verdict", "token"):
        v = obj.get(key)
        if isinstance(v, str) and v in VALID_TOKENS:
            return v
    return None


def evaluate() -> Tuple[str, Dict[str, Any]]:
    checks: Dict[str, Any] = {}

    prereg_json = STATE / f"c23_prereg_{TS}.json"
    prereg_md = STATE / f"c23_prereg_{TS}.md"
    probe_path = STATE / f"c23_venue_acquisition_probe_{TS}.json"
    universe_path = STATE / "universe_bitget_multiyear_verified.json"

    checks["prereg_json_present"] = prereg_json.exists()
    checks["prereg_md_present"] = prereg_md.exists()
    checks["probe_present"] = probe_path.exists()

    prereg = _load(prereg_json) if prereg_json.exists() else None
    probe = _load(probe_path) if probe_path.exists() else None

    # Config drift detection
    config_ok = False
    if isinstance(prereg, dict) and isinstance(prereg.get("config"), dict):
        cfg = prereg["config"]
        config_ok = all(cfg.get(k) == v for k, v in FROZEN_CONFIG.items())
    checks["config_matches_frozen_spec_literal"] = config_ok
    checks["prereg_status"] = (prereg or {}).get("prereg_status")
    checks["prereg_campaign"] = (prereg or {}).get("campaign")

    data_status = (probe or {}).get("c23_data_status")
    checks["c23_data_status"] = data_status
    acquisition_viable = isinstance(data_status, str) and data_status.startswith("ACQUISITION_VIABLE")
    checks["acquisition_viable"] = acquisition_viable

    # Cache presence (heavy acquisition may or may not have run yet)
    cache_dir = STATE / "cache" / "bitget_1h_multiyear_20230101_20260928"
    cache_candles = cache_dir / "candles"
    n_cached = len(list(cache_candles.glob("*.json"))) if cache_candles.is_dir() else 0
    checks["bitget_cache_symbols"] = n_cached
    checks["bitget_cache_present"] = (cache_dir / "provenance.json").exists()
    checks["bitget_universe_present"] = universe_path.exists()

    # Battery
    present = [a for a in BATTERY_ARTIFACTS if (STATE / a).exists()]
    missing = [a for a in BATTERY_ARTIFACTS if not (STATE / a).exists()]
    checks["battery_present"] = len(present)
    checks["battery_required"] = len(BATTERY_ARTIFACTS)
    checks["battery_missing"] = missing

    # Prerequisites
    prereq_ok = (checks["prereg_json_present"] and checks["prereg_md_present"]
                 and checks["probe_present"] and config_ok and acquisition_viable)

    if not prereq_ok:
        reasons = []
        if not checks["prereg_json_present"]:
            reasons.append("prereg json missing")
        if not checks["prereg_md_present"]:
            reasons.append("prereg md missing")
        if not checks["probe_present"]:
            reasons.append("acquisition probe missing")
        if not config_ok:
            reasons.append("prereg config does not match frozen spec-literal values (drift)")
        if not acquisition_viable:
            reasons.append(f"acquisition not viable (c23_data_status={data_status!r})")
        checks["fail_reasons"] = reasons
        return "FAIL", checks

    if missing:
        checks["pending_missing"] = missing
        return "PENDING", checks

    # Consistency checks on the completed battery
    problems: List[str] = []
    bitget_verdict = _load(STATE / f"c23_decision_verdict_bitget_stability_{TS}.json")
    consolidated = _load(STATE / f"c23_decision_verdict_CONSOLIDATED_{TS}.json")
    pooled = _load(STATE / f"c23_pooled_stability_synthesis_{TS}.json")
    campaign = _load(STATE / f"c23_bitget_fold_campaign_{TS}.json")

    bitget_tok = _token_of(bitget_verdict)
    cons_tok = _token_of(consolidated)
    pooled_tok = _token_of(pooled) or (pooled or {}).get("token")
    checks["bitget_verdict_token"] = bitget_tok
    checks["consolidated_verdict_token"] = cons_tok

    if bitget_tok is None:
        problems.append("bitget verdict token missing/invalid")
    if cons_tok is None:
        problems.append("consolidated verdict token missing/invalid")
    if pooled_tok not in VALID_TOKENS:
        problems.append(f"pooled token missing/invalid ({pooled_tok!r})")
    if bitget_tok is not None and cons_tok is not None and bitget_tok != cons_tok:
        problems.append(f"bitget verdict ({bitget_tok}) != consolidated ({cons_tok})")

    # Campaign identity (prevents silently reusing a prior campaign's artifacts)
    for name, obj in (("campaign", campaign), ("bitget_verdict", bitget_verdict),
                      ("consolidated", consolidated), ("pooled", pooled)):
        if isinstance(obj, dict) and obj.get("campaign") not in (None, "C23"):
            problems.append(f"{name} campaign={obj.get('campaign')!r} (expected 'C23')")

    # All four pre-specified folds must be present in the merged campaign artifact
    if isinstance(campaign, dict):
        got = [f.get("id") for f in (campaign.get("folds") or []) if isinstance(f, dict)]
        checks["folds_present"] = got
        if got != FOLD_IDS:
            problems.append(f"campaign folds {got} != {FOLD_IDS}")

    # Prereg SHA binding (artifact must reference THIS prereg file, not a stale one)
    if prereg_json.exists():
        want = _sha256(prereg_json)
        checks["prereg_sha256_matches_actual"] = (
            isinstance(consolidated, dict) and consolidated.get("prereg_sha256") == want)
        if not checks["prereg_sha256_matches_actual"]:
            problems.append("consolidated prereg_sha256 does not match the on-disk C23 prereg")

    # Provenance guard: never Hyperliquid
    for name, obj in (("bitget_verdict", bitget_verdict), ("consolidated", consolidated),
                      ("pooled", pooled)):
        if isinstance(obj, dict):
            prov = obj.get("provenance") if isinstance(obj.get("provenance"), dict) else obj
            if prov.get("is_hyperliquid_venue_data") is True:
                problems.append(f"{name} mislabels data as Hyperliquid")
            if prov.get("fabricated_data") is True or prov.get("synthetic_data") is True:
                problems.append(f"{name} declares fabricated/synthetic data")

    if problems:
        checks["consistency_problems"] = problems
        return "FAIL", checks

    return "PASS", checks


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="C23 acceptance gate")
    ap.add_argument("--json", action="store_true", help="Emit machine-readable checks JSON")
    args = ap.parse_args(argv)

    token, checks = evaluate()
    if args.json:
        print(json.dumps({"token": token, "checks": checks}, indent=2))
    else:
        for k, v in checks.items():
            if k in ("battery_missing", "pending_missing", "fail_reasons", "consistency_problems"):
                continue
            print(f"[{ 'OK' if v not in (False, None) else '!!' }] {k}: {v}")
        if checks.get("battery_missing"):
            print(f"[--] battery_missing: {len(checks['battery_missing'])} artifact(s)")
            for m in checks["battery_missing"]:
                print(f"      - {m}")
        if checks.get("pending_missing"):
            print("[PENDING] heavy work required — missing artifacts:")
            for m in checks["pending_missing"]:
                print(f"      - {m}")
        if checks.get("fail_reasons"):
            print("[FAIL] prerequisite failures:")
            for r in checks["fail_reasons"]:
                print(f"      - {r}")
        if checks.get("consistency_problems"):
            print("[FAIL] consistency problems:")
            for p in checks["consistency_problems"]:
                print(f"      - {p}")

    if token == "PASS":
        print(f"\nC23 ACCEPTANCE: PASS — Bitget out-of-sample battery complete "
              f"(bitget={checks.get('bitget_verdict_token')}, consolidated={checks.get('consolidated_verdict_token')})")
        return 0
    if token == "PENDING":
        print(f"\nC23 ACCEPTANCE: PENDING — prerequisites OK; heavy Bitget battery required "
              f"({checks['battery_present']}/{checks['battery_required']} artifacts present)")
        return 0
    print(f"\nC23 ACCEPTANCE: FAIL — {checks.get('fail_reasons') or checks.get('consistency_problems')}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
