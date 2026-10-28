# A dimension-independent PAC learner returning a partition

## The precise prediction theorem

Let n>=1, 0<epsilon<1, and 0<delta<=1/2. Suppose a distribution on
(x,y) in {0,1}^n x {-1,+1} has a vector s* in {-1,+1}^n such that

    y <s*,2x-1> >= n/5

almost surely. Set

    q = ceil(log_2(2/delta)),
    r = the least nonnegative integer with epsilon 2^r >= 512(r+2)+q,
    m = 2^r.

The algorithm below uses m i.i.d. labeled observations, no unlabeled
observations, and at most 5nq independent random bits. It always runs in time
polynomial in n, 1/epsilon, and log(1/delta). With probability at least 1-delta
it returns a sign vector s whose classifier

    h_s(x) = +1 if <s,2x-1> >= 0, and -1 otherwise

has true error at most epsilon. In particular,

    m = O((1+log(1/epsilon)+log(1/delta))/epsilon).

The sign vector defines a partition P={i:s_i=+1}, N={i:s_i=-1}. The decision
rule is the majority of the n literals x_i on P and 1-x_i on N, equivalently

    h_s(x)=+1 iff p(x)+|N|-q(x) >= n/2.

This theorem concerns that displayed decision rule. It does not assert that
the returned partition itself has 60/40 compatibility. Outside compatible
examples it can differ from the one-sided rule sign(2p(x)-|P|).

The original group-normalized promise implies the theorem's premise, since

    <s*,2x-1> = (2p-|P|) - (2q-|N|),

and the two original inequalities give y<s*,2x-1> >= (|P|+|N|)/5=n/5.

## Exact-arithmetic algorithm

Before drawing the labeled observations, independently draw q tables
R^(1),...,R^(q), each of length n, whose entries are independent uniform
integers in {0,...,31}. This consumes exactly 5nq random bits. The same
distribution can be implemented by independent lazy access to these bits.

Draw the m labeled observations and put z_j=2x_j-1. Let

    b = ceil(log_2(2m)).

If n<512b, enumerate all sign vectors s and return the first satisfying

    5 y_j<s,z_j> >= n   for all j.

The premise guarantees one exists. On non-promised inputs with no such
vector, return an arbitrary vector and report failure.

If n>=512b, initialize an integer vector a=0. Whenever there is an observation
with y_j<a,z_j><2n, replace

    a_i <- max(-16,min(16,a_i+y_j z_{j,i})).

Restart the search for a violated observation. If no observation violates
the inequality, proceed to rounding. Explicitly cap the procedure at 183
corrections so it also has bounded running time on non-promised inputs.

For each table R^(ell), in order, form

    s_i = +1 if R_i^(ell)<a_i+16, and -1 otherwise.

Return the first rounded vector satisfying

    16 y_j<s,z_j> >= n  for all j.

If all q tables fail, return an arbitrary vector and report failure.

## Why there are at most 182 corrections

Fix t=16s*. The nonnegative potential Phi(a)=||a-t||_2^2 initially equals
256n. On a violated observation,

    y_j<t-a,z_j> > (16/5-2)n = 6n/5.

Before clipping,

    Phi(a+y_j z_j)
      = Phi(a)-2y_j<t-a,z_j>+||z_j||_2^2
      < Phi(a)-7n/5.

Coordinatewise clipping cannot increase distance to t, which belongs to
[-16,16]^n. Hence there are fewer than 1280/7 corrections: at most 182.
The resulting v=a/16 satisfies y_j<v,z_j>>=n/8 on every observation.

## Why rounding succeeds

For a fixed observation, the independent variables X_i=y_j s_i z_{j,i} lie
in [-1,1] and their sum has mean at least n/8. The elementary exponential
bound for independent variables in intervals of length 2 is

    Pr[sum X_i-E sum X_i <= -u] <= exp(-u^2/(2n)).

For completeness, a variable V in an interval of length c satisfies
E exp(lambda(V-EV))<=exp(lambda^2 c^2/8): the second derivative of its log
moment-generating function is a tilted variance, at most c^2/4; integrate
twice from zero. Multiplying this bound for independent variables and
optimizing exponential Markov gives the displayed tail inequality.

Taking u=n/16, the failure probability on one observation is at most
exp(-n/512). The probability that a table fails some observation is at most

    m exp(-n/512) <= m exp(-b) <= 1/2,

because b>=ln(2m). All q independent tables fail with probability at most
2^-q<=delta/2.

