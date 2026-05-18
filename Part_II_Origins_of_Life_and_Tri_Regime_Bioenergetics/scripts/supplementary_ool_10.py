"""
Supplementary Material - CDFD OOL Paper 10
Parasitic Threshold and Boundary Logic

A minimal host-parasite competition diagnostic with boundary specificity.
Outputs are written to outputs/paper_10/.
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


def rhs(boundary_specificity: float):
    def f(t: float, y: np.ndarray) -> list[float]:
        host, parasite, resource = np.maximum(y, 0.0)
        access = max(1.0 - boundary_specificity, 0.0)
        host_growth = 0.45 * host * resource / (1.0 + resource)
        parasite_growth = 0.75 * access * parasite * resource / (1.0 + resource)
        resource_replenish = 0.6 * (1.0 - resource)
        resource_use = 0.35 * host * resource + 0.55 * access * parasite * resource
        return [host_growth - 0.08 * host, parasite_growth - 0.05 * parasite, resource_replenish - resource_use]
    return f


def run(label: str, specificity: float) -> tuple[dict[str, object], pd.DataFrame]:
    sol = solve_ivp(rhs(specificity), (0.0, 60.0), [0.8, 0.05, 1.0], max_step=0.1, rtol=1e-8, atol=1e-10)
    frame = pd.DataFrame({"time": sol.t, "host": sol.y[0], "parasite": sol.y[1], "resource": sol.y[2], "scenario": label, "boundary_specificity": specificity})
    final = frame.iloc[-1]
    row = {
        "scenario": label,
        "boundary_specificity": specificity,
        "final_host": float(final["host"]),
        "final_parasite": float(final["parasite"]),
        "host_parasite_ratio": float(final["host"] / max(final["parasite"], 1e-12)),
        "state": "host_retained" if float(final["host"] > final["parasite"]) else "parasite_dominated",
    }
    return row, frame


def main() -> None:
    scenarios = [("open_boundary", 0.0), ("weak_specificity", 0.35), ("strong_specificity", 0.75)]
    rows: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []
    for args in scenarios:
        row, frame = run(*args)
        rows.append(row)
        frames.append(frame)
    data = pd.concat(frames, ignore_index=True)
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_10"
    out_dir.mkdir(parents=True, exist_ok=True)
    data.to_csv(out_dir / "host_parasite_timeseries.csv", index=False)
    pd.DataFrame(rows).to_csv(out_dir / "parasitic_threshold_summary.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps({"paper": 10, "model": "host-parasite boundary specificity toy diagnostic", "rows": rows}, indent=2) + "\n")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), constrained_layout=True)
    for label, frame in data.groupby("scenario"):
        axes[0].plot(frame["time"], frame["host"], lw=2, label=f"host {label}")
        axes[0].plot(frame["time"], frame["parasite"], lw=1.6, ls="--", label=f"parasite {label}")
    labels = [str(row["scenario"]).replace("_", "\n") for row in rows]
    ratios = [float(row["host_parasite_ratio"]) for row in rows]
    axes[1].bar(range(len(ratios)), ratios, color=["#b9574f" if r < 1.0 else "#4f8f5b" for r in ratios])
    axes[1].axhline(1.0, color="black", lw=1, ls="--")
    axes[1].set_xticks(range(len(ratios)))
    axes[1].set_xticklabels(labels, fontsize=8)
    axes[0].set_title("host-parasite trajectories")
    axes[0].set_xlabel("time")
    axes[0].set_ylabel("abundance proxy")
    axes[0].legend(frameon=False, fontsize=7)
    axes[1].set_title("boundary gate")
    axes[1].set_ylabel("host / parasite")
    fig.savefig(out_dir / "parasitic_threshold_boundary_logic.png", dpi=220)
    plt.close(fig)
    print("=" * 70)
    print("CDFD OOL Paper 10: Parasitic Threshold")
    print("=" * 70)
    for row in rows:
        print(f"  {row['scenario']:<18} ratio={row['host_parasite_ratio']:.3f} {row['state']}")
    print("  Figure: outputs/paper_10/parasitic_threshold_boundary_logic.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
