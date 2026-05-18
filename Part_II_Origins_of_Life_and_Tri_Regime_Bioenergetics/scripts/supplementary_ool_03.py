"""
Supplementary Material - CDFD OOL Paper 3
Magnetite Networks and Electron Transport

The model demonstrates adaptive transport resistance under imposed electron
drive. It is a toy corridor-forming calculation, not a first-principles model
of magnetite defect chemistry.

Outputs are written to outputs/paper_03/.
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
STEPS = 300
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


def simulate_magnetite_network() -> tuple[list[float], list[float], list[float], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    np.random.seed(2)
    phi = np.random.rand(N, N) * 0.1
    constraint = np.ones((N, N)) * 2.0
    S = np.ones((N, N))
    M_s = np.ones((N, N)) * 0.1

    source = (10, 10)
    sink = (40, 40)

    efficiency: list[float] = []
    mean_s: list[float] = []
    mean_ms: list[float] = []

    for _ in range(STEPS):
        phi[source] = 10.0
        phi[sink] = 0.0

        safe_constraint = np.where(constraint > 1e-9, constraint, 1e-9)
        grad_y, grad_x = np.gradient((phi / safe_constraint) * S)
        flux_mag = np.sqrt(grad_x**2 + grad_y**2)

        constraint = np.clip(
            constraint + DT * (-0.15 * flux_mag + 0.02 * (2.0 - constraint)),
            0.1,
            2.0,
        )
        phi = np.clip(phi + DT * laplacian((phi / safe_constraint) * S), 0.0, 100.0)

        psi = (phi / safe_constraint) * S * M_s
        dm_s = np.clip(phi * S - D_M * M_s, -10.0, 10.0)
        M_s = np.maximum(M_s + DT * dm_s, 0.0)

        ds = np.clip(KAPPA_S * (psi - S), -10.0, 10.0)
        S = np.maximum(S + DT * ds, 0.01)

        efficiency.append(float(1.0 / np.mean(constraint)))
        mean_s.append(float(np.mean(S)))
        mean_ms.append(float(np.mean(M_s)))

    return efficiency, mean_s, mean_ms, phi, constraint, S, M_s


def write_outputs(
    summary: dict[str, object],
    rows: list[dict[str, float]],
    final_phi: np.ndarray,
    final_constraint: np.ndarray,
) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_03"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "efficiency_timeseries.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["step", "network_efficiency", "mean_s", "mean_ms"])
        writer.writeheader()
        writer.writerows(rows)
    fig, axes = plt.subplots(1, 4, figsize=(16, 3.8), constrained_layout=True)

    im0 = axes[0].imshow(final_phi, cmap="magma", origin="lower")
    axes[0].set_title("Electron flux proxy")
    axes[0].set_xlabel("x")
    axes[0].set_ylabel("y")
    fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)

    im1 = axes[1].imshow(final_constraint, cmap="viridis_r", origin="lower", vmin=0.1, vmax=2.0)
    axes[1].set_title("Transport constraint")
    axes[1].set_xlabel("x")
    axes[1].set_ylabel("y")
    fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)

    axes[2].plot([row["step"] for row in rows], [row["network_efficiency"] for row in rows], lw=2)
    axes[2].set_title("Network efficiency")
    axes[2].set_xlabel("step")
    axes[2].set_ylabel("1 / mean constraint")

    axes[3].plot([row["step"] for row in rows], [row["mean_ms"] for row in rows], lw=2, color="#ff7f0e", label="Mean M_s")
    axes[3].plot([row["step"] for row in rows], [row["mean_s"] for row in rows], lw=2, color="#2ca02c", label="Mean S")
    axes[3].set_title("Adaptive Surface Dynamics")
    axes[3].set_xlabel("step")
    axes[3].set_ylabel("S & M_s Proxy")
    axes[3].legend(frameon=False)

    fig.savefig(out_dir / "magnetite_transport_network.png", dpi=220)
    plt.close(fig)


def main() -> None:
    eff_hist, s_hist, ms_hist, final_phi, final_constraint, S, M_s = simulate_magnetite_network()
    rows = [{"step": i, "network_efficiency": value, "mean_s": s_val, "mean_ms": ms_val}
            for i, (value, s_val, ms_val) in enumerate(zip(eff_hist, s_hist, ms_hist))]

    summary = {
        "paper": 3,
        "model": "magnetite-like adaptive transport toy model",
        "initial_network_efficiency": eff_hist[0],
        "final_network_efficiency": eff_hist[-1],
        "final_mean_s": s_hist[-1],
        "final_mean_ms": ms_hist[-1],
        "min_constraint": float(np.min(final_constraint)),
        "max_constraint": float(np.max(final_constraint)),
        "interpretation": "This parameter set lowers transport resistance but trends toward broad erosion rather than a sharply localized wire.",
    }
    write_outputs(summary, rows, final_phi, final_constraint)

    print("=" * 70)
    print("CDFD OOL Paper 3: Magnetite-Like Electron Transport")
    print("=" * 70)
    print(f"  Initial network efficiency: {eff_hist[0]:.3f}")
    print(f"  Final network efficiency:   {eff_hist[-1]:.3f}")
    print(f"  Final Mean S:               {s_hist[-1]:.3f}")
    print(f"  Final Mean M_s:             {ms_hist[-1]:.3f}")
    print(f"  Min constraint:             {np.min(final_constraint):.3f}")
    print(f"  Max constraint:             {np.max(final_constraint):.3f}")
    print("  Figure: outputs/paper_03/magnetite_transport_network.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