## A short, self-contained generalization proof

### The large-dimensional branch: count compressed descriptions

Condition on all presampled rounding tables. These tables are independent
of the labeled observations. The correction vector a is determined by the
ordered sequence of the at most 182 labeled observations on which a
correction was made. The same observation may occur several times. Starting
at zero and replaying this sequence reconstructs a exactly.

Fix a sequence I of k<=182 sample indices, and fix a rounding-table index.
Replay its updates and apply that table. Conditional on the observations at
the distinct indices in I, this produces a fixed classifier; all remaining
at least m-k observations remain independent and identically distributed.
Thus

    Pr[its true error>epsilon and it is correct on all m observations]
      <= (1-epsilon)^(m-k)
      <= exp(-epsilon(m-182)).

There are at most

    q sum_{k=0}^{182} m^k <=183q m^182

descriptions. Every accepted output is among them and is correct on the
whole training sample. Taking a union bound and then averaging over the
independent tables proves

    Pr[accepted output has error>epsilon]
      <=183q m^182 exp(-epsilon(m-182)).                 (L)

This argument explicitly accounts for the adaptive choice and repeated use
of correction examples; it does not assume those indices were fixed by
the actual algorithm in advance.

### The small-dimensional branch: count sign vectors

A fixed classifier of true error>epsilon is correct on every one of m
independent observations with probability at most exp(-epsilon m).
There are 2^n classifiers, so the failure probability is at most

    2^n exp(-epsilon m) <= (4m)^512 exp(-epsilon m),      (S)

using n<512ceil(log_2(2m)) and 2^ceil(log_2(2m))<=4m.

### The chosen sample size bounds both branches

Since m=2^r and epsilon m>=512(r+2)+q,

    (4m)^512 exp(-epsilon m)
      =exp(512ln(2)(r+2)-epsilon m)
      <=exp(-q) <=delta/2.

Moreover m>q and m>183. The logarithm of (S)'s right-hand side minus the
logarithm of (L)'s right-hand side equals

    512ln4+330lnm-lnq-ln183-182epsilon
      >512ln4+329lnm-ln183-182
      >0.

Thus (L) is also at most delta/2. In the large-dimensional branch add the
rounding failure probability at most delta/2. The total failure probability
is at most delta. The small-dimensional branch has no construction failure
on promised inputs.

## Explicit polynomial sample upper bound

Let k=ceil(log_2(1/epsilon)) and A=q+k+12. Choose m0 to be the least power
of two at least 1024A/epsilon, and write m0=2^r0. Then

    m0<=2048A/epsilon,
    r0<=11+k+log_2(A).

Since log_2(A)<=A and q>=2,

    2A >=13+k+log_2(A)+q/512.

It follows that

    epsilon m0 >=1024A >=512(r0+2)+q.

The minimal m in the algorithm is therefore at most m0, proving

    m<=2048(q+ceil(log_2(1/epsilon))+12)/epsilon.

## Bit complexity

The integer r is found by successive exact rational comparisons

    epsilon_numerator * 2^r
      >= epsilon_denominator * (512(r+2)+q).

All logarithmic ceilings are computed by integer comparisons to powers of
two. No real-number oracle or irrational normalization is used.

Each a_i belongs to {-16,...,16}. Dot products need O(log n) bits. The
correction stage uses at most 183 full scans, with integer additions and
clipping only. The large-dimensional branch needs

    O(nm(183+q)log n)

bit operations under a straightforward implementation. The small branch
examines at most (4m)^512 candidates and needs

    O((4m)^512 nm log n)

bit operations. Both are polynomials with absolute constant exponents.
Sample storage and the precomputed tables use O(n(m+q))=O(nm) bits under
the theorem's sample choice.

The polynomial exponent in the enumeration branch is very large. This is
a rigorous polynomial-time existence result, not a practically attractive
alternative to the much simpler weighted-perceptron predictor.

## Optional nonempty groups

If the output must have both groups nonempty and the premise includes a
target with both groups nonempty, restrict the small-branch enumeration
accordingly. In the large branch, if an accepted vector has all signs equal,
flip one fixed coordinate. The training signed score decreases by at most
2; n>=512b>=512 implies n/16-2>0, so training classification remains correct.
The repair is deterministic and remains a function of the same compressed
description. Consequently the compression proof is unchanged; no increase
in sample size is necessary. Original 60/40 compatibility is still not
claimed.
