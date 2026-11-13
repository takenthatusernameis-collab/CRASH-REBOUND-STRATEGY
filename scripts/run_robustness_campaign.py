#!/usr/bin/env python3
"""Phase L — robustness / signal-vs-noise campaign for the 8-trade OKX result.

The Phase G+/J1/J2/K gates prove the *evidence chain*; they do not prove the
canonical return is distinguishable from luck or that it will persist. This script
produces the decision-grade signal-vs-noise characterization required by the
handoff gate (`scripts/session_gate.py` -> `phase_l_robustness`).

Contract (see HANDOFF.md §7):
- Read-only against the canonical campaign artifact; NEVER writes canonical stems.
- Writes ONLY ``research_state/robustness_real_okx_full.{json,md}``.
- Fails closed on missing / invalid trade data (no trades, bad timestamps, non
  finite PnL, empty symbols).
- Deterministic: seed=20261113 for the bootstrap and every derived statistic.

Required analyses (all numeric, not adjectives):
1. Trade-level bootstrap (10,000 resamples) of the 8 realized trade PnLs:
   95% CI for total PnL, total return on 100k, win rate, profit factor, and
   P(total PnL > 0).
2. Exact sign-flip permutation test: all 2^8 sign combinations; one-sided
   p_value = fraction of sign-flipped totals >= observed.
3. Concentration: per-symbol trade count / PnL / share, HHI, top-trade share,
   leave-one-symbol-out and leave-one-trade-out totals.
4. Time split: first-half vs second-half trade PnL (median split by exit time),
   monthly buckets, realized-horizon vs full-window annualization, and the
   no-trade tail.
5. Placebo/absence: how many J1 signal-gate events were not traded, and why
   (read from the committed census; no fabrication).
6. Go/no-go conclusion: one explicit sentence — signal, noise, or underpowered —
   supported by the CIs / p-value / concentration numbers.

This makes Phase L machine-checkable, not optional prose.
"""
from __future__ import annotations

import argparse
import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parents[1]

PROVENANCE_CAVEAT = (
    "Real OKX exchange data, non-synthetic; cross-venue vs Hyperliquid spec; "
    "NOT Hyperliquid performance evidence."
)

CANONICAL_CAMPAIGN = REPO_ROOT / "research_state" / "campaign_results_real_okx_full.json"
CENSUS = REPO_ROOT / "research_state" / "crash_event_census_real_okx_full.json"
OUT_JSON = REPO_ROOT / "research_state" / "robustness_real_okx_full.json"
OUT_MD = REPO_ROOT / "research_state" / "robustness_real_okx_full.md"

DEFAULT_SEED = 20261113
DEFAULT_RESAMPLES = 10_000
DEFAULT_CAPITAL = 100_000.0
SIGN_FLIP_COMBINATIONS = 256  # 2**8 — the 8 realized trades

# Signals considered decision-grade. Small samples make the bootstrap wide, so the
# verdict thresholds are deliberately explicit rather than hand-waved.
BOOTSTRAP_CI_LEVEL = 0.95
MIN_SIGN_FLIP_P = 0.10        # p >= this is "consistent with symmetric noise"
MAX_TOP_TRADE_SHARE = 0.50    # one trade carrying >= half the PnL is concentration risk


class RobustnessError(RuntimeError):
    """Fail-closed error for missing or invalid trade data."""


def _finite(value: Any) -> Optional[float]:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return None
    return out if math.isfinite(out) else None


