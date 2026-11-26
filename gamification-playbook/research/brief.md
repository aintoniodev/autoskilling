# Brief: an evidence-based gamification playbook skill

## Question
Which design principles should an agent skill teach so that an agent, asked to design a
workplace incentive programme ("make people adopt tool X / habit Y"), produces a design
that the empirical evidence says will change behaviour durably and not backfire?

Starting point: the principles of one real design (case.md, anonymised). Each principle is a
hypothesis. Keep it, change it, or drop it according to evidence. Add principles the
evidence supports that the case lacks.

## What "better" means (the number)
Primary metric: **design score**, 0 to 100. An agent (gpt-6.2-sol, medium effort) designs an
incentive programme for each of 4 held-out scenarios (scenarios.md). Two blind judges score
each design against rubric.md (built from the evidence in findings.md, frozen before any
skill text is scored). Score = mean over scenarios and judges. 3 runs per condition.

Secondary metric: **evidence coverage**, the share of the skill's normative claims that cite
a source a reviewer verified says what is claimed (target 100%).

## Baseline
- B0: no skill (the agent's own knowledge).
- B1: skill v0 = the case's principles as written, no evidence.

## Hard constraints
- Public repo. No client names, people, products or internal systems. The case is
  "a B2B software vendor's renewal sales team adopting an AI quote builder".
- Sources: peer-reviewed field experiments, meta-analyses, large natural experiments and
  credible postmortems first; vendor blogs only as illustration, labelled as such.
- The skill must stay short: SKILL.md under ~250 lines, details in references/.
- Agent Skills format (agentskills.io): SKILL.md frontmatter name + description.

## Budget
One research delegate, four debaters x 2 rounds, one experiment round, at most 6 loop
iterations. Wall clock: one working session.
