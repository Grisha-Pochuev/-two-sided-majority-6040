"""Finite checks for the active-normalization learner and counting lemma.

Run: python3 verify_active.py
Writes active_verification_results.json next to this file.  Only the Python standard
library is required.  These finite checks are not a proof of the universal
theorem, of iid sampling, or of the promised model on an arbitrary dataset.
"""

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import json
import random

from majority_active import exact_streak_length, learn_active_6040, promise_holds


def exact_edge_probability_checks():
    reports = []
    for eps in (Fraction(1, 2), Fraction(1, 10), Fraction(1, 100)):
        p = eps / 5
        values = []
        for k in range(1, 61):
            bad = sum((Fraction(comb(k, r)) * p**r * (1-p)**(k-r)
                       for r in range(k+1) if 5*abs(k-2*r) < k), Fraction(0))
            assert bad <= eps / 2
            values.append((bad, k))
        largest, at_k = max(values)
        reports.append({
            "epsilon": str(eps), "minus_probability": str(p),
            "edge_sizes_checked": [1, 60], "number_of_exact_checks": 60,
            "maximum_bad_probability": str(largest), "a_maximizing_edge_size": at_k,
            "all_bad_probabilities_le_epsilon_over_two": True,
        })
    return reports


def exact_finite_counting_checks():
    n = 6
    distributions = {
        "one_singleton_n1": (1, [1]),
        "all_singletons_n6": (n, [1 << i for i in range(n)]),
        "one_full_example_n6": (n, [(1 << n)-1]),
        "all_pairs_n6": (n, [(1 << i) | (1 << j) for i, j in combinations(range(n), 2)]),
        "mixed_support_sizes_n6": (n, [1, 2, 3, 5, 9, 17, 33, 15, 63]),
    }
    reports = []
    for name, (n, support_list) in distributions.items():
        for eps in (Fraction(1, 2), Fraction(1, 10), Fraction(1, 100)):
            p = eps / 5
            good_mass = Fraction(0)
            K = 0
            for negative_mask in range(1 << n):
                bad = 0
                for x in support_list:
                    k = x.bit_count()
                    r = (x & negative_mask).bit_count()
                    bad += 5 * abs(k-2*r) < k
                unlabeled_error = Fraction(bad, len(support_list))
                if unlabeled_error <= eps:
                    K += 1
                    r = negative_mask.bit_count()
                    good_mass += p**r * (1-p)**(n-r)
            max_atom = (1-p)**n
            assert good_mass >= Fraction(1, 2)
            assert K * max_atom >= Fraction(1, 2)
            assert K >= 2
            reports.append({
                "distribution": name, "dimension": n,
                "uniform_support_list_size": len(support_list),
                "epsilon": str(eps), "K_epsilon": K,
                "biased_good_mass": str(good_mass),
                "K_times_maximum_atom": str(K*max_atom),
                "both_exact_quantities_at_least_one_half": True,
            })
    return reports


def boundary_example(rng, signs, requested_k, y):
    aligned = [i for i, s in enumerate(signs) if s == y]
    opposite = [i for i, s in enumerate(signs) if s == -y]
    if not aligned:
        y = -y
        aligned, opposite = opposite, aligned
    k = min(requested_k, len(signs), 5 * len(aligned) // 3)
    k = max(k, 1)
    a_min = max((3*k+4)//5, k-len(opposite))
    assert a_min <= min(k, len(aligned))
    x = [0] * len(signs)
    for i in rng.sample(aligned, a_min):
        x[i] = 1
    for i in rng.sample(opposite, k-a_min):
        x[i] = 1
    assert promise_holds(x, y, signs)
    return tuple(x), y


def finite_iid_pool_trials():
    rng = random.Random(20261020)
    eps, delta = Fraction(1, 10), Fraction(1, 20)
    configs = [
        (1, 0, "singletons"), (1, 1, "singletons"),
        (6, 3, "mixed"), (20, 7, "mixed"),
        (50, 25, "singletons"), (100, 10, "mixed"),
        (100, 50, "mixed"), (100, 90, "mixed"),
    ]
    reports = []
    errors_above_epsilon = 0
    for n, positives, mode in configs:
        signs = (1,) * positives + (-1,) * (n-positives)
        pool = []
        for i in range(n):
            x = tuple(1 if j == i else 0 for j in range(n))
            pool.append((x, signs[i]))
        if mode == "mixed":
            sizes = (1, 2, 3, max(1, n//3), max(1, 2*n//3), n)
            for _ in range(240):
                pool.append(boundary_example(rng, signs, rng.choice(sizes), rng.choice((-1, 1))))
            # Repeated points are retained: D is uniform on this exact list.
            repeated = boundary_example(rng, signs, max(1, n//2), 1)
            pool.extend([repeated] * 60)
        assert all(promise_holds(x, y, signs) for x, y in pool)
        runs = []
        for _ in range(8):
            model = learn_active_6040(lambda: rng.choice(pool), n, eps, delta)
            errors = sum(model.predict(x) != y for x, y in pool)
            population_error = Fraction(errors, len(pool))
            errors_above_epsilon += population_error > eps
            assert model.updates <= 25*n
            assert model.labels_used <= (25*n+1)*model.streak_length
            assert all(isinstance(w, int) for w in model.weights)
            assert all(abs(w) <= 25*n*model.normalization_scale for w in model.weights)
            runs.append({"updates": model.updates, "labels_used": model.labels_used,
                         "exact_population_error": str(population_error)})
        reports.append({
            "dimension": n, "positive_signs": positives, "sampling_mode": mode,
            "uniform_support_list_size": len(pool),
            "active_counts_in_pool": sorted({sum(x) for x, y in pool}),
            "runs": runs,
        })
    return {"epsilon": str(eps), "delta": str(delta), "number_of_trials": 64,
            "trials_with_error_above_epsilon": errors_above_epsilon,
            "note": "Observed errors are recorded; finite trials do not prove the confidence guarantee.",
            "configurations": reports}


def exact_stopping_checks():
    reports = []
    for n in (1, 10, 100):
        for eps in (Fraction(1, 2), Fraction(1, 10), Fraction(1, 100)):
            for delta in (Fraction(1, 2), Fraction(1, 20), Fraction(1, 10000)):
                length = exact_streak_length(n, eps, delta)
                bound = (25*n+1) * (1-eps)**length
                assert bound <= delta
                reports.append({
                    "dimension": n, "epsilon": str(eps), "delta": str(delta),
                    "exact_integer_L": length,
                    "exact_survival_bound_le_delta": True,
                })
    return reports


def main():
    results = {
        "status": "PASS",
        "scope": "finite checks only; the universal theorem requires its mathematical proof",
        "edge_probability_checks": exact_edge_probability_checks(),
        "finite_counting_checks": exact_finite_counting_checks(),
        "iid_pool_trials": finite_iid_pool_trials(),
        "exact_stopping_checks": exact_stopping_checks(),
    }
    destination = Path(__file__).with_name("active_verification_results.json")
    destination.write_text(json.dumps(results, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({
        "status": results["status"], "exact_edge_probability_checks": 180,
        "exact_finite_distribution_counting_checks": len(results["finite_counting_checks"]),
        "iid_learner_trials": results["iid_pool_trials"]["number_of_trials"],
        "trials_with_error_above_epsilon": results["iid_pool_trials"]["trials_with_error_above_epsilon"],
        "exact_stopping_checks": len(results["exact_stopping_checks"]),
        "result_file": str(destination),
    }, indent=2))


if __name__ == "__main__":
    main()
