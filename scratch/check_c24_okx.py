import json, glob
files = sorted(glob.glob('research_state/c24_ckpt_d15_okx_*_20261119T013154Z.json'))
for f in files:
    d = json.load(open(f))
    perm = (d.get('episode') or {}).get('temporal_edge_permutation') or {}
    print('%-28s mode=%s exact=%s resampled=%s draws=%s wall=%s' % (
        f.split('/')[-1].replace('c24_ckpt_d15_','').replace('_20261119T013154Z.json',''),
        perm.get('mode'), perm.get('exact_null_space_size'), perm.get('exact_null_resampled'),
        perm.get('draws_evaluated'), perm.get('wall_seconds')))