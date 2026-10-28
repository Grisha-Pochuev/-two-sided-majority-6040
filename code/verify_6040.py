"""Reproducible checks of the implementation and edge cases, not a proof.

Run: python3 verify_6040.py
Writes verification_results.json next to this file.
Uses only the Python standard library.
"""

import json
import random
from fractions import Fraction
from pathlib import Path

from majority_6040 import learn_6040, promise_holds, exact_streak_length


def exhaustive_margin_check(max_n=10):
    pairs_checked = 0
    admissible_labeled_pairs = 0
    min_ratio = None
    for n in range(1, max_n + 1):
        full = (1 << n) - 1
        for positive_mask in range(1 << n):
            a = positive_mask.bit_count()
            b = n - a
            for x in range(1 << n):
                pairs_checked += 1
                p = (positive_mask & x).bit_count()
                q = ((full ^ positive_mask) & x).bit_count()
                score = (2 * p - a) - (2 * q - b)
                positive = 5 * p >= 3 * a and 5 * q <= 2 * b
                negative = 5 * p <= 2 * a and 5 * q >= 3 * b
                assert not (positive and negative)
                for y, valid in [(1, positive), (-1, negative)]:
                    if valid:
                        admissible_labeled_pairs += 1
                        assert 5 * y * score >= n
                        ratio = Fraction(y * score, n)
                        min_ratio = ratio if min_ratio is None else min(min_ratio, ratio)
    return {
        "max_n": max_n,
        "partition_example_pairs_checked": pairs_checked,
        "admissible_labeled_pairs_checked": admissible_labeled_pairs,
        "minimum_normalized_signed_margin": str(min_ratio),
        "includes_empty_groups": True,
    }


def example_with_counts(rng, n, a, y, boundary=True):
    # The learner never receives a, p, q, or the target partition.
    if y == 1:
        p_lo, p_hi, q_lo, q_hi = (3 * a + 4) // 5, a, 0, 2 * (n - a) // 5
        p, q = (p_lo, q_hi) if boundary else (rng.randint(p_lo, p_hi), rng.randint(q_lo, q_hi))
    else:
        p_lo, p_hi, q_lo, q_hi = 0, 2 * a // 5, (3 * (n - a) + 4) // 5, n - a
        p, q = (p_hi, q_lo) if boundary else (rng.randint(p_lo, p_hi), rng.randint(q_lo, q_hi))
    x = [0] * n
    for i in rng.sample(range(a), p):
        x[i] = 1
    for i in rng.sample(range(a, n), q):
        x[i] = 1
    assert promise_holds(x, y, [i < a for i in range(n)])
    return tuple(x), y


def finite_distribution_trials():
    rng = random.Random(20261020)
    eps, delta = Fraction(1, 10), Fraction(1, 20)
    configs = [(1, 0), (1, 1), (10, 1), (10, 9), (20, 10), (100, 10), (100, 50), (100, 90)]
    results = []
    for n, a in configs:
        pool = [example_with_counts(rng, n, a, 1 if rng.random() < 0.5 else -1)
                for _ in range(240)]
        # Includes class imbalance; D is exactly uniform on this finite list.
        pool.extend([example_with_counts(rng, n, a, 1)] * 60)
        runs = []
        for _ in range(12):
            model = learn_6040(lambda: rng.choice(pool), n, eps, delta)
            errors = sum(model.predict(x) != y for x, y in pool)
            assert model.updates <= 25
            assert model.labels_used <= 26 * model.streak_length
            assert all(abs(w) <= 25 for w in model.weights)
            runs.append({"updates": model.updates, "labels_used": model.labels_used,
                         "exact_population_error": str(Fraction(errors, len(pool)))})
        results.append({"n": n, "positive_group_size": a, "support_list_size": len(pool), "runs": runs})
    return {"epsilon": str(eps), "delta": str(delta), "trials": results}


def centering_counterexample():
    # Correct + label despite p-q < 0 when the negative group is much larger.
    n, a, p, q = 100, 10, 6, 36
    raw_score = p - q
    centered_score = 2 * (p - q) - (2 * a - n)
    assert raw_score == -30 and centered_score == 20
    return {"n": n, "P_size": a, "N_size": n - a, "p": p, "q": q,
            "label": 1, "uncentered_score": raw_score,
            "centered_score": centered_score}


def exact_probability_check():
    results = []
    for eps in [Fraction(1, 2), Fraction(1, 10), Fraction(1, 100)]:
        for delta in [Fraction(1, 2), Fraction(1, 20), Fraction(1, 10000)]:
            length = exact_streak_length(eps, delta)
            upper = 26 * (1 - eps) ** length
            assert upper <= delta
            results.append({"epsilon": str(eps), "delta": str(delta), "L": length,
                            "26_times_survival_probability_le_delta": True})
    return results


def main():
    results = {
        "status": "PASS",
        "scope": "finite checks only; the universal result is proved in the research note",
        "exhaustive_margin": exhaustive_margin_check(),
        "centering_edge_case": centering_counterexample(),
        "exact_probability_bounds": exact_probability_check(),
        "implementation_trials": finite_distribution_trials(),
    }
    path = Path(__file__).with_name("verification_results.json")
    path.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"status": results["status"],
                      "exhaustive_margin": results["exhaustive_margin"],
                      "iid_learner_trials": 8 * 12,
                      "result_file": path.name}, indent=2))


if __name__ == "__main__":
    main()
