"""Finite checks of the explicit compatibility reduction, not a proof.

The default run uses only the Python standard library.  Pass --with-solver
to additionally check three instances with SciPy/HiGHS MILP.  A requested
but incomplete solver check gives INCONCLUSIVE and a nonzero exit status.
"""
from itertools import product
from pathlib import Path
import argparse
import json
import math


def _require(condition, message):
    # Verification must remain enabled even under python -O.
    if not condition:
        raise AssertionError(message)


def _validated_formula(clauses, width, variables):
    """Return immutable clauses and the unpadded number of variables."""
    if variables is not None and (type(variables) is not int or variables < 0):
        raise ValueError("variables must be a nonnegative integer or None")
    try:
        clauses = tuple(tuple(clause) for clause in clauses)
    except TypeError as exc:
        raise TypeError("clauses must be an iterable of literal iterables") from exc
    largest = 0
    for clause in clauses:
        if len(clause) != width:
            raise ValueError(f"each clause must contain exactly {width} literals")
        if any(type(lit) is not int or lit == 0 for lit in clause):
            raise ValueError("literals must be nonzero Python integers; bool is not a literal")
        if len({abs(lit) for lit in clause}) != width:
            raise ValueError("the variables in a clause must be distinct")
        largest = max(largest, *(abs(lit) for lit in clause))
    if variables is None:
        variables = largest
    if variables < largest:
        raise ValueError("variables is smaller than a literal's absolute index")
    return clauses, variables


