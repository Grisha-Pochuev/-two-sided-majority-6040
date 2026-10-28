# Primary sources and claim map

Source review date: 21 October 2026. The bibliography in the manuscript gives
the formal references. This map identifies the roles of the primary sources;
it does not claim an exhaustive priority search. Full third-party PDFs are
not redistributed in this package.

## The historical question and its models

1. **Avrim Blum and Maria-Florina Balcan (2007), “Open Problems in
   Efficient Semi-Supervised PAC Learning.”**
   https://home.ttic.edu/~avrim/Papers/openproblems.pdf  
   Section 3 states the approximate-compatibility raw-count benchmark and
   permits a polynomial in that label count. The footnote on the second PDF
   page discusses a stronger refinement using covers. Section 3.2 on the
   third page states two-sided majority with margins and the positive-result
   prize. This historical document does not by itself establish the prize's
   present availability or acceptance of this manuscript.

2. **Maria-Florina Balcan and Avrim Blum (2010), “A Discriminative Model
   for Semi-Supervised Learning.”** Journal of the ACM 57(3), Article 19,
   pages 1–46. DOI: https://doi.org/10.1145/1706591.1706599  
   Author manuscript:
   https://home.ttic.edu/~avrim/Papers/labeled_unlabeled-2009.pdf  
   Theorem 4 and Section 6.2 supply the corresponding learning bound and
   majority example. The 2009 filename identifies the author-manuscript
   version; the journal publication is 2010.

3. **Maria-Florina Balcan, Christopher Berlind, Steven Ehrlich, and
   Yingyu Liang (2013), “Efficient Semi-supervised and Active Learning of
   Disjunctions.”** PMLR 28(1), pages 633–641.  
   https://proceedings.mlr.press/v28/balcan13.pdf  
   Section 3.2 already uses a nonproper online learner and a stopping
   condition based on consecutive correct predictions. Our stopping lemma
   gives a complete proof with explicit constants and phase conventions;
   it is not presented as a new conversion.

4. **Supplement to Balcan et al. (2013).**  
   https://proceedings.mlr.press/v28/balcan13-supp.pdf  
   Section 2, Theorem 4 proves hardness of the joint consistency and
   compatibility search for two-sided disjunctions. This is relevant prior
   hardness work, distinct from our group-normalized majority construction.

5. **Maria-Florina Balcan and Christopher Berlind (2014),
   “A New Perspective on Learning Linear Separators with Large L_q L_p Margins.”**
   PMLR 33, pages 68–76.  
   https://proceedings.mlr.press/v33/balcan14.pdf  
   Theorem 3, printed page 71 (fourth PDF page), gives the cited
   margin/fat-shattering generalization route. The manuscript explains its
   application to the Closest String output as a mathematical inference.

6. **Supplement to Balcan and Berlind (2014).**  
   https://proceedings.mlr.press/v33/balcan14-supp.pdf  
   Appendix A.2 gives the majority model with percentages among active
   coordinates. Its displayed domain includes zero; our normalized update
   explicitly restricts to nonzero examples. The two different normalizations
   must not be identified.

## Classical mechanisms and relevant earlier algorithms

7. **A. B. J. Novikoff, “On Convergence Proofs for Perceptrons.”**
   Presented at the Symposium on the Mathematical Theory of Automata,
   Polytechnic Institute of Brooklyn, 24–26 April 1962; archived pages 615–622.  
   Primary scan:
   https://cs.uwaterloo.ca/~y328yu/classics/novikoff.pdf  
   The manuscript cites the classical perceptron update analysis and proves
   the exact version it uses. The date here is the presentation date, not
   an asserted publication year of a proceedings edition.

8. **Sally Floyd and Manfred Warmuth (1995), “Sample Compression,
   Learnability, and the Vapnik–Chervonenkis Dimension.”** Machine Learning 21,
   pages 269–304. DOI: https://doi.org/10.1007/BF00993593  
   Author-hosted primary copy:
   https://mwarmuth.bitbucket.io/pubs/J30.pdf  
   General background for learning from short sample descriptions. The
   ordered-index and external-random-table calculation needed here is proved
   directly in Appendix A.

9. **Wassily Hoeffding (1963), “Probability Inequalities for Sums of
   Bounded Random Variables.”** Journal of the American Statistical
   Association 58(301), pages 13–30.  
   https://doi.org/10.1080/01621459.1963.10500830  
   Source for the bounded-variable concentration mechanism. Appendix A
   includes the elementary moment-generating-function argument, so the
   relevant constant is checkable without consulting the source.

10. **Stephen A. Cook (1971), “The Complexity of Theorem-Proving
    Procedures.”** Proceedings of the Third Annual ACM Symposium on Theory
    of Computing, pages 151–158.  
    https://doi.org/10.1145/800157.805047  
    Author-hosted primary copy:
    https://www.cs.toronto.edu/~sacook/homepage/1971.pdf  
    Classical NP-completeness starting point. Appendix B gives the particular
    transformation from three-literal SAT to the signed exact-two-in-four
    source used by its construction.

11. **Ming Li, Bin Ma, and Lusheng Wang (2002), “On the Closest String and
    Substring Problems.”** Journal of the ACM 49(2), pages 157–171.  
    https://doi.org/10.1145/506147.506150  
    Author-hosted primary copy:
    https://www.cs.cityu.edu.hk/~lwang/research/jacm02.pdf  
    Theorem 2.6, printed page 165, supplies a PTAS for Closest String.
    Lemma 2.5 on pages 163–164 provides its derandomization ingredient.
    For training rows u_j=y_j(2x_j−1), the group promise gives Hamming radius
    at most 2n/5 around the target signs. Approximation ratio 9/8 gives a
    sign vector with radius at most 9n/20 and signed margin at least n/10.
    Standard uniform margin generalization then gives a
    dimension-independent PAC existence result. This application is our
    inference from earlier theorems, not a claim stated verbatim in that paper.

## What this review establishes

The cited sources support the definitions, historical criterion, attribution,
and related-work comparisons used in the manuscript. Source review and
mathematical verification are different tasks. This review cannot establish
that every specialized theorem is new, that a stronger cover-based version
has been solved, or that the historical prize sponsors would accept the
manuscript. The accompanying review report records these distinctions.
