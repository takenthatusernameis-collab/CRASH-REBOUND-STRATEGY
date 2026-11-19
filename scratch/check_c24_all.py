import json, glob
files = sorted(glob.glob('research_state/c24_ckpt_d15_*_20261119T013154Z.json'))
for f in files:
    d = json.load(open(f))
    perm = (d.get('episode') or {}).get('temporal_edge_permutation') or {}
    print('%-24s mode=%-42s exact=%-8s draws=%-6s wall=%s' % (
        f.split('/')[-1].replace('c24_ckpt_d15_','').replace('_20261119T013154Z.json',''),
        str(perm.get('mode'))[:42], perm.get('exact_null_space_size'),
        perm.get('draws_evaluated'), perm.get('wall_seconds')))