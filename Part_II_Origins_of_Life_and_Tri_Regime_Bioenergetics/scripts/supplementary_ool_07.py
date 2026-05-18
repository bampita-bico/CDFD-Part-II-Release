"""
Supplementary Material - CDFD OOL Paper 7
Aromatic Stabilization, Chemical Alphabets, and Homochirality

Outputs are written to outputs/paper_07/.
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
from scipy.integrate import solve_ivp


def aromatic_stabilization(flux_energy: float, steps: int = 200, dt: float = 0.05) -> pd.DataFrame:
    c_aliphatic = 1.0
    c_aromatic = 10.0
    pattern_aliphatic = 1.0
    pattern_aromatic = 1.0
    rows = []
    for step in range(steps):
        deg_aliphatic = max(flux_energy - c_aliphatic, 0.0) * 0.1
        deg_aromatic = max(flux_energy - c_aromatic, 0.0) * 0.1
        pattern_aliphatic = max(pattern_aliphatic - dt * deg_aliphatic * pattern_aliphatic, 0.0)
        pattern_aromatic = max(pattern_aromatic - dt * deg_aromatic * pattern_aromatic, 0.0)
        rows.append({"step": step, "aliphatic": pattern_aliphatic, "aromatic": pattern_aromatic})
    return pd.DataFrame(rows)


def chirality_rhs(t: float, y: np.ndarray) -> list[float]:
    left, right = y
    amplification = 0.35
    cross_inhibition = 0.06
    feed = 0.01
    carrying = max(1.0 - (left + right) / 24.0, 0.0)
    d_left = feed + carrying * amplification * left * left / (1.0 + left + right) - cross_inhibition * left * right
    d_right = feed + carrying * 0.96 * amplification * right * right / (1.0 + left + right) - cross_inhibition * left * right
    return [d_left, d_right]


def chirality_breaking() -> pd.DataFrame:
    sol = solve_ivp(chirality_rhs, (0.0, 40.0), [1.011, 0.989], max_step=0.1, rtol=1e-8, atol=1e-10)
    return pd.DataFrame({"time": sol.t, "left": sol.y[0], "right": sol.y[1]})


def main() -> None:
    pattern = aromatic_stabilization(5.0)
    chiral = chirality_breaking()
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_07"
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern.to_csv(out_dir / "aromatic_stability_timeseries.csv", index=False)
    chiral.to_csv(out_dir / "chirality_timeseries.csv", index=False)
    summary_rows = [
        {"metric": "final_aliphatic_pattern", "value": float(pattern["aliphatic"].iloc[-1])},
        {"metric": "final_aromatic_pattern", "value": float(pattern["aromatic"].iloc[-1])},
        {"metric": "initial_left", "value": float(chiral["left"].iloc[0])},
        {"metric": "initial_right", "value": float(chiral["right"].iloc[0])},
        {"metric": "final_left", "value": float(chiral["left"].iloc[-1])},
        {"metric": "final_right", "value": float(chiral["right"].iloc[-1])},
    ]
    pd.DataFrame(summary_rows).to_csv(out_dir / "aromatic_chirality_summary.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps({"paper": 7, "model": "aromatic stability and chiral amplification toy diagnostic", "summary_rows": summary_rows}, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    axes[0].plot(pattern["step"], pattern["aliphatic"], label="aliphatic", lw=2)
    axes[0].plot(pattern["step"], pattern["aromatic"], label="aromatic", lw=2)
    axes[0].set_title("pattern persistence")
    axes[0].set_xlabel("step")
    axes[0].set_ylabel("remaining pattern")
    axes[0].legend(frameon=False)
    axes[1].plot(chiral["time"], chiral["left"], label="left-like", lw=2)
    axes[1].plot(chiral["time"], chiral["right"], label="right-like", lw=2)
    axes[1].set_title("chiral amplification")
    axes[1].set_xlabel("time")
    axes[1].set_ylabel("abundance proxy")
    axes[1].legend(frameon=False)
    fig.savefig(out_dir / "aromatic_chirality_stability.png", dpi=220)
    plt.close(fig)
    print("=" * 70)
    print("CDFD OOL Paper 7: Aromatic Stabilization and Homochirality")
    print("=" * 70)
    for row in summary_rows:
        print(f"  {row['metric']:<28} {row['value']:.3f}")
    print("  Figure: outputs/paper_07/aromatic_chirality_stability.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
