# PDF production check

Date: 21 October 2026.

- Source: paper/majority_6040_note.tex.
- Build: two successful pdflatex passes through build_paper.py.
- Engine: pdfTeX 1.40.25, TeX Live 2023/Debian.
- Final article length: 17 A4 pages.
- Build log: no unresolved references or citations; no overfull or underfull
  box warnings.
- All 17 pages were rasterized with pdftoppm at 105 dpi and visually inspected.
  Titles, mathematical symbols, equations, cross-references, page headers,
  page numbers, and bibliography links are legible. No clipped formulas,
  overlapping text, missing symbols, or unintended blank pages were observed.
- pdffonts reports every used font embedded, with Unicode mappings.
- PDF metadata identifies the manuscript title and Grisha Pochuev as author.

This is a document-production check. Mathematical conclusions are addressed
by the proof reviews, and reproducible finite checks are recorded separately.
The PDF is not asserted to be PDF/A or to satisfy an unspecified venue's
submission template.
