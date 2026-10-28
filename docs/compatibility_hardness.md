# Exact 60/40 compatibility is NP-complete

## Problem

Input: a finite list of points x in {0,1}^n. Question: does there exist a partition P,N of all coordinates such that every point satisfies either

    p >= 3|P|/5 and q <= 2|N|/5,

or the reversed inequalities

    p <= 2|P|/5 and q >= 3|N|/5?

No labels are supplied. The answer remains NP-complete for inputs in which every point has exactly n/2 active coordinates, and there is a graph connecting all input points with Hamming distance exactly 4 on every edge. The successful partition in the reduction, when it exists, can give every point the positive branch.

This is a complexity theorem about recovering an exactly compatible partition. It does not obstruct the dimension-independent prediction learner, which returns a weighted classifier and need not return a compatible partition.

## Two elementary observations

Write z=2x-1, s_i=+1 on P and -1 on N, A=s.z, S=sum_i s_i, Z=sum_i z_i. For a point on branch y in {+1,-1}, the two inequalities imply

    5 y A >= n + |S - 5 y Z|.                 (1)

In particular y A >= n/5. If both A=n/5 and Z=0 on the positive branch, (1) implies S=0.

If x and x' satisfy opposite branches for the same partition, their Hamming distance is at least n/5. Indeed, the positive-group active counts differ by at least |P|/5 and the negative-group counts by at least |N|/5 in the opposite direction. Their sum is bounded above by the total Hamming distance.

## NP-complete source problem

Use exact-2-in-4-SAT with signed literals and four distinct variables in each clause. In signed variables t_i in {+1,-1}, a clause with literal signs lambda_j requires

    sum_{j=1}^4 lambda_j t_{i_j}=0.          (2)

For completeness, its NP-hardness follows directly from ordinary 3-SAT with three distinct variables per clause. Introduce a shared Boolean variable F and replace each clause (a OR b OR c) by NAE(a,b,c,F). Since global complementation preserves NAE, any satisfying NAE assignment can be oriented so that F=false, giving exactly the original OR requirements. Replace NAE(a,b,c,F) by

    NAE(a,b,d) AND NAE(NOT d,c,F),

with a fresh d. These are equivalent after existentially quantifying d: if a=b, d is forced opposite to them; if a differs from b, d can always make the second clause NAE. Finally replace every NAE(L1,L2,L3) by the exact-two condition on (L1,L2,L3,w), with a fresh w. The sum of the first three Boolean literals is 1 or 2 exactly when a Boolean w can bring it to 2. All four variables are distinct in these clauses. Membership in NP is immediate.

## Construction

Pad with unused variables so that the number v of variables is a multiple of four and v>=12. Set h=v/2, m=v/2, n=5v/2. Use v pairs of free coordinates (i,0),(i,1), together with m anchors. The fixed anchor vector a has v/4 entries +1 and v/4 entries -1.

For any balanced free row r in {+1,-1}^{2v}, define

    z_r=(a,r),     x_r=(1+z_r)/2.

Every such x_r has n/2 active coordinates. Only balanced rows r will be used.

### Rows forcing opposite signs inside every free pair

For e in {+1,-1}^v with sum e=0, let R(e) repeat every sign twice: R(e)=(e_1,e_1,...,e_v,e_v).

Let e^0 have +1 on I={1,...,h} and -1 on J={h+1,...,v}. Use R(e^0) and, for every edge (i,j) of the following spanning tree of the complete bipartite graph I,J, use R(e^{ij}), where e^{ij} exchanges the signs at i and j in e^0:

    T = {(1,j): j in J} union {(i,h+1): i in I, i!=1}.

Thus there are v such rows. Include each row and its negative in the core list.

### Clause rows

For each clause (2), set the entries of the four participating pairs to (lambda_j,-lambda_j). On the remaining v-4 pairs, use (+1,+1) on exactly (v-4)/2 pairs and (-1,-1) on the others, in any fixed order. This defines a balanced row r_c. Include r_c and -r_c in the core list.

### Paths connecting the rows

Connect every core row to R(e^0), adding rows as necessary.

If a row is a clause row, first replace its four mixed pairs by two (+1,+1) pairs and two (-1,-1) pairs. The result is a balanced pure-pair row R(e). Exactly one coordinate in each of the four mixed pairs changes, so the Hamming distance of this step is 4.

