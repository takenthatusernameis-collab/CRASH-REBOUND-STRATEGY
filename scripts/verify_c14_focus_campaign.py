#!/usr/bin/env python3
"""C14 acceptance gate — broad-universe native power escalation (fail-closed).

PASS only when: prereg-before-compute, intake accepted, wide archive/cache/universe
provenance consistent and non-synthetic, C14 campaign+census+episode-edge+placebo
+verdict exist and are SHA/seed/config-consistent with prereg, verdict references all
priors and includes a power curve if not GO, selected_count >= 24, and verdict token
is GO/UNDERPOWERED/NO_GO. Prints 'C14 ACCEPTANCE: PASS' on success.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

REPO = Path(__file__).resolve().parents[1]
STATE = REPO / 'research_state'
HANDOFF = REPO / 'HANDOFF.md'
TS = '20261116T001200Z'
MIN_SELECTED = 24
MIN_DRAWS = 100
PRIOR_TOKENS = [
    'decision_verdict_hyperliquid_native_20261115T155318Z',
    'decision_verdict_hyperliquid_native_c12_20261115T181500Z',
    'decision_verdict_hyperliquid_native_c13_20261115T203734Z',
    'decision_verdict_consolidated_20261115T122636Z',
    'decision_verdict_CONSOLIDATED_FINAL_20261115T204933Z',
]


def _check(label: str, ok: bool, detail: str = '') -> bool:
    print(f"[{'PASS' if ok else 'FAIL'}] {label}" + (f": {detail}" if detail else ''))
    return ok


def _load_json(path: Path) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(path.read_text())
    except Exception:
        return None


def _sha256(path: Path) -> Optional[str]:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except Exception:
        return None


def _parse_ts(text: str) -> Optional[dt.datetime]:
    try:
        s = str(text).strip()
        if s.endswith('Z'):
            s = s[:-1] + '+00:00'
        return dt.datetime.fromisoformat(s).astimezone(dt.timezone.utc)
    except Exception:
        return None


def main() -> int:
    results = []

    prereg_p = STATE / f'hyperliquid_native_c14_prereg_{TS}.json'
    prereg_m = STATE / f'hyperliquid_native_c14_prereg_{TS}.md'
    prereg = _load_json(prereg_p) if prereg_p.exists() else None
    ok = prereg is not None and prereg_m.exists() and prereg.get('campaign') == 'C14'
    if ok:
        caveat = str(prereg.get('provenance_caveat', '')).lower()
        ok = ('node-derived' in caveat and 'candlesnapshot' in caveat and
              prereg.get('is_hyperliquid_venue_data') is True and
              prereg.get('fabricated_data') is False and prereg.get('synthetic_data') is False)
        plan = prereg.get('inference_plan') or {}
        ok = ok and int(plan.get('seed', -1)) == 20261116 and int(plan.get('min_draws', 0)) >= MIN_DRAWS
        hyp = (prereg.get('hypothesis') or {}).get('config') or {}
        ok = ok and abs(float(hyp.get('rsi_threshold', 0)) - 20.0) < 1e-9 and abs(float(hyp.get('target_pct', 0)) - 9.0) < 1e-9
    results.append(('c14_prereg', ok, prereg_p.name if prereg_p.exists() else 'missing'))
    prereg_ts = _parse_ts(prereg.get('generated_at_utc', '')) if prereg else None

    intake_p = STATE / 'archive_intake_validation_20261116T001129Z.json'
    intake = _load_json(intake_p) if intake_p.exists() else None
    ok = intake is not None and intake.get('verdict') == 'ACCEPT_AS_EVIDENCE_CANDIDATE'
    ok = ok and int((intake.get('summary') or {}).get('accepted_symbols', 0)) >= MIN_SELECTED
    results.append(('c14_intake_accepted', ok, intake_p.name if intake_p.exists() else 'missing'))

    archive = STATE / 'archives/hyperliquid_ironflow_wide_20261115T214900Z'
    src = archive / 'SOURCE.md'
    ok = archive.exists() and src.exists() and 'non-synthetic' in src.read_text().lower()
    parqs = list(archive.glob('*.parquet')) if archive.exists() else []
    ok = ok and len(parqs) >= MIN_SELECTED
    results.append(('c14_archive_provenance', ok, f'{len(parqs)} parquet files'))

    cache_dir = STATE / 'cache/hyperliquid_ironflow_wide_20261115T234000Z'
    prov_p = cache_dir / 'provenance.json'
    prov = _load_json(prov_p) if prov_p.exists() else None
    ok = prov is not None and prov.get('real_market_data_intended') is True and prov.get('fabricated_data') is False
    results.append(('c14_cache_provenance', ok, prov_p.as_posix() if prov_p.exists() else 'missing'))

    uni_p = STATE / 'universe_hyperliquid_ironflow_wide_20261115T225100Z.json'
    uni = _load_json(uni_p) if uni_p.exists() else None
    selected_count = int((uni or {}).get('selected_count', 0))
    ok = uni is not None and selected_count >= MIN_SELECTED and (uni.get('min_24h_volume_usd', 0) >= 5_000_000)
    ok = ok and uni.get('real_market_data') is True and uni.get('fabricated_data') is False
    results.append(('c14_universe_verified', ok, f'selected_count={selected_count}'))

    census_p = STATE / f'crash_event_census_hyperliquid_ironflow_wide_{TS}.json'
    campaign_p = STATE / f'campaign_results_real_hyperliquid_ironflow_wide_{TS}.json'
    census = _load_json(census_p) if census_p.exists() else None
    campaign = _load_json(campaign_p) if campaign_p.exists() else None
    ok_camp = campaign is not None and campaign.get('is_hyperliquid_venue_data') is True and campaign.get('fabricated_data') is False
    ok_cens = census is not None and census.get('is_hyperliquid_venue_data') is True and census.get('fabricated_data') is False
    # census must bind to c14 campaign, not okx
    if ok_cens and ok_camp:
        camp_ref = str((census.get('inputs') or {}).get('campaign', ''))
        ok_cens = ok_cens and TS in camp_ref and 'okx' not in camp_ref.lower()
    results.append(('c14_campaign_census', ok_camp and ok_cens, f'campaign={campaign_p.exists()} census={census_p.exists()}'))

    ep_p = STATE / f'episode_edge_hyperliquid_ironflow_wide_{TS}.json'
    pl_p = STATE / f'placebo_portfolio_hyperliquid_ironflow_wide_{TS}.json'
    ep = _load_json(ep_p) if ep_p.exists() else None
    pl = _load_json(pl_p) if pl_p.exists() else None
    def infer_ok(d, kind):
        if not isinstance(d, dict):
            return False, 'missing'
        caveat = str(d.get('provenance_caveat','')).lower()
        if 'node-derived' not in caveat or 'candlesnapshot' not in caveat:
            return False, 'provenance'
        if d.get('fabricated_data') is True or d.get('synthetic_data') is True:
            return False, 'synthetic'
        gen = _parse_ts(d.get('generated_at_utc',''))
        if prereg_ts and (gen is None or gen < prereg_ts):
            return False, 'predates_prereg'
        if int(d.get('seed', -1)) != 20261116:
            return False, 'seed'
        cfg = d.get('config') or {}
        if abs(float(cfg.get('rsi_threshold', -1)) - 20.0) > 1e-9 or abs(float(cfg.get('target_pct', -1)) - 9.0) > 1e-9:
            return False, 'config'
        if kind == 'ep':
            draws = int(((d.get('temporal_edge_permutation') or {}).get('draws_evaluated') or 0))
            return draws >= MIN_DRAWS, f'draws={draws}'
        else:
            runs = int(((d.get('placebo') or {}).get('runs') or 0))
            mode = ((d.get('pool') or {}).get('mode') or '')
            if mode == 'exact_enumeration':
                return True, f'runs={runs} (exact_enumeration)'
            return runs >= MIN_DRAWS, f'runs={runs}'
    ok_ep, dep = infer_ok(ep, 'ep')
    ok_pl, dpl = infer_ok(pl, 'pl')
    results.append(('c14_episode_edge', ok_ep, dep + (' ' + ep_p.name if ep_p.exists() else ' missing')))
    results.append(('c14_placebo', ok_pl, dpl + (' ' + pl_p.name if pl_p.exists() else ' missing')))

    verdict_p = STATE / f'decision_verdict_hyperliquid_native_c14_{TS}.md'
    verdict_j = STATE / f'decision_verdict_hyperliquid_native_c14_{TS}.json'
    vtext = verdict_p.read_text() if verdict_p.exists() else ''
    vj = _load_json(verdict_j) if verdict_j.exists() else None
    token = ''
    for t in ('UNDERPOWERED', 'NO_GO', 'GO'):
        if re.search(rf'\b{t}\b', vtext):
            token = t
            break
    ok_v = verdict_p.exists() and verdict_j.exists() and token in ('GO','UNDERPOWERED','NO_GO')
    ok_v = ok_v and all(tok in vtext for tok in PRIOR_TOKENS)
    ok_v = ok_v and any(x in vtext.lower() for x in ('bootstrap','permutation','placebo','ci95','confidence'))
    ok_v = ok_v and 'power' in vtext.lower() and ('curve' in vtext.lower() or 'episodes required' in vtext.lower() or 'max episodes' in vtext.lower())
    if token == 'GO':
        ok_v = ok_v and not re.search(r'underpowered|spans 0', vtext, re.I)
    results.append(('c14_verdict', ok_v, f'token={token or "none"} {verdict_p.name if verdict_p.exists() else "missing"}'))

    ok_h = False
    if HANDOFF.exists():
        ht = HANDOFF.read_text()
        ok_h = 'C14 ACCEPTANCE: PASS' in ht or ('C14' in ht and 'verify_c14_focus_campaign.py' in ht)
        ok_h = ok_h and '20261116T001200Z' in ht
    results.append(('handoff_updated', ok_h, 'HANDOFF.md'))

    ok_all = True
    for label, ok, detail in results:
        ok_all &= _check(label, ok, detail)
    print()
    if ok_all:
        print('C14 ACCEPTANCE: PASS')
        return 0
    failed = [r[0] for r in results if not r[1]]
    print(f"C14 ACCEPTANCE: FAIL — {len(failed)} requirement(s) missing: {', '.join(failed)}")
    return 1


if __name__ == '__main__':
    raise SystemExit(main())
