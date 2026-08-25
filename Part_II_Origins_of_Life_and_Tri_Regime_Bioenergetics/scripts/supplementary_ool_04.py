"""
Supplementary Material - CDFD OOL Paper 4
Structured Water and Proton/Ion Coherence

The script tracks a scalar orientational-disorder proxy under imposed gradient.
It is not molecular dynamics; it only tests the paper's reduced feedback logic.

Outputs are written to outputs/paper_04/.
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

KAPPA_S = 0.05
D_M = 0.01

def simulate_structured_water(
    gradient_strength: float, steps: int = 200, dt: float = 0.05
) -> tuple[list[float], list[float], list[float], list[float]]:
    phi = 0.1
    disorder = 1.0
    S = 1.0
    M_s = 0.1
    phi_hist: list[float] = []
    disorder_hist: list[float] = []
    s_hist: list[float] = []
    ms_hist: list[float] = []

    for _ in range(steps):
        proton_flux = gradient_strength / disorder
        d_disorder = -0.2 * proton_flux + 0.05 * (1.0 - disorder)
        disorder = max(disorder + dt * d_disorder, 0.05)
        phi = phi + dt * (proton_flux - 0.1 * phi)

        psi = proton_flux * M_s
        dM_s = max(min(proton_flux - D_M * M_s, 10.0), -10.0)
        M_s = max(M_s + dt * dM_s, 0.0)

        dS = max(min(KAPPA_S * (psi - S), 10.0), -10.0)
        S = max(S + dt * dS, 0.01)

        phi_hist.append(phi)
        disorder_hist.append(disorder)
        s_hist.append(S)
        ms_hist.append(M_s)

    return phi_hist, disorder_hist, s_hist, ms_hist


def write_outputs(summary: dict[str, object], rows: list[dict[str, float]]) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_04"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "gradient_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["gradient", "final_disorder", "final_proton_flux", "final_s", "final_ms"],
        )
        writer.writeheader()
        writer.writerows(rows)
    gradients = [row["gradient"] for row in rows]
    final_disorder = [row["final_disorder"] for row in rows]
    final_flux = [row["final_proton_flux"] for row in rows]
    final_s = [row["final_s"] for row in rows]
    final_ms = [row["final_ms"] for row in rows]

    fig, (ax1, ax3) = plt.subplots(1, 2, figsize=(12.9, 6.5), constrained_layout=True)

    ax1.plot(gradients, final_flux, marker="o", lw=2, color="#2f6f9f", label="proton flux proxy")
    ax1.set_xlabel("imposed gradient")
    ax1.set_ylabel("final proton flux proxy", color="#2f6f9f")
    ax1.tick_params(axis="y", labelcolor="#2f6f9f")

    ax2 = ax1.twinx()
    ax2.plot(gradients, final_disorder, marker="s", lw=2, color="#b4553b", label="disorder proxy")
    ax2.set_ylabel("final disorder proxy", color="#b4553b")
    ax2.tick_params(axis="y", labelcolor="#b4553b")
    ax1.set_title("Gradient-driven interfacial ordering")

    ax3.plot(gradients, final_ms, marker="^", lw=2, color="#ff7f0e", label="Final M_s")
    ax3.plot(gradients, final_s, marker="v", lw=2, color="#2ca02c", label="Final S")
    ax3.set_xlabel("imposed gradient")
    ax3.set_ylabel("S & M_s proxy")
    ax3.set_title("Adaptive Surface Coherence")
    ax3.legend(frameon=False)

    fig.savefig(out_dir / "structured_water_gradient_scan.png", dpi=220)
    plt.close(fig)


def main() -> None:
    rows: list[dict[str, float]] = []
    for gradient in [0.5, 1.0, 3.0, 5.0]:
        phi_hist, disorder_hist, s_hist, ms_hist = simulate_structured_water(gradient)
        rows.append(
            {
                "gradient": gradient,
                "final_disorder": disorder_hist[-1],
                "final_proton_flux": phi_hist[-1],
                "final_s": s_hist[-1],
                "final_ms": ms_hist[-1]
            }
        )

    summary = {
        "paper": 4,
        "model": "structured interfacial-water proton flux toy model",
        "minimum_disorder_floor": 0.05,
        "rows": rows,
        "interpretation": "Stronger gradients drive the disorder proxy toward its floor and raise the proton-flux proxy.",
    }
    write_outputs(summary, rows)

    print("=" * 70)
    print("CDFD OOL Paper 4: Structured Water Proton/Ion Coherence")
    print("=" * 70)
    print(f"  {'Gradient':<10} {'Final disorder':>18} {'Final proton flux':>22} {'Final S':>10} {'Final M_s':>10}")
    print("-" * 75)
    for row in rows:
        print(
            f"  {row['gradient']:<10.1f} {row['final_disorder']:>18.3f} "
            f"{row['final_proton_flux']:>22.3f} {row['final_s']:>10.3f} {row['final_ms']:>10.3f}"
        )
    print("  Figure: outputs/paper_04/structured_water_gradient_scan.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
