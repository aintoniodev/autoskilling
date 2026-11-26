# usage: pack.py <label> ; folds scores/<label>/ and holistic/<label>/ into results.jsonl,
# replacing that label's lines. One line per design: rubric total and worst flaw per judge, plus the holistic scores.
import json,re,sys,glob,os
def obj(p):
    try: return json.loads(re.search(r"\{.*\}",open(p).read(),re.S).group(0))
    except Exception: return None
L=sys.argv[1]; rows={}
for p in glob.glob(f"scores/{L}/*.json"):
    b,j=os.path.basename(p).rsplit(".",2)[:2]; o=obj(p)
    if o and "total" in o: rows.setdefault(b,{"label":L,"design":b}).setdefault("rubric",{})[j]={"total":o["total"],"worst_flaw":o.get("worst_flaw")}
for p in glob.glob(f"holistic/{L}/*.json"):
    o=obj(p)
    if o: rows.setdefault(os.path.basename(p)[:-5],{"label":L,"design":os.path.basename(p)[:-5]})["holistic"]=o
keep=[l for l in open("results.jsonl")] if os.path.exists("results.jsonl") else []
keep=[l for l in keep if json.loads(l)["label"]!=L]+[json.dumps(rows[b],ensure_ascii=False)+"\n" for b in sorted(rows)]
keep.sort(key=lambda l:(json.loads(l)["label"],json.loads(l)["design"]))
open("results.jsonl","w").writelines(keep)
print(f"results.jsonl: {L} {len(rows)} designs")
