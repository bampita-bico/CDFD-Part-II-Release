"""
Supplementary Material - CDFD OOL Paper 1
Thermodynamic Mandate and Dependency-Gate Surface

This script visualizes the release-level CDFL bookkeeping relation
Psi_s=(Phi/C) S M_s over drive and constraint. It is a diagnostic map of
necessary conditions, not a historical abiogenesis simulation.

Outputs are written to outputs/paper_01/.
"""
from __future__ import annotations

import csv
import json
import os

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cdfd_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/cdfd_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from partii_runtime import adaptive_ratio, finite_summary, output_dir


N = 60


def build_gate_surface() -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    phi = np.linspace(0.05, 6.0, N)
    constraint = np.linspace(0.1, 6.0, N)
    phi_grid, constraint_grid = np.meshgrid(phi, constraint, indexing="ij")

    # Responsiveness increases with useful drive but saturates; memory increases
    # with constraint only while exchange is still possible.
    S = 0.25 + 1.25 * (phi_grid / (1.0 + phi_grid))
    M_s = 0.20 + 1.15 * (constraint_grid / (1.0 + constraint_grid)) * np.exp(-0.055 * constraint_grid)
    psi = adaptive_ratio(phi_grid, constraint_grid, S, M_s)
    return phi_grid, constraint_grid, S * M_s, psi


def gate_rows(phi_grid: np.ndarray, constraint_grid: np.ndarray, memory_surface: np.ndarray, psi: np.ndarray) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for i in range(phi_grid.shape[0]):
        for j in range(phi_grid.shape[1]):
            value = float(psi[i, j])
            if 0.85 <= value <= 1.15:
                regime = "near_critical"
            elif value < 0.85:
                regime = "underdriven_or_overconstrained"
            else:
                regime = "overload_or_unbounded"
            rows.append(
                {
                    "phi": float(phi_grid[i, j]),
                    "constraint": float(constraint_grid[i, j]),
                    "S_times_Ms": float(memory_surface[i, j]),
                    "psi_s": value,
                    "regime": regime,
                }
            )
    return rows


def main() -> None:
    phi_grid, constraint_grid, memory_surface, psi = build_gate_surface()
    rows = gate_rows(phi_grid, constraint_grid, memory_surface, psi)
    near = [row for row in rows if row["regime"] == "near_critical"]

    out_dir = output_dir(__file__, "paper_01")
    with (out_dir / "dependency_gate_surface.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["phi", "constraint", "S_times_Ms", "psi_s", "regime"])
        writer.writeheader()
        writer.writerows(rows)

    conditions = [
        {
            "condition": "sustained_disequilibrium",
            "symbolic_gate": "Phi > 0 over repeated cycles",
            "failure_mode": "no work source; chemistry equilibrates or decays",
        },
        {
            "condition": "finite_constraint",
            "symbolic_gate": "0 < C < infinity",
            "failure_mode": "washout when C is too low; isolation when C is too high",
        },
        {
            "condition": "responsive_routing",
            "symbolic_gate": "S > 0 and coupled to product-forming pathways",
            "failure_mode": "drive becomes heat/noise without selective chemistry",
        },
        {
            "condition": "retained_memory",
            "symbolic_gate": "M_s(t + nT) > M_s(t) for some n",
            "failure_mode": "products do not seed later cycles",
        },
    ]
    with (out_dir / "necessary_conditions.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["condition", "symbolic_gate", "failure_mode"])
        writer.writeheader()
        writer.writerows(conditions)

    summary = {
        "paper": 1,
        "model": "CDFL dependency-gate surface for the Part II opening paper",
        "grid_points": len(rows),
        "near_critical_points": len(near),
        "psi_summary": finite_summary(psi),
        "interpretation": "The near-critical band is a necessary-condition map: flux, constraint, responsiveness, and memory must be co-present before later OOL mechanisms matter.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    fig, axes = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)
    im0 = axes[0].imshow(
        psi.T,
        origin="lower",
        aspect="auto",
        extent=[phi_grid.min(), phi_grid.max(), constraint_grid.min(), constraint_grid.max()],
        cmap="viridis",
        vmin=0.0,
        vmax=3.0,
    )
    axes[0].contour(phi_grid, constraint_grid, psi, levels=[0.85, 1.0, 1.15], colors=["white", "black", "white"], linewidths=[1, 1.3, 1])
    axes[0].set_title("Dependency-gate surface")
    axes[0].set_xlabel("drive Phi")
    axes[0].set_ylabel("constraint C")
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04, label="Psi_s")

    im1 = axes[1].imshow(
        memory_surface.T,
        origin="lower",
        aspect="auto",
        extent=[phi_grid.min(), phi_grid.max(), constraint_grid.min(), constraint_grid.max()],
        cmap="magma",
    )
    axes[1].set_title("responsive memory S M_s")
    axes[1].set_xlabel("drive Phi")
    axes[1].set_ylabel("constraint C")
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    regimes = {"underdriven_or_overconstrained": 0, "near_critical": 0, "overload_or_unbounded": 0}
    for row in rows:
        regimes[str(row["regime"])] += 1
    axes[2].bar(range(len(regimes)), list(regimes.values()), color=["#b9574f", "#d6a04f", "#4f8f5b"])
    axes[2].set_xticks(range(len(regimes)))
    axes[2].set_xticklabels([key.replace("_", "\n") for key in regimes], fontsize=8)
    axes[2].set_ylabel("grid points")
    axes[2].set_title("necessary-condition regimes")

    fig.savefig(out_dir / "dependency_gate_surface.png", dpi=220)
    plt.close(fig)

    print("=" * 70)
    print("CDFD OOL Paper 1: Dependency-Gate Surface")
    print("=" * 70)
    print(f"  Grid points:           {len(rows)}")
    print(f"  Near-critical points:  {len(near)}")
    print(f"  Psi_s range:           {np.nanmin(psi):.3f} -> {np.nanmax(psi):.3f}")
    print("  Figure: outputs/paper_01/dependency_gate_surface.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
