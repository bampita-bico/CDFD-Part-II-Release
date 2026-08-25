# CDFD Multi-Origin Life Convergence Simulator

**Status:** computational experiment (toy model), not a historical claim about Earth  
**Script:** `scripts/multi_origin_convergence_sim.py`  
**Outputs:** `outputs/multi_origin_convergence/`  
**Runtime bridge:** optional import from parent `CDFD-Runtime` (Life Number helpers); core dynamics use Part II `partii_runtime`

---

## 1. What question does this answer?

**Not this:**

> Did life originate more than once on Earth?

**This instead:**

> If several independent (or semi-independent) proto-biological populations start in the **same** environment, can they naturally end up as a **single** surviving lineage through competition, information exchange, cooperation, fusion, and extinction?

The simulator must be able to produce:

- outcomes that **support** mono-lineage convergence, and
- outcomes that **contradict** it (coexistence or total extinction).

Convergence is an **empirical result of the dynamics**, not a hard-coded target.

---

## 2. How to read this in plain language

This experiment is about the **deep origins window** — before modern animals, plants, and familiar microbes — not about rewriting later evolutionary relationships.

### The right framing

| Layer | Best reading |
|---|---|
| **Deep past (origins)** | Life *might* have started at more than one “focal point” (separate proto-populations). That is a **live possibility**, not proven by this simulator. |
| **Current tree of life** | Present-day biology strongly looks like one deep common trunk / shared ancestry pattern (often discussed around LUCA — a last universal common ancestor pattern). |
| **This experiment** | Asks whether many early lines **can converge** toward one surviving lineage — and shows **yes and no**, depending on conditions. |

So:

- Multiple early starts are **possible** in a toy model.
- They are **not forced** to stay many, or to become one.
- They *can* end as one surviving line (competition, fusion, extinction of the others).
- Or they can keep coexisting.
- Or they can look genetically similar via **HGT** while still being separate lines — so similarity alone does not prove “one origin.”

### What this does *not* mean

- It does **not** claim Earth historically had multiple origins.
- It does **not** say humans and other apes (or any later groups) might not share common ancestry.
- It does **not** say the DNA similarity of later life is “just HGT between separate origins.”

For later biology, shared ancestry through **vertical inheritance** remains the main explanation for the nested family-tree pattern. HGT is real (especially in microbes) and can move some traits sideways, but that is a different claim from “multiple unrelated animal origins.”

### Short takeaway

Early on, different focal points *might* have formed life-like systems. Current biology suggests today’s living world is dominated by **one** deep surviving trunk. This simulator only maps whether “many early lines → one survivor” is **mechanically plausible** — and shows that coexistence and total extinction are plausible too.

---

## 3. What is HGT?

**HGT = Horizontal Gene Transfer** (here: horizontal *information* transfer).

In modern biology, genes usually move **vertically**: parent → offspring.

**Horizontal** transfer means genetic (or chemical-information) material moves **sideways** between contemporaries that are not parent and child — for example between two coexisting microbes.

### In this simulator

| Term | Meaning |
|---|---|
| **HGT** | One lineage copies a segment of another lineage’s genome / traits. **Both lineages still exist afterward.** |
| **Fusion** | A separate, rarer event: two lineages truly merge into one new lineage. |
| **Vertical inheritance** | A lineage keeps / mutates its own genome over time (mutation + growth). |

**Critical design rule:** HGT does **not** automatically merge lineages. That was the main correction relative to the earlier blueprint.

Everyday analogy:

- **HGT** = two companies exchange a recipe; both companies still exist.
- **Fusion** = the two companies merge into one company.

---

## 4. What is a lineage here?

Each lineage is a toy proto-population with:

- **biomass** (how large / persistent it is)
- **genome** (length-16 pattern of traits)
- **CDFL state:** `Phi` (drive), `C` (constraint), `S` (routing), `M_s` (memory)
- **origin IDs** (which initial origins contributed to it; fusion can combine these)

