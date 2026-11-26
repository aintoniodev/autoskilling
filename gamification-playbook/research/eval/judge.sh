#!/bin/bash
# usage: judge.sh <label> ; scores designs/<label>/*.md against ../rubric.md with two blind judges
# (codex gpt-6.2-sol high, claude opus). Writes scores/<label>/<design>.<judge>.json; prints mean.
set -u; cd "$(dirname "$0")"; L=$1; mkdir -p scores/$L
for f in designs/$L/*.md; do
  b=$(basename $f .md); s=${b%%-*}
  SC=$(awk -v s="$s." '$1==s{f=1;print;next} f&&/^    /{print;next} {f=0}' ../scenarios.md)
  P="You are a strict reviewer of workplace incentive-programme designs. Score the design below against the rubric. Judge only the design text; ignore length and style. Output ONLY a JSON object: {\"criteria\": {\"<criterion id>\": <0-10>, ...}, \"total\": <0-100, the rubric's weighted total>, \"worst_flaw\": \"<one sentence>\"}.

<rubric>
$(cat ../rubric.md)
</rubric>

<scenario>
$SC
</scenario>

<design>
$(cat $f)
</design>"
  [ -s scores/$L/$b.codex.json ] || ( CODEX_HOME=${CODEX_HOME:-$HOME/.codex} codex exec --skip-git-repo-check -s read-only -m gpt-6.2-sol -c model_reasoning_effort=high --output-last-message scores/$L/$b.codex.json "$P" </dev/null >/dev/null 2>&1 ) &
  [ -s scores/$L/$b.claude.json ] || ( claude -p --model opus "$P" </dev/null > scores/$L/$b.claude.json 2>/dev/null ) &
done; wait
python3 score.py $L