def build(clauses, variables=None):
    """Reduce signed exact-2-in-4-SAT to unlabeled 60/40 compatibility.

    Variable identifiers are positive, one-based integers.  By default the
    dimension includes their maximum index; an explicit count may include
    unused variables but cannot omit an index occurring in the formula.
    The logical count is padded to a multiple of four and at least twelve.
    """
    clauses, variables = _validated_formula(clauses, 4, variables)
    v = max(12, 4 * ((variables + 3) // 4))
    h = v // 2
    anchors = (1,) * (v // 4) + (-1,) * (v // 4)
    e0 = (1,) * h + (-1,) * h
    base = tuple(value for e in e0 for value in (e, e))
    core = []
    paths = []

    def add_core(row):
        core.append(tuple(row))
        core.append(tuple(-z for z in row))

    add_core(base)
    tree = [(0, j) for j in range(h, v)] + [(i, h) for i in range(1, h)]
    for i, j in tree:
        e = list(e0)
        e[i], e[j] = e[j], e[i]
        add_core(tuple(value for t in e for value in (t, t)))
    for clause in clauses:
        chosen = {abs(t) - 1: 1 if t > 0 else -1 for t in clause}
        inactive = [i for i in range(v) if i not in chosen]
        signs = {i: 1 if k < len(inactive) // 2 else -1
                 for k, i in enumerate(inactive)}
        row = []
        for i in range(v):
            row.extend((chosen[i], -chosen[i]) if i in chosen
                       else (signs[i], signs[i]))
        add_core(row)
    vertices = set(core)
    for start in core:
        row = list(start)
        path = [tuple(row)]
        mixed = [i for i in range(v) if row[2*i] != row[2*i+1]]
        if mixed:
            _require(len(mixed) == 4, "a clause row must have four mixed pairs")
            for k, i in enumerate(mixed):
                e = 1 if k < 2 else -1
                row[2*i:2*i+2] = (e, e)
            path.append(tuple(row))
        while tuple(row) != base:
            i = next(i for i in range(h) if row[2*i] == -1)
            j = next(j for j in range(h, v) if row[2*j] == 1)
            row[2*i:2*i+2] = (1, 1)
            row[2*j:2*j+2] = (-1, -1)
            path.append(tuple(row))
        paths.append(path)
        vertices.update(path)
    for path in paths:
        _require(path[-1] == base, "path does not end at the base row")
        for a, b in zip(path, path[1:]):
            _require(sum(x != y for x, y in zip(a, b)) == 4,
                     "a path step does not have Hamming distance four")
    for row in vertices:
        _require(len(row) == 2*v and sum(row) == 0, "unbalanced free row")
    rows = sorted(vertices)
    points = [tuple((1+z)//2 for z in anchors + row) for row in rows]
    _require(all(len(x) == 5*v//2 and 2*sum(x) == len(x) for x in points),
             "wrong dimension or unbalanced point")
    return v, anchors, rows, points


def compatible(x, signs):
    if len(x) != len(signs):
        raise ValueError("point and sign vector must have equal lengths")
    a = sum(s == 1 for s in signs)
    b = len(signs) - a
    p = sum(bit for bit, s in zip(x, signs) if s == 1)
    q = sum(bit for bit, s in zip(x, signs) if s == -1)
    pos = 5*p >= 3*a and 5*q <= 2*b
    neg = 5*p <= 2*a and 5*q >= 3*b
    return pos, neg


def _satisfies(clauses, assignment):
    return all(sum((1 if lit > 0 else -1) * assignment[abs(lit)-1]
                   for lit in clause) == 0 for clause in clauses)


def sat_solutions(clauses, v):
    clauses, v = _validated_formula(clauses, 4, v)
    for assignment in product((-1, 1), repeat=v):
        if _satisfies(clauses, assignment):
            yield assignment


def transform_three_sat(clauses, variables=None):
    """Return the explicit 3-SAT -> signed exact-2-in-4-SAT construction.

    Every source clause must have three distinct variables.  A single fresh
    F is shared.  Clause (a,b,c) gets fresh d,w1,w2 and produces
    (a,b,d,w1), (-d,c,F,w2).  With F=false this is equivalent, after
    existentially choosing the fresh variables, to a OR b OR c.  Without
    fixing F, global complementation orients any solution to F=false.
    Metadata exposes every fresh identifier so witnesses can be replayed.
    """
    clauses, source_variables = _validated_formula(clauses, 3, variables)
    false_variable = source_variables + 1
    next_variable = false_variable + 1
    transformed = []
    gadgets = []
    for a, b, c in clauses:
        d, w1, w2 = range(next_variable, next_variable + 3)
        next_variable += 3
        transformed.extend(((a, b, d, w1), (-d, c, false_variable, w2)))
        gadgets.append({"source_clause": (a, b, c), "d": d,
                        "w_first": w1, "w_second": w2})
    _validated_formula(transformed, 4, next_variable - 1)
    return {"clauses": tuple(transformed), "variables": next_variable - 1,
            "source_variables": source_variables, "false_variable": false_variable,
            "gadgets": tuple(gadgets)}


def solve_original_unlabeled_milp(points, time_limit=45.0):
    """Optional numerical search; every returned witness is checked exactly."""
    import numpy as np
    from scipy.optimize import milp, Bounds, LinearConstraint
    from scipy.sparse import lil_matrix

    if not points or not points[0]:
        raise ValueError("MILP requires a nonempty list of nonempty points")
    n, count = len(points[0]), len(points)
    if any(len(x) != n or any(type(t) is not int or t not in (0, 1) for t in x)
           for x in points):
        raise ValueError("MILP points must be equal-length binary integer tuples")
    if not math.isfinite(time_limit) or time_limit <= 0:
        raise ValueError("time_limit must be finite and positive")
    big_m = 5*n
    mat = lil_matrix((4*count, n+count), dtype=float)
    lower = np.full(4*count, -np.inf)
    upper = np.full(4*count, np.inf)
    for j, x in enumerate(points):
        r = sum(x)
        c1 = [5*t - 3 for t in x]
        c2 = [5*t - 2 for t in x]
        for off, coefficients in enumerate((c1, c2, c2, c1)):
            mat[4*j+off, :n] = coefficients
            mat[4*j+off, n+j] = -big_m
        lower[4*j] = -big_m
        lower[4*j+1] = 5*r-2*n-big_m
        upper[4*j+2] = 0
        upper[4*j+3] = 5*r-3*n
    lo, hi = np.zeros(n+count), np.ones(n+count)
    # Global reversal permits this orientation for any feasible instance.
    lo[n] = 1
    result = milp(np.zeros(n+count), integrality=np.ones(n+count),
                  bounds=Bounds(lo, hi),
                  constraints=LinearConstraint(mat.tocsr(), lower, upper),
                  options={"time_limit": time_limit, "mip_rel_gap": 0.0})
    report = {"status": int(result.status), "message": str(result.message),
              "checked_integer_witness": False}
    if result.x is not None:
        signs = tuple(1 if t > 0.5 else -1 for t in result.x[:n])
        branches = [compatible(x, signs) for x in points]
        report.update({"witness_signs": list(signs),
                       "checked_integer_witness": all(p or q for p, q in branches),
                       "all_positive_branch": all(p for p, q in branches),
                       "positive_group_size": sum(t == 1 for t in signs)})
    return report


def _solver_verdict(report, source_satisfiable):
    has_witness = bool(report.get("witness_signs"))
    if has_witness and (not report.get("checked_integer_witness")
                        or not report.get("all_positive_branch")
                        or not source_satisfiable):
        return "FAIL"
    if report["status"] == 0:
        return "PASS" if source_satisfiable and has_witness else "FAIL"
    if report["status"] == 2:
        return "FAIL" if source_satisfiable or has_witness else "PASS"
    # In particular, a timeout is not a completed check, even with an incumbent.
    return "INCONCLUSIVE"


def _check_local_gadgets():
    nae = lambda bits: any(bits) and not all(bits)
    for a, b, c, f in product((False, True), repeat=4):
        split = any(nae((a, b, d)) and nae((not d, c, f)) for d in (False, True))
        full = any(sum((a, b, d, w1)) == 2 and sum((not d, c, f, w2)) == 2
                   for d, w1, w2 in product((False, True), repeat=3))
        _require(nae((a, b, c, f)) == split == full, "NAE4 gadget failed")
        _require(nae((a, b, c, f)) == nae((not a, not b, not c, not f)),
                 "global complement symmetry failed")
    for a, b, c in product((False, True), repeat=3):
        exact_extension = any(sum((a, b, c, w)) == 2 for w in (False, True))
        _require(nae((a, b, c)) == exact_extension, "NAE3 to exact-two gadget failed")
        _require(nae((a, b, c, False)) == (a or b or c), "F=false orientation failed")
    signed_cases = 0
    for polarities in product((-1, 1), repeat=3):
        clause = tuple(polarities[i] * (i+1) for i in range(3))
        transformed = transform_three_sat([clause])
        gadget = transformed["gadgets"][0]
        for source in product((-1, 1), repeat=3):
            extension_exists = False
            for extension in product((-1, 1), repeat=3):
                assignment = list(source) + [-1] * (transformed["variables"] - 3)
                assignment[transformed["false_variable"] - 1] = -1
                for key, value in zip(("d", "w_first", "w_second"), extension):
                    assignment[gadget[key] - 1] = value
                extension_exists |= _satisfies(transformed["clauses"], assignment)
            _require(extension_exists == any(a*b == 1 for a, b in zip(polarities, source)),
                     "signed 3-SAT gadget failed")
            signed_cases += 1
    transformed = transform_three_sat([(1, -2, 3), (-1, 4, -5), (2, -4, 6)])
    fresh = [transformed["false_variable"]]
    for gadget in transformed["gadgets"]:
        fresh.extend(gadget[key] for key in ("d", "w_first", "w_second"))
    _require(len(fresh) == len(set(fresh)) and min(fresh) > 6,
             "fresh gadget variables collide")
    return {"nae4_truth_cases": 16, "nae3_truth_cases": 8,
            "composed_nae4_truth_cases": 16, "signed_three_sat_truth_cases": signed_cases,
            "fresh_variable_check": True}


def _check_inputs():
    rejected = 0
    invalid_calls = [
        ([(1, 2, 3)], None), ([(1, 2, 3, 0)], None),
        ([(1, 2, 3, True)], None), ([(1, 2, 3, 4.0)], None),
        ([(1, -1, 3, 4)], None), ([(1, 2, 3, 4)], 3),
        ([(13, 14, 15, 16)], 12), ([], -1), ([], True), ([], 12.0),
        (None, None), ([1], None),
    ]
    for clauses, variables in invalid_calls:
        try:
            build(clauses, variables)
        except (ValueError, TypeError):
            rejected += 1
        else:
            raise AssertionError("an invalid constructor input was accepted")
    _require(build([], variables=0)[0] == 12, "empty-formula padding failed")
    high = [(13, 14, 15, 16), (-13, 14, 15, 16)]
    v, anchors, rows, points = build(high)
    _require(v == 16 and len(points[0]) == 40, "high indices were not included")
    _require(any([i for i in range(v) if row[2*i] != row[2*i+1]] == [12, 13, 14, 15]
                 for row in rows), "high-index clause coordinates were dropped")
    for tail in product((-1, 1), repeat=4):
        assignment = (1,) * 12 + tail
        signs = anchors + tuple(z for value in assignment for z in (value, -value))
        _require(not _satisfies(high, assignment), "contradictory regression formula became SAT")
        _require(not all(any(compatible(x, signs)) for x in points),
                 "the former false witness survived the corrected construction")
    return {"invalid_calls_rejected": rejected, "high_index_dimension": 40,
            "high_index_candidate_assignments_checked": 16}


def _check_status_rules():
    valid = {"witness_signs": [1], "checked_integer_witness": True,
             "all_positive_branch": True}
    cases = [({"status": 0, **valid}, True, "PASS"),
             ({"status": 0, **valid}, False, "FAIL"),
             ({"status": 0}, True, "FAIL"),
             ({"status": 2}, False, "PASS"),
             ({"status": 2}, True, "FAIL"),
             ({"status": 2, **valid}, True, "FAIL"),
             ({"status": 0, **valid, "checked_integer_witness": False}, True, "FAIL")]
    for status in (1, 3, 4, -1):
        cases.extend([({"status": status}, False, "INCONCLUSIVE"),
                      ({"status": status, **valid}, True, "INCONCLUSIVE")])
    for report, truth, expected in cases:
        _require(_solver_verdict(report, truth) == expected, "solver verdict rule failed")
    return {"status_rule_cases": len(cases), "timeout_with_witness_is_inconclusive": True}


def _check_case(clauses, expected_sat, with_solver, time_limit):
    v, anchors, rows, points = build(clauses)
    n = len(points[0])
    _require(20 < n, "Hamming-four edges do not separate the two branches")
    # An independent traversal verifies connectivity of the actual output set.
    remaining = set(rows)
    frontier = [remaining.pop()]
    while frontier:
        row = frontier.pop()
        adjacent = {other for other in remaining
                    if sum(a != b for a, b in zip(row, other)) == 4}
        remaining.difference_update(adjacent)
        frontier.extend(adjacent)
    _require(not remaining, "the output Hamming-four graph is disconnected")
    count = 0
    first_assignment = first_signs = None
    for assignment in sat_solutions(clauses, v):
        signs = anchors + tuple(z for value in assignment for z in (value, -value))
        _require(all(compatible(x, signs) == (True, False) for x in points),
                 "a satisfying source assignment lost compatibility on an output point")
        count += 1
        if first_assignment is None:
            first_assignment, first_signs = assignment, signs
    source_sat = count > 0
    _require(source_sat == expected_sat, "source brute force disagrees with expected truth")
    report = {"status": "PASS", "logical_variables_with_padding": v,
              "dimension": n, "points": len(points), "hamming_four_connected": True,
              "source_satisfiable": source_sat, "sat_assignments_checked": count}
    if source_sat:
        report.update({"source_witness": list(first_assignment),
                       "witness_signs": list(first_signs)})
    if with_solver:
        try:
            solver = solve_original_unlabeled_milp(points, time_limit)
        except ImportError as exc:
            solver = {"verdict": "INCONCLUSIVE", "error": str(exc)}
        else:
            solver["verdict"] = _solver_verdict(solver, source_sat)
        report["original_unlabeled_milp"] = solver
        report["status"] = solver["verdict"]
    return report


def run_checks(with_solver=False, time_limit=45.0):
    tests = {
        "one_satisfiable_clause": ([(1, 2, 3, 4)], True),
        "two_contradictory_clauses": ([(1, 2, 3, 4), (-1, 2, 3, 4)], False),
        "three_satisfiable_signed_clauses":
            ([(1, 2, 3, 4), (-1, -2, 5, 6), (3, -4, 5, -6)], True),
    }
    checks = {"input_validation": _check_inputs, "local_gadgets": _check_local_gadgets,
              "solver_status_rules": _check_status_rules}
    for name, (clauses, expected) in tests.items():
        checks[name] = lambda c=clauses, e=expected: _check_case(c, e, with_solver, time_limit)
    reports = {}
    for name, check in checks.items():
        try:
            result = check()
            result.setdefault("status", "PASS")
        except Exception as exc:
            result = {"status": "FAIL", "error": f"{type(exc).__name__}: {exc}"}
        reports[name] = result
    statuses = {report["status"] for report in reports.values()}
    status = "FAIL" if "FAIL" in statuses else "INCONCLUSIVE" if "INCONCLUSIVE" in statuses else "PASS"
    return {"status": status, "solver_requested": with_solver,
            "notice": "Finite checks are not a proof; the manuscript gives the universal reduction.",
            "checks": reports}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--with-solver", action="store_true", help="add optional SciPy/HiGHS MILP checks")
    parser.add_argument("--solver-time-limit", type=float, default=45.0,
                        help="positive time limit in seconds for each requested MILP check")
    parser.add_argument("--output", type=Path,
                        default=Path(__file__).with_name("compatibility_verification_results.json"))
    args = parser.parse_args(argv)
    if not math.isfinite(args.solver_time_limit) or args.solver_time_limit <= 0:
        parser.error("--solver-time-limit must be finite and positive")
    report = run_checks(args.with_solver, args.solver_time_limit)
    with args.output.open("w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2, ensure_ascii=False)
        handle.write("\n")
    print(json.dumps({"status": report["status"], "solver_requested": args.with_solver,
                      "checks": {name: value["status"] for name, value in report["checks"].items()},
                      "results_file": str(args.output)}, ensure_ascii=False), flush=True)
    return {"PASS": 0, "FAIL": 1, "INCONCLUSIVE": 2}[report["status"]]


if __name__ == "__main__":
    raise SystemExit(main())

