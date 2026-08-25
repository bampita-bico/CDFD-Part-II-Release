"""
Supplementary Material - CDFD OOL Paper 6
Autocatalytic Closure and Chemical Memory

SciPy integrates a minimal closure model; SymPy records the mean-field ignition
criterion. Outputs are written to outputs/paper_06/.
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


def rhs(constraint: float, substrate: float):
    k_auto = 0.05
    loss = 0.02
    saturation = 12.0
    def f(t: float, y: np.ndarray) -> list[float]:
        x = max(float(y[0]), 0.0)
        production = k_auto * substrate * x * x / (1.0 + x / saturation)
        decay = loss * x / constraint
        return [production - decay]
    return f


def run(phi0: float, constraint: float, substrate: float = 1.0) -> tuple[dict[str, object], pd.DataFrame]:
    sol = solve_ivp(rhs(constraint, substrate), (0.0, 20.0), [phi0], max_step=0.05, rtol=1e-8, atol=1e-10)
    frame = pd.DataFrame({"time": sol.t, "phi": sol.y[0], "initial_phi": phi0, "constraint": constraint})
    final_phi = float(frame["phi"].iloc[-1])
    row = {
        "initial_phi": phi0,
        "constraint": constraint,
        "substrate": substrate,
        "final_phi": final_phi,
        "closure_state": "ignition" if final_phi > 1.0 else "sub_ignition",
    }
    return row, frame


def main() -> None:
    rows: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []
    for phi0, constraint in [(0.1, 1.0), (0.5, 1.0), (0.1, 5.0), (0.5, 5.0)]:
        row, frame = run(phi0, constraint)
        rows.append(row)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    k, c_a, c, L = sp.symbols("k c_A C L", positive=True)
    gamma = sp.simplify(k * c_a * c * L**2)
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_06"
    out_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(out_dir / "closure_timeseries.csv", index=False)
    pd.DataFrame(rows).to_csv(out_dir / "closure_summary.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps({"paper": 6, "model": "autocatalytic closure scan", "gamma": str(gamma), "rows": rows}, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(10.1, 5.8), constrained_layout=True)
    for label, frame in data.groupby(["initial_phi", "constraint"]):
        axes[0].plot(frame["time"], frame["phi"], lw=2, label=f"Phi0={label[0]}, C={label[1]}")
    labels = [f"{row['initial_phi']},{row['constraint']}" for row in rows]
    values = [float(row["final_phi"]) for row in rows]
    axes[1].bar(range(len(values)), values, color="#4c78a8")
    axes[1].axhline(1.0, color="black", lw=1, ls="--")
    axes[1].set_xticks(range(len(values)))
    axes[1].set_xticklabels(labels)
    axes[0].set_title("closure trajectories")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("Phi proxy")
    axes[0].legend(frameon=False, fontsize=8)
    axes[1].set_title("final closure state")
    axes[1].set_ylabel("final Phi")
    fig.savefig(out_dir / "autocatalytic_closure_scan.png", dpi=220)
    plt.close(fig)
    print("=" * 70)
    print("CDFD OOL Paper 6: Autocatalytic Closure")
    print("=" * 70)
    for row in rows:
        print(f"  Phi0={row['initial_phi']:.1f} C={row['constraint']:.1f} final={row['final_phi']:.3f} {row['closure_state']}")
    print("  Figure: outputs/paper_06/autocatalytic_closure_scan.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
