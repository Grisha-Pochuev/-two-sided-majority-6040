#!/usr/bin/env python3
"""Build the manuscript in a temporary directory using two pdflatex passes."""

from argparse import ArgumentParser
from pathlib import Path
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path,
                        default=ROOT / "paper" / "majority_6040_note.pdf")
    args = parser.parse_args()
    executable = shutil.which("pdflatex")
    if executable is None:
        parser.error("pdflatex is required; install a TeX distribution with the listed packages")
    source = ROOT / "paper" / "majority_6040_note.tex"
    output = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="majority6040-tex-") as temporary:
        work = Path(temporary)
        shutil.copy2(source, work)
        for number in (1, 2):
            result = subprocess.run(
                [executable, "-interaction=nonstopmode", "-halt-on-error",
                 "-file-line-error", source.name],
                cwd=work, text=True, encoding="utf-8", errors="replace",
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
            if result.returncode:
                raise SystemExit("pdflatex pass " + str(number) + " failed:\n" + result.stdout)
        log = (work / "majority_6040_note.log").read_text(
            encoding="utf-8", errors="replace")
        unresolved = ("There were undefined references",
                      "There were undefined citations",
                      "Label(s) may have changed")
        if any(message in log for message in unresolved):
            raise SystemExit("Unresolved references after two passes:\n" + log)
        shutil.copy2(work / "majority_6040_note.pdf", output)
        (output.parent / "build.log").write_text(log, encoding="utf-8")
    print("Built " + str(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
