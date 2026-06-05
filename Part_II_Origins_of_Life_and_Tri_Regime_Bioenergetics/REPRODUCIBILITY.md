# Reproducibility

Last local verification: 2026-05-30.

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
Paper 7 now includes `aromatic_source_mix.csv` and a three-panel figure that
separates aromatic pattern persistence, model-space chirality, and feedstock
provenance. Paper 11 labels chlorophyll and eumelanin as mature endpoints of
wider functional classes, not origin requirements.

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
latexmk -pdf -interaction=nonstopmode -halt-on-error -outdir=/tmp/cdfd_partii_build papers/*.tex
```

Copy the final active PDFs from `/tmp/cdfd_partii_build/` to `PDFs/`.

## What This Verifies

The scripts regenerate the stated toy outputs and the LaTeX build verifies that
the active manuscript sequence compiles. This does not validate the historical
origin-of-life hypotheses.

## Current Verification Result

The active script outputs, interactive panels, and twelve-paper PDF set were
regenerated locally on 2026-05-30 after the Paper 7 source-mix and Paper 11
eumelanin endpoint updates. The final LaTeX log scan found no undefined
citations, unresolved references, rerun requests, or LaTeX/BibTeX errors in the
active PDF build logs.