Fitness depends on:

- adaptive operating ratio `Psi_s ≈ (Phi / C) * S * M_s`
- match to an environmental target pattern
- optional parasite / cooperation traits read from genome segments

A lineage goes **extinct** if biomass falls below a floor.

---

## 5. Mechanisms (each has its own rate)

These are **independent**. Turning one up does not silently force another.

| Mechanism | What it does |
|---|---|
| **Competition** | Shared-resource interference; stronger competitors can exclude weaker ones |
| **Mutation** | Small random genome / CDFL changes |
| **HGT** | Copy genome segments between lineages; **no merger** |
| **Cooperation** | Compatible, cooperative lineages give each other small growth / routing boosts |
| **Parasitism** | High-parasite lineages drain cooperative hosts (Mujjabi parasitic-threshold idea) |
| **Fusion** | Optional true merger into one lineage (compatibility threshold required) |
| **Extinction noise** | Extra chance that critically small populations vanish |
| **Environmental selection** | Mismatch to environment costs biomass (harsher worlds punish harder) |

---

## 6. How we score outcomes

| Outcome label | Meaning | Supports “converge to one lineage”? |
|---|---|---|
| `competitive_mono_lineage` | Exactly one lineage left; no multi-origin fusion survivor required | **Supports** |
| `fusion_mediated_mono_lineage` | One lineage left, produced with fusion + combined origin IDs | **Supports** |
| `multi_lineage_coexistence` | More than one lineage still alive | **Contradicts** |
| `information_homogenized_coexistence` | Several lineages alive, but genomes became very similar via HGT | **Contradicts** (no lineage collapse) |
| `total_extinction` | No survivors | **Contradicts** |

“Supports” here only means: *under these rates, independent starts can collapse to one surviving lineage.*  
It does **not** mean Earth historically had multiple origins.

---

## 7. Scenarios explained

All primary scenarios start with **5 origins** unless noted. Each scenario was also repeated **16 times** with different seeds to measure how stable the outcome is.

### 7.1 `competition_dominant`

**Setup:** strong interference competition, weak HGT / cooperation / fusion, tighter resources.

**Intuition:** several groups fight over a limited pie; usually one wins.

**Typical result (16 reps):** ~75% mono-lineage, ~25% still multi-lineage.

**Reading:** competition *can* drive convergence, but not always.

---

### 7.2 `niche_abundance_coexistence`

**Setup:** high resource inflow, large capacity, weak competition, strong cooperation, fusion off.

**Intuition:** there is enough room for several groups; helping each other does not force merger.

**Typical result:** ~100% multi-lineage coexistence (~4.9 lineages on average).

**Reading:** strongly **contradicts** “they must become one.”

---

### 7.3 `hgt_without_fusion`  ← clearest teaching scenario

**Setup:** frequent HGT, **fusion rate = 0**, mild competition, enough resources to survive.

**Intuition:** groups keep swapping information, so they start to *look alike*, but they remain separate populations.

**Primary-seed result:**

- HGT events: **153**
- Fusion events: **0**
- Final lineages: **5**
- Mean genome similarity: **~0.97**

**Mechanism check:** `passed = True`  
(HGT happened, fusion did not, multiple lineages remained.)

**Reading:** informational / chemical convergence ≠ genealogical merger.

---

### 7.4 `fusion_enabled`

**Setup:** moderate competition plus a nonzero fusion rate; genomes start less divergent so fusion compatibility is reachable.

**Intuition:** sometimes two lineages truly combine into one.

**Typical result:** ~100% `fusion_mediated_mono_lineage`.

**Reading:** **supports** mono-lineage endpoints — but only because fusion is explicitly allowed, not because HGT secretly merged anyone.

---

### 7.5 `parasitic_drain`

**Setup:** elevated parasitism on cooperative hosts (boundary / parasitic-threshold stress).