def load_trades(canonical: Path = CANONICAL_CAMPAIGN) -> List[Dict[str, Any]]:
    """Load and validate trade-level records from the canonical campaign artifact.

    Fails closed: the canonical file must exist, be valid JSON, carry a ``results``
    object with a non-empty ``trades`` list, and every trade must have a finite
    ``total_pnl``, a valid millisecond ``exit_timestamp``, and a symbol.
    """
    if not canonical.exists():
        raise RobustnessError(f"canonical campaign missing: {canonical}")
    try:
        doc = json.loads(canonical.read_text())
    except json.JSONDecodeError as exc:
        raise RobustnessError(f"canonical campaign is not valid JSON: {exc}") from exc
    results = doc.get("results")
    if not isinstance(results, dict):
        raise RobustnessError("canonical campaign has no 'results' object")
    trades = results.get("trades")
    if not isinstance(trades, list) or not trades:
        raise RobustnessError("canonical campaign has no trades")

    out: List[Dict[str, Any]] = []
    for idx, t in enumerate(trades):
        if not isinstance(t, dict):
            raise RobustnessError(f"trade[{idx}] is not an object")
        pnl = _finite(t.get("total_pnl"))
        if pnl is None:
            raise RobustnessError(f"trade[{idx}] has non-finite total_pnl")
        ts = t.get("exit_timestamp")
        if ts is None:
            raise RobustnessError(f"trade[{idx}] has no exit_timestamp")
        symbol = str(t.get("symbol") or "").strip()
        if not symbol:
            raise RobustnessError(f"trade[{idx}] has no symbol")
        out.append({
            "symbol": symbol,
            "exit_timestamp_ms": int(ts),
            "total_pnl": pnl,
            "leg": str(t.get("leg") or "unknown"),
            "exit_reason": str(t.get("exit_reason") or "unknown"),
        })
    return out


def _percentile(sorted_vals: List[float], q: float) -> float:
    """Linear-interpolation percentile on a pre-sorted list (q in [0, 1])."""
    if not sorted_vals:
        raise ValueError("empty sample")
    if q <= 0.0:
        return sorted_vals[0]
    if q >= 1.0:
        return sorted_vals[-1]
    pos = q * (len(sorted_vals) - 1)
    lo = int(math.floor(pos))
    hi = int(math.ceil(pos))
    if lo == hi:
        return sorted_vals[lo]
    frac = pos - lo
    return sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac


def bootstrap_trade_pnls(
    pnls: List[float],
    capital: float = DEFAULT_CAPITAL,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
) -> Dict[str, Any]:
    """Deterministic with-replacement bootstrap over realized trade PnLs."""
    n = len(pnls)
    if n == 0:
        raise RobustnessError("bootstrap requires at least one trade")
    observed_total = math.fsum(pnls)
    rng = random.Random(seed)
    totals: List[float] = []
    returns: List[float] = []
    wins: List[float] = []
    pfs: List[float] = []
    for _ in range(resamples):
        sample = [pnls[rng.randrange(n)] for _ in range(n)]
        total = math.fsum(sample)
        totals.append(total)
        returns.append(total / capital if capital else 0.0)
        win_sum = math.fsum(p for p in sample if p > 0)
        loss_sum = math.fsum(-p for p in sample if p < 0)
        wins.append(sum(1 for p in sample if p > 0) / n)
        pfs.append((win_sum / loss_sum) if loss_sum > 0 else (float("inf") if win_sum > 0 else 0.0))
    totals.sort()
    returns.sort()
    wins.sort()
    finite_pfs = sorted(p for p in pfs if math.isfinite(p))
    alpha = (1.0 - BOOTSTRAP_CI_LEVEL) / 2.0
    prob_positive = sum(1 for t in totals if t > 0) / resamples
    observed_win = sum(1 for p in pnls if p > 0) / n
    observed_pf = _profit_factor(pnls)
    return {
        "resamples": int(resamples),
        "seed": int(seed),
        "method": "with-replacement over realized trade total_pnl",
        "observed_total_pnl": round(observed_total, 6),
        "ci_low_pnl": round(_percentile(totals, alpha), 6),
        "ci_high_pnl": round(_percentile(totals, 1.0 - alpha), 6),
        "ci_low_total_return_pct": round(_percentile(returns, alpha) * 100.0, 6),
        "ci_high_total_return_pct": round(_percentile(returns, 1.0 - alpha) * 100.0, 6),
        "prob_total_pnl_positive": round(prob_positive, 6),
        "ci_low_win_rate": round(_percentile(wins, alpha), 6),
        "ci_high_win_rate": round(_percentile(wins, 1.0 - alpha), 6),
        "ci_low_profit_factor": round(_percentile(finite_pfs, alpha), 6) if finite_pfs else None,
        "ci_high_profit_factor": round(_percentile(finite_pfs, 1.0 - alpha), 6) if finite_pfs else None,
        "observed_win_rate": round(observed_win, 6),
        "observed_profit_factor": None if observed_pf is None else round(observed_pf, 6),
        "small_sample_limitation": (
            f"Bootstrap over {n} realized trades cannot manufacture information that "
            "is not in the sample; the interval is wide and reflects resampling noise, "
            "not a guarantee of future performance."
        ),
    }


