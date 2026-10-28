"""Reproducible finite audits of the exact arithmetic construction.

These checks verify finite algebraic instances, both construction branches,
and the potential calculation. The asymptotic PAC theorem is proved in the
accompanying note; finite checks are not a replacement for that proof.
"""

import json
from pathlib import Path
from fractions import Fraction
from itertools import product
from random import Random

from proper_signed_majority import (
    ceil_log2_ratio, centered_sample, confidence_trials, correct_integer_box,
    fit_sign_vector, group_branch, labeled_sample_bound, round_with_five_bits,
    learn_sign_vector,
)


def audit_margin_implication():
    tested = compatible = 0
    for n in range(1, 9):
        for signs in product((-1, 1), repeat=n):
            for x in product((0, 1), repeat=n):
                tested += 1
                y = group_branch(signs, x)
                if y is not None:
                    compatible += 1
                    score = sum(s * (2 * bit - 1) for s, bit in zip(signs, x))
                    assert 5 * y * score >= n
    return {"all_sign_vector_point_pairs": tested, "compatible_pairs": compatible}


def audit_exhaustive_fits():
    targets = 0
    total_observations = 0
    for n in range(1, 7):
        for target in product((-1, 1), repeat=n):
            sample = [(x, group_branch(target, x))
                      for x in product((0, 1), repeat=n)
                      if group_branch(target, x) is not None]
            fitted = fit_sign_vector(sample, Fraction(1, 4))
            assert fitted.branch == "enumeration"
            assert fitted.certified_training_margin
            assert all(fitted.predict(x) == y for x, y in sample)
            assert all(5 * y * sum(s * (2 * bit - 1)
                                  for s, bit in zip(fitted.signs, x)) >= n
                       for x, y in sample)
            targets += 1
            total_observations += len(sample)
    return {"fully_checked_target_distributions": targets,
            "total_support_observations": total_observations}


def boundary_sample(n, positive_size, m, seed):
    rng = Random(seed)
    pos = list(range(positive_size))
    neg = list(range(positive_size, n))
    a, b = len(pos), len(neg)
    sample = []
    for j in range(m):
        y = 1 if j % 2 == 0 else -1
        p = (3 * a + 4) // 5 if y == 1 else (2 * a) // 5
        q = (2 * b) // 5 if y == 1 else (3 * b + 4) // 5
        active = set(rng.sample(pos, p)) | set(rng.sample(neg, q))
        x = tuple(int(i in active) for i in range(n))
        sample.append((x, y))
    return sample, (1,) * a + (-1,) * b


