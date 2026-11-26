#!/bin/bash
# usage: design.sh <label> <skillfile|none> ; writes designs/<label>/S<n>-r<k>.md (4 scenarios x 3 runs, parallel)
set -u; cd "$(dirname "$0")"; L=$1; SK=$2; mkdir -p designs/$L
PROMPT='Design an incentive programme for this scenario. Cover what is rewarded, how it is measured, what people see, how long it runs and how it ends, and what could go wrong. Be specific. Max 900 words. Reply with the design only.'
for s in 1 2 3 4; do
  SC=$(awk -v s="S$s." '$1==s{f=1;print;next} f&&/^    /{print;next} {f=0}' ../scenarios.md)
  for r in 1 2 3; do
    out=designs/$L/S$s-r$r.md; [ -s $out ] && continue
    if [ "$SK" = none ]; then P="$PROMPT

Scenario: $SC"; else P="Follow this skill:
<skill>
$(cat $SK)
</skill>

$PROMPT

Scenario: $SC"; fi
    ( CODEX_HOME=${CODEX_HOME:-$HOME/.codex} codex exec --skip-git-repo-check -s read-only -m gpt-6.2-sol -c model_reasoning_effort=medium --output-last-message $out "$P" </dev/null >/dev/null 2>&1 ) &
  done
done; wait; ls designs/$L | wc -l
