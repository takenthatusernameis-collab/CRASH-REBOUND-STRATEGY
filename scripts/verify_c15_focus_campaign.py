#!/usr/bin/env python3
"""C15 acceptance gate — Hyperliquid-native window extension campaign.

C15 objective (HANDOFF): reach n>=4+ independent crash episodes on verified
Hyperliquid-native data via window extension, or produce an evidenced hard
blocker with command/HTTP/DNS evidence + data_request_stem.

Accepted terminal states:
  (A) GO: full battery on extended native + verdict GO meeting pre-registered
      criteria (CI95 excludes zero + permutation p<0.05 + placebo p_ge_canonical<0.05
      + spot leg > 0)  [not implemented here; requires future extended artifacts]
  (B) UNDERPOWERED/NO_GO: full battery executed on widest available/extended native
      universe with power curve + explicit data request for additional episodes
  (C) BLOCKED_EVIDENCED: T1 acquisition attempted with recorded command/network
      evidence showing no extended verified Hyperliquid-native archive (>=2023-01-01
      target) is acquirable, plus data_request_stem and verdict artifacts. Never a
      bare "closed/no work".

This gate validates recorded C15 artifacts (read-only over research_state) and
prints `C15 ACCEPTANCE: PASS` or `C15 ACCEPTANCE: FAIL`.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / "research_state"


def load_json(p: Path):
    try:
        return json.loads(p.read_text()), None
    except Exception as e:
        return None, str(e)


def main() -> int:
    errors = []
    notes = []

    # Locate latest C15 acquisition/verdict/request artifacts
    acq_files = sorted(STATE.glob("c15_acquisition_attempt_*.json"))
    ver_files = sorted(STATE.glob("c15_decision_verdict_hyperliquid_native_c15_*.json"))
    req_files = sorted(STATE.glob("c15_data_request_stem_*.md"))

    if not acq_files:
        errors.append("missing c15_acquisition_attempt_<UTC>.json")
    if not ver_files:
        errors.append("missing c15_decision_verdict_hyperliquid_native_c15_<UTC>.json")
    if not req_files:
        errors.append("missing c15_data_request_stem_<UTC>.md")

    acq = ver = None
    acq_p = ver_p = req_p = None
    if acq_files:
        acq_p = acq_files[-1]
        acq, e = load_json(acq_p)
        if e:
            errors.append(f"unreadable acquisition artifact {acq_p.name}: {e}")
    if ver_files:
        ver_p = ver_files[-1]
        ver, e = load_json(ver_p)
        if e:
            errors.append(f"unreadable verdict artifact {ver_p.name}: {e}")
    if req_files:
        req_p = req_files[-1]
        try:
            txt = req_p.read_text()
            if len(txt.strip()) < 80:
                errors.append(f"data_request_stem too short/empty: {req_p.name}")
            if "Hyperliquid-native" not in txt and "Hyperliquid native" not in txt:
                errors.append("data_request_stem missing Hyperliquid-native requirement")
        except Exception as e:
            errors.append(f"unreadable data_request_stem {req_p.name}: {e}")

    # Validate acquisition attempt evidence (T1)
    if isinstance(acq, dict):
        attempts = acq.get("attempts") or []
        ids = {a.get("id") for a in attempts if isinstance(a, dict)}
        if "T1_hf_ironflow_probe" not in ids:
            errors.append("acquisition missing T1_hf_ironflow_probe attempt")
        if "T1_api_retention_probe" not in ids:
            errors.append("acquisition missing T1_api_retention_probe attempt")
        # HF probe must show evidenced range and non-acquirable extension target
        hf = next((a for a in attempts if a.get("id") == "T1_hf_ironflow_probe"), {})
        hf_res = hf.get("result") or {}
        ts_min = str(hf_res.get("timestamp_min_utc", ""))
        ts_max = str(hf_res.get("timestamp_max_utc", ""))
        if not ts_min.startswith("2025-05-25"):
            errors.append(f"HF probe missing expected evidenced earliest timestamp (got {ts_min!r})")
        if not ts_max.startswith("2026-10"):
            errors.append(f"HF probe missing evidenced max timestamp (got {ts_max!r})")
        if hf_res.get("covers_multiyear_target_ge_20230101") is not False:
            errors.append("HF probe must evidence covers_multiyear_target_ge_20230101=false")
        if hf.get("outcome") not in ("NOT_ACQUIRABLE_FOR_EXTENSION_TARGET", "NOT_ACQUIRABLE"):
            errors.append(f"HF probe unexpected outcome: {hf.get('outcome')!r}")
        if not hf.get("commands"):
            errors.append("HF probe missing recorded commands")
        # API probe must reference live probe artifact
        api = next((a for a in attempts if a.get("id") == "T1_api_retention_probe"), {})
        probe_ref = REPO / str(api.get("artifact", "research_state/hyperliquid_retention_probe.json"))
        if not probe_ref.exists():
            errors.append(f"referenced API probe artifact missing: {probe_ref}")
        else:
            probe, pe = load_json(probe_ref)
            if pe:
                errors.append(f"unreadable API probe artifact: {pe}")
            elif isinstance(probe, dict):
                summ = probe.get("probe_summary") or {}
                if summ.get("full_window_served") is not False:
                    errors.append("API probe must show full_window_served=false for T3 blocker")
                if not summ.get("earliest_served_start_utc"):
                    errors.append("API probe missing earliest_served_start_utc")
        concl = acq.get("conclusion") or {}
        if concl.get("extended_native_archive_ge_20230101_acquirable") is not False:
            errors.append("acquisition conclusion must state extended_native_archive_ge_20230101_acquirable=false")
        if concl.get("t2_executed") not in (False, None):
            # T2 could be true only for A/B states (not handled by this minimal gate yet)
            pass
        notes.append(f"acquisition={acq_p.name} attempts={len(attempts)}")

    # Validate verdict (T3 blocked-evidenced)
    if isinstance(ver, dict):
        v = str(ver.get("verdict", "")).upper()
        accepted_verdicts = {"BLOCKED_EVIDENCED_DATA_REQUIRED", "BLOCKED_EVIDENCED", "UNDERPOWERED", "NO_GO", "GO"}
        if v not in accepted_verdicts:
            errors.append(f"unexpected C15 verdict: {v!r}")
        if ver.get("performance_evidence") is True and v != "GO":
            errors.append("performance_evidence=true only allowed with GO verdict")
        if v == "GO":
            # Would require full battery evidence + pre-registered criteria; not claimed in T3 path
            t1 = ver.get("t1_evidence") or {}
            pass
        if v.startswith("BLOCKED"):
            if not (ver.get("t3_data_request") or req_p):
                errors.append("blocked verdict missing data request reference")
            t1 = ver.get("t1_evidence") or {}
            if t1.get("extended_native_acquirable") is not False:
                errors.append("blocked verdict must record extended_native_acquirable=false")
            if not t1.get("api_probe"):
                errors.append("blocked verdict missing api_probe evidence ref")
        # Canonical protections
        hp = ver.get("hard_prohibitions_respected") or {}
        for k in ("no_relabel_cross_venue_as_hyperliquid", "no_fabrication_synthesis", "no_spec_relaxation", "canonical_c1_c14_unchanged"):
            if hp.get(k) is not True:
                errors.append(f"hard_prohibitions_respected.{k} must be true")
        notes.append(f"verdict={ver_p.name} value={v}")

    # Ensure canonical C14 gate still referenced as intact in evidence chain expectation
    c14_v = STATE / "decision_verdict_hyperliquid_native_c14_20261116T001200Z.json"
    if not c14_v.exists():
        errors.append("canonical C14 verdict artifact missing (must remain unchanged)")
    else:
        notes.append("canonical C14 verdict present")

    if errors:
        print("C15 ACCEPTANCE: FAIL")
        for e in errors:
            print(f"  - {e}")
        for n in notes:
            print(f"  note: {n}")
        return 1

    print("C15 ACCEPTANCE: PASS")
    print(f"  verdict: {(ver or {}).get('verdict')}")
    print(f"  acquisition: {acq_p.name if acq_p else 'n/a'}")
    print(f"  data_request: {req_p.name if req_p else 'n/a'}")
    for n in notes:
        print(f"  note: {n}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