def audit_large_branch():
    cases = []
    n, m = 2560, 16
    assert n == 512 * ceil_log2_ratio(2 * m)
    for case, positive_size in enumerate((1, n // 4, n // 2, n - 1)):
        sample, target = boundary_sample(n, positive_size, m, 20261020 + case)
        assert all(group_branch(target, x) == y for x, y in sample)
        records = centered_sample(sample)
        corrected = correct_integer_box(records)
        assert corrected.certified and len(corrected.update_indices) <= 182

        a = [0] * n
        t = [16 * s for s in target]
        potential = sum((v - ti) ** 2 for v, ti in zip(a, t))
        for index in corrected.update_indices:
            z, y = records[index]
            assert y * sum(v * zi for v, zi in zip(a, z)) < 2 * n
            a = [max(-16, min(16, v + y * zi)) for v, zi in zip(a, z)]
            new_potential = sum((v - ti) ** 2 for v, ti in zip(a, t))
            assert 5 * (potential - new_potential) > 7 * n
            potential = new_potential
        assert tuple(a) == corrected.coefficients
        assert all(y * sum(v * zi for v, zi in zip(a, z)) >= 2 * n
                   for z, y in records)

        fitted = fit_sign_vector(sample, Fraction(1, 1024),
                                 Random(1000 + case).getrandbits)
        assert fitted.branch == "rounding" and fitted.certified_training_margin
        assert all(fitted.predict(x) == y for x, y in sample)
        scores = [y * sum(s * zi for s, zi in zip(fitted.signs, z))
                  for z, y in records]
        assert 16 * min(scores) >= n
        cases.append({"n": n, "m": m, "positive_group_size": positive_size,
                      "corrections": fitted.corrections,
                      "rounding_trials": fitted.rounding_trials,
                      "smallest_signed_training_score": min(scores)})
    return cases


def audit_exact_rounding_and_integer_bounds():
    for a in range(-16, 17):
        outputs = []
        for r in range(32):
            calls = []
            def bits(k, r=r):
                calls.append(k)
                return r
            outputs.append(round_with_five_bits((a,), bits)[0])
            assert calls == [5]
        assert Fraction(sum(outputs), 32) == Fraction(a, 16)
    for numerator in range(1, 65):
        for denominator in range(1, 33):
            q = ceil_log2_ratio(numerator, denominator)
            assert denominator * 2 ** q >= numerator
            assert q == 0 or denominator * 2 ** (q - 1) < numerator
    epsilon, delta = Fraction(1, 10), Fraction(1, 100)
    q = confidence_trials(delta)
    m = labeled_sample_bound(epsilon, delta)
    assert Fraction(1, 2**q) <= delta / 2
    r = m.bit_length() - 1
    assert m == 2**r
    assert epsilon * m >= 512 * (r + 2) + q
    assert r == 0 or epsilon * (m // 2) < 512 * (r + 1) + q
    k = ceil_log2_ratio(epsilon.denominator, epsilon.numerator)
    assert m <= 2048 * (q + k + 12) / epsilon
    return {"rounded_coefficient_values": 33, "five_bit_inputs_each": 32,
            "exact_example_epsilon": str(epsilon), "exact_example_delta": str(delta),
            "q": q, "r": r, "m": m}


def audit_distinction_from_compatibility():
    x = (1, 1, 1, 1, 1, 0, 0, 0, 0, 0)
    true_positive = {0, 1, 2, 5, 6}
    target = tuple(1 if i in true_positive else -1 for i in range(10))
    candidate = (1,) + (-1,) * 9
    assert group_branch(target, x) == 1
    assert group_branch(candidate, x) is None
    score = sum(s * (2 * bit - 1) for s, bit in zip(candidate, x))
    assert score == 2 and 5 * score == 10
    return {"n": 10, "x": list(x), "target_signs": list(target),
            "candidate_signs": list(candidate), "candidate_centered_score": score,
            "candidate_group_compatibility": False}


def audit_presampling_order():
    n, epsilon, delta = 1, Fraction(9, 10), Fraction(1, 2)
    q = confidence_trials(delta)
    m = labeled_sample_bound(epsilon, delta)
    calls = {"random_calls": 0, "random_bits": 0, "observations": 0}

    def bits(k):
        assert calls["observations"] == 0
        assert k == 5
        calls["random_calls"] += 1
        calls["random_bits"] += k
        return 0

    def observation():
        assert calls["random_calls"] == n * q
        calls["observations"] += 1
        return (1,), 1

    fitted = learn_sign_vector(observation, n, epsilon, delta, bits)
    assert fitted.certified_training_margin and fitted.predict((1,)) == 1
    assert calls["observations"] == m
    assert calls["random_bits"] == 5 * n * q
    return calls


if __name__ == "__main__":
    result = {
        "status": "all finite checks passed",
        "margin_implication": audit_margin_implication(),
        "enumeration_branch": audit_exhaustive_fits(),
        "integer_and_rounding_details": audit_exact_rounding_and_integer_bounds(),
        "large_dimension_branch": audit_large_branch(),
        "full_constructor_randomness_before_sample": audit_presampling_order(),
        "prediction_does_not_imply_compatibility": audit_distinction_from_compatibility(),
    }
    Path(__file__).with_name("proper_verification_results.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": result["status"],
                      "margin_implication": result["margin_implication"],
                      "target_distributions": result["enumeration_branch"]["fully_checked_target_distributions"],
                      "large_branch_cases": len(result["large_dimension_branch"]),
                      "result_file": "proper_verification_results.json"}, indent=2))
