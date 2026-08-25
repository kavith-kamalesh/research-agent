RESEARCH_PROTOCOLS = """
Every protocol below must include an explicit confidence/probability element
and consider all reasonably possible angles before concluding — never present
a single-path answer as certain without stating your confidence in it.

=====================================================
VERITAS (testable/empirical questions)
=====================================================
VERITAS REPORT
Claim being tested: [one sentence]
Hypothesis: [a falsifiable statement]
Variables: Independent — [what changes] | Controlled — [what stays fixed]
Evidence gathered: [reasoning/data supporting or challenging the hypothesis]
Confidence: [low/medium/high, with why]
Verdict: Supported / Not supported / Inconclusive — [why]
If inconclusive, next test needed: [what data would settle it]

=====================================================
GENESIS (engineering/design questions)
=====================================================
GENESIS REPORT
Problem, stripped of assumptions: [the bare, basic version]
Fundamental constraints: [non-negotiable physical/logical truths]
What common approaches get wrong: [why "usual way" may not fit]
Rebuilt solution: [built only from the fundamentals above]
Confidence: [low/medium/high, with why]
Why this holds up: [justification paragraph]

=====================================================
AXIOM (quantitative/optimization questions)
=====================================================
AXIOM REPORT
Variables defined: [symbol = meaning, for each]
Governing relationship: [the formula/equation]
Calculation: [step-by-step, with real numbers]
Result: [the numeric answer]
Confidence: [low/medium/high, with why]
Reality check: [does this make sense? what would make it wrong?]

=====================================================
SENTRY (fast feasibility/sanity checks)
=====================================================
SENTRY REPORT
Question: [one sentence]
Dimensional check: [do units/scales match?]
Order of magnitude: [roughly how far off, if at all?]
Boundary test: [what happens at the extremes?]
Confidence: [low/medium/high]
Verdict: Feasible / Infeasible / Borderline — [one clear sentence]

=====================================================
ORACLE (full deep investigation)
=====================================================
ORACLE REPORT
1. PROBLEM DEFINITION
2. RESEARCH — Verified facts / Reasonable inferences / Assumptions to check
3. SOLUTION SPACE — 2-4 approaches compared, with recommendation
4. ENGINEERING ARCHITECTURE
5. FEASIBILITY ANALYSIS
6. COST ENGINEERING
7. FAILURE ANALYSIS
8. PROTOTYPE PLAN
9. KILL TEST
10. FINAL VERDICT — include an overall confidence score (X/10)
"""
