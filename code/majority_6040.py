"""PAC learner for the group-normalized two-sided 60/40 majority promise.

The mathematical guarantee assumes fresh iid examples with correct labels and
one fixed partition of all n coordinates satisfying the promise.  The learner
does not know that partition.  The output is a weighted affine classifier.

All prediction and update arithmetic is integral.  Pass epsilon and delta as
fractions or decimal strings to obtain exact parameter arithmetic as well.
"""

from dataclasses import dataclass
from fractions import Fraction
from typing import Callable, Sequence, Tuple, Union
from pac_thresholds import certified_streak_length

Probability = Union[Fraction, str, int, float]
Example = Tuple[Sequence[int], int]


def _probability(value: Probability) -> Fraction:
    if isinstance(value, Fraction):
        result = value
    elif isinstance(value, float):
        result = Fraction(str(value))
    else:
        result = Fraction(value)
    if not 0 < result < 1:
        raise ValueError("epsilon and delta must be strictly between 0 and 1")
    return result


def exact_streak_length(epsilon: Probability, delta: Probability) -> int:
    """Return the least L>=1 with 26*(1-epsilon)**L <= delta.

    Exact integer comparisons certify the threshold.  In particular, L is
    no larger than ceil(ln(26/delta)/epsilon), the manuscript's upper bound.
    """
    eps = _probability(epsilon)
    dlt = _probability(delta)
    return certified_streak_length(26, eps, dlt)


@dataclass(frozen=True)
class MajorityModel:
    weights: Tuple[int, ...]
    labels_used: int
    updates: int
    streak_length: int

    def predict(self, x: Sequence[int]) -> int:
        if len(x) != len(self.weights) or any(v not in (0, 1) for v in x):
            raise ValueError("x must be an n-dimensional binary vector")
        score = sum(w * (2 * int(v) - 1) for w, v in zip(self.weights, x))
        return 1 if score >= 0 else -1


def learn_6040(
    sample: Callable[[], Example],
    n: int,
    epsilon: Probability = "0.05",
    delta: Probability = "0.05",
    *,
    streak_length: int = None,
) -> MajorityModel:
    """Learn from an iid labeled sampler using at most 26*L observations.

    If streak_length is provided, it must be at least the exact sufficient
    length computed here.  The routine rejects an observed 26th mistake,
    which would contradict the promised model.  Fewer mistakes do not by
    themselves certify the promise; the guarantee is conditional on it.
    """
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")
    required = exact_streak_length(epsilon, delta)
    length = required if streak_length is None else streak_length
    if not isinstance(length, int) or length < required:
        raise ValueError("streak_length is smaller than the certified bound")
    weights = [0] * n
    consecutive = 0
    updates = 0
    for used in range(1, 26 * length + 1):
        x, y = sample()
        if len(x) != n or any(v not in (0, 1) for v in x) or y not in (-1, 1):
            raise ValueError("sampler must return (binary n-vector, +/-1 label)")
        # Membership checks also accept 0.0/1.0. Normalize exact bit values
        # before arithmetic so every stored coefficient stays a Python int.
        x, y = tuple(int(v) for v in x), int(y)
        z = [2 * v - 1 for v in x]
        score = sum(w * v for w, v in zip(weights, z))
        prediction = 1 if score >= 0 else -1
        if prediction == y:
            consecutive += 1
            if consecutive == length:
                return MajorityModel(tuple(weights), used, updates, length)
        else:
            weights = [w + y * v for w, v in zip(weights, z)]
            updates += 1
            consecutive = 0
            if updates > 25:
                raise ValueError("observed 26 mistakes: the 60/40 promise is violated")
    raise RuntimeError("the proved stopping bound was exceeded")


def promise_holds(x: Sequence[int], y: int, positive: Sequence[bool]) -> bool:
    """Exact check for a KNOWN partition; not used by the learner."""
    if len(x) != len(positive) or not x or y not in (-1, 1):
        return False
    if any(v not in (0, 1) for v in x):
        return False
    x = tuple(int(v) for v in x)
    a = sum(positive)
    b = len(x) - a
    p = sum(v for v, is_positive in zip(x, positive) if is_positive)
    q = sum(v for v, is_positive in zip(x, positive) if not is_positive)
    if y == 1:
        return 5 * p >= 3 * a and 5 * q <= 2 * b
    return 5 * p <= 2 * a and 5 * q >= 3 * b
