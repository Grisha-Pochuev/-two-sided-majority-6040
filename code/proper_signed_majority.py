"""Exact-arithmetic construction from proper_signed_majority.md.

The returned classifier is the majority of signed literals: x_i for a + sign,
1-x_i for a - sign. It is not asserted to satisfy 60/40 compatibility, and it
is not in general the majority of the positive group alone.

The small-dimensional branch is deliberately the polynomial-time existence
construction from the proof. Its polynomial has a very large exponent.
"""

from dataclasses import dataclass
from fractions import Fraction
from itertools import product
from random import SystemRandom
from typing import Callable, Iterable, Sequence


@dataclass(frozen=True)
class FitResult:
    signs: tuple[int, ...]
    certified_training_margin: bool
    branch: str
    corrections: int
    rounding_trials: int

    def predict(self, x: Sequence[int]) -> int:
        if len(x) != len(self.signs) or any(v not in (0, 1) for v in x):
            raise ValueError("x must be a Boolean vector of the fitted dimension")
        score = sum(s * (2 * int(bit) - 1) for s, bit in zip(self.signs, x))
        return 1 if score >= 0 else -1


@dataclass(frozen=True)
class CorrectionResult:
    coefficients: tuple[int, ...]
    update_indices: tuple[int, ...]
    certified: bool


def ceil_log2_ratio(numerator: int, denominator: int = 1) -> int:
    """Smallest nonnegative q with denominator * 2**q >= numerator."""
    if numerator <= 0 or denominator <= 0:
        raise ValueError("positive integers required")
    q = max(0, numerator.bit_length() - denominator.bit_length())
    while (denominator << q) < numerator:
        q += 1
    while q > 0 and (denominator << (q - 1)) >= numerator:
        q -= 1
    return q


def confidence_trials(delta: Fraction) -> int:
    delta = Fraction(delta)
    if not 0 < delta <= Fraction(1, 2):
        raise ValueError("the theorem uses 0 < delta <= 1/2")
    return ceil_log2_ratio(2 * delta.denominator, delta.numerator)


def labeled_sample_bound(epsilon: Fraction, delta: Fraction) -> int:
    """Main compression bound: least 2**r with eps*2**r >=512(r+2)+q."""
    epsilon = Fraction(epsilon)
    if not 0 < epsilon < 1:
        raise ValueError("0 < epsilon < 1 required")
    q = confidence_trials(Fraction(delta))
    r = 0
    while (epsilon.numerator << r) < epsilon.denominator * (512 * (r + 2) + q):
        r += 1
    return 1 << r






def _dot(a: Sequence[int], z: Sequence[int]) -> int:
    return sum(u * v for u, v in zip(a, z))


def centered_sample(
    samples: Iterable[tuple[Sequence[int], int]],
) -> tuple[tuple[tuple[int, ...], int], ...]:
    records = tuple((tuple(x), y) for x, y in samples)
    if not records:
        raise ValueError("a nonempty labeled sample is required")
    n = len(records[0][0])
    if n == 0:
        raise ValueError("dimension must be positive")
    if any(len(x) != n or any(v not in (0, 1) for v in x) or y not in (-1, 1)
           for x, y in records):
        raise ValueError("sample must contain equally sized Boolean vectors and +/-1 labels")
    return tuple((tuple(2 * int(bit) - 1 for bit in x), int(y)) for x, y in records)


def correct_integer_box(
    records: Sequence[tuple[Sequence[int], int]],
) -> CorrectionResult:
    """Find a in [-16,16]^n with y<a,z> >= 2n, or report capped failure.

    `records` uses already centered +/-1 vectors. The supplied margin promise
    implies at most 182 corrections. The cap bounds time off the promise too.
    Update indices are returned to permit exact potential-decrease audits.
    """
    if not records:
        raise ValueError("nonempty records required")
    n = len(records[0][0])
    a = [0] * n
    updates: list[int] = []
    while True:
        violated = next((j for j, (z, y) in enumerate(records)
                         if y * _dot(a, z) < 2 * n), None)
        if violated is None:
            return CorrectionResult(tuple(a), tuple(updates), True)
        z, y = records[violated]
        a = [max(-16, min(16, v + y * zi)) for v, zi in zip(a, z)]
        updates.append(violated)
        if len(updates) >= 183:
            return CorrectionResult(tuple(a), tuple(updates), False)


