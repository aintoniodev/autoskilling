#!/bin/bash
# usage: holistic.sh <label> ; rubric-free blind judge (claude sonnet) to guard against rubric leakage.
set -u; cd "$(dirname "$0")"; L=$1; mkdir -p holistic/$L
for f in designs/$L/*.md; do
  b=$(basename $f .md); s=${b%%-*}; o=holistic/$L/$b.json; [ -s $o ] && continue
  SC=$(awk -v s="$s." '$1==s{f=1;print;next} f&&/^    /{print;next} {f=0}' ../scenarios.md)
  P="You are an experienced operations leader who has run several employee incentive programmes, some that worked and some that backfired. Read this proposal for the scenario. Output ONLY JSON: {\"launch\": <0-100, how confident you are you would approve it as written>, \"noticed\": <0-100, how likely employees notice it and feel motivated to try>, \"lasting\": <0-100, likelihood the behaviour change lasts 3 months after it ends>, \"reason\": \"<one sentence>\"}.

<scenario>
$SC
</scenario>

<proposal>
$(cat $f)
</proposal>"
  ( claude -p --model sonnet "$P" </dev/null > $o 2>/dev/null ) &
done; wait
python3 - "$L" <<'PY'
import json,re,sys,glob,statistics as st
L=sys.argv[1]; k={"launch":[],"noticed":[],"lasting":[]}; w=[]
for p in glob.glob(f"holistic/{L}/*.json"):
    m=re.search(r"\{.*\}",open(p).read(),re.S)
    try: d=json.loads(m.group(0))
    except Exception: continue
    for x in k: k[x].append(float(d[x]))
for p in glob.glob(f"designs/{L}/*.md"): w.append(len(open(p).read().split()))
print(L," ".join(f"{x} {st.mean(v):.1f}" for x,v in k.items()), f"words {st.mean(w):.0f}")
PY
