"""
Supplementary Material - CDFD OOL Paper 9
Evolutionary Dynamics, Error Thresholds, and Protocell Integration

This script includes both a flux-dependent error-threshold toy model and the
deliberately fragile integrated protocell diagnostic for the active
twelve-paper spine.

Outputs are written to outputs/paper_09/.
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

N = 40
STEPS = 200
DT = 0.05

def simulate_quasispecies(
    flux_energy: float, sequence_length: int = 50, steps: int = 200, dt: float = 0.05
) -> list[float]:
    fitness = 1.0
    history: list[float] = []

    for _ in range(steps):
        rep_rate = 0.5 * flux_energy
        error_rate_per_base = 0.05 / max(flux_energy, 0.1)
        q = (1.0 - error_rate_per_base) ** sequence_length
        d_fit = rep_rate * q * fitness - rep_rate * (1.0 - q) * fitness
        fitness = max(fitness + dt * d_fit, 0.0)
        fitness = min(fitness, 1.0)
        history.append(fitness)

    return history


def laplacian(z: np.ndarray) -> np.ndarray:
    return (
        -4 * z
        + np.roll(z, 1, 0)
        + np.roll(z, -1, 0)
        + np.roll(z, 1, 1)
        + np.roll(z, -1, 1)
    )


def finite_mean(values: np.ndarray) -> float:
    finite = values[np.isfinite(values)]
    return float(np.mean(finite)) if finite.size else float("nan")


def json_clean(value: object) -> object:
    if isinstance(value, dict):
        return {key: json_clean(item) for key, item in value.items()}
    if isinstance(value, list):
        return [json_clean(item) for item in value]
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def simulate_protocell() -> tuple[list[float], list[float], int | None]:
    np.random.seed(9)
    phi = np.random.rand(N, N) * 0.1
    constraint = np.ones((N, N))

    cx, cy = N // 2, N // 2
    radius = 6
    y, x = np.ogrid[:N, :N]
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    boundary = (dist >= radius - 1) & (dist <= radius + 1)
    core = dist < radius - 1
    constraint[boundary] = 15.0
    constraint[core] = 0.5

    internal_psi: list[float] = []
    external_psi: list[float] = []
    first_nonfinite_step: int | None = None

    with np.errstate(over="ignore", invalid="ignore"):
        for step in range(STEPS):
            env_flux = 5.0 + 2.0 * np.sin(step * 0.1)
            phi[0, :] = env_flux
            phi[core] += DT * 0.1 * phi[core] ** 2

            safe_constraint = np.where(constraint > 1e-9, constraint, 1e-9)
            constraint[core] = constraint[core] * 0.95 + 0.05 * phi[core]

            phi = np.clip(phi + DT * laplacian(phi / safe_constraint), 0, None)
            psi_field = phi / safe_constraint

            if first_nonfinite_step is None and (
                not np.all(np.isfinite(phi)) or not np.all(np.isfinite(constraint))
            ):
                first_nonfinite_step = step

            if first_nonfinite_step is None:
                internal_psi.append(finite_mean(psi_field[core]))
                external_psi.append(finite_mean(psi_field[0, :]))
            else:
                internal_psi.append(float("nan"))
                external_psi.append(float("nan"))

    return internal_psi, external_psi, first_nonfinite_step


def write_outputs(
    summary: dict[str, object],
    error_rows: list[dict[str, object]],
    protocell_rows: list[dict[str, float]],
    internal: list[float],
    external: list[float],
    first_nonfinite: int | None,
) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_09"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(json_clean(summary), indent=2) + "\n")
    with (out_dir / "error_threshold_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["flux_energy", "final_master_sequence_fitness", "state"],
        )
        writer.writeheader()
        writer.writerows(error_rows)
    with (out_dir / "protocell_snapshots.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["time", "external_psi", "internal_psi"],
        )
        writer.writeheader()
        writer.writerows(protocell_rows)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    axes[0].plot(
        [float(row["flux_energy"]) for row in error_rows],
        [float(row["final_master_sequence_fitness"]) for row in error_rows],
        marker="o",
        lw=2,
    )
    axes[0].set_title("Flux-dependent error threshold")
    axes[0].set_xlabel("flux energy proxy")
    axes[0].set_ylabel("final master-sequence fitness")
    axes[0].set_ylim(0, 1.05)
    axes[1].plot(external, label="external Psi", lw=2)
    axes[1].plot(internal, label="internal Psi", lw=2)
    if first_nonfinite is not None:
        axes[1].axvline(first_nonfinite, color="black", lw=1, ls="--", label="first non-finite")
    axes[1].set_title("Integrated protocell diagnostic")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("Psi proxy")
    axes[1].set_yscale("symlog", linthresh=1.0)
    axes[1].legend(frameon=False)
    fig.savefig(out_dir / "error_threshold_and_protocell.png", dpi=220)
    plt.close(fig)


def main() -> None:
    error_rows: list[dict[str, object]] = []
    for flux in [0.2, 0.5, 1.0, 5.0, 10.0]:
        hist = simulate_quasispecies(flux)
        final_fitness = hist[-1]
        error_rows.append(
            {
                "flux_energy": flux,
                "final_master_sequence_fitness": final_fitness,
                "state": "survives" if final_fitness > 0.5 else "error_catastrophe",
            }
        )

    internal, external, first_nonfinite = simulate_protocell()
    snapshot_times = [10, 50, 100, 150, 199]
    protocell_rows = [
        {"time": t, "external_psi": external[t], "internal_psi": internal[t]}
        for t in snapshot_times
    ]

    summary = {
        "paper": 9,
        "model": "merged error-threshold and integrated-protocell diagnostic toy models",
        "error_rows": error_rows,
        "first_nonfinite_step": first_nonfinite,
        "protocell_snapshots": protocell_rows,
        "interpretation": "The replication toy model supports high-flux sequence persistence, while the integrated explicit update remains numerically fragile.",
    }
    write_outputs(summary, error_rows, protocell_rows, internal, external, first_nonfinite)

    print("=" * 70)
    print("CDFD OOL Paper 9: Error Thresholds and Protocell Integration")
    print("=" * 70)
    print("Flux-dependent error threshold:")
    for row in error_rows:
        print(
            f"  Phi={row['flux_energy']:<4.1f} fitness={row['final_master_sequence_fitness']:.3f} "
            f"{row['state']}"
        )
    print("Integrated protocell diagnostic:")
    for row in protocell_rows:
        print(
            f"  t={row['time']:<3d} external Psi={row['external_psi']:.3f} "
            f"internal Psi={row['internal_psi']:.3f}"
        )
    print(f"  First non-finite step: {first_nonfinite}")
    print("  Figure: outputs/paper_09/error_threshold_and_protocell.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
