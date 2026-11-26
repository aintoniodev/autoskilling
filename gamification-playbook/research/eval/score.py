import json,re,sys,glob,statistics as st
L=sys.argv[1]; rows={}
for p in sorted(glob.glob(f"scores/{L}/*.json")):
    t=open(p).read(); m=re.search(r"\{.*\}",t,re.S)
    try: tot=float(json.loads(m.group(0))["total"])
    except Exception: print("unparsed",p); continue
    b,j=p.split("/")[-1].rsplit(".",2)[:2]; rows.setdefault(j,{})[b]=tot
runs={}
for j,d in rows.items():
    for b,v in d.items(): runs.setdefault(b.split("-")[1],[]).append(v)
per_run=[st.mean(v) for v in runs.values()]
print(f"{L}: mean {st.mean([v for d in rows.values() for v in d.values()]):.1f}  per-run {[round(x,1) for x in per_run]}  sd {st.pstdev(per_run):.1f}  " + "  ".join(f"{j} {st.mean(d.values()):.1f}" for j,d in rows.items()))
