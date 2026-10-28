"""Exact finite stopping thresholds for a bounded number of iid phases.

The returned L is the smallest positive integer satisfying
    phases * (1 - epsilon)**L <= delta.
All certification arithmetic is integral.  No logarithm approximation is used.
"""

from fractions import Fraction


def certified_streak_length(
    phases: int, epsilon: Fraction, delta: Fraction
) -> int:
    """Compute the minimal sufficient streak by monotone integer comparisons.

    For epsilon=p/q and delta=r/s, test
        phases*s*(q-p)**L <= r*q**L.
    A power-of-two ceiling supplies a certified search interval.  If U is
    its upper endpoint, intermediate integers have O(U*log(q) + log(s*phases))
    bits.  This is polynomial in the parameter encoding lengths, 1/epsilon,
    and log(phases), as required by the mathematical model.
    """
    if not isinstance(phases, int) or phases < 1:
        raise ValueError("phases must be a positive integer")
    if not isinstance(epsilon, Fraction) or not isinstance(delta, Fraction):
        raise TypeError("epsilon and delta must be fractions.Fraction")
    if not 0 < epsilon < 1 or not 0 < delta < 1:
        raise ValueError("epsilon and delta must be strictly between 0 and 1")

    target = (phases * delta.denominator + delta.numerator - 1) // delta.numerator
    exponent = (target - 1).bit_length()
    upper = (exponent * epsilon.denominator + epsilon.numerator - 1) // epsilon.numerator

    p, q = epsilon.numerator, epsilon.denominator
    r, s = delta.numerator, delta.denominator
    low, high = 0, upper
    while high - low > 1:
        middle = (low + high) // 2
        if phases * s * pow(q - p, middle) <= r * pow(q, middle):
            high = middle
        else:
            low = middle
    return high
