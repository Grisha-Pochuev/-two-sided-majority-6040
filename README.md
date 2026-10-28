# Two-sided 60/40 majority: prediction, counting, and compatibility

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23717313.svg)](https://doi.org/10.5281/zenodo.23717313)
[![Paper: CC BY 4.0](https://img.shields.io/badge/paper-CC%20BY%204.0-lightgrey.svg)](LICENSE-CC-BY-4.0)
[![Code: MIT](https://img.shields.io/badge/code-MIT-yellow.svg)](LICENSE)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Checks: standard library](https://img.shields.io/badge/checks-stdlib%20only-green.svg)

**Grisha Pochuev**, Independent Researcher ·
ORCID [0009-0005-0078-0857](https://orcid.org/0009-0005-0078-0857) ·
n_854@mail.ru

Preprint, version 1.0, published on Zenodo on 28 October 2026:
**https://doi.org/10.5281/zenodo.23717313**

This repository is the source, code, and reproducibility package for a note on
the *two-sided majority with margins* question from Avrim Blum and Maria-Florina
Balcan, [*Open Problems in Efficient Semi-Supervised PAC Learning*](https://home.ttic.edu/~avrim/Papers/openproblems.pdf)
(COLT 2007).

📄 **Read the paper:** [`paper/majority_6040_note.pdf`](paper/majority_6040_note.pdf)
(17 pages, LaTeX source alongside). Russian overview: [`README_ru.md`](README_ru.md).

## Abstract

We give self-contained prediction guarantees for two precise interpretations of
the two-sided majority with a 60/40 gap. When the percentages are taken within
the positive and negative indicator groups, centering the Boolean coordinates
gives a Euclidean margin of 1/5. A perceptron with an elementary stopping rule
learns from at most 26⌈ε⁻¹ ln(26/δ)⌉ labeled examples, independently of
dimension. When the percentages are taken among the active indicators, we prove
the distribution-free counting inequality ln K_ε ≥ εn/5 − ln 2, where K_ε is the
number of hypotheses whose incompatibility is at most ε. A normalized perceptron
consequently uses O(B² log(2+B)) labels, where B = (ln K_ε + ln(1/δ))/ε is the
raw-count benchmark. Both procedures have polynomial bit complexity and require
no additional unlabeled observations. Appendix A gives a polynomial-time learner
returning a signed-literal majority, with a sample bound proved by compressed
descriptions. Appendix B proves NP-completeness of finding an exactly compatible
partition and derives an NP = RP consequence for general polynomial-time
learning with an output-compatibility guarantee.

## The problem

Each example is x ∈ {0,1}ⁿ. The coordinates are split by an unknown partition
into positive indicators P and negative indicators N. The 60/40 promise says,
roughly, that on a positive example at least 60% of the indicators that count
are from P and at most 40% from N, and symmetrically on a negative example; the
paper treats two precise readings: percentages taken **within** the groups P and
N, and percentages taken **among the active** (nonzero) indicators. The question
asks for polynomial-time semi-supervised learning whose number of labels is
polynomial in log K_ε (the number of hypotheses approximately compatible with
the unlabeled distribution), 1/ε and 1/δ, rather than in n.

## Results at a glance

| # | Setting | Result | Where |
|---|---------|--------|-------|
| 1 | Percentages within groups P and N | Centered margin 1/5 ⇒ ≤ 25 perceptron mistakes; PAC with ≤ 26⌈ln(26/δ)/ε⌉ labels, **independent of n** | §3 |
| 2 | Percentages among active indicators | ln K_ε ≥ εn/5 − ln 2; normalized perceptron uses O(B² log(2+B)) labels, B = (ln K_ε + ln(1/δ))/ε | §4 |
| 3 | Signed-literal output | Poly-time learner returning sign(Σ sᵢ(2xᵢ−1)), sᵢ ∈ {±1}; label bound independent of n (compression argument) | App. A |
| 4 | Exact compatibility | Deciding whether an exactly compatible partition exists is NP-complete; a general learner with an output-compatibility guarantee would give NP = RP | App. B |

The key calculation: with sᵢ = +1 on P, −1 on N, and z = 2x − 1,
s·z = (2p − |P|) − (2q − |N|), which is ≥ n/5 on positives and ≤ −n/5 on
negatives, while ‖s‖ = ‖z‖ = √n. Hence margin 1/5 and at most 25 mistakes.

## Scope and limitations

Please read [`docs/CLAIMS_AND_LIMITATIONS.md`](docs/CLAIMS_AND_LIMITATIONS.md)
and [`audit/REVIEW_INDEX.md`](audit/REVIEW_INDEX.md) before describing this work
as a solution to a particular reading of the 2007 question. In short:

- The main guarantee concerns **prediction error**; the output may be a weighted
  centered linear classifier, not a partition satisfying the 60/40 inequalities.
- The active-normalized comparison uses the raw count K_ε with the same ε for
  compatibility and error; a cover-based or exact-compatibility (K₀) bound is
  not claimed.
- The perceptron bound and the consecutive-correct stopping conversion are
  classical. Existence of a dimension-independent signed-literal learner already
  follows from the Closest String PTAS of Li, Ma and Wang (2002) plus margin
  generalization; Appendix A is an explicit alternative construction.
- Compatibility hardness for two-sided disjunctions was shown by Balcan,
  Berlind, Ehrlich and Liang (ICML 2013); Appendix B gives a separate reduction
  for the majority constraints.
- The audit reports are internal AI-assisted reviews, not external peer review
  or a proof-assistant certificate. No endorsement by the authors of the open
  problem or prize decision is implied.

## Repository layout

| Path | Contents |
|------|----------|
| [`paper/`](paper) | Manuscript: PDF, LaTeX source, build log |
| [`code/`](code) | Learners (`majority_6040.py`, `majority_active.py`, `proper_signed_majority.py`), exact stopping helper (`pac_thresholds.py`), verification scripts |
| [`results/`](results) | Archived verification results, stdout/stderr logs, environment and source hashes |
| [`audit/`](audit) | Proof and source reviews, packaging review, independent checks and evidence |
| [`docs/`](docs) | Claims/limitations map and companion notes (in Russian) |
| [`references/PRIMARY_SOURCES.md`](references/PRIMARY_SOURCES.md) | Primary sources and the relevant passages |
| `run_all_checks.py` | Runs all finite check suites on a temporary copy |
| `build_paper.py` | Rebuilds the PDF (two pdflatex passes) |
| `verify_manifest.py`, `MANIFEST.sha256` | SHA-256 integrity check of every package file |
| `CITATION.cff` | Citation metadata (GitHub “Cite this repository”) |

## Reproduce

Python 3.10+; the learners and default checks use only the standard library.

```sh
git clone https://github.com/Grisha-Pochuev/-two-sided-majority-6040.git
cd -- -two-sided-majority-6040
python3 verify_manifest.py     # PASS: all file hashes match
python3 run_all_checks.py      # six suites; writes reproduced_results/
```

Expected output ends with `Overall: PASS` (suites: group, active,
signed_literal, thresholds, compatibility, independent_audit). The runner exits
nonzero on any failed or inconclusive suite.

Optional MILP cross-checks of the NP-completeness reduction (Python 3.11+):

```sh
python3 -m pip install -r requirements-optional.txt
python3 run_all_checks.py --with-solver
```

The solver is only a cross-check; the reduction is proved algebraically.

Rebuild the paper (needs pdflatex with geometry, lmodern, amsmath, amssymb,
amsthm, enumitem, microtype, hyperref, fancyhdr):

```sh
python3 build_paper.py
```

## Citation

```bibtex
@misc{pochuev2026majority6040,
  author    = {Pochuev, Grisha},
  title     = {Two-sided 60/40 majority: prediction, counting, and compatibility},
  year      = {2026},
  month     = oct,
  publisher = {Zenodo},
  version   = {1.0},
  doi       = {10.5281/zenodo.23717313},
  url       = {https://doi.org/10.5281/zenodo.23717313},
  note      = {Preprint}
}
```

## License

- **Paper, documentation and data** (`paper/`, `docs/`, `audit/`, `results/`,
  `references/`): [CC BY 4.0](LICENSE-CC-BY-4.0), matching the Zenodo record.
- **Code** (`code/`, `*.py`): [MIT](LICENSE).

Please cite the DOI when reusing.

## Related

- A. Blum, M.-F. Balcan. *Open Problems in Efficient Semi-Supervised PAC Learning.* COLT 2007. doi:[10.1007/978-3-540-72927-3_45](https://doi.org/10.1007/978-3-540-72927-3_45)
- M.-F. Balcan, A. Blum. *A Discriminative Model for Semi-Supervised Learning.* JACM 57(3), 2010. doi:[10.1145/1706591.1706599](https://doi.org/10.1145/1706591.1706599)
- M.-F. Balcan, C. Berlind, S. Ehrlich, Y. Liang. *Efficient Semi-supervised and Active Learning of Disjunctions.* ICML 2013.
