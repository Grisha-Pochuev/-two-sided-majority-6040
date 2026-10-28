# Internal adversarial review: scope and resolutions

Review date: 21 October 2026. Three separate AI-assisted review threads
examined different parts of the manuscript. The complete reports are in
Russian; this index provides an English map for readers of the article.
The reviewers were instructed to seek counterexamples, missing assumptions,
incorrect constants, invalid probability conditioning, implementation
discrepancies, and unsupported source claims.

## Reports

| Report | Scope |
| --- | --- |
| audit_main_active_20261021.md | Main group margin, perceptron bounds, adaptive stopping, active count, bit complexity, corresponding code |
| audit_appendices_20261021.md | Integer correction, rounding, compressed descriptions, SAT gadgets, exact compatibility reduction, verifier |
| audit_scope_literature_20261021.md | Original question, model distinctions, prediction criterion, citations, closest prior results, limits of novelty claims |
| audit_packaging_20261021.md | Final runner, PDF builder, reproducibility paths, interpreter requirements, and closure of packaging findings |

The main and appendix reviewers did not identify a blocking mathematical
defect in the theorems as finally stated. They identified several concrete
implementation and presentation issues, corrected in this version. The
literature review materially narrows what may be claimed as a new result.
These are bounded internal conclusions, not an external endorsement.

## Findings and resolutions

| Finding | Resolution |
| --- | --- |
| Earlier stopping implementation used a safe but larger log-base-two bound than the exact displayed label limit | A shared exact-integer search now returns the minimal L with H(1−epsilon)^L≤delta; the manuscript proves its complexity and comparison |
| Numeric Boolean inputs such as 1.0 passed validation and could force floating arithmetic | Inputs are converted to integer values after validation; an n=1000 regression checks a 1438-bit common denominator |
| The public five-bit rounding helper did not enforce its integral-coefficient contract | Nonintegral coefficients are rejected and a regression test covers that case |
| Adaptive phases and oracle/bit assumptions needed explicit wording | Phases are defined by counter resets; rational encoding lengths, iid observations, and independent uniform random tables are stated |
| Active-normalized source formally includes zero | The article explicitly states its restriction to nonzero examples |
| Reduction verifier could omit literals outside a default dimension | The builder infers or validates the variable count and rejects malformed clauses |
| A solver timeout or disagreement could have escaped a meaningful check | Requested solver runs return PASS, FAIL, or INCONCLUSIVE, compared with brute-force source truth; incomplete runs have a nonzero exit code |
| Source gadgets and connectivity warranted independent checks | Finite truth tables and traversal of the actual Hamming-four graph were added |
| Classical learning conversions and related hardness were insufficiently attributed | Direct references and comparisons were added at the relevant mathematical statements |
| A first-existence claim for signed-literal PAC learning would overlook older work | The Closest String PTAS implication is derived explicitly, and such a priority claim is excluded |
| Reusing a result directory after a failed suite could retain an old result JSON | The package runner removes each expected old JSON before its suite and saves a RUNNING summary before and during execution |
| Optional dependency versions require a newer interpreter than the core code | The instructions now distinguish Python 3.10 for core checks from Python 3.11 for the pinned solver dependencies |

The reports retain the original observations and their closure notes.
File hashes identify the versions inspected. The final verification run
records its own hashes in **results/run_summary.json**. This distinction
allows a reader to see that later documentary edits do not silently replace
the versions addressed by an earlier finding.

## Computational evidence

The common runner executes five author-side suites plus a separately written
audit suite on an isolated copy of the delivered source. Every requested
suite must complete successfully. Its output files record exact counts and
the supplied witnesses rather than only a general success statement.

The independent suite includes:

- 150 exact rational checks of the minimal stopping threshold;
- 867 exact distribution/epsilon checks of the active counting inequality;
- 30 stepwise comparisons with a separate Fraction-based perceptron;
- 8 exact phase-tree calculations of the probability of bad adaptive stopping;
- zero-input, empty-group, and large-integer input regressions.

The main suites additionally exhaust small group-normalized cases, exercise
both signed-literal branches, check the integer correction potential and
rounding identities, test source gadgets and reduction instances, and verify
3,803 stopping thresholds.

The **evidence/** directory preserves extra runs of the reduction verifier:
successful standard-library and solver modes, and intentionally induced
missing-solver and timeout cases. An INCONCLUSIVE status in those two negative
tests is the expected behavior, not an unnoticed failure of the archived
full run. Exact exit-code observations are documented in the appendix report.

## Remaining scientific boundaries

No report establishes exhaustive novelty, solves a cover-based or
independent-tolerance learning criterion, verifies resistance to arbitrary
label noise, or certifies historical prize eligibility. The large polynomial
exponent in the signed-literal construction is a theoretical limitation.
No proof assistant was used. A fresh human review may find issues outside
the checks performed here.

The article's mathematical proofs, named assumptions, exact implementation,
recorded corrections, and explicit prior-work comparisons are the material
offered for that review.
