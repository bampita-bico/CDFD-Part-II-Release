# Part II: Origins of Life and Tri-Regime Bioenergetics

Author: Steve Bico Mujjabi, MD  
ORCID: https://orcid.org/0009-0001-0556-5516

This directory contains the active Part II origins-of-life sequence for the
Constraint-Driven Flux Dynamics project.

## Active Manuscripts

1. Thermodynamic Mandate and Dissipative Structuring
2. Iron-Sulfur Redox and Mineral Constraint Scaffolds
3. Magnetite Networks and Distributed Electron Transport
4. Interfacial Water, Proton/Ion Coupling, and Proto-Chemiosmosis
5. Oscillating Constraints and the Polymerization Ratchet
6. Autocatalytic Closure and Chemical Memory
7. Aromatic Stabilization, Chemical Alphabets, and Homochirality
8. Boundaries, Mineral-Organic Interfaces, and Coacervate Phase Separation
9. Protocell Integration, Replication, and Error Thresholds
10. The Parasitic Threshold and Boundary Logic
11. Photochemical Energy Capture and Overload Stabilization
12. Master Synthesis: Tri-Regime Bioenergetics and Falsification

The active sequence is twelve papers. Each major gate is kept visible so the
reader can evaluate the dependency chain without relying on separate draft
history.

## Contents

- `papers/` - active LaTeX sources.
- `PDFs/` - compiled PDFs for the active twelve-paper sequence.
- `scripts/` - deterministic paper-local supplementary Python scripts.
- `outputs/` - generated figures, CSV files, and JSON summaries only where a
  paper cites a diagnostic output.
- `make_interactive_panels.py` - offline HTML viewer generator for the existing
  output folders.
- `ool_references.bib` - shared bibliography, including the Part I DOI.
- `CLAIM_STATUS.md` - binding claim boundary for this release.
- `ARCHIVE_NOTICE_2026-08-24.md` - retained release scope and the separate
  archive boundary for working material.
- `methods/` - shared auditable toy-model declaration protocol.
- `REPRODUCIBILITY.md` - commands used to regenerate scripts and PDFs.

## Relationship To Part I

Part I supplies CDFL, the public CDFD
flow-constraint-responsiveness-memory language, and should be cited when Part
II notation is used:

Steve Bico Mujjabi, MD. CDFD Part I: Fundamental Physics. Zenodo.
https://doi.org/10.5281/zenodo.20250821

Part II applies that grammar to origin-of-life dependency order. The reader
does not have to accept every physical interpretation in Part I to evaluate
Part II as a coarse-grained origins framework.

## Series Flow

| Paper | Series role |
|---|---|
| 1 | Defines the thermodynamic vocabulary: flux, constraint, responsiveness, and memory. |
| 2 | Grounds the chain in Fe-S redox surfaces and mineral constraint scaffolds. |
| 3 | Extends local redox chemistry into mixed-valence distributed electron transport. |
| 4 | Adds the proton/ion and interfacial-water side of proto-chemiosmotic coupling. |
| 5 | Turns environmental cycling into a polymerization and retention ratchet. |
| 6 | Defines autocatalytic closure and chemical memory without overclaiming ignition. |
| 7 | Separates durable chemical alphabets, source-mix provenance, and homochirality from genetic code. |
| 8 | Moves from geological confinement to adaptive compartments and soft boundaries. |
| 9 | Tests replication, error thresholds, and protocell integration together. |
| 10 | Defines the parasitic threshold after copying and boundary inheritance exist. |
| 11 | Adds photochemical capture and overload stabilization as later functional expansion; chlorophyll and eumelanin remain mature endpoint examples. |
| 12 | Synthesizes the tri-regime Life Number and falsification program. |

## Scientific Python Stack

The Part II scripts use the public scientific stack where it materially
supports a paper-local check: NumPy, SciPy, Pandas, Matplotlib, SymPy,
Statsmodels, and scikit-learn. Not every paper needs every library. The rule is
to use the stack for independent numerical integration, symbolic thresholds,
tables, plots, or regime diagnostics rather than decorative dependencies.

## Script And Output Policy

Part II is script-first. Placeholder `.ipynb` notebooks are not included in the
active release. Paper 1 now includes a lightweight dependency-gate surface so
the opening CDFL notation is reproducible in the same script-first style as the
rest of the release. Papers 2-12 include outputs because their manuscripts cite
generated diagnostics. Paper 7 writes `aromatic_source_mix.csv` to separate
terrestrial and exogenous feedstock from retention and coupling. Paper 11 writes
photochemical capture and overload-buffering tables while labeling eumelanin as
a mature endpoint exemplar. The interactive panels are generated from those
outputs and do not introduce a separate computational source of truth.

## Review Status

These manuscripts are not peer reviewed. The supplementary scripts reproduce
internal toy diagnostics and figures; they do not validate the historical origin
of life. Claim strength is marked directly inside the manuscripts with derived,
inferred, hypothesis, and open-status labels.
