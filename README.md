# TwinPhase Resonant Fusor

A conceptual magnetic-electrostatic aneutronic fusion architecture in the Farnsworth IEC lineage, by Marcus Roberts.

The paper sets out nested RF phase buckets for counter-streaming p-⁷Li ions, grounded-HTS confinement and electrostatic direct energy conversion. It claims no net power and states no gain figure. Open questions are tagged [OMR-xx] in the text and listed in Appendix A.

## Read the paper

- paper/TwinPhase_Resonant_Fusor_Version_X_clean_2026-11-02.pdf (40 pages)
- paper/TwinPhase_Resonant_Fusor_Version_X_clean_2026-11-02.md (same text, source)

## Contents

- `paper/`: Version X as PDF and Markdown, with the two figures it embeds.
- `figures/`: SVG sources of Figure 6.1 (schematic v17) and Figure 10.1 (converter c1).
- `pack/`: supplementary material to Version X, kept out of the paper to keep it lean. It holds the inductive harvester option for a bunched mode, the earlier short-packet space-charge text, the earlier reaction-rate model for bunched packets, and a holding note on flat ribbon streams, with the harvester figure (Figure S1).
- `calcs/`: `twinphase_kinematics.py`, the reproducible kinematics script cited in Appendix M of the paper.

## Working in the open

The paper will keep changing here after release, and the version history is the git history. Supporting scripts and notes will be added over time. Issues and pull requests are welcome, especially simulation work (particle-in-cell, beam-beam, space charge) and converter design.

## Licences

Copyright 2026 Marcus Roberts.

- Paper, figures and notes: Creative Commons Attribution 4.0 International (CC BY 4.0), full text in `LICENSE`. Any use or quotation must credit the author.
- Code (`calcs/*.py` and any later scripts): GNU General Public License v3.0 or later (GPL-3.0-or-later), full text in `LICENSE-GPL-3.0.txt`.
