"""
Supplementary Material - CDFD OOL Paper 2
Fe-S Redox and Mineral Constraint Scaffolds

This deterministic toy model illustrates how a mineral interface can localize
and amplify redox flux in a constraint-field description. It is not a molecular
simulation of Fe-S surface chemistry.

Outputs are written to outputs/paper_02/.
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

N = 50
STEPS = 200
DT = 0.05
KAPPA_S = 0.05
D_M = 0.01


def laplacian(z: np.ndarray) -> np.ndarray:
    return (
        -4 * z
        + np.roll(z, 1, 0)
        + np.roll(z, -1, 0)
        + np.roll(z, 1, 1)
        + np.roll(z, -1, 1)
    )


def simulate_mineral_catalysis() -> tuple[list[float], list[float], list[float], list[float], np.ndarray, np.ndarray]:
    np.random.seed(1)
    phi = np.random.rand(N, N) * 0.1
    constraint = np.ones((N, N))
    S = np.ones((N, N))
    M_s = np.ones((N, N)) * 0.1

    cx, cy = N // 2, N // 2
    constraint[cx - 5 : cx + 5, cy - 5 : cy + 5] = 10.0

    mean_flux: list[float] = []
    peak_interface_flux: list[float] = []
    mean_s: list[float] = []
    mean_ms: list[float] = []

    for _ in range(STEPS):
        phi[0, :] = 5.0

        grad_y, grad_x = np.gradient(constraint)
        grad_mag = np.sqrt(grad_x**2 + grad_y**2)
        interface_mask = grad_mag > 2.0

        phi[interface_mask] += DT * 0.5 * phi[interface_mask]

        safe_constraint = np.where(constraint > 1e-9, constraint, 1e-9)
        phi = np.clip(phi + DT * laplacian((phi / safe_constraint) * S), 0.0, 100.0)

        psi = (phi / safe_constraint) * S * M_s
        dm_s = np.clip(phi * S - D_M * M_s, -10.0, 10.0)
        M_s = np.maximum(M_s + DT * dm_s, 0.0)

        ds = np.clip(KAPPA_S * (psi - S), -10.0, 10.0)
        S = np.maximum(S + DT * ds, 0.01)

        mean_flux.append(float(np.mean(phi)))
        mean_s.append(float(np.mean(S)))
        mean_ms.append(float(np.mean(M_s)))
        peak_interface_flux.append(
            float(np.max(phi[interface_mask]) if np.any(interface_mask) else 0.0)
        )

    return mean_flux, peak_interface_flux, mean_s, mean_ms, phi, constraint


def write_outputs(
    summary: dict[str, object],
    rows: list[dict[str, float]],
    final_phi: np.ndarray,
    constraint: np.ndarray,
) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_02"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "timeseries.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["step", "mean_flux", "peak_interface_flux", "mean_s", "mean_ms"])
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(1, 3, figsize=(15, 4), constrained_layout=True)
    im = axes[0].imshow(final_phi, cmap="inferno", origin="lower")
    axes[0].contour(constraint, levels=[5.0], colors="cyan", linewidths=1.2)
    axes[0].set_title("Final redox flux field")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    fig.colorbar(im, ax=axes[0], fraction=0.046, pad=0.04, label="flux proxy")
    axes[1].plot([row["step"] for row in rows], [row["mean_flux"] for row in rows], label="mean flux", lw=2)
    axes[1].plot(
        [row["step"] for row in rows],
        [row["peak_interface_flux"] for row in rows],
        label="peak interface flux",
        lw=2,
    )
    axes[1].set_title("Interface amplification")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("flux proxy")
    axes[1].legend(frameon=False)

    axes[2].plot([row["step"] for row in rows], [row["mean_ms"] for row in rows], label="Mean M_s", color="#ff7f0e", lw=2)
    axes[2].plot([row["step"] for row in rows], [row["mean_s"] for row in rows], label="Mean S", color="#2ca02c", lw=2)
    axes[2].set_title("Adaptive Surface Dynamics")
    axes[2].set_xlabel("step")
    axes[2].set_ylabel("S & M_s proxy")
    axes[2].legend(frameon=False)

    fig.savefig(out_dir / "fe_s_redox_interface.png", dpi=220)
    plt.close(fig)


def main() -> None:
    mean_hist, peak_hist, s_hist, ms_hist, final_phi, final_constraint = simulate_mineral_catalysis()
    rows = [
        {"step": i, "mean_flux": mean, "peak_interface_flux": peak, "mean_s": s_val, "mean_ms": ms_val}
        for i, (mean, peak, s_val, ms_val) in enumerate(zip(mean_hist, peak_hist, s_hist, ms_hist))
    ]
    summary = {
        "paper": 2,
        "model": "Fe-S interface redox flux toy model",
        "initial_mean_redox_flux": mean_hist[0],
        "final_mean_redox_flux": mean_hist[-1],
        "final_peak_interface_flux": peak_hist[-1],
        "final_mean_s": s_hist[-1],
        "final_mean_ms": ms_hist[-1],
        "interpretation": "Interface gradients can localize and amplify flux in the toy field.",
    }
    write_outputs(summary, rows, final_phi, final_constraint)

    print("=" * 70)
    print("CDFD OOL Paper 2: Fe-S Redox Interface")
    print("=" * 70)
    print(f"  Initial mean redox flux: {mean_hist[0]:.3f}")
    print(f"  Final mean redox flux:   {mean_hist[-1]:.3f}")
    print(f"  Peak flux at interface:  {peak_hist[-1]:.3f}")
    print(f"  Final Mean S:            {s_hist[-1]:.3f}")
    print(f"  Final Mean M_s:          {ms_hist[-1]:.3f}")
    print("  Figure: outputs/paper_02/fe_s_redox_interface.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
