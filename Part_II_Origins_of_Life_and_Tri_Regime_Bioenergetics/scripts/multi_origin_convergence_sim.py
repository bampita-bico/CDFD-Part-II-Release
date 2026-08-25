"""
CDFD Multi-Origin Life Convergence Simulator

Scientific question (NOT a historical claim):
  Can multiple independent or semi-independent proto-biological populations,
  initialized in the same environment, naturally converge toward a single
  surviving lineage through competition, information exchange, cooperation,
  fusion, and extinction?

Critical design rule:
  Horizontal information transfer does NOT automatically merge lineages.
  Fusion is a separate, independently rate-controlled event.
  Convergence is an empirical outcome of the dynamics, not an encoded target.

Uses Part II CDFL helpers (Phi, C, S, M_s) via partii_runtime.
Optionally imports CDFD-Runtime life-number channel helpers when available.

Outputs: outputs/multi_origin_convergence/
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cdfd_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/cdfd_cache")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from partii_runtime import adaptive_ratio, finite_summary, life_number, output_dir, regime_from_value

# Optional Runtime bridge (parent CDFD-Runtime). Soft-fail if unavailable.
_RUNTIME_LIFE = None
try:
    _rt_root = Path(__file__).resolve().parents[3] / "CDFD-Runtime"
    if not _rt_root.exists():
        _rt_root = Path("/home/bampita/Projects/CDFD/CDFD-Runtime")
    if _rt_root.exists() and str(_rt_root) not in sys.path:
        sys.path.insert(0, str(_rt_root))
    from engine.origins_of_life import compute_life_number  # type: ignore

    _RUNTIME_LIFE = compute_life_number
except Exception:  # pragma: no cover - optional
    _RUNTIME_LIFE = None

EPS = 1e-12
GENOME_LEN = 16
EXTINCTION_FLOOR = 1e-3


@dataclass
class Rates:
    """Independently configurable mechanism rates / strengths."""

    competition: float = 0.35
    mutation: float = 0.02
    hgt: float = 0.05
    cooperation: float = 0.08
    parasitism: float = 0.04
    fusion: float = 0.0
    extinction_noise: float = 0.01
    environmental_selection: float = 0.25
    resource_inflow: float = 0.55
    resource_capacity: float = 4.0
    carrying_scale: float = 1.2


@dataclass
class Lineage:
    lineage_id: int
    origin_ids: frozenset[int]
    biomass: float
    genome: np.ndarray
    phi: float
    constraint: float
    S: float
    M_s: float
    born_step: int = 0
    parent_ids: tuple[int, ...] = ()

    def copy(self) -> "Lineage":
        return Lineage(
            lineage_id=self.lineage_id,
            origin_ids=self.origin_ids,
            biomass=float(self.biomass),
            genome=self.genome.copy(),
            phi=float(self.phi),
            constraint=float(self.constraint),
            S=float(self.S),
            M_s=float(self.M_s),
            born_step=self.born_step,
            parent_ids=self.parent_ids,
        )

    @property
    def psi(self) -> float:
        return float(adaptive_ratio(np.array([self.phi]), np.array([self.constraint]), self.S, self.M_s)[0])

    @property
    def coop_trait(self) -> float:
        return float(np.mean(self.genome[: GENOME_LEN // 4]))

    @property
    def parasite_trait(self) -> float:
        return float(np.mean(self.genome[GENOME_LEN // 4 : GENOME_LEN // 2]))

    def env_match(self, env_target: np.ndarray) -> float:
        return float(1.0 - np.mean(np.abs(self.genome - env_target)))


@dataclass
class EventCounts:
    mutations: int = 0
    hgt_events: int = 0
    coop_events: int = 0
    parasite_events: int = 0
    fusion_events: int = 0
    extinctions: int = 0
    competition_kills: int = 0


@dataclass
class Scenario:
    name: str
    description: str
    n_origins: int
    rates: Rates
    steps: int = 400
    seed: int = 0
    env_harshness: float = 0.35
    initial_biomass: float = 0.45
    genome_divergence: float = 0.55


def _fitness(lin: Lineage, env_target: np.ndarray, rates: Rates) -> float:
    match = lin.env_match(env_target)
    psi = max(lin.psi, EPS)
    # Parasites get a short-term growth bump paid elsewhere.
    parasite_boost = 1.0 + 0.35 * lin.parasite_trait
    return max(EPS, (0.35 + rates.environmental_selection * match) * psi * parasite_boost)


def _init_lineages(scenario: Scenario, rng: np.random.Generator) -> list[Lineage]:
    lineages: list[Lineage] = []
    base = rng.random(GENOME_LEN)
    for i in range(scenario.n_origins):
        noise = rng.normal(0.0, scenario.genome_divergence, GENOME_LEN)
        genome = np.clip(base * (1.0 - scenario.genome_divergence) + noise, 0.0, 1.0)
        # Distinct CDFL niches: different Phi/C/S/M_s seeds
        phi = float(np.clip(0.4 + 0.5 * rng.random() + 0.15 * i, 0.05, 3.0))
        constraint = float(np.clip(0.8 + 0.7 * rng.random(), 0.2, 4.0))
        S = float(np.clip(0.6 + 0.8 * rng.random(), 0.05, 3.0))
        M_s = float(np.clip(0.2 + 0.6 * rng.random(), 0.05, 3.0))
        lineages.append(
            Lineage(
                lineage_id=i,
                origin_ids=frozenset({i}),
                biomass=scenario.initial_biomass * (0.75 + 0.5 * rng.random()),
                genome=genome,
                phi=phi,
                constraint=constraint,
                S=S,
                M_s=M_s,
                born_step=0,
            )
        )
    return lineages


def _maybe_mutate(lin: Lineage, rates: Rates, rng: np.random.Generator, counts: EventCounts) -> None:
    if rng.random() > rates.mutation:
        return
    idx = int(rng.integers(0, GENOME_LEN))
    lin.genome[idx] = float(np.clip(lin.genome[idx] + rng.normal(0.0, 0.18), 0.0, 1.0))
    lin.phi = float(np.clip(lin.phi + rng.normal(0.0, 0.05), 0.05, 4.0))
    lin.constraint = float(np.clip(lin.constraint + rng.normal(0.0, 0.05), 0.1, 5.0))
    lin.S = float(np.clip(lin.S + rng.normal(0.0, 0.04), 0.05, 4.0))
    lin.M_s = float(np.clip(lin.M_s + rng.normal(0.0, 0.04), 0.05, 4.0))
    counts.mutations += 1


def _maybe_hgt(lineages: list[Lineage], rates: Rates, rng: np.random.Generator, counts: EventCounts) -> None:
    """Copy a genome segment from donor to recipient. Does NOT merge lineages."""
    if len(lineages) < 2 or rng.random() > rates.hgt:
        return
    donor, recipient = rng.choice(len(lineages), size=2, replace=False)
    start = int(rng.integers(0, GENOME_LEN - 3))
    width = int(rng.integers(2, 5))
    lineages[recipient].genome[start : start + width] = lineages[donor].genome[start : start + width].copy()
    # Mild memory bleed from information contact, still separate lineages
    lineages[recipient].M_s = float(
        np.clip(0.85 * lineages[recipient].M_s + 0.15 * lineages[donor].M_s, 0.05, 4.0)
    )
    counts.hgt_events += 1


def _apply_cooperation(lineages: list[Lineage], rates: Rates, rng: np.random.Generator, counts: EventCounts) -> None:
    if len(lineages) < 2 or rates.cooperation <= 0:
        return
    for i, a in enumerate(lineages):
        for b in lineages[i + 1 :]:
            compat = 1.0 - float(np.mean(np.abs(a.genome - b.genome)))
            strength = rates.cooperation * a.coop_trait * b.coop_trait * compat
            if strength <= 0 or rng.random() > min(0.85, strength):
                continue
            boost = 0.012 * strength
            a.biomass = float(np.clip(a.biomass + boost, 0.0, 8.0))
            b.biomass = float(np.clip(b.biomass + boost, 0.0, 8.0))
            a.S = float(np.clip(a.S + 0.008 * strength, 0.05, 4.0))
            b.S = float(np.clip(b.S + 0.008 * strength, 0.05, 4.0))
            counts.coop_events += 1


def _apply_parasitism(lineages: list[Lineage], rates: Rates, rng: np.random.Generator, counts: EventCounts) -> None:
    if len(lineages) < 2 or rates.parasitism <= 0:
        return
    for i, parasite in enumerate(lineages):
        if parasite.parasite_trait < 0.45:
            continue
        for j, host in enumerate(lineages):
            if i == j:
                continue
            if host.coop_trait < 0.25:
                continue
            if rng.random() > min(0.9, rates.parasitism * parasite.parasite_trait):
                continue
            drain = 0.05 * parasite.parasite_trait * host.biomass
            host.biomass = max(0.0, host.biomass - drain)
            parasite.biomass = float(np.clip(parasite.biomass + 0.45 * drain, 0.0, 8.0))
            # Boundary specificity gate: high host constraint punishes parasite memory
            if host.constraint > 1.5:
                parasite.M_s = float(np.clip(parasite.M_s * 0.97, 0.05, 4.0))
            counts.parasite_events += 1


def _maybe_fuse(
    lineages: list[Lineage],
    rates: Rates,
    rng: np.random.Generator,
    counts: EventCounts,
    next_id: int,
    step: int,
) -> tuple[list[Lineage], int]:
    """Optional lineage fusion. Independent of HGT. Never automatic on exchange."""
    if len(lineages) < 2 or rates.fusion <= 0 or rng.random() > rates.fusion:
        return lineages, next_id
    i, j = sorted(rng.choice(len(lineages), size=2, replace=False).tolist(), reverse=True)
    a, b = lineages[i], lineages[j]
    compat = 1.0 - float(np.mean(np.abs(a.genome - b.genome)))
    # Fusion requires nontrivial compatibility; otherwise abort (lineages stay separate)
    if compat < 0.45:
        return lineages, next_id
    w_a = a.biomass / max(a.biomass + b.biomass, EPS)
    genome = np.clip(w_a * a.genome + (1.0 - w_a) * b.genome + rng.normal(0.0, 0.02, GENOME_LEN), 0.0, 1.0)
    fused = Lineage(
        lineage_id=next_id,
        origin_ids=frozenset(a.origin_ids | b.origin_ids),
        biomass=a.biomass + b.biomass,
        genome=genome,
        phi=0.5 * (a.phi + b.phi),
        constraint=0.5 * (a.constraint + b.constraint),
        S=max(a.S, b.S),
        M_s=0.5 * (a.M_s + b.M_s) + 0.05,
        born_step=step,
        parent_ids=(a.lineage_id, b.lineage_id),
    )
    remaining = [lin for k, lin in enumerate(lineages) if k not in (i, j)]
    remaining.append(fused)
    counts.fusion_events += 1
    return remaining, next_id + 1


def _classify_outcome(
    initial_n: int,
    final_lineages: list[Lineage],
    counts: EventCounts,
    mean_pairwise_similarity: float,
) -> dict[str, Any]:
    n_final = len(final_lineages)
    multi_origin_survivor = any(len(lin.origin_ids) > 1 for lin in final_lineages)
    if n_final == 0:
        label = "total_extinction"
    elif n_final == 1 and initial_n > 1:
        if counts.fusion_events > 0 and multi_origin_survivor:
            label = "fusion_mediated_mono_lineage"
        else:
            label = "competitive_mono_lineage"
    elif n_final > 1 and mean_pairwise_similarity >= 0.82 and counts.hgt_events > 0:
        label = "information_homogenized_coexistence"
    elif n_final > 1:
        label = "multi_lineage_coexistence"
    else:
        label = "single_origin_persistence"

    # "Supports convergence hypothesis" only if independent starts collapse to one lineage
    supports_convergence = label in {"competitive_mono_lineage", "fusion_mediated_mono_lineage"}
    contradicts_convergence = label in {
        "multi_lineage_coexistence",
        "information_homogenized_coexistence",
        "total_extinction",
    }
    return {
        "outcome": label,
        "supports_convergence_hypothesis": supports_convergence,
        "contradicts_convergence_hypothesis": contradicts_convergence,
        "n_final": n_final,
        "multi_origin_survivor": multi_origin_survivor,
        "mean_pairwise_similarity": mean_pairwise_similarity,
    }


def _pairwise_similarity(lineages: list[Lineage]) -> float:
    if len(lineages) < 2:
        return 1.0
    sims: list[float] = []
    for i, a in enumerate(lineages):
        for b in lineages[i + 1 :]:
            sims.append(1.0 - float(np.mean(np.abs(a.genome - b.genome))))
    return float(np.mean(sims)) if sims else 1.0


def simulate(scenario: Scenario) -> dict[str, Any]:
    rng = np.random.default_rng(scenario.seed)
    rates = scenario.rates
    lineages = _init_lineages(scenario, rng)
    next_id = scenario.n_origins
    counts = EventCounts()
    env_target = rng.random(GENOME_LEN)
    resource = min(1.5, 0.55 * rates.resource_capacity)
    history: list[dict[str, Any]] = []
    dt = 0.25

    for step in range(scenario.steps):
        # Environmental oscillation (wet-dry / redox cycle proxy)
        env_drive = 0.90 + 0.20 * np.sin(2.0 * np.pi * step / 50.0)
        leak = 0.04 * scenario.env_harshness
        resource = float(
            np.clip(
                resource + dt * (rates.resource_inflow * (1.0 - resource / rates.resource_capacity) - leak),
                0.08,
                rates.resource_capacity,
            )
        )

        # Competitive Lotka–Volterra growth on shared resource.
        # Competition intensity scales interference; it does not force extinction alone.
        if lineages:
            fits = np.array([_fitness(lin, env_target, rates) for lin in lineages], dtype=float)
            total_bio = float(sum(lin.biomass for lin in lineages)) + EPS
            for lin, fit in zip(lineages, fits):
                # Intrinsic growth rises with fitness and available resource
                r = 0.22 * fit * (resource / max(rates.resource_capacity, EPS)) * env_drive
                # Interference competition (stronger under high rates.competition)
                interference = rates.competition * (total_bio / max(rates.carrying_scale, EPS))
                mismatch = 1.0 - lin.env_match(env_target)
                env_tax = rates.environmental_selection * scenario.env_harshness * mismatch
                dN = dt * lin.biomass * (r - 0.04 - 0.10 * interference - 0.08 * env_tax)
                lin.biomass = float(np.clip(lin.biomass + dN, 0.0, 8.0))
                resource = max(0.08, resource - 0.015 * max(dN, 0.0))
                # Slow CDFL adaptation toward productive operating point
                psi = lin.psi
                lin.M_s = float(np.clip(lin.M_s + dt * 0.02 * (lin.phi * lin.S - 0.04 * lin.M_s), 0.05, 4.0))
                lin.S = float(np.clip(lin.S + dt * 0.02 * (psi - lin.S), 0.05, 4.0))

        # Independent stochastic mechanisms (rates are per-step Bernoulli probabilities)
        for lin in lineages:
            _maybe_mutate(lin, rates, rng, counts)
        _maybe_hgt(lineages, rates, rng, counts)
        _apply_cooperation(lineages, rates, rng, counts)
        _apply_parasitism(lineages, rates, rng, counts)
        lineages, next_id = _maybe_fuse(lineages, rates, rng, counts, next_id, step)

        # Extinction floor + rare stochastic wipe of critically small populations
        alive: list[Lineage] = []
        for lin in lineages:
            critical = lin.biomass < 0.04
            stochastic_kill = critical and (rng.random() < rates.extinction_noise * (0.25 + scenario.env_harshness))
            if lin.biomass < EXTINCTION_FLOOR or stochastic_kill:
                counts.extinctions += 1
                continue
            alive.append(lin)
        lineages = alive

        history.append(
            {
                "step": step,
                "n_lineages": len(lineages),
                "total_biomass": float(sum(lin.biomass for lin in lineages)),
                "resource": resource,
                "mean_similarity": _pairwise_similarity(lineages),
                "fusion_events_cum": counts.fusion_events,
                "hgt_events_cum": counts.hgt_events,
            }
        )

    mean_sim = _pairwise_similarity(lineages)
    classification = _classify_outcome(scenario.n_origins, lineages, counts, mean_sim)

    # Life-number gauge for surviving mean state
    if lineages:
        mean_phi = float(np.mean([lin.phi for lin in lineages]))
        mean_c = float(np.mean([lin.constraint for lin in lineages]))
        mean_s = float(np.mean([lin.S for lin in lineages]))
        mean_ms = float(np.mean([lin.M_s for lin in lineages]))
        lam = life_number(mean_phi, 1.0 / max(mean_c, EPS), mean_s, 1.0, 1.0, 1.0, mean_s, mean_ms)
    else:
        mean_phi = mean_c = mean_s = mean_ms = lam = 0.0

    survivors = [
        {
            "lineage_id": lin.lineage_id,
            "origin_ids": sorted(lin.origin_ids),
            "biomass": lin.biomass,
            "psi": lin.psi,
            "parent_ids": list(lin.parent_ids),
        }
        for lin in lineages
    ]

    return {
        "scenario": scenario.name,
        "description": scenario.description,
        "n_origins": scenario.n_origins,
        "rates": asdict(rates),
        "event_counts": asdict(counts),
        "survivors": survivors,
        "life_number": float(lam),
        "life_regime": regime_from_value(float(lam)) if lineages else "extinct",
        "mean_phi": mean_phi,
        "mean_constraint": mean_c,
        "mean_S": mean_s,
        "mean_M_s": mean_ms,
        "runtime_life_available": _RUNTIME_LIFE is not None,
        "history": history,
        **classification,
    }


def default_scenarios() -> list[Scenario]:
    """Contrasting scenarios: some favor mono-lineage collapse, others coexistence or extinction."""
    return [
        Scenario(
            name="competition_dominant",
            description="Strong interference competition, weak HGT/coop/fusion → competitive exclusion expected.",
            n_origins=5,
            seed=11,
            env_harshness=0.35,
            genome_divergence=0.65,
            rates=Rates(
                competition=0.95,
                mutation=0.02,
                hgt=0.01,
                cooperation=0.01,
                parasitism=0.01,
                fusion=0.0,
                environmental_selection=0.45,
                resource_inflow=0.45,
                resource_capacity=2.5,
                carrying_scale=0.9,
            ),
        ),
        Scenario(
            name="niche_abundance_coexistence",
            description="High resource inflow, strong cooperation, weak competition → multi-lineage persistence.",
            n_origins=5,
            seed=22,
            env_harshness=0.08,
            genome_divergence=0.40,
            rates=Rates(
                competition=0.08,
                mutation=0.015,
                hgt=0.03,
                cooperation=0.35,
                parasitism=0.0,
                fusion=0.0,
                environmental_selection=0.05,
                resource_inflow=1.10,
                resource_capacity=8.0,
                carrying_scale=4.5,
            ),
        ),
        Scenario(
            name="hgt_without_fusion",
            description="Frequent HGT, fusion disabled → genomes may homogenize while lineages remain distinct.",
            n_origins=5,
            seed=33,
            env_harshness=0.12,
            genome_divergence=0.70,
            rates=Rates(
                competition=0.12,
                mutation=0.01,
                hgt=0.35,
                cooperation=0.18,
                parasitism=0.0,
                fusion=0.0,
                environmental_selection=0.08,
                resource_inflow=0.90,
                resource_capacity=6.0,
                carrying_scale=3.5,
            ),
        ),
        Scenario(
            name="fusion_enabled",
            description="Moderate competition plus nonzero fusion rate → possible fusion-mediated consolidation.",
            n_origins=5,
            seed=44,
            env_harshness=0.20,
            genome_divergence=0.30,
            rates=Rates(
                competition=0.35,
                mutation=0.02,
                hgt=0.10,
                cooperation=0.15,
                parasitism=0.01,
                fusion=0.08,
                environmental_selection=0.18,
                resource_inflow=0.70,
                resource_capacity=4.5,
                carrying_scale=2.0,
            ),
        ),
        Scenario(
            name="parasitic_drain",
            description="Elevated parasitism → host collapse or parasite-driven instability (Mujjabi parasitic threshold).",
            n_origins=5,
            seed=55,
            env_harshness=0.25,
            rates=Rates(
                competition=0.25,
                mutation=0.03,
                hgt=0.08,
                cooperation=0.20,
                parasitism=0.45,
                fusion=0.0,
                environmental_selection=0.15,
                resource_inflow=0.55,
                resource_capacity=3.8,
                carrying_scale=1.8,
            ),
        ),
        Scenario(
            name="harsh_extinction_cascade",
            description="Harsh environment + low inflow → possible total extinction (contradicts tidy convergence).",
            n_origins=5,
            seed=66,
            steps=500,
            env_harshness=1.0,
            initial_biomass=0.12,
            genome_divergence=0.85,
            rates=Rates(
                competition=0.85,
                mutation=0.06,
                hgt=0.01,
                cooperation=0.0,
                parasitism=0.10,
                fusion=0.0,
                extinction_noise=0.45,
                environmental_selection=1.0,
                resource_inflow=0.05,
                resource_capacity=0.9,
                carrying_scale=0.45,
            ),
        ),
        Scenario(
            name="balanced_baseline",
            description="Mid-range rates; outcome should be contingent, not hard-wired.",
            n_origins=5,
            seed=77,
            env_harshness=0.22,
            rates=Rates(
                competition=0.40,
                mutation=0.02,
                hgt=0.08,
                cooperation=0.12,
                parasitism=0.06,
                fusion=0.015,
                environmental_selection=0.22,
                resource_inflow=0.65,
                resource_capacity=4.5,
                carrying_scale=2.2,
            ),
        ),
    ]


def _replicate_sweep(base: Scenario, n_reps: int = 12) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for r in range(n_reps):
        sc = Scenario(
            name=base.name,
            description=base.description,
            n_origins=base.n_origins,
            rates=base.rates,
            steps=base.steps,
            seed=base.seed + 1000 * r + 17,
            env_harshness=base.env_harshness,
            initial_biomass=base.initial_biomass,
            genome_divergence=base.genome_divergence,
        )
        result = simulate(sc)
        rows.append(
            {
                "scenario": result["scenario"],
                "replicate": r,
                "seed": sc.seed,
                "outcome": result["outcome"],
                "supports_convergence_hypothesis": result["supports_convergence_hypothesis"],
                "contradicts_convergence_hypothesis": result["contradicts_convergence_hypothesis"],
                "n_final": result["n_final"],
                "mean_pairwise_similarity": result["mean_pairwise_similarity"],
                "fusion_events": result["event_counts"]["fusion_events"],
                "hgt_events": result["event_counts"]["hgt_events"],
                "extinctions": result["event_counts"]["extinctions"],
                "coop_events": result["event_counts"]["coop_events"],
                "parasite_events": result["event_counts"]["parasite_events"],
                "life_number": result["life_number"],
                "life_regime": result["life_regime"],
                "multi_origin_survivor": result["multi_origin_survivor"],
            }
        )
    return rows


def main() -> None:
    out = output_dir(__file__, "multi_origin_convergence")
    scenarios = default_scenarios()

    primary_results: list[dict[str, Any]] = []
    histories: list[pd.DataFrame] = []
    for sc in scenarios:
        result = simulate(sc)
        primary_results.append({k: v for k, v in result.items() if k != "history"})
        hist = pd.DataFrame(result["history"])
        hist["scenario"] = sc.name
        histories.append(hist)

    hist_df = pd.concat(histories, ignore_index=True)
    hist_df.to_csv(out / "lineage_timeseries.csv", index=False)

    summary_rows = []
    for r in primary_results:
        summary_rows.append(
            {
                "scenario": r["scenario"],
                "outcome": r["outcome"],
                "supports_convergence": r["supports_convergence_hypothesis"],
                "contradicts_convergence": r["contradicts_convergence_hypothesis"],
                "n_origins": r["n_origins"],
                "n_final": r["n_final"],
                "mean_similarity": r["mean_pairwise_similarity"],
                "fusion_events": r["event_counts"]["fusion_events"],
                "hgt_events": r["event_counts"]["hgt_events"],
                "extinctions": r["event_counts"]["extinctions"],
                "mutations": r["event_counts"]["mutations"],
                "coop_events": r["event_counts"]["coop_events"],
                "parasite_events": r["event_counts"]["parasite_events"],
                "life_number": r["life_number"],
                "life_regime": r["life_regime"],
                "multi_origin_survivor": r["multi_origin_survivor"],
            }
        )
    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(out / "scenario_summary.csv", index=False)

    # Replicate statistics for robustness (supports AND contradicts must both be reachable)
    rep_rows: list[dict[str, Any]] = []
    for sc in scenarios:
        rep_rows.extend(_replicate_sweep(sc, n_reps=16))
    rep_df = pd.DataFrame(rep_rows)
    rep_df.to_csv(out / "replicate_sweep.csv", index=False)

    agg = (
        rep_df.groupby("scenario")
        .agg(
            n_reps=("replicate", "count"),
            support_frac=("supports_convergence_hypothesis", "mean"),
            contradict_frac=("contradicts_convergence_hypothesis", "mean"),
            mean_n_final=("n_final", "mean"),
            mean_similarity=("mean_pairwise_similarity", "mean"),
            mean_fusion=("fusion_events", "mean"),
            mean_hgt=("hgt_events", "mean"),
            outcome_mode=("outcome", lambda s: s.value_counts().index[0]),
        )
        .reset_index()
    )
    agg.to_csv(out / "replicate_aggregate.csv", index=False)

    # Figures
    fig, axes = plt.subplots(2, 2, figsize=(11.2, 8.6), constrained_layout=True)
    for name, frame in hist_df.groupby("scenario"):
        axes[0, 0].plot(frame["step"], frame["n_lineages"], lw=1.6, label=name)
    axes[0, 0].set_title("Lineage count (no forced merger)")
    axes[0, 0].set_xlabel("step")
    axes[0, 0].set_ylabel("n lineages")
    axes[0, 0].legend(frameon=False, fontsize=7, ncol=2)

    for name, frame in hist_df.groupby("scenario"):
        axes[0, 1].plot(frame["step"], frame["mean_similarity"], lw=1.6, label=name)
    axes[0, 1].set_title("Mean pairwise genome similarity")
    axes[0, 1].set_xlabel("step")
    axes[0, 1].set_ylabel("similarity")

    colors = ["#4c78a8" if s else "#e45756" for s in summary_df["supports_convergence"]]
    axes[1, 0].bar(range(len(summary_df)), summary_df["n_final"], color=colors)
    axes[1, 0].set_xticks(range(len(summary_df)))
    axes[1, 0].set_xticklabels(summary_df["scenario"], rotation=35, ha="right", fontsize=7)
    axes[1, 0].set_ylabel("final lineage count")
    axes[1, 0].set_title("Primary-seed outcomes (blue=supports, red=not)")

    x = np.arange(len(agg))
    w = 0.38
    axes[1, 1].bar(x - w / 2, agg["support_frac"], w, color="#4c78a8", label="supports mono-lineage")
    axes[1, 1].bar(x + w / 2, agg["contradict_frac"], w, color="#e45756", label="contradicts")
    axes[1, 1].set_xticks(x)
    axes[1, 1].set_xticklabels(agg["scenario"], rotation=35, ha="right", fontsize=7)
    axes[1, 1].set_ylim(0, 1.05)
    axes[1, 1].set_ylabel("fraction of replicates")
    axes[1, 1].set_title("16-replicate outcome fractions")
    axes[1, 1].legend(frameon=False, fontsize=8)

    fig.savefig(out / "multi_origin_convergence_scan.png", dpi=220)
    plt.close(fig)

    # Event mechanism separation check for hgt_without_fusion primary run
    hgt_run = next(r for r in primary_results if r["scenario"] == "hgt_without_fusion")
    mechanism_check = {
        "hgt_events": hgt_run["event_counts"]["hgt_events"],
        "fusion_events": hgt_run["event_counts"]["fusion_events"],
        "n_final": hgt_run["n_final"],
        "mean_similarity": hgt_run["mean_pairwise_similarity"],
        "rule": "HGT transfers information without merging lineages (fusion stays 0)",
        "passed": (
            hgt_run["event_counts"]["hgt_events"] > 0
            and hgt_run["event_counts"]["fusion_events"] == 0
            and hgt_run["n_final"] >= 2
        ),
    }

    payload = {
        "question": (
            "Can multiple independent proto-biological populations converge to a single "
            "surviving lineage through competition, exchange, cooperation, fusion, and extinction?"
        ),
        "non_claim": "Does not assert that multiple origins occurred historically on Earth.",
        "design_rules": [
            "HGT does not merge lineages",
            "Fusion is independently rate-controlled",
            "Convergence is not encoded as the target outcome",
            "Scenarios must be able to support OR contradict mono-lineage convergence",
        ],
        "mechanism_check": mechanism_check,
        "primary_outcomes": summary_rows,
        "replicate_aggregate": agg.to_dict(orient="records"),
        "both_outcome_classes_observed": bool(
            (agg["support_frac"] > 0).any() and (agg["contradict_frac"] > 0).any()
        ),
        "runtime_bridge_available": _RUNTIME_LIFE is not None,
        "finite_life_numbers": finite_summary(summary_df["life_number"].to_numpy()),
    }
    (out / "summary.json").write_text(json.dumps(payload, indent=2) + "\n")

    # Console report
    print("=" * 72)
    print("CDFD Multi-Origin Life Convergence Simulator")
    print("=" * 72)
    print("Question: can multi-origin populations converge to one lineage?")
    print("Non-claim: does NOT prove multiple origins occurred on Earth.")
    print("-" * 72)
    for row in summary_rows:
        flag = "SUPPORTS" if row["supports_convergence"] else ("CONTRADICTS" if row["contradicts_convergence"] else "NEUTRAL")
        print(
            f"  [{flag:11}] {row['scenario']}: {row['outcome']} "
            f"(n_final={row['n_final']}, sim={row['mean_similarity']:.3f}, "
            f"HGT={row['hgt_events']}, fusion={row['fusion_events']})"
        )
    print("-" * 72)
    print("Replicate fractions (support / contradict):")
    for _, row in agg.iterrows():
        print(
            f"  {row['scenario']}: support={row['support_frac']:.2f} "
            f"contradict={row['contradict_frac']:.2f} mode={row['outcome_mode']} "
            f"<n_final>={row['mean_n_final']:.2f}"
        )
    print("-" * 72)
    print(
        f"Mechanism check (HGT≠fusion): passed={mechanism_check['passed']} "
        f"(HGT={mechanism_check['hgt_events']}, fusion={mechanism_check['fusion_events']}, "
        f"n_final={mechanism_check['n_final']})"
    )
    print(f"Both outcome classes observed across scenarios: {payload['both_outcome_classes_observed']}")
    print(f"Runtime life-number bridge available: {_RUNTIME_LIFE is not None}")
    print(f"Outputs: {out}")
    print("=" * 72)


if __name__ == "__main__":
    main()
