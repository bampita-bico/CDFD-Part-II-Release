"""
Supplementary Material - CDFD OOL Paper 8
Mineral Compartments and Mineral-Organic Interfaces

This script treats localization and catalytic interface selection as one
boundary bottleneck class for the active twelve-paper spine.

Outputs are written to outputs/paper_08/.
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

def simulate_compartment(
    synthesis_rate: float, pore_resistance: float, steps: int = 300, dt: float = 0.05
) -> tuple[list[float], list[float], list[float], list[float]]:
    phi = 0.01
    S = 1.0
    M_s = 0.1
    psi_hist: list[float] = []
    concentration_hist: list[float] = []
    s_hist: list[float] = []
    ms_hist: list[float] = []

    for _ in range(steps):
        diffusion_loss = phi / pore_resistance
        phi = max(phi + dt * (synthesis_rate - diffusion_loss), 0.0)
        raw_psi = synthesis_rate / max(diffusion_loss, 1e-9)
        psi = min(raw_psi * (1.0 + 0.05 * np.log1p(pore_resistance)), 12.0)

        dM_s = max(min(synthesis_rate * S - D_M * M_s, 10.0), -10.0)
        M_s = max(M_s + dt * dM_s, 0.0)

        dS = max(min(KAPPA_S * (psi - S), 2.0), -2.0)
        S = max(S + dt * dS, 0.01)

        psi_hist.append(psi)
        concentration_hist.append(phi)
        s_hist.append(S)
        ms_hist.append(M_s)

    return psi_hist, concentration_hist, s_hist, ms_hist


def hybrid_interface(
    mineral_constraint: float,
    organic_alpha: float,
    organic_beta: float,
    steps: int = 300,
    dt: float = 0.05,
) -> tuple[list[float], list[float], list[float], list[float]]:
    mineral = mineral_constraint
    organic = 0.1
    flux = 0.1
    S = 1.0
    M_s = 0.1
    flux_hist: list[float] = []
    total_constraint_hist: list[float] = []
    s_hist: list[float] = []
    ms_hist: list[float] = []

    for step in range(steps):
        env_drive = 2.0 if 100 < step < 200 else 0.5
        total_constraint = mineral + organic

        psi = (env_drive / total_constraint) * S * M_s
        d_flux = env_drive - flux * total_constraint * S
        flux = max(flux + dt * d_flux, 0.0)
        organic = max(organic + dt * (organic_alpha * abs(d_flux) - organic_beta * organic), 0.0)

        dM_s = max(min(flux * S - D_M * M_s, 10.0), -10.0)
        M_s = max(M_s + dt * dM_s, 0.0)

        dS = max(min(KAPPA_S * (psi - S), 10.0), -10.0)
        S = max(S + dt * dS, 0.01)

        flux_hist.append(flux)
        total_constraint_hist.append(total_constraint)
        s_hist.append(S)
        ms_hist.append(M_s)

    return flux_hist, total_constraint_hist, s_hist, ms_hist


def write_outputs(
    summary: dict[str, object],
    compartment_rows: list[dict[str, object]],
    interface_rows: list[dict[str, float]],
    pure_flux: list[float],
    hybrid_flux: list[float],
) -> None:
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_08"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "compartment_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["environment", "synthesis", "pore_constraint", "final_psi", "final_concentration", "final_s", "final_ms", "state"],
        )
        writer.writeheader()
        writer.writerows(compartment_rows)
    with (out_dir / "interface_summary.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=["phase", "pure_mineral_flux", "hybrid_flux"],
        )
        writer.writeheader()
        writer.writerows(interface_rows)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.2), constrained_layout=True)
    labels = [str(row["environment"]) for row in compartment_rows]
    x = np.arange(len(labels))
    axes[0].bar(x - 0.18, [float(row["final_psi"]) for row in compartment_rows], width=0.36, label="final Psi")
    axes[0].bar(
        x + 0.18,
        [float(row["final_concentration"]) for row in compartment_rows],
        width=0.36,
        label="concentration",
    )
    axes[0].axhline(1.0, color="black", lw=1, ls="--")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(labels, rotation=25, ha="right")
    axes[0].set_title("Localization threshold")
    axes[0].legend(frameon=False)

    axes[1].plot(pure_flux, label="pure mineral", lw=2)
    axes[1].plot(hybrid_flux, label="hybrid interface", lw=2)
    axes[1].axvspan(100, 200, color="#e7b35a", alpha=0.2, label="surge window")
    axes[1].set_title("Interface surge attenuation")
    axes[1].set_xlabel("step")
    axes[1].set_ylabel("flux proxy")
    axes[1].legend(frameon=False)

    s_vals = [float(row["final_s"]) for row in compartment_rows]
    ms_vals = [float(row["final_ms"]) for row in compartment_rows]
    axes[2].bar(x - 0.18, s_vals, width=0.36, label="Final S", color="#2ca02c")
    axes[2].bar(x + 0.18, ms_vals, width=0.36, label="Final M_s", color="#ff7f0e")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(labels, rotation=25, ha="right")
    axes[2].set_title("Adaptive Surface Final States")
    axes[2].legend(frameon=False)

    fig.savefig(out_dir / "compartments_and_interfaces.png", dpi=220)
    plt.close(fig)


def main() -> None:
    scenarios = [
        ("Open ocean", 0.5, 0.1),
        ("Shallow pool", 0.5, 1.0),
        ("Hydrothermal pore", 0.5, 5.0),
        ("Deep sealed cavity", 0.5, 20.0),
    ]
    compartment_rows: list[dict[str, object]] = []
    for label, synthesis, constraint in scenarios:
        psi_hist, conc_hist, s_hist, ms_hist = simulate_compartment(synthesis, constraint)
        final_psi = psi_hist[-1]
        state = "threshold" if final_psi <= 1.0001 else "accumulated"
        compartment_rows.append(
            {
                "environment": label,
                "synthesis": synthesis,
                "pore_constraint": constraint,
                "final_psi": final_psi,
                "final_concentration": conc_hist[-1],
                "final_s": s_hist[-1],
                "final_ms": ms_hist[-1],
                "state": state,
            }
        )

    pure_flux, _, _, _ = hybrid_interface(1.0, 0.0, 0.0)
    hybrid_flux, _, _, _ = hybrid_interface(1.0, 0.1, 0.02)
    interface_rows = [
        {"phase": "baseline_low_drive", "pure_mineral_flux": pure_flux[50], "hybrid_flux": hybrid_flux[50]},
        {"phase": "surge_high_drive", "pure_mineral_flux": pure_flux[150], "hybrid_flux": hybrid_flux[150]},
        {"phase": "post_surge_recovery", "pure_mineral_flux": pure_flux[250], "hybrid_flux": hybrid_flux[250]},
    ]

    summary = {
        "paper": 8,
        "model": "merged compartment localization and mineral-organic interface toy models",
        "compartment_rows": compartment_rows,
        "interface_rows": interface_rows,
        "interpretation": "Confinement increases retention, while hybrid interfaces attenuate flux surges in this parameterization.",
    }
    write_outputs(summary, compartment_rows, interface_rows, pure_flux, hybrid_flux)

    print("=" * 70)
    print("CDFD OOL Paper 8: Compartments and Interfaces")
    print("=" * 70)
    print("Compartment localization:")
    for row in compartment_rows:
        print(
            f"  {row['environment']:<20} C={row['pore_constraint']:>4.1f} "
            f"Psi={row['final_psi']:>5.2f} Conc={row['final_concentration']:>5.2f} "
            f"S={row['final_s']:>5.2f} M_s={row['final_ms']:>5.2f} {row['state']}"
        )
    print("Hybrid mineral-organic interface:")
    for row in interface_rows:
        print(
            f"  {row['phase']:<20} pure={row['pure_mineral_flux']:.3f} "
            f"hybrid={row['hybrid_flux']:.3f}"
        )
    print("  Figure: outputs/paper_08/compartments_and_interfaces.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