For any balanced pure-pair row R(e), repeatedly exchange a +1 pair outside I with a -1 pair inside I until reaching R(e^0). Each exchange changes four coordinates and preserves balance. There are at most h exchanges.

The number K of constructed rows is O((v+c)v), where c is the number of clauses. All construction steps are polynomial. The graph formed by these paths is connected, and every graph edge has Hamming distance 4, strictly less than n/5=v/2>=6.

## Correctness: a SAT solution gives compatibility

Given a solution t to (2), assign s=a on the anchors and assign (t_i,-t_i) in free pair i. Then S=0.

For every pure-pair row R(e), the free inner product is zero because the two signs of each free pair cancel. For each clause row r_c, the free inner product is 2 times the left side of (2), hence zero. Thus it is zero on every constructed row, since the additional path rows are all pure-pair rows.

Consequently s.z_r=m=n/5 and Z=0 for every constructed example. The group sizes are n/2 each. More explicitly, p=3n/10 and q=n/5, so every example satisfies the positive branch at equality.

## Correctness: compatibility gives a SAT solution

Suppose a partition makes all constructed examples compatible. Their branches are well-defined because n>=1. Neighboring examples in the path graph cannot have opposite branches: their Hamming distance is 4<n/5. Connectedness forces one common branch for all examples. If it is negative, globally swap P and N. We may therefore assume every constructed example satisfies the positive branch.

Consider the two core rows r^0=R(e^0) and -r^0. By (1),

    s_A.a + s_F.r^0 >= m,
    s_A.a - s_F.r^0 >= m.

Their sum gives s_A.a>=m. There are m anchor coordinates, so this forces s_A=a coordinate by coordinate. The two inequalities then force s_F.r^0=0. Because Z=0 and the full inner product is m=n/5, (1) forces S=0. Since the anchors are balanced, sum s_F=0.

For every other core row r, both r and -r occur. The same inequalities now imply s_F.r=0.

Set T_i=s_{i,0}+s_{i,1}. We have sum_i T_i=0. Orthogonality to R(e^0) and R(e^{ij}) yields T_i=T_j for each edge of the spanning tree T. Hence all T_i are equal; their sum is zero, so all T_i=0. Therefore s_{i,1}=-s_{i,0} for every i.

Define t_i=s_{i,0}. In a clause row, all inactive pure pairs now contribute zero, and orthogonality becomes

    2 sum_j lambda_j t_{i_j}=0.

Thus t satisfies every exact-2-in-4 clause. This finishes the reduction. Membership of the target problem in NP follows by checking an n-bit partition against the finite input list.

## Consequence for efficient approximate compatibility learning

Suppose a polynomial-time learner, on every perfectly compatible distribution, returns an explicit partition whose incompatibility probability is at most epsilon with probability at least 1-delta. The learner may also require correctly labeled examples and may guarantee prediction accuracy; this does not weaken the following consequence.

Given the constructed K-point list, pad it with repetitions of the first point to a list of length H=2^ceil(log_2 K), where K<=H<2K unless K itself is a power of two. Simulate the uniform distribution on these H positions using exactly log_2 H fair bits per observation, supply label +1 whenever a label is requested, and choose epsilon=1/(2H), delta=1/4. In YES instances the distribution with all-positive labels is realizable, by the forward construction. In NO instances no output partition can be compatible with every point. Since each distinct listed point has probability at least 1/H, incompatibility probability at most epsilon implies compatibility with every point.

Run the learner and verify its returned partition on the entire list. On a NO instance verification always rejects. On a YES instance it accepts with probability at least 3/4. Polynomial resource bounds in n, 1/epsilon and log(1/delta) remain polynomial in the SAT input size. Any label bound polynomial in log|C_compat|, 1/epsilon and log(1/delta) is also polynomial, because |C_compat|<=2^n. Clock the learner by its stated polynomial runtime if its behavior outside the promise is unspecified.

This would place an NP-complete problem in RP, implying NP=RP. Therefore, unless NP=RP, no such general polynomial-time learner returning an approximately compatible partition exists. This conclusion concerns output compatibility, not merely prediction accuracy by a partition or a weighted classifier.
