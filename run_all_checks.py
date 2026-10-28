#!/usr/bin/env python3
"""Run finite checks on an isolated copy; keep the archived results intact."""

from argparse import ArgumentParser
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time


ROOT = Path(__file__).resolve().parent
SUITES = (
    ("group", "verify_6040.py", "verification_results.json"),
    ("active", "verify_active.py", "active_verification_results.json"),
    ("signed_literal", "check_proper.py", "proper_verification_results.json"),
    ("thresholds", "verify_thresholds.py", "threshold_verification_results.json"),
    ("compatibility", "verify_reduction.py", "compatibility_verification_results.json"),
)
PASS_STATUSES = {"PASS", "all finite checks passed"}


def file_hash(path):
    return sha256(path.read_bytes()).hexdigest()


def dependency_versions():
    result = {}
    for name in ("numpy", "scipy"):
        try:
            result[name] = metadata.version(name)
        except metadata.PackageNotFoundError:
            result[name] = None
    return result


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--with-solver", action="store_true",
                        help="also require the optional SciPy MILP checks")
    parser.add_argument("--output", type=Path, default=ROOT / "reproduced_results")
    parser.add_argument("--timeout", type=int, default=900,
                        help="maximum seconds per suite (default: 900)")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.pop("PYTHONOPTIMIZE", None)
    env.pop("PYTHONPATH", None)
    env.update(PYTHONHASHSEED="0", PYTHONIOENCODING="utf-8",
               PYTHONNOUSERSITE="1", PYTHONDONTWRITEBYTECODE="1")
    tracked = sorted((ROOT / "code").glob("*.py"))
    tracked += [ROOT / "paper" / "majority_6040_note.tex",
                ROOT / "audit" / "independent_checks.py",
                ROOT / "run_all_checks.py"]
    summary = {
        "status": "RUNNING",
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "platform": platform.platform(),
        "optional_dependencies": dependency_versions(),
        "solver_requested": args.with_solver,
        "source_sha256": {str(p.relative_to(ROOT)): file_hash(p) for p in tracked},
        "scope": "Finite checks and regression tests; not a formal proof or an external review.",
        "suites": [],
    }
    def save_summary():
        (output / "run_summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    save_summary()
    with tempfile.TemporaryDirectory(prefix="majority6040-checks-") as temporary:
        work = Path(temporary)
        code = work / "code"
        shutil.copytree(ROOT / "code", code,
                        ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
        # The independent audit records the exact manuscript hash too.
        shutil.copy2(ROOT / "paper" / "majority_6040_note.tex", code)
        audit = work / "audit"
        audit.mkdir()
        shutil.copy2(ROOT / "audit" / "independent_checks.py", audit)
        jobs = []
        for name, script, result_file in SUITES:
            command = [sys.executable, "-B", str(code / script)]
            if name == "compatibility" and args.with_solver:
                command.append("--with-solver")
            jobs.append((name, command, code / result_file, result_file))
        jobs.append(("independent_audit",
                     [sys.executable, "-B", str(audit / "independent_checks.py"), str(code)],
                     audit / "results.json", "independent_audit_results.json"))
        for name, command, result_path, output_name in jobs:
            # A failed repeat run must never leave a previous PASS result.
            destination = output / output_name
            if destination.is_file():
                destination.unlink()
            print("Running " + name + "...", flush=True)
            start = time.monotonic()
            status, returncode, detail = "FAIL", None, None
            try:
                completed = subprocess.run(
                    command, cwd=work, env=env, text=True, encoding="utf-8",
                    errors="replace", stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    timeout=args.timeout, check=False)
                returncode = completed.returncode
                stdout, stderr = completed.stdout, completed.stderr
                if result_path.is_file():
                    shutil.copy2(result_path, output / output_name)
                    result = json.loads(result_path.read_text(encoding="utf-8"))
                    detail = result.get("status")
                    if returncode == 0 and detail in PASS_STATUSES:
                        status = "PASS"
                    elif detail == "INCONCLUSIVE":
                        status = "INCONCLUSIVE"
            except subprocess.TimeoutExpired as error:
                status, detail = "INCONCLUSIVE", "suite timeout"
                stdout = error.stdout or ""
                stderr = error.stderr or ""
                if isinstance(stdout, bytes):
                    stdout = stdout.decode("utf-8", errors="replace")
                if isinstance(stderr, bytes):
                    stderr = stderr.decode("utf-8", errors="replace")
            except (OSError, ValueError) as error:
                stdout, stderr, detail = "", repr(error), "execution or result error"
            (output / (name + ".stdout.txt")).write_text(stdout, encoding="utf-8")
            (output / (name + ".stderr.txt")).write_text(stderr, encoding="utf-8")
            row = {"name": name, "status": status, "returncode": returncode,
                   "reported_status": detail,
                   "seconds": round(time.monotonic() - start, 3)}
            if (output / output_name).is_file() and result_path.is_file():
                row.update(result_file=output_name,
                           result_sha256=file_hash(output / output_name))
            summary["suites"].append(row)
            save_summary()
            print(name + ": " + status, flush=True)
    summary["status"] = (
        "PASS" if all(row["status"] == "PASS" for row in summary["suites"])
        else "FAIL_OR_INCONCLUSIVE")
    summary["finished_at_utc"] = datetime.now(timezone.utc).isoformat()
    save_summary()
    print("Overall: " + summary["status"], flush=True)
    print("Results: " + str(output), flush=True)
    return 0 if summary["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
