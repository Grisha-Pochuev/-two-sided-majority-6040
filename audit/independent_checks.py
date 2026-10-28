"""Additional audit checks; not a substitute for the mathematical proof.

This file does not write into or modify the publication package.
"""

from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from itertools import product
from math import comb, lcm
from pathlib import Path
import json
import random
import sys

def find_package():
    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()
    for directory in Path(__file__).resolve().parents:
        for candidate in (directory, directory / 'two_sided_majority_6040'):
            if all((candidate/name).is_file() for name in
                   ('majority_6040.py', 'majority_active.py', 'pac_thresholds.py')):
                return candidate
    raise FileNotFoundError('Pass the publication package directory as the first argument')


ROOT = find_package()
sys.path.insert(0, str(ROOT))
import majority_6040 as grp
import majority_active as act
from pac_thresholds import certified_streak_length


def threshold_checks():
    cases = 0
    largest_length = 0
    for phases in (1, 2, 26, 251, 2501):
        for eps in (F(1, 1000), F(1, 7), F(2, 7), F(5, 7), F(99, 100),
                    F(10**30 - 1, 10**30)):
            for delta in (F(1, 2), F(1, 3), F(1, 100), F(1, 2**80),
                          F(2**90 - 1, 2**90)):
                length = certified_streak_length(phases, eps, delta)
                assert isinstance(length, int) and length >= 1
                # Different expression from the implementation's integer test.
                assert phases * (1 - eps)**length <= delta
                assert phases * (1 - eps)**(length - 1) > delta
                cases += 1
                largest_length = max(largest_length, length)
    return {'exact_cases': cases, 'largest_minimal_length': largest_length}


def weak_compositions(total, size):
    if size == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, size - 1):
            yield (first,) + tail


def count_for_distribution(n, point_weights, eps):
    denominator = sum(weight for x, weight in point_weights)
    p = eps / 5
    good_mass = F(0)
    K = 0
    discrete_good = 0
    r = (eps.numerator * n) // (5 * eps.denominator)
    for negative_mask in range(1 << n):
        bad = sum(weight for x, weight in point_weights
                  if 5 * abs(x.bit_count() - 2 * (x & negative_mask).bit_count())
                  < x.bit_count())
        if F(bad, denominator) <= eps:
            K += 1
            negatives = negative_mask.bit_count()
            good_mass += p**negatives * (1 - p)**(n - negatives)
            discrete_good += negatives == r
    assert good_mass >= F(1, 2)
    assert K * (1 - p)**n >= F(1, 2)
    assert 2 * discrete_good >= comb(n, r)
    assert K >= 2
    return K


def counting_checks():
    # Every probability vector with denominator 4 on all seven nonzero points.
    n = 3
    distributions = 0
    total_cases = 0
    for weights in weak_compositions(4, 7):
        points = tuple((i + 1, weight) for i, weight in enumerate(weights) if weight)
        distributions += 1
        for eps in (F(1, 8), F(1, 4), F(1, 2), F(3, 4)):
            count_for_distribution(n, points, eps)
            total_cases += 1
    rng = random.Random(947112)
    for n in (8, 12, 14):
        for _ in range(3):
            points = tuple((rng.randrange(1, 1 << n), rng.randrange(1, 6))
                           for _ in range(11))
            for eps in (F(1, 10), F(4, 5), F(99, 100)):
                count_for_distribution(n, points, eps)
                total_cases += 1
    return {'all_denominator_4_distributions_n3': distributions,
            'exact_distribution_epsilon_cases': total_cases}


def valid_group_pool(n, positive_mask):
    a = positive_mask.bit_count()
    full = (1 << n) - 1
    b = n - a
    pool = []
    for mask in range(1 << n):
        p = (positive_mask & mask).bit_count()
        q = ((full ^ positive_mask) & mask).bit_count()
        positive = 5*p >= 3*a and 5*q <= 2*b
        negative = 5*p <= 2*a and 5*q >= 3*b
        assert not (positive and negative)
        if positive or negative:
            pool.append((tuple((mask >> i) & 1 for i in range(n)),
                         1 if positive else -1))
    return pool


def valid_active_pool(n, positive_mask):
    signs = tuple(1 if positive_mask & (1 << i) else -1 for i in range(n))
    pool = []
    for mask in range(1, 1 << n):
        x = tuple((mask >> i) & 1 for i in range(n))
        score = sum(s*v for s, v in zip(signs, x))
        if 5*abs(score) >= sum(x):
            pool.append((x, 1 if score > 0 else -1))
    return pool


def crosscheck_runs():
    rng = random.Random(531407)
    runs = 0
    observations = 0
    for active in (False, True):
        for n in (1, 2, 3, 5, 8):
            for positives in (0, (1 << n) - 1, rng.randrange(1 << n)):
                pool = (valid_active_pool if active else valid_group_pool)(n, positives)
                history = []
                def sample():
                    item = rng.choice(pool)
                    history.append(item)
                    return item
                model = (act.learn_active_6040 if active else grp.learn_6040)(
                    sample, n, F(2, 7), F(1, 3))
                w = [F(0) for _ in range(n)]
                mistakes = streak = 0
                for x, y in history:
                    v = [F(bit, sum(x)) for bit in x] if active else [F(2*bit-1) for bit in x]
                    score = sum(a*b for a, b in zip(w, v))
                    prediction = 1 if score >= 0 else -1
                    if prediction == y:
                        streak += 1
                    else:
                        mistakes += 1
                        streak = 0
                        w = [a+y*b for a, b in zip(w, v)]
                scale = model.normalization_scale if active else 1
                assert tuple(scale*a for a in w) == model.weights
                assert all(type(weight) is int for weight in model.weights)
                assert model.updates == mistakes
                assert streak == model.streak_length
                assert len(history) == model.labels_used
                for x, y in pool:
                    feature = x if active else [2*bit-1 for bit in x]
                    score = sum(a*b for a, b in zip(w, feature))
                    assert model.predict(x) == (1 if score >= 0 else -1)
                observations += len(history)
                runs += 1
    return {'rational_reference_runs': runs, 'observations_crosschecked': observations}


