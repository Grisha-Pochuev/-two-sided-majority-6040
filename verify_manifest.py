#!/usr/bin/env python3
"""Verify all package files against MANIFEST.sha256 (standard library only)."""

from hashlib import sha256
from pathlib import Path


def main():
    root = Path(__file__).resolve().parent
    failures = []
    checked = 0
    for line in (root / "MANIFEST.sha256").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        expected, name = line.split("  ", 1)
        relative = Path(name)
        if relative.is_absolute() or ".." in relative.parts:
            failures.append("unsafe manifest path: " + name)
            continue
        path = root / relative
        if not path.is_file():
            failures.append("missing: " + name)
        elif sha256(path.read_bytes()).hexdigest() != expected:
            failures.append("changed: " + name)
        checked += 1
    if failures:
        raise SystemExit("\n".join(failures))
    print("PASS: " + str(checked) + " file hashes match.")


if __name__ == "__main__":
    main()