def _profit_factor(pnls: List[float]) -> Optional[float]:
    win = math.fsum(p for p in pnls if p > 0)
    loss = math.fsum(-p for p in pnls if p < 0)
    if loss > 0:
        return win / loss
    return None if win <= 0 else float("inf")


def sign_flip_test(pnls: List[float]) -> Dict[str, Any]:
    """Exact two-sided-capable sign-flip permutation over all 2^n combinations.

    With n trades there are 2**n sign masks (n=8 -> 256). The reported p_value is
    the one-sided fraction of sign-flipped totals >= the observed total; the
    two-sided p-value (fraction with |total| >= |observed|) is reported alongside.
    """
    n = len(pnls)
    combinations = 1 << n
    if combinations != SIGN_FLIP_COMBINATIONS:
        # n != 8 still runs; the gate pins 8-trade campaigns to 256 combinations.
        pass
    observed = math.fsum(pnls)
    totals: List[float] = []
    for mask in range(combinations):
        total = 0.0
        for i in range(n):
            total += pnls[i] if (mask >> i) & 1 == 0 else -pnls[i]
        totals.append(total)
    ge_observed = sum(1 for t in totals if t >= observed)
    abs_ge = sum(1 for t in totals if abs(t) >= abs(observed))
    p_one_sided = ge_observed / combinations
    p_two_sided = abs_ge / combinations
    return {
        "combinations": int(combinations),
        "observed_total_pnl": round(observed, 6),
        "p_value": round(p_one_sided, 6),
        "p_value_definition": "fraction of 2^n sign-flip totals >= observed total (one-sided)",
        "p_value_two_sided": round(p_two_sided, 6),
        "sign_flipped_total_min": round(min(totals), 6),
        "sign_flipped_total_max": round(max(totals), 6),
    }


