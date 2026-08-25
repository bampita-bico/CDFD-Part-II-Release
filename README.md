# CDFD Part II: Origins of Life and Tri-Regime Bioenergetics

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20264779.svg)](https://doi.org/10.5281/zenodo.20264779)

This release contains the public Part II origins-of-life archive for the
Constraint-Driven Flux Dynamics project.

## Author

Steve Bico Mujjabi, MD<br>
Independent Researcher<br>
Founder, VuraLabs<br>
Kampala, Uganda<br>
ORCID: https://orcid.org/0009-0001-0556-5516

Institutional home: **VuraLabs**

## Release Naming

CDFD Part II: Origins of Life and Tri-Regime Bioenergetics

## Keywords

Constraint-Driven Flux Dynamics; CDFD; origins of life; abiogenesis;
prebiotic chemistry; geochemistry; redox chemistry; alkaline hydrothermal
vents; hot-spring hypothesis; iron-sulfur chemistry; magnetite; mixed-valence
minerals; interfacial water; proton gradients; proto-chemiosmosis; wet-dry
cycling; thermal gradients; phosphate activation; autocatalysis; chemical
memory; chemical alphabets; homochirality; coacervates; liquid-liquid phase
separation; protocells; vesicles; thioesters; RNA aminoacylation; peptide-RNA
chemistry; RNA world; metabolism-first; error threshold; parasitic threshold;
photochemistry; photoredox chemistry; overload stabilization; tri-regime
bioenergetics; Life Number; Mujjabi Life Number; CDFL; CDFD Runtime;
reproducible research; open science; preprint.

## GitHub Topics

`cdfd`, `cdfd-runtime`, `cdfl`, `constraint-driven-flux-dynamics`,
`origins-of-life`, `abiogenesis`, `prebiotic-chemistry`, `bioenergetics`,
`geochemistry`, `redox-chemistry`, `hydrothermal-vents`, `iron-sulfur`,
`protocells`, `autocatalysis`, `coacervates`, `homochirality`, `rna-world`,
`chemiosmosis`, `photochemistry`, `reproducible-research`

## Contents

- `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/` - Part II
  manuscripts, PDFs, supplementary scripts, generated outputs, bibliography,
  named hypotheses/tests, interactive panels, and reproducibility instructions.
- `CITATION.cff` - GitHub citation metadata.
- `.zenodo.json` - Zenodo deposit metadata.
- `requirements.txt` - Python dependencies for the public supplementary
  scripts.
- `environment.yml` - Conda environment for the public science stack.
- `LICENSE` - CC BY 4.0 release license.
- `LICENSE_BOUNDARY.md` - explains the boundary between this scholarly archive
  and the separately licensed public CDFD Runtime.

## Final Part II Architecture

The final edit turns Part II into a twelve-paper dependency chain rather than a
compressed origin story. The series moves from thermodynamic vocabulary to Fe-S
redox, distributed mineral transport, proton/ion coupling, environmental
cycling, autocatalytic closure, chemical alphabets, adaptive boundaries,
replication, parasitic failure, photochemical expansion, and the master
tri-regime synthesis.

This release explicitly cites Part I as the source of the public CDFD
flow-constraint-memory grammar, here named CDFL:
https://doi.org/10.5281/zenodo.20250821

## Review Status

These manuscripts are archived as research/preprint materials and are not peer
reviewed. The supplementary scripts reproduce toy diagnostics, figures, tables,
and consistency checks. They do not establish empirical validation of any
historical origin-of-life pathway.

## Suggested Reading Order

1. `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/README.md`
2. `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/CLAIM_STATUS.md`
3. `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/REPRODUCIBILITY.md`
4. `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/outputs/interactive_index.html`
5. `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/PDFs/`

Honesty audit for Φ/C / Life Number novelty (Parts II & III):  
The detailed cross-release audit was moved to the separate local archive on
2026-08-24; this release's `CLAIM_STATUS.md` is the binding public boundary.

## Reproducibility

See `Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/REPRODUCIBILITY.md`
for rebuild and verification commands. The active release is script-first. It
does not include placeholder notebooks. Output folders are included only where a
paper cites a generated figure, table, or diagnostic. The optional
`make_interactive_panels.py` script builds local HTML viewers over those
generated outputs.

The May 2026 follow-up adds a guarded Paper 7 aromatic source-mix diagnostic
(`outputs/paper_07/aromatic_source_mix.csv`) and keeps Paper 11 eumelanin
language as a mature photochemical endpoint example, not an origin requirement.
The best retained source-mix row is `mixed_source_surface_trap` with functional
score `0.610`; the result is a provenance guardrail, not historical proof.

## Public CDFD Runtime

The CDFD Runtime is the reusable implementation target for CDFL, the
flow-constraint-memory language used across the CDFD series. This Part II
release remains a scholarly archive: its paper-local Python scripts and outputs
reproduce the diagnostics cited by the origins-of-life manuscripts.

Cite and license the two layers separately until a combined CDFD Runtime release
DOI exists.

## Reference Verification

All DOI-backed bibliography entries were checked online against Crossref or
DataCite on 2026-05-18. The 2024-2026 release anchors used for the final sweep
were rechecked against publisher or PubMed records on 2026-05-20. The
Murchison aromatic/organic and eumelanin endpoint anchors added after release
were rechecked against publisher, PubMed, or DOI records on 2026-05-30. The
bibliography includes real DOI-backed references, Part II Zenodo DOI, plus the
Part I Zenodo DOI.

## License

This release is licensed under the Creative Commons Attribution 4.0
International License (CC BY 4.0). See `LICENSE` and `LICENSE_BOUNDARY.md`.

## Citation

Mujjabi, S. B. (2026). CDFD Part II: Origins of Life and Tri-Regime Bioenergetics - Constraint-Driven Flux Dynamics. Zenodo.
https://doi.org/10.5281/zenodo.20264779

Steve Bico Mujjabi, MD. CDFD Part I: Fundamental Physics. Zenodo.
https://doi.org/10.5281/zenodo.20250821
