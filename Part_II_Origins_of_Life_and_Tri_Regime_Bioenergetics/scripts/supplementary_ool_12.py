"""
Supplementary Material - CDFD OOL Paper 12
Origins-of-Life Master Synthesis

This script collects the capstone diagnostics: Life Number regimes, phosphate
packet formation, LLPS-like heterogeneity, and environment-cycle persistence.

Outputs are written to outputs/paper_12/.
"""
from __future__ import annotations

import csv
import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cdfd_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/cdfd_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from partii_runtime import finite_summary, life_number as cdfd_life_number, output_dir, regime_from_value

KAPPA_S = 0.05
D_M = 0.01

def life_number_rows() -> list[dict[str, object]]:
    scenarios = [
        ("dispersed_bulk_chemistry", 0.4, 0.20, 0.20, 1.0, 1.5),
        ("mineral_redox_pore", 2.0, 0.50, 0.40, 4.0, 1.2),
        ("photochemical_unbuffered", 6.0, 0.80, 0.60, 2.0, 4.0),
        ("buffered_proto_cell", 6.0, 0.75, 0.65, 4.0, 2.0),
    ]
    rows: list[dict[str, object]] = []
    S = 1.0
    M_s = 1.0
    for label, input_energy, sigma_e, sigma_p, tau, stabilization in scenarios:
        lam_base = cdfd_life_number(input_energy, sigma_e, sigma_p, tau, stabilization)
        lam = lam_base * S * M_s
        regime = regime_from_value(lam)
        rows.append(
            {
                "scenario": label,
                "input_energy": input_energy,
                "sigma_e": sigma_e,
                "sigma_p": sigma_p,
                "tau_relax": tau,
                "stabilization": stabilization,
                "life_number": lam,
                "regime": regime,
            }
        )
    return rows


def simulate_phosphate(continuous_flux: float, steps: int = 100, dt: float = 0.1) -> tuple[float, float]:
    packets = 0.0
    continuous = continuous_flux
    threshold = 1.5
    for _ in range(steps):
        if continuous > threshold:
            amount = dt * 0.5 * continuous
            packets += amount
            continuous -= amount
    return continuous, packets


def simulate_llps(size: int = 30, steps: int = 100, dt: float = 0.1) -> tuple[float, float, np.ndarray]:
    np.random.seed(10)
    flux = np.random.rand(size, size) * 2.0
    constraint = np.ones((size, size))
    S = np.ones((size, size))
    M_s = np.ones((size, size)) * 0.1
    initial_std = float(np.std(constraint))

    for _ in range(steps):
        ratio = (flux / constraint) * S * M_s
        mean_ratio = np.mean(ratio)
        droplets = ratio > mean_ratio * 1.1
        dilute = ratio < mean_ratio * 0.9

        constraint[droplets] *= 1.0 + dt * 0.5
        constraint[dilute] *= max(1.0 - dt * 0.2, 0.1)

        dM_s = np.clip(flux * S - D_M * M_s, -10.0, 10.0)
        M_s = np.maximum(M_s + dt * dM_s, 0.0)

        ds = np.clip(KAPPA_S * (ratio - S), -10.0, 10.0)
        S = np.maximum(S + dt * ds, 0.01)

    return initial_std, float(np.std(constraint)), constraint


def environmental_cycle_rows() -> list[dict[str, object]]:
    cycle_inputs = [0.6, 3.6, 1.2, 4.2, 0.8, 3.0]
    rows: list[dict[str, object]] = []
    memory = 1.0
    S = 1.0
    M_s = 0.1
    for cycle, input_energy in enumerate(cycle_inputs, start=1):
        lam_base = cdfd_life_number(input_energy, 0.55, 0.45, tau_relax=2.5 * memory, stabilization=1.4)
        lam = lam_base * S * M_s

        dM_s = max(min(lam_base * S - D_M * M_s, 10.0), -10.0)
        M_s = max(M_s + dM_s, 0.0)

        dS = max(min(KAPPA_S * (lam - S), 10.0), -10.0)
        S = max(S + dS, 0.01)

        survives = lam >= 1.0
        memory = min(memory * 1.15, 1.8) if survives else max(memory * 0.75, 0.4)
        rows.append(
            {
                "cycle": cycle,
                "input_energy": input_energy,
                "life_number": lam,
                "localized_loop_survives": survives,
                "memory_factor_after_cycle": memory,
            }
        )
    return rows