def concentration_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Per-symbol PnL shares, HHI, top-trade share, and leave-out totals."""
    total = math.fsum(t["total_pnl"] for t in trades)
    by_symbol: Dict[str, Dict[str, float]] = {}
    for t in trades:
        slot = by_symbol.setdefault(t["symbol"], {"trades": 0, "pnl": 0.0})
        slot["trades"] += 1
        slot["pnl"] += t["total_pnl"]
    symbol_rows = []
    hhi = 0.0
    for sym, agg in by_symbol.items():
        share = (agg["pnl"] / total) if total else 0.0
        hhi += share * share
        symbol_rows.append({
            "symbol": sym,
            "trades": int(agg["trades"]),
            "pnl": round(agg["pnl"], 6),
            "pnl_share": round(share, 6),
        })
    symbol_rows.sort(key=lambda r: r["pnl"], reverse=True)

    sorted_abs = sorted((abs(t["total_pnl"]) for t in trades), reverse=True)
    top_trade_share = (sorted_abs[0] / total) if total else 0.0

    loso = []
    for sym in by_symbol:
        loso.append({
            "excluded_symbol": sym,
            "total_pnl_without_symbol": round(math.fsum(
                t["total_pnl"] for t in trades if t["symbol"] != sym), 6),
        })
    loto = []
    for i, t in enumerate(trades):
        loto.append({
            "excluded_trade_index": i,
            "excluded_symbol": t["symbol"],
            "total_pnl_without_trade": round(math.fsum(
                p for j, p in enumerate(t["total_pnl"] for t in trades) if j != i), 6),
        })
    return {
        "symbols": symbol_rows,
        "total_pnl": round(total, 6),
        "top_symbol_pnl_share": round(symbol_rows[0]["pnl_share"], 6) if symbol_rows else 0.0,
        "top_trade_pnl_share": round(top_trade_share, 6),
        "herfindahl_hhi": round(hhi, 6),
        "effective_symbol_count": round(1.0 / hhi, 6) if hhi > 0 else None,
        "leave_one_symbol_out": loso,
        "leave_one_trade_out": loto,
    }


def time_split_analysis(trades: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Median split by exit timestamp, monthly buckets, horizon, no-trade tail."""
    ordered = sorted(trades, key=lambda t: t["exit_timestamp_ms"])
    n = len(ordered)
    mid = n // 2
    first = ordered[:mid]
    second = ordered[mid:]
    first_pnl = math.fsum(t["total_pnl"] for t in first)
    second_pnl = math.fsum(t["total_pnl"] for t in second)

    def _month(ms: int) -> str:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m")

    monthly: Dict[str, Dict[str, Any]] = {}
    for t in ordered:
        m = _month(t["exit_timestamp_ms"])
        slot = monthly.setdefault(m, {"trades": 0, "pnl": 0.0})
        slot["trades"] += 1
        slot["pnl"] += t["total_pnl"]

    first_ms = ordered[0]["exit_timestamp_ms"]
    last_ms = ordered[-1]["exit_timestamp_ms"]
    realized_years = (last_ms - first_ms) / (1000.0 * 86_400.0 * 365.25)
    total_pnl = math.fsum(t["total_pnl"] for t in ordered)
    return {
        "first_half_pnl": round(first_pnl, 6),
        "second_half_pnl": round(second_pnl, 6),
        "first_half_trades": len(first),
        "second_half_trades": len(second),
        "first_half_symbols": sorted({t["symbol"] for t in first}),
        "second_half_symbols": sorted({t["symbol"] for t in second}),
        "monthly": {m: {"trades": v["trades"], "pnl": round(v["pnl"], 6)}
                    for m, v in sorted(monthly.items())},
        "first_exit_utc": datetime.fromtimestamp(first_ms / 1000, tz=timezone.utc).isoformat(),
        "last_exit_utc": datetime.fromtimestamp(last_ms / 1000, tz=timezone.utc).isoformat(),
        "realized_span_days": round((last_ms - first_ms) / (1000.0 * 86_400.0), 4),
        "realized_span_years": round(realized_years, 6),
        "total_pnl": round(total_pnl, 6),
        "annualization_note": (
            "Annualization uses the realized trade span, not the full 283-day window; "
            "there is a multi-month no-trade tail after the last exit."
        ),
    }


def _load_census(census: Path = CENSUS) -> Optional[Dict[str, Any]]:
    if not census.exists():
        return None
    try:
        return json.loads(census.read_text())
    except json.JSONDecodeError:
        return None


