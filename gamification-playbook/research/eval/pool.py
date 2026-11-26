# usage: pool.py B0=<labels joined by +> NAME=<labels> ... ; reads results/<label>.jsonl
import json,statistics as st,sys,random
def load(L):
    out=[]
    for line in open(f"results/{L}.jsonl"):
        r=json.loads(line); h=r.get("holistic",{}); j=r.get("rubric",{})
        if not j or not all(k in h for k in ("launch","noticed","lasting")): continue
        out.append({"rubric":st.mean(float(v["total"]) for v in j.values()),**{k:float(h[k]) for k in ("launch","noticed","lasting")}})
    return out
groups={g.split('=')[0]:sum((load(l) for l in g.split('=')[1].split('+')),[]) for g in sys.argv[1:]}
base=groups.pop("B0")
random.seed(1)
for g,xs in [("B0",base)]+list(groups.items()):
    line=f"{g:5} n={len(xs):2}"
    for k in ("rubric","launch","noticed","lasting"):
        m=st.mean(x[k] for x in xs)
        if g=="B0": line+=f"  {k} {m:.1f}"; continue
        diffs=[]
        for _ in range(4000):
            a=[random.choice(xs)[k] for _ in xs]; b=[random.choice(base)[k] for _ in base]
            diffs.append(st.mean(a)-st.mean(b))
        diffs.sort(); lo,hi=diffs[100],diffs[3899]
        line+=f"  {k} {m:.1f} ({m-st.mean(x[k] for x in base):+.1f} [{lo:+.1f},{hi:+.1f}])"
    print(line)
