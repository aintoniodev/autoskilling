# usage: pack.py <label> ; folds scores/<label>/ and holistic/<label>/ into results/<label>.jsonl,
# one line per design: rubric total and worst flaw per judge, plus the holistic scores.
import json,re,sys,glob,os
def obj(p):
    try: return json.loads(re.search(r"\{.*\}",open(p).read(),re.S).group(0))
    except Exception: return None
L=sys.argv[1]; rows={}
for p in glob.glob(f"scores/{L}/*.json"):
    b,j=os.path.basename(p).rsplit(".",2)[:2]; o=obj(p)
    if o and "total" in o: rows.setdefault(b,{"design":b}).setdefault("rubric",{})[j]={"total":o["total"],"worst_flaw":o.get("worst_flaw")}
for p in glob.glob(f"holistic/{L}/*.json"):
    o=obj(p)
    if o: rows.setdefault(os.path.basename(p)[:-5],{"design":os.path.basename(p)[:-5]})["holistic"]=o
os.makedirs("results",exist_ok=True)
with open(f"results/{L}.jsonl","w") as f:
    for b in sorted(rows): f.write(json.dumps(rows[b],ensure_ascii=False)+"\n")
print(f"results/{L}.jsonl: {len(rows)} designs")