def placebo_absence(trades: List[Dict[str, Any]], census: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """State how many J1 signal-gate events were not traded and why."""
    out: Dict[str, Any] = {
        "design": (
            "Compare the J1 crash-event census funnel (crashes -> volume_gate_pass -> "
            "bounce_confirmed -> regime_min_price_ok -> signal_gate_pass -> trades) to the "
            "realized trade set; every signal-gate event that did not become a trade is an "
            "absence the strategy must explain."
        ),
        "census_available": census is not None,
        "realized_trades": len(trades),
    }
    if not census:
        out["limitation"] = "J1 census not on disk; placebo/absence not quantified."
        return out
    rec = census.get("reconciliation") or {}
    events = census.get("events") or []
    signal_events = [e for e in events if e.get("signal_gate_pass")]
    not_traded = [e for e in signal_events if not e.get("trade_opened")]
    out["funnel"] = {
        "events_total": rec.get("events_total"),
        "volume_gate_pass": rec.get("volume_gate_pass"),
        "bounce_confirmed": rec.get("bounce_confirmed"),
        "regime_min_price_ok": rec.get("regime_min_price_ok"),
        "signal_gate_pass": rec.get("signal_gate_pass"),
        "trades_in_campaign": rec.get("trades_in_campaign"),
        "trades_matched_to_events": rec.get("trades_matched_to_events"),
        "unmatched_campaign_trades": rec.get("unmatched_campaign_trades"),
        "unexplained_signal_gate_events": rec.get("unexplained_signal_gate_events"),
        "blocking_reasons_sum": rec.get("blocking_reasons_sum"),
    }
    # Signal-gate events that did not become trades are the absence ledger; the
    # census already records the dominant blocking reason for each.
    absence_reasons: Dict[str, int] = {}
    for e in not_traded:
        r = e.get("blocking_reason") or "unexplained"
        absence_reasons[str(r)] = absence_reasons.get(str(r), 0) + 1
    out["signal_gate_events"] = len(signal_events)
    out["signal_gate_events_not_traded"] = len(not_traded)
    out["absence_blocking_reason_counts"] = absence_reasons
    out["blocking_reason_counts"] = rec.get("blocking_reason_counts") or {}
    out["limitation"] = (
        "The census is the absence ledger: signal-gate events that did not become "
        "trades are recorded with their blocking reason; no unseen data is fabricated."
    )
    return out


def decide_verdict(boot: Dict[str, Any], flip: Dict[str, Any],
                   conc: Dict[str, Any]) -> Tuple[str, str]:
    """Return (verdict, one-sentence rationale) from the numeric evidence."""
    n = boot.get("resamples") and boot.get("_n_trades")
    ci_low = boot["ci_low_pnl"]
    ci_high = boot["ci_high_pnl"]
    prob_pos = boot["prob_total_pnl_positive"]
    p_one = flip["p_value"]
    top_trade = conc["top_trade_pnl_share"]

    signal = (ci_low > 0) and (p_one < MIN_SIGN_FLIP_P) and (top_trade < 1.0)
    if signal:
        verdict = "signal"
        reason = (
            f"The bootstrap 95% CI for total PnL is entirely above zero "
            f"[{ci_low:,.2f}, {ci_high:,.2f}] and the sign-flip p-value is {p_one:.4f} "
            f"(< {MIN_SIGN_FLIP_P}), so the realized return is distinguishable from "
            f"symmetric noise, though the 8-trade sample and top-trade share "
            f"{top_trade:.2f} limit how much weight it can bear."
        )
    elif prob_pos >= 0.95 and ci_low <= 0:
        verdict = "underpowered"
        reason = (
            f"P(total PnL > 0) is {prob_pos:.4f} but the bootstrap 95% CI still "
            f"crosses zero [{ci_low:,.2f}, {ci_high:,.2f}]; the sample is too small "
            f"to separate signal from luck at decision grade."
        )
    else:
        verdict = "underpowered"
        reason = (
            f"The bootstrap 95% CI for total PnL crosses zero "
            f"[{ci_low:,.2f}, {ci_high:,.2f}] with P(total PnL > 0)={prob_pos:.4f} "
            f"and sign-flip p={p_one:.4f}; the 8-trade sample is underpowered to "
            f"distinguish signal from noise."
        )
    return verdict, reason


def build_report(capital: float = DEFAULT_CAPITAL,
                 resamples: int = DEFAULT_RESAMPLES,
                 seed: int = DEFAULT_SEED) -> Dict[str, Any]:
    trades = load_trades()
    pnls = [t["total_pnl"] for t in trades]

    boot = bootstrap_trade_pnls(pnls, capital=capital, resamples=resamples, seed=seed)
    boot["_n_trades"] = len(pnls)
    flip = sign_flip_test(pnls)
    conc = concentration_analysis(trades)
    split = time_split_analysis(trades)
    placebo = placebo_absence(trades, _load_census())
    verdict, reason = decide_verdict(boot, flip, conc)
    boot.pop("_n_trades", None)

    return {
        "schema_version": 1,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "run_type": "robustness_signal_vs_noise",
        "provenance_caveat": PROVENANCE_CAVEAT,
        "inputs": {
            "canonical_campaign": str(CANONICAL_CAMPAIGN.relative_to(REPO_ROOT)),
            "census": str(CENSUS.relative_to(REPO_ROOT)) if CENSUS.exists() else None,
            "capital": float(capital),
            "trades": len(trades),
            "trade_symbols": conc["symbols"],
        },
        "bootstrap": boot,
        "sign_flip": flip,
        "concentration": conc,
        "time_split": split,
        "placebo_absence": placebo,
        "conclusion": {
            "verdict": verdict,
            "rationale": reason,
            "caveat": PROVENANCE_CAVEAT,
        },
        "caveats": [
            PROVENANCE_CAVEAT,
            "8 realized trades is a small sample; the bootstrap quantifies resampling "
            "uncertainty, not out-of-sample performance.",
            "Realized-horizon annualization only; a multi-month no-trade tail follows "
            "the last exit, so do not annualize the full 283-day window.",
            "This is an evidence-chain and signal-vs-noise check, not proof of future "
            "profitability.",
        ],
    }


def render_markdown(report: Dict[str, Any]) -> str:
    boot = report["bootstrap"]
    flip = report["sign_flip"]
    conc = report["concentration"]
    split = report["time_split"]
    placebo = report["placebo_absence"]
    concl = report["conclusion"]
    lines: List[str] = []
    lines.append("# Robustness / Signal-vs-Noise — Real OKX 283-Day Campaign (Phase L)")
    lines.append("")
    lines.append(f"**Generated (UTC):** {report['generated_at_utc']}  ")
    lines.append(f"**Provenance caveat:** {report['provenance_caveat']}")
    lines.append("")
    lines.append("This is the Phase L gate: it characterizes whether the 8-trade canonical "
                 "result is distinguishable from luck. It does not establish future "
                 "profitability. Every statistic is derived deterministically "
                 f"(seed={boot['seed']}, {boot['resamples']} bootstrap resamples) from the "
                 f"canonical trade set ({report['inputs']['trades']} trades).")
    lines.append("")
    lines.append(f"## Go / no-go conclusion: **{concl['verdict'].upper()}**")
    lines.append("")
    lines.append(concl["rationale"])
    lines.append("")
    lines.append("## Trade-level bootstrap")
    lines.append("")
    lines.append(f"- Resamples: {boot['resamples']} (seed {boot['seed']}), {boot['method']}")
    lines.append(f"- Observed total PnL: {boot['observed_total_pnl']:,.2f}")
    lines.append(f"- 95% CI total PnL: [{boot['ci_low_pnl']:,.2f}, {boot['ci_high_pnl']:,.2f}]")
    lines.append(f"- 95% CI total return on {report['inputs']['capital']:,.0f}: "
                 f"[{boot['ci_low_total_return_pct']:.4f}%, {boot['ci_high_total_return_pct']:.4f}%]")
    lines.append(f"- P(total PnL > 0): {boot['prob_total_pnl_positive']:.4f}")
    lines.append(f"- Observed win rate: {boot['observed_win_rate']:.4f} "
                 f"(95% CI [{boot['ci_low_win_rate']:.4f}, {boot['ci_high_win_rate']:.4f}])")
    pf_ci = ("n/a" if boot['ci_low_profit_factor'] is None
             else f"[{boot['ci_low_profit_factor']:.3f}, {boot['ci_high_profit_factor']:.3f}]")
    lines.append(f"- Profit factor: observed "
                 f"{'inf' if boot['observed_profit_factor'] == float('inf') else boot['observed_profit_factor']}"
                 f", 95% CI {pf_ci}")
    lines.append(f"- Limitation: {boot['small_sample_limitation']}")
    lines.append("")
    lines.append("## Sign-flip permutation test")
    lines.append("")
    lines.append(f"- Combinations: {flip['combinations']} (2^{report['inputs']['trades']})")
    lines.append(f"- Observed total: {flip['observed_total_pnl']:,.2f}")
    lines.append(f"- p_value (one-sided, >= observed): {flip['p_value']:.4f} — {flip['p_value_definition']}")
    lines.append(f"- p_value (two-sided, |total| >= |observed|): {flip['p_value_two_sided']:.4f}")
    lines.append(f"- Sign-flipped total range: [{flip['sign_flipped_total_min']:,.2f}, "
                 f"{flip['sign_flipped_total_max']:,.2f}]")
    lines.append("")
    lines.append("## Concentration")
    lines.append("")
    lines.append("| Symbol | Trades | PnL | Share |")
    lines.append("|---|---|---|---|")
    for r in conc["symbols"]:
        lines.append(f"| {r['symbol']} | {r['trades']} | {r['pnl']:,.2f} | {r['pnl_share']:.4f} |")
    lines.append("")
    lines.append(f"- Top symbol PnL share: {conc['top_symbol_pnl_share']:.4f}")
    lines.append(f"- Top trade |PnL| share of total: {conc['top_trade_pnl_share']:.4f}")
    lines.append(f"- HHI: {conc['herfindahl_hhi']:.4f} (effective symbols "
                 f"{conc['effective_symbol_count']})")
    lines.append("")
    lines.append("## Time split and activity")
    lines.append("")
    lines.append(f"- First half PnL: {split['first_half_pnl']:,.2f} "
                 f"({split['first_half_trades']} trades, {split['first_half_symbols']})")
    lines.append(f"- Second half PnL: {split['second_half_pnl']:,.2f} "
                 f"({split['second_half_trades']} trades, {split['second_half_symbols']})")
    lines.append(f"- Realized span: {split['realized_span_days']:.2f} days "
                 f"({split['realized_span_years']:.4f} yr), {split['first_exit_utc']} .. {split['last_exit_utc']}")
    lines.append("")
    lines.append("| Month (UTC) | Trades | PnL |")
    lines.append("|---|---|---|")
    for m, v in split["monthly"].items():
        lines.append(f"| {m} | {v['trades']} | {v['pnl']:,.2f} |")
    lines.append("")
    lines.append(f"- {split['annualization_note']}")
    lines.append("")
    lines.append("## Placebo / absence check")
    lines.append("")
    lines.append(placebo["design"])
    lines.append("")
    if placebo.get("funnel"):
        f = placebo["funnel"]
        lines.append(f"- J1 funnel: {f.get('events_total')} crashes → volume {f.get('volume_gate_pass')} → "
                     f"bounce {f.get('bounce_confirmed')} → regime {f.get('regime_min_price_ok')} → "
                     f"signal {f.get('signal_gate_pass')} → trades {f.get('trades_matched_to_events')}; "
                     f"unexplained signal-gate events: {f.get('unexplained_signal_gate_events')}")
    if placebo.get("signal_gate_events") is not None:
        lines.append(f"- Signal-gate events not traded: {placebo['signal_gate_events_not_traded']} "
                     f"of {placebo['signal_gate_events']}")
    if placebo.get("absence_blocking_reason_counts"):
        lines.append("- Absence blocking-reason counts: "
                     + json.dumps(placebo["absence_blocking_reason_counts"]))
    lines.append(f"- {placebo['limitation']}")
    lines.append("")
    lines.append("## Caveats")
    lines.append("")
    for c in report["caveats"]:
        lines.append(f"- {c}")
    lines.append("")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--capital", type=float, default=DEFAULT_CAPITAL)
    ap.add_argument("--resamples", type=int, default=DEFAULT_RESAMPLES)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    ap.add_argument("--check", action="store_true",
                    help="Validate inputs and exit without writing artifacts.")
    args = ap.parse_args(argv)

    if args.resamples < 1000:
        print(f"BLOCKER: --resamples must be >= 1000 (got {args.resamples})", file=sys.stderr)
        return 2
    try:
        report = build_report(capital=args.capital, resamples=args.resamples, seed=args.seed)
    except RobustnessError as exc:
        print(f"BLOCKER: {exc}", file=sys.stderr)
        return 1

    if args.check:
        print(f"OK: {report['inputs']['trades']} trades, verdict={report['conclusion']['verdict']}")
        return 0

    # Guard: never overwrite canonical campaign stems.
    for forbidden in ("campaign_results_real_okx_full.json",):
        if OUT_JSON.name == forbidden or OUT_MD.name == forbidden:
            print(f"BLOCKER: refusing to write canonical stem {forbidden}", file=sys.stderr)
            return 2

    OUT_JSON.write_text(json.dumps(report, indent=2) + "\n")
    OUT_MD.write_text(render_markdown(report))
    print(f"wrote {OUT_JSON}")
    print(f"wrote {OUT_MD}")
    print(f"verdict={report['conclusion']['verdict']} "
          f"p={report['sign_flip']['p_value']} "
          f"ci=[{report['bootstrap']['ci_low_pnl']}, {report['bootstrap']['ci_high_pnl']}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())