def write_outputs(
    summary: dict[str, object],
    lambda_rows: list[dict[str, object]],
    cycle_rows: list[dict[str, object]],
    llps_constraint: np.ndarray,
) -> None:
    out_dir = output_dir(__file__, "paper_12")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "life_number_regimes.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "input_energy",
                "sigma_e",
                "sigma_p",
                "tau_relax",
                "stabilization",
                "life_number",
                "regime",
            ],
        )
        writer.writeheader()
        writer.writerows(lambda_rows)
    with (out_dir / "environmental_cycles.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "cycle",
                "input_energy",
                "life_number",
                "localized_loop_survives",
                "memory_factor_after_cycle",
            ],
        )
        writer.writeheader()
        writer.writerows(cycle_rows)
    fig, axes = plt.subplots(1, 3, figsize=(12.0, 5.8), constrained_layout=True)
    labels = [str(row["scenario"]).replace("_", "\n") for row in lambda_rows]
    values = [float(row["life_number"]) for row in lambda_rows]
    axes[0].bar(range(len(values)), values, color=["#b4553b", "#d6a04f", "#d6a04f", "#4f8f5b"])
    axes[0].axhline(1.0, color="black", lw=1, ls="--")
    axes[0].set_xticks(range(len(values)))
    axes[0].set_xticklabels(labels, fontsize=8)
    axes[0].set_ylabel("Life Number (Psi_s)")
    axes[0].set_title("Tri-regime crossing (Adaptive Surface)")
    axes[1].plot(
        [int(row["cycle"]) for row in cycle_rows],
        [float(row["life_number"]) for row in cycle_rows],
        marker="o",
        lw=2,
    )
    axes[1].axhline(1.0, color="black", lw=1, ls="--")
    axes[1].set_title("Environmental cycling")
    axes[1].set_xlabel("cycle")
    axes[1].set_ylabel("Life Number (Psi_s)")
    im = axes[2].imshow(llps_constraint, cmap="viridis", origin="lower")
    axes[2].set_title("LLPS-like heterogeneity")
    axes[2].set_xlabel("x")
    axes[2].set_ylabel("y")
    fig.colorbar(im, ax=axes[2], fraction=0.046, pad=0.04)
    fig.savefig(out_dir / "master_synthesis_regimes.png", dpi=220)
    plt.close(fig)


def main() -> None:
    lambda_rows = life_number_rows()
    final_continuous, phosphate_packets = simulate_phosphate(5.0)
    initial_llps_std, final_llps_std, llps_constraint = simulate_llps()
    cycle_rows = environmental_cycle_rows()
    summary = {
        "paper": 12,
        "model": "capstone Life Number and functional synthesis diagnostics",
        "lambda_rows": lambda_rows,
        "phosphate_initial_continuous_flux": 5.0,
        "phosphate_final_continuous_flux": final_continuous,
        "stored_phosphate_packets": phosphate_packets,
        "llps_initial_constraint_std": initial_llps_std,
        "llps_final_constraint_std": final_llps_std,
        "llps_constraint_summary": finite_summary(llps_constraint),
        "cycle_rows": cycle_rows,
        "interpretation": "Life-like persistence is treated as a regime crossing, now integrated with Adaptive Surface Memory.",
    }
    write_outputs(summary, lambda_rows, cycle_rows, llps_constraint)

    print("=" * 70)
    print("CDFD OOL Paper 12: Master Synthesis")
    print("=" * 70)
    print("Life Number regimes:")
    for row in lambda_rows:
        print(
            f"  {row['scenario']:<28} Life Number={row['life_number']:.3f} "
            f"{row['regime']}"
        )
    print("Phosphate and LLPS:")
    print(f"  Final continuous flux:   {final_continuous:.2f}")
    print(f"  Stored phosphate packets: {phosphate_packets:.2f}")
    print(f"  LLPS constraint std:      {initial_llps_std:.3f}->{final_llps_std:.3f}")
    print("  Figure: outputs/paper_12/master_synthesis_regimes.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
