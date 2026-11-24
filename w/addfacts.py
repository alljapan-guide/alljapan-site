import json,sys
sys.path.insert(0,'.')
from pipeline import facts as F
def add(new, only_verify=True):
    f=json.load(open('data/facts.json')); ids={x['id'] for x in f}
    for n in new:
        assert n['id'] not in ids, n['id']
        f.append(n)
    open('data/facts.json','w').write(json.dumps(f,indent=1,ensure_ascii=False)+'\n')
    r=F.verify(only={n['id'] for n in new})
    bad={k:v for k,v in r.items() if not v[0]}
    print('verified',len(r)-len(bad),'of',len(r)); print(bad or 'all OK')