**Intuition:** exploiters can destabilize neat “everyone merges happily” stories; hosts and parasites may persist together or reshape who survives.

**Typical result:** mostly multi-lineage coexistence; mono-lineage is rare (~6%).

**Reading:** parasitism usually **prevents** tidy single-lineage convergence in this toy regime.

---

### 7.6 `harsh_extinction_cascade`

**Setup:** very harsh environment, low inflow, high selection mismatch cost, high extinction noise.

**Intuition:** the world can kill everyone, or leave a single tough survivor — neither is a guaranteed multi-origin success story.

**Typical result:** mix of mono-lineage survival and total extinction (primary seed hit total extinction).

**Reading:** harsh conditions **contradict** any claim that convergence to one living lineage is automatic.

---

### 7.7 `balanced_baseline`

**Setup:** mid-range rates, small fusion probability.

**Intuition:** a “default” mixed world; outcome should be contingent.

**Typical result in current parameterization:** fusion-mediated mono-lineage is common.

**Reading:** even a “balanced” mix can converge if fusion is present; compare against `hgt_without_fusion` and `niche_abundance_coexistence` to see non-convergence.

---

## 8. Summary of run results

From the last local verification run:

| Scenario | Support mono-lineage | Contradict | Modal outcome |
|---|---:|---:|---|
| competition_dominant | 0.75 | 0.25 | competitive_mono_lineage |
| niche_abundance_coexistence | 0.00 | 1.00 | multi_lineage_coexistence |
| hgt_without_fusion | 0.00 | 1.00 | information_homogenized_coexistence |
| fusion_enabled | 1.00 | 0.00 | fusion_mediated_mono_lineage |
| parasitic_drain | 0.06 | 0.94 | multi_lineage_coexistence |
| harsh_extinction_cascade | 0.69 | 0.31 | competitive_mono_lineage / total_extinction mix |
| balanced_baseline | 1.00 | 0.00 | fusion_mediated_mono_lineage |

**Both outcome classes observed:** yes.

**Runtime Life Number bridge available:** yes.

---

## 9. Bottom line

1. **HGT** = sideways information copying; lineages stay separate.
2. **Fusion** = true merger; separately rate-controlled.
3. Multiple starting lineages **can** collapse to one (competition / fusion).
4. Multiple starting lineages **need not** collapse (abundance / HGT-without-fusion).
5. Everyone can also die (harsh world).
6. Early **multiple focal points** are a live possibility; **current biology** still looks like one deep surviving trunk.
7. This experiment maps **mechanical possibility**, not Earth’s historical origin count, and does not rewrite later common-ancestry relationships.

---

## 10. How to reproduce

From `CDFD-Part-II-Release`:

```bash
/home/bampita/Projects/CDFD/.venv/bin/python \
  Part_II_Origins_of_Life_and_Tri_Regime_Bioenergetics/scripts/multi_origin_convergence_sim.py
```

### Output files

| File | Contents |
|---|---|
| `outputs/multi_origin_convergence/summary.json` | Question, design rules, mechanism check, aggregates |
| `scenario_summary.csv` | Primary-seed outcome per scenario |
| `replicate_sweep.csv` | All replicate rows |
| `replicate_aggregate.csv` | Support/contradict fractions |
| `lineage_timeseries.csv` | Step-wise lineage counts / similarity |
| `multi_origin_convergence_scan.png` | Figure panel |

---

## 11. Relation to Part II language

This experiment sits next to:

- **Mujjabi Origin Constraint Law** (`Psi_s = (Phi/C) S M_s`) — persistence bookkeeping per lineage
- **Mujjabi Parasitic Threshold** — parasitism scenario
- **Mujjabi Chemical Memory / closure ideas** — memory `M_s` and retained pattern similarity after HGT

It does **not** replace Papers 1–12; it is an additional computational probe about multi-lineage fate under separated interaction mechanisms.
