# GitHub mirror — 28 October 2026

Published on Zenodo as version 1.0, DOI 10.5281/zenodo.23717313, under
CC BY 4.0. In this repository README.md, README_ru.md and CITATION.cff were
updated with the DOI, publication date and licenses (paper and data CC BY 4.0,
code MIT); LICENSE-CC-BY-4.0 and .gitignore were added; MANIFEST.sha256 was regenerated for the updated metadata files.
The manuscript source, code, results and audit files are byte-identical to
the Zenodo archive majority_6040_complete.zip
(md5 982cf19fa41a9c74404ec936fd3c7caf).

# Version 1.0 — 21 October 2026

This publication package supersedes the earlier working bundle. Changes
following the fresh adversarial internal review:

1. The common stopping helper now computes the smallest integer L satisfying
   H(1−epsilon)^L ≤ delta using exact integer comparisons. This meets the
   manuscript's stated upper bound without a floating logarithm.
2. Accepted Boolean numeric values and labels are converted to Python integers
   before updates. This prevents binary floating inputs such as 1.0 from
   moving the active learner into floating arithmetic with a very large
   normalization denominator.
3. The five-bit rounding helper rejects nonintegral coefficients, matching its
   exact expectation identity.
4. Counter-reset phases, rational parameter encoding, and the active model's
   nonzero-domain restriction are explicit.
5. The reduction verifier validates literal indices and four distinct
   variables per clause; it no longer silently ignores an out-of-range
   variable. Its standard-library checks cover the source gadgets and the
   connectivity of the constructed instance. Optional MILP conclusions are
   compared with source satisfiability; an inconclusive run fails the requested
   verification instead of being recorded as success.
6. Attribution was expanded for the perceptron, consecutive-correct conversion,
   sample compression, concentration, and the SAT starting point. Related work
   now includes the Closest String implication and the neighboring 2013
   compatibility-hardness result. Unsupported first-existence claims are
   explicitly excluded.
7. The archive separates the manuscript, code, fresh results, internal reviews,
   source map, and companion notes. A common runner, PDF builder, citation
   metadata, and integrity manifest were added.

The review reports preserve the original findings and record their resolution.
The mathematical boundaries of prediction, signed-literal output, and exact
partition compatibility remain explicit.
