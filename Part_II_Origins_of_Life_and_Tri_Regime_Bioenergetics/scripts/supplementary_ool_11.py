"""
Supplementary Material - CDFD OOL Paper 11
Photochemical Energy Capture and Functional Bioenergetic Materials

This script makes the corrected chain explicit: photochemical capture is tested
before surplus stabilization. Literal chlorophyll and literal melanin are not
assumed at the origin; they are mature examples of wider functions.

Outputs are written to outputs/paper_11/.
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

from partii_runtime import life_number, output_dir


def capture_scenarios() -> list[dict[str, object]]:
    scenarios = [
        ("geochemical_redox_only", 1.2, 0.55, 0.40, 1.2, "chemical input before phototrophy"),
        ("mineral_photoredox", 2.4, 0.55, 0.38, 1.4, "pre-chlorophyll light capture candidate"),
        ("porphyrinoid_or_chromophore", 4.0, 0.65, 0.50, 1.8, "stronger pre-chlorophyll capture"),
        ("modern_chlorophyll_endpoint", 8.0, 0.85, 0.80, 2.2, "late high-performance endpoint"),
    ]
    rows: list[dict[str, object]] = []
    for label, input_energy, sigma_e, sigma_p, stabilization, note in scenarios:
        lam = life_number(input_energy, sigma_e, sigma_p, tau_relax=1.0, stabilization=stabilization)
        rows.append(
            {
                "scenario": label,
                "input_energy": input_energy,
                "sigma_e": sigma_e,
                "sigma_p": sigma_p,
                "stabilization": stabilization,
                "life_number": lam,
                "regime": "sustained" if lam > 1.0 else "subcritical",
                "note": note,
            }
        )
    return rows


def overload_scenarios() -> list[dict[str, object]]:
    scenarios = [
        ("low_capture_no_buffer", 1.0, 1.5, 0.5, "low input; no overload"),
        ("high_capture_no_buffer", 8.0, 2.0, 0.5, "capture precedes overload"),
        ("high_capture_with_buffer", 8.0, 2.0, 6.0, "buffer reduces overload"),
        ("high_capture_excessive_screening", 8.0, 0.8, 9.0, "too much screening can block useful capture"),
    ]
    rows: list[dict[str, object]] = []
    for label, input_energy, usable_capacity, dissipative_capacity, note in scenarios:
        S = 1.0
        M_s = 1.0
        overload = (input_energy / max(usable_capacity + dissipative_capacity, 1e-12)) * S * M_s
        usable_fraction = usable_capacity / max(usable_capacity + dissipative_capacity, 1e-12)
        rows.append(
            {
                "scenario": label,
                "input_energy": input_energy,
                "usable_capacity": usable_capacity,
                "dissipative_capacity": dissipative_capacity,
                "overload_proxy": overload,
                "usable_fraction": usable_fraction,
                "state": "overload" if overload > 1.0 else "buffered",
                "note": note,
            }
        )
    return rows


def write_outputs(
    summary: dict[str, object],
    capture_rows: list[dict[str, object]],
    overload_rows: list[dict[str, object]],
) -> None:
    out_dir = output_dir(__file__, "paper_11")
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    with (out_dir / "capture_chain.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "input_energy",
                "sigma_e",
                "sigma_p",
                "stabilization",
                "life_number",
                "regime",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(capture_rows)
    with (out_dir / "overload_buffering.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "scenario",
                "input_energy",
                "usable_capacity",
                "dissipative_capacity",
                "overload_proxy",
                "usable_fraction",
                "state",
                "note",
            ],
        )
        writer.writeheader()
        writer.writerows(overload_rows)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.3), constrained_layout=True)
    capture_labels = [str(row["scenario"]).replace("_", "\n") for row in capture_rows]
    capture_values = [float(row["life_number"]) for row in capture_rows]
    colors = ["#7a9cc6" if value < 1.0 else "#4f8f5b" for value in capture_values]
    axes[0].bar(np.arange(len(capture_values)), capture_values, color=colors)
    axes[0].axhline(1.0, color="black", lw=1, ls="--")
    axes[0].set_xticks(np.arange(len(capture_values)))
    axes[0].set_xticklabels(capture_labels, fontsize=8)
    axes[0].set_ylabel("Life Number proxy")
    axes[0].set_title("Energy capture chain (S & M_s integrated)")
    overload_labels = [str(row["scenario"]).replace("_", "\n") for row in overload_rows]
    overload_values = [float(row["overload_proxy"]) for row in overload_rows]
    overload_colors = ["#c95f55" if value > 1.0 else "#6b8e5a" for value in overload_values]
    axes[1].bar(np.arange(len(overload_values)), overload_values, color=overload_colors)
    axes[1].axhline(1.0, color="black", lw=1, ls="--")
    axes[1].set_xticks(np.arange(len(overload_values)))
    axes[1].set_xticklabels(overload_labels, fontsize=8)
    axes[1].set_ylabel("overload proxy")
    axes[1].set_title("Stabilization after capture")
    fig.savefig(out_dir / "photochemical_capture_before_buffering.png", dpi=220)
    plt.close(fig)


def main() -> None:
    capture_rows = capture_scenarios()
    overload_rows = overload_scenarios()
    summary = {
        "paper": 11,
        "model": "photochemical capture before overload stabilization",
        "corrected_chain": "capture -> couple -> retain -> close -> stabilize surplus",
        "chlorophyll_status": "late high-performance endpoint of energy-input amplification",
        "melanin_status": "mature exemplar of surplus stabilization, not an origin requirement",
        "capture_rows": capture_rows,
        "overload_rows": overload_rows,
    }
    write_outputs(summary, capture_rows, overload_rows)

    print("=" * 70)
    print("CDFD OOL Paper 11: Photochemical Capture Before Stabilization")
    print("=" * 70)
    print("Capture chain:")
    for row in capture_rows:
        print(
            f"  {row['scenario']:<30} Life Number={row['life_number']:.3f} "
            f"{row['regime']}"
        )
    print("Overload buffering:")
    for row in overload_rows:
        print(
            f"  {row['scenario']:<32} overload={row['overload_proxy']:.3f} "
            f"{row['state']}"
        )
    print("  Figure: outputs/paper_11/photochemical_capture_before_buffering.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
