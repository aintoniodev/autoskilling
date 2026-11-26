import json,re,glob,statistics as st,sys,random
def load(L):
    d={}
    for p in glob.glob(f"scores/{L}/*.json"):
        b=p.split('/')[-1].split('.')[0]
        try: d.setdefault(b,[]).append(float(json.loads(re.search(r"\{.*\}",open(p).read(),re.S).group(0))["total"]))
        except Exception: pass
    out={}
    for b,v in d.items(): out[b]={"rubric":st.mean(v)}
    for p in glob.glob(f"holistic/{L}/*.json"):
        b=p.split('/')[-1][:-5]
        try:
            h=json.loads(re.search(r"\{.*\}",open(p).read(),re.S).group(0))
            out.setdefault(b,{}).update({k:float(h[k]) for k in ("launch","noticed","lasting")})
        except Exception: pass
    return [x for x in out.values() if len(x)==4]
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
