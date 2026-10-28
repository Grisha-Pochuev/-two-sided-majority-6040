"""Independent rational checks of exact stopping and integral input handling."""

from fractions import Fraction
import json
from pathlib import Path

from pac_thresholds import certified_streak_length
from majority_6040 import learn_6040
from majority_active import learn_active_6040
from proper_signed_majority import centered_sample, round_with_five_bits


def check_minimal_thresholds():
    count = 0
    for denominator in range(2, 21):
        for numerator in range(1, denominator):
            epsilon = Fraction(numerator, denominator)
            for delta in (Fraction(1, 2), Fraction(1, 10),
                          Fraction(1, 101), Fraction(9, 10)):
                for phases in (1, 2, 26, 251, 2501):
                    length = certified_streak_length(phases, epsilon, delta)
                    # Check the mathematical rational inequality directly,
                    # independently of the integer-search implementation.
                    assert phases * (1 - epsilon) ** length <= delta
                    assert phases * (1 - epsilon) ** (length - 1) > delta
                    count += 1
    extremes = (
        (26, Fraction(999999, 1000000), Fraction(1, 10**100)),
        (25000001, Fraction(1, 100), Fraction(1, 10**30)),
        (1, Fraction(1, 2), Fraction(999999, 1000000)),
    )
    for phases, epsilon, delta in extremes:
        length = certified_streak_length(phases, epsilon, delta)
        assert phases * (1 - epsilon) ** length <= delta
        assert phases * (1 - epsilon) ** (length - 1) > delta
        count += 1
    return count


def check_integral_inputs():
    # A negative label forces a nonzero update, exposing any float weights.
    group = learn_6040(lambda: ((1.0,), -1.0), 1, "0.1", "0.05")
    active = learn_active_6040(lambda: ((1.0,), -1.0), 1, "0.1", "0.05")
    assert group.updates == active.updates == 1
    assert all(type(w) is int for w in group.weights + active.weights)
    assert group.predict((1.0,)) == active.predict((1.0,)) == -1
    records = centered_sample([((0.0, 1.0), -1.0)])
    assert all(type(v) is int for v in records[0][0])
    assert type(records[0][1]) is int
    try:
        round_with_five_bits((Fraction(1, 2),), lambda _: 0)
    except ValueError:
        pass
    else:
        raise AssertionError("rounding must reject nonintegral coefficients")
    try:
        learn_active_6040(lambda: ((0,), 1), 1, "0.1", "0.05")
    except ValueError:
        pass
    else:
        raise AssertionError("the active learner must reject a zero vector")
    return {"normalized_integral_coefficients": True,
            "nonintegral_rounding_coefficients_rejected": True,
            "zero_active_vector_rejected": True,
            "group_example_length": group.streak_length,
            "active_example_length": active.streak_length}


if __name__ == "__main__":
    result = {"status": "PASS", "minimal_exact_threshold_checks": check_minimal_thresholds(),
              "input_boundary_checks": check_integral_inputs()}
    Path(__file__).with_name("threshold_verification_results.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
