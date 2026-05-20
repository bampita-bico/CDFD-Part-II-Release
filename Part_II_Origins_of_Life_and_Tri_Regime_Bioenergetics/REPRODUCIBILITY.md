# Reproducibility

Last local verification: 2026-05-20.

## Environment Used

- Python: `/home/bampita/Projects/CDFD/.venv/bin/python`
- LaTeX: `latexmk`, `pdflatex`, and `bibtex`
- Python dependencies used by scripts: NumPy, SciPy, Pandas, Matplotlib,
  SymPy, Statsmodels, and scikit-learn where needed by paper-local diagnostics.

## Rebuild Supplementary Outputs

From `CDFD-Part-II-Release`:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_01.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_02.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_03.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_04.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_05.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_06.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_07.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_08.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_09.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_10.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_11.py
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/supplementary_ool_12.py
```

Paper 1 now has a lightweight dependency-gate diagnostic. It remains a
necessary-condition visualization, not a historical abiogenesis simulation.

## Build Local Interactive Panels

From `CDFD-Part-II-Release`:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/make_interactive_panels.py
```

This creates `outputs/interactive_index.html` and one `interactive_panel.html`
inside each output-bearing paper folder. These HTML files only view existing
PNG, CSV, and JSON outputs; the supplementary scripts remain the source of
generated data.

## Rebuild PDFs

From `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics`:

```bash
mkdir -p /tmp/cdfd_partii_build PDFs
pdflatex -interaction=nonstopmode -halt-on-error -output-directory /tmp/cdfd_partii_build papers/01_The_Thermodynamic_Mandate_and_Dissipative_Structuring.tex
```

For papers with citations, run `bibtex /tmp/cdfd_partii_build/<basename>`
between the first and second `pdflatex` passes, then run `pdflatex` twice more.
Copy the final active PDFs from `/tmp/cdfd_partii_build/` to `PDFs/`.

## What This Verifies

The scripts regenerate the stated toy outputs and the LaTeX build verifies that
the active manuscript sequence compiles. This does not validate the historical
origin-of-life hypotheses.

## Current Verification Result

The active script outputs, interactive panels, and twelve-paper PDF set were
regenerated locally on 2026-05-20 during the final release sweep. The final
LaTeX log scan found no undefined citations, unresolved references, rerun
requests, LaTeX/BibTeX errors, or overfull boxes in the active PDF build logs.