def exact_adaptive_failure(pool, probabilities, n, eps, delta, active):
    cap = 25*n if active else 25
    length = certified_streak_length(cap+1, eps, delta)
    scale = lcm(*range(1, n+1)) if active else 1
    features = tuple(tuple(scale*bit//sum(x) for bit in x) if active
                     else tuple(2*bit-1 for bit in x) for x, y in pool)
    @lru_cache(None)
    def failure(w, updates):
        wrong = tuple(i for i, ((x, y), v) in enumerate(zip(pool, features))
                      if (1 if sum(a*b for a, b in zip(w, v)) >= 0 else -1) != y)
        error = sum((probabilities[i] for i in wrong), F(0))
        if not wrong:
            return F(0)
        assert updates < cap, (n, active, w, wrong)
        survive = (1-error)**length
        result = survive if error > eps else F(0)
        reach_mistake = (1-survive)/error
        for i in wrong:
            y = pool[i][1]
            next_w = tuple(a+y*b for a, b in zip(w, features[i]))
            result += reach_mistake * probabilities[i] * failure(next_w, updates+1)
        return result
    probability = failure((0,)*n, 0)
    assert probability <= delta
    return {'active': active, 'n': n, 'epsilon': str(eps), 'delta': str(delta),
            'streak': length, 'reachable_states': failure.cache_info().currsize,
            'failure_probability': str(probability)}


def adaptive_checks():
    configurations = []
    for active, n, positive_mask in ((False, 3, 0), (False, 5, 7),
                                    (True, 3, 3), (True, 5, 7)):
        full_pool = (valid_active_pool if active else valid_group_pool)(n, positive_mask)
        if active and n == 5:
            positive = sorted((item for item in full_pool if item[1] == 1),
                              key=lambda item: sum(item[0]), reverse=True)
            negative = sorted((item for item in full_pool if item[1] == -1),
                              key=lambda item: sum(item[0]), reverse=True)
            pool = tuple(positive[:3] + negative[:3])
        else:
            pool = tuple(full_pool)
        assert {y for x, y in pool} == {-1, 1}
        weights = tuple(range(1, len(pool)+1))
        probabilities = tuple(F(w, sum(weights)) for w in weights)
        for eps, delta in ((F(1, 5), F(1, 4)), (F(1, 2), F(1, 3))):
            configurations.append(exact_adaptive_failure(pool, probabilities, n, eps, delta, active))
    return configurations


def zero_and_empty_checks():
    records = []
    for n in (1, 2, 5):
        x = (0,)*n
        # The zero vector is group-compatible precisely at the empty-positive
        # positive target, or empty-negative negative target.
        for mask in range(1 << n):
            positive = tuple(bool(mask & (1 << i)) for i in range(n))
            assert grp.promise_holds(x, 1, positive) == (mask == 0)
            assert grp.promise_holds(x, -1, positive) == (mask == (1 << n)-1)
        for y, positive in ((1, (False,)*n), (-1, (True,)*n)):
            model = grp.learn_6040(lambda: (x, y), n, F(1, 2), F(1, 3))
            assert model.predict(x) == y
            assert model.updates == (0 if y == 1 else 1)
            records.append({'n': n, 'zero_label': y, 'updates': model.updates})
        try:
            act.learn_active_6040(lambda: (x, 1), n, F(1, 2), F(1, 3))
        except ValueError:
            pass
        else:
            raise AssertionError('active zero input accepted')
    return records


def numeric_input_regression():
    # These exact binary floating values passed the old membership checks but
    # used to send updates through floating arithmetic.  In the active case,
    # the old code attempted to convert a common denominator larger than the
    # finite float range.  The corrected learners normalize accepted values.
    n = 1000
    zero = (0.0,)*n
    one = (1.0,)*n
    group_model = grp.learn_6040(lambda: (zero, -1.0), n, F(1, 2), F(1, 3))
    active_model = act.learn_active_6040(lambda: (one, -1.0), n, F(1, 2), F(1, 3))
    assert all(type(w) is int for w in group_model.weights)
    assert all(type(w) is int for w in active_model.weights)
    assert group_model.predict(zero) == -1
    assert active_model.predict(one) == -1
    assert active_model.normalization_scale.bit_length() > 1024
    return {'dimension': n, 'accepted_binary_float_values_normalized': True,
            'common_denominator_bits': active_model.normalization_scale.bit_length()}


def main():
    result = {
        'status': 'PASS',
        'scope': 'Independent finite checks; universal claims need the proof audit.',
        'source_sha256': {name: sha256((ROOT/name).read_bytes()).hexdigest()
                          for name in ('majority_6040.py', 'majority_active.py',
                                       'pac_thresholds.py', 'majority_6040_note.tex')},
        'thresholds': threshold_checks(),
        'counting': counting_checks(),
        'rational_reference': crosscheck_runs(),
        'adaptive_failure': adaptive_checks(),
        'zero_and_empty_groups': zero_and_empty_checks(),
        'numeric_input_regression': numeric_input_regression(),
    }
    path = Path(__file__).with_name('results.json')
    path.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({key: value for key, value in result.items()
                      if key not in ('adaptive_failure', 'source_sha256')}, indent=2))
    print('Exact adaptive phase trees:', len(result['adaptive_failure']))
    print('Largest phase-state count:', max(case['reachable_states'] for case in result['adaptive_failure']))


if __name__ == '__main__':
    main()