def round_with_five_bits(
    coefficients: Sequence[int], getrandbits: Callable[[int], int],
) -> tuple[int, ...]:
    """Use exactly five bits per coordinate; E[s_i] = coefficients[i]/16.

    The mathematical theorem assumes fresh independent fair bits. A seeded
    pseudorandom generator may be supplied for reproducible finite checks.
    """
    if any(not isinstance(a, int) or a < -16 or a > 16 for a in coefficients):
        raise ValueError("coefficients must be integers between -16 and 16")
    return tuple(1 if getrandbits(5) < a + 16 else -1 for a in coefficients)


def fit_sign_vector(
    samples: Iterable[tuple[Sequence[int], int]],
    delta: Fraction = Fraction(1, 4),
    getrandbits: Callable[[int], int] | None = None,
    rounding_tables: Sequence[Sequence[int]] | None = None,
) -> FitResult:
    """Fit the proof's sign-vector classifier to an existing labeled sample.

    A training-margin certificate alone is not a PAC guarantee for an arbitrary
    sample. For the theorem use at least labeled_sample_bound(epsilon, delta)
    i.i.d. observations and the stated realizability/margin promise.
    Supplied rounding tables must be independent of the observations, with
    independent uniform entries in {0,...,31}; the full constructor presamples
    them before asking the example oracle for any observations.
    """
    records = centered_sample(samples)
    n = len(records[0][0])
    m = len(records)
    q = confidence_trials(Fraction(delta))
    b = ceil_log2_ratio(2 * m)
    fallback = (1,) * n

    if rounding_tables is not None:
        if len(rounding_tables) != q or any(
            len(table) != n or any(r not in range(32) for r in table)
            for table in rounding_tables
        ):
            raise ValueError("q independent rounding tables of n five-bit entries are required")

    if n < 512 * b:
        for signs in product((-1, 1), repeat=n):
            if all(5 * y * _dot(signs, z) >= n for z, y in records):
                return FitResult(signs, True, "enumeration", 0, 0)
        return FitResult(fallback, False, "enumeration", 0, 0)

    corrected = correct_integer_box(records)
    corrections = len(corrected.update_indices)
    if not corrected.certified:
        return FitResult(fallback, False, "correction_cap", corrections, 0)

    if getrandbits is None:
        getrandbits = SystemRandom().getrandbits
    if rounding_tables is None:
        # These fresh independent tables may equivalently be presampled before
        # the observations. The full learn_sign_vector constructor does that.
        rounding_tables = tuple(tuple(getrandbits(5) for _ in range(n))
                                for _ in range(q))
    for trial in range(1, q + 1):
        signs = tuple(1 if r < a + 16 else -1
                      for a, r in zip(corrected.coefficients, rounding_tables[trial - 1]))
        if all(16 * y * _dot(signs, z) >= n for z, y in records):
            return FitResult(signs, True, "rounding", corrections, trial)
    return FitResult(fallback, False, "rounding_failure", corrections, q)


def learn_sign_vector(
    draw_labeled_example: Callable[[], tuple[Sequence[int], int]],
    n: int,
    epsilon: Fraction,
    delta: Fraction,
    getrandbits: Callable[[int], int] | None = None,
) -> FitResult:
    """Full PAC constructor with the theorem's number of labeled examples.

    The supplied example oracle is assumed to return i.i.d. observations.
    """
    if n <= 0:
        raise ValueError("dimension must be positive")
    m = labeled_sample_bound(Fraction(epsilon), Fraction(delta))
    q = confidence_trials(Fraction(delta))
    if getrandbits is None:
        getrandbits = SystemRandom().getrandbits
    # Explicitly independent of the sample: every table is drawn first.
    tables = tuple(tuple(getrandbits(5) for _ in range(n)) for _ in range(q))
    samples = tuple(draw_labeled_example() for _ in range(m))
    if any(len(x) != n for x, _ in samples):
        raise ValueError("the observation oracle returned the wrong dimension")
    return fit_sign_vector(samples, Fraction(delta), rounding_tables=tables)


def group_branch(signs: Sequence[int], x: Sequence[int]) -> int | None:
    """Exact original group-normalized 60/40 compatibility; audit helper."""
    positive = [i for i, s in enumerate(signs) if s == 1]
    negative = [i for i, s in enumerate(signs) if s == -1]
    p = sum(x[i] for i in positive)
    q = sum(x[i] for i in negative)
    a, b = len(positive), len(negative)
    if 5 * p >= 3 * a and 5 * q <= 2 * b:
        return 1
    if 5 * p <= 2 * a and 5 * q >= 3 * b:
        return -1
    return None
