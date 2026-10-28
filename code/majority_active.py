"""Exact PAC learner for active-indicator two-sided 60/40 majority.

Domain: nonzero vectors x in {0,1}^n.  One fixed unknown sign vector s must
satisfy 5*y*sum(s_i*x_i) >= sum(x_i) almost surely.  Examples supplied to the
learner must be fresh iid observations with correct labels.

The learner returns a weighted linear classifier.  It does not reconstruct
the unknown sign partition or promise output compatibility.  Prediction and
updates use integers; epsilon and delta can be exact fractions or strings.
"""

from dataclasses import dataclass
from fractions import Fraction
from math import lcm
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


def _dimension(n: int) -> None:
    if not isinstance(n, int) or n < 1:
        raise ValueError("n must be a positive integer")


def exact_streak_length(
    n: int, epsilon: Probability, delta: Probability
) -> int:
    """Return the least L>=1 with (25*n+1)*(1-epsilon)**L <= delta.

    All comparisons are integral.  The result is no larger than
    ceil(ln((25*n+1)/delta)/epsilon), the manuscript's upper bound.
    """
    _dimension(n)
    eps = _probability(epsilon)
    dlt = _probability(delta)
    return certified_streak_length(25 * n + 1, eps, dlt)


@dataclass(frozen=True)
class ActiveMajorityModel:
    weights: Tuple[int, ...]
    normalization_scale: int
    labels_used: int
    updates: int
    streak_length: int

    def predict(self, x: Sequence[int]) -> int:
        if len(x) != len(self.weights) or any(v not in (0, 1) for v in x):
            raise ValueError("x must be an n-dimensional binary vector")
        if not any(x):
            raise ValueError("active normalization requires a nonzero example")
        score = sum(w * int(v) for w, v in zip(self.weights, x))
        return 1 if score >= 0 else -1


def learn_active_6040(
    sample: Callable[[], Example],
    n: int,
    epsilon: Probability = "0.05",
    delta: Probability = "0.05",
    *,
    streak_length: int = None,
) -> ActiveMajorityModel:
    """Learn with at most (25*n+1)*L iid labeled observations.

    Q=lcm(1,...,n) is the common denominator for normalized examples x/|x|.
    The integral weights W represent Q*w.  A classification mistake updates
    W by y*(Q/|x|)*x.  Correct predictions, including positive-label ties,
    leave W unchanged.  The procedure stops after L correct predictions in
    succession.  Its returned classifier uses the sign of W*x, with + at 0.

    An optional streak_length may increase, but not decrease, the certified
    threshold.  The mistake cap follows from the fixed-target promise and
    does not by itself verify that promise or that sampling was iid.
    """
    _dimension(n)
    required = exact_streak_length(n, epsilon, delta)
    length = required if streak_length is None else streak_length
    if not isinstance(length, int) or length < required:
        raise ValueError("streak_length is smaller than the certified bound")
    scale = 1
    for k in range(1, n + 1):
        scale = lcm(scale, k)
    weights = [0] * n
    consecutive = 0
    updates = 0
    cap = 25 * n
    for used in range(1, (cap + 1) * length + 1):
        x, y = sample()
        if len(x) != n or any(v not in (0, 1) for v in x) or y not in (-1, 1):
            raise ValueError("sampler must return (binary n-vector, +/-1 label)")
        x, y = tuple(int(v) for v in x), int(y)
        k = sum(x)
        if k == 0:
            raise ValueError("active normalization requires a nonzero example")
        score = sum(w * v for w, v in zip(weights, x))
        prediction = 1 if score >= 0 else -1
        if prediction == y:
            consecutive += 1
            if consecutive == length:
                return ActiveMajorityModel(tuple(weights), scale, used, updates, length)
        else:
            step = y * (scale // k)
            weights = [w + step * v for w, v in zip(weights, x)]
            updates += 1
            consecutive = 0
            if updates > cap:
                raise ValueError("observed more than 25*n mistakes: the fixed-target promise is violated")
    raise RuntimeError("the proved stopping bound was exceeded")


def promise_holds(x: Sequence[int], y: int, signs: Sequence[int]) -> bool:
    """Check the active promise for a KNOWN +/-1 target; not used to learn."""
    if len(x) != len(signs) or not x or y not in (-1, 1):
        return False
    if any(v not in (0, 1) for v in x) or any(s not in (-1, 1) for s in signs):
        return False
    x, signs, y = tuple(int(v) for v in x), tuple(int(s) for s in signs), int(y)
    k = sum(x)
    if k == 0:
        return False
    return 5 * y * sum(s * v for s, v in zip(signs, x)) >= k
