"""
Supplementary Material - CDFD OOL Paper 5
Oscillating Constraints and the Polymerization Ratchet

This full-stack diagnostic uses SciPy for cycle integration, Pandas for output
frames, and SymPy for the ratchet threshold expression. It is a toy model, not
a historical reconstruction.

Outputs are written to outputs/paper_05/.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

os.environ.setdefault("MPLCONFIGDIR", "/tmp/cdfd_matplotlib")
os.environ.setdefault("XDG_CACHE_HOME", "/tmp/cdfd_cache")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sympy as sp
from scipy.integrate import solve_ivp

from partii_runtime import finite_summary, output_dir


def water_activity(t: float, period: float) -> float:
    return 0.5 + 0.5 * np.cos(2.0 * np.pi * t / period)


def rhs(period: float, activation: float, retention: float, hydrolysis: float):
    def f(t: float, y: np.ndarray) -> list[float]:
        monomer, product, memory = y
        wet = water_activity(t, period)
        dry = 1.0 - wet
        concentration_gain = 1.0 + 4.0 * dry
        condensation = activation * concentration_gain * monomer**2
        loss = hydrolysis * wet * product
        d_monomer = -2.0 * condensation + 0.15 * wet * (1.0 - monomer)
        d_product = condensation - loss
        d_memory = retention * product - 0.12 * wet * memory
        return [d_monomer, d_product, d_memory]
    return f


def run_scenario(label: str, period: float, activation: float, retention: float, hydrolysis: float) -> tuple[dict[str, object], pd.DataFrame]:
    t_end = 12.0 * period
    sol = solve_ivp(rhs(period, activation, retention, hydrolysis), (0.0, t_end), [1.0, 0.01, 0.01], max_step=period / 40.0, rtol=1e-7, atol=1e-9)
    frame = pd.DataFrame({
        "time": sol.t,
        "monomer": sol.y[0],
        "product": sol.y[1],
        "memory": sol.y[2],
        "water_activity": [water_activity(t, period) for t in sol.t],
        "scenario": label,
    })
    final = frame.iloc[-1]
    row = {
        "scenario": label,
        "period": period,
        "activation": activation,
        "retention": retention,
        "hydrolysis": hydrolysis,
        "final_product": float(final["product"]),
        "final_memory": float(final["memory"]),
        "ratchet_state": "retained" if float(final["memory"]) > 1.0 else "weak_or_lost",
    }
    return row, frame


def threshold_expression() -> str:
    k_a, c, r, h, w = sp.symbols("k_a c r h w", positive=True)
    retained = sp.simplify((k_a * c**2 * r) / (h * w))
    return str(retained)


def ratchet_response_surface() -> tuple[pd.DataFrame, np.ndarray, np.ndarray, np.ndarray]:
    """Fast 2D scan over cycle period and hydrolysis pressure."""
    periods = np.linspace(1.5, 12.0, 32)
    hydrolysis_values = np.linspace(0.08, 0.75, 32)
    memory_grid = np.zeros((len(periods), len(hydrolysis_values)))
    rows: list[dict[str, float | str]] = []
    for i, period in enumerate(periods):
        for j, hydrolysis in enumerate(hydrolysis_values):
            monomer = 1.0
            product = 0.01
            memory = 0.01
            dt = period / 30.0
            for step in range(12 * 30):
                t = step * dt
                wet = water_activity(t, period)
                dry = 1.0 - wet
                concentration = 1.0 + 3.8 * dry
                condensation = 0.16 * concentration * monomer**2
                loss = hydrolysis * wet * product
                monomer = max(monomer + dt * (-2.0 * condensation + 0.12 * wet * (1.0 - monomer)), 0.0)
                product = max(product + dt * (condensation - loss), 0.0)
                memory = max(memory + dt * (0.55 * product - 0.10 * wet * memory), 0.0)
            memory_grid[i, j] = memory
            rows.append(
                {
                    "period": float(period),
                    "hydrolysis": float(hydrolysis),
                    "final_memory": float(memory),
                    "ratchet_state": "retained" if memory > 1.0 else "weak_or_lost",
                }
            )
    return pd.DataFrame(rows), periods, hydrolysis_values, memory_grid


def main() -> None:
    scenarios = [
        ("steady_wet", 8.0, 0.08, 0.25, 0.30),
        ("fast_cycle", 2.0, 0.12, 0.45, 0.22),
        ("slow_wet_dry", 8.0, 0.18, 0.70, 0.20),
        ("overheated_loss", 8.0, 0.20, 0.25, 0.65),
    ]
    rows: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []
    for args in scenarios:
        row, frame = run_scenario(*args)
        rows.append(row)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    surface_frame, periods, hydrolysis_values, memory_grid = ratchet_response_surface()
    out_dir = output_dir(__file__, "paper_05")
    data.to_csv(out_dir / "wet_dry_timeseries.csv", index=False)
    pd.DataFrame(rows).to_csv(out_dir / "ratchet_summary.csv", index=False)
    surface_frame.to_csv(out_dir / "ratchet_response_surface.csv", index=False)
    summary = {
        "paper": 5,
        "model": "wet-dry polymerization ratchet toy diagnostic",
        "threshold_proxy": threshold_expression(),
        "rows": rows,
        "response_surface": finite_summary(memory_grid),
        "interpretation": "A ratchet requires activation, concentration, retention, and survival across rehydration, not dryness alone.",
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")

    fig, axes = plt.subplots(1, 4, figsize=(16.6, 7.7), constrained_layout=True)
    for label, frame in data.groupby("scenario"):
        axes[0].plot(frame["time"], frame["product"], label=label, lw=2)
        axes[1].plot(frame["time"], frame["memory"], label=label, lw=2)
    axes[0].set_title("polymer product")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("product proxy")
    axes[1].set_title("retained memory")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("memory proxy")
    labels = [str(row["scenario"]).replace("_", "\n") for row in rows]
    values = [float(row["final_memory"]) for row in rows]
    colors = ["#4f8f5b" if value > 1.0 else "#b9574f" for value in values]
    axes[2].bar(range(len(values)), values, color=colors)
    axes[2].axhline(1.0, color="black", lw=1, ls="--")
    axes[2].set_xticks(range(len(values)))
    axes[2].set_xticklabels(labels, fontsize=8)
    axes[2].set_title("ratchet gate")
    axes[2].set_ylabel("final memory")
    axes[0].legend(frameon=False, fontsize=8)
    im = axes[3].imshow(
        memory_grid.T,
        origin="lower",
        aspect="auto",
        extent=[periods.min(), periods.max(), hydrolysis_values.min(), hydrolysis_values.max()],
        cmap="viridis",
    )
    axes[3].contour(periods, hydrolysis_values, memory_grid.T, levels=[1.0], colors="white", linewidths=1.4)
    axes[3].set_title("2D ratchet window")
    axes[3].set_xlabel("cycle period")
    axes[3].set_ylabel("hydrolysis pressure")
    fig.colorbar(im, ax=axes[3], fraction=0.046, pad=0.04, label="final memory")
    fig.savefig(out_dir / "wet_dry_polymerization_ratchet.png", dpi=220)
    plt.close(fig)

    print("=" * 70)
    print("CDFD OOL Paper 5: Oscillating Polymerization Ratchet")
    print("=" * 70)
    for row in rows:
        print(f"  {row['scenario']:<16} product={row['final_product']:.3f} memory={row['final_memory']:.3f} {row['ratchet_state']}")
    print("  Figure: outputs/paper_05/wet_dry_polymerization_ratchet.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
