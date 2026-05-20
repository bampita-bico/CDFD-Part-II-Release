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

from partii_runtime import finite_summary, laplacian, output_dir


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


def simulate_spatial_gate(specificity: float, size: int = 46, steps: int = 140) -> tuple[float, np.ndarray]:
    """2D host/parasite boundary gate used as a visual stress test."""
    y, x = np.ogrid[:size, :size]
    cx = cy = size // 2
    radius = 8
    dist = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
    core = dist < radius
    boundary = (dist >= radius) & (dist <= radius + 2)

    resource = np.ones((size, size)) * 0.35
    host = np.zeros((size, size))
    parasite = np.ones((size, size)) * 0.012
    host[core] = 0.18
    parasite[core] = 0.05

    gate = np.ones((size, size))
    gate[boundary] = max(0.05, 1.0 - specificity)
    gate[core] = max(0.08, 1.0 - 0.85 * specificity)

    for step in range(steps):
        resource[0, :] = 1.0 + 0.2 * np.sin(step / 8.0)
        resource = np.clip(resource + 0.08 * laplacian(resource), 0.0, 2.0)
        host_growth = 0.045 * host * resource * core
        parasite_growth = 0.070 * parasite * resource * gate
        host_loss = 0.012 * host + 0.015 * parasite * host
        parasite_loss = 0.010 * parasite + 0.035 * specificity * boundary * parasite
        resource_use = 0.030 * host * resource + 0.045 * parasite * resource * gate
        host = np.clip(host + host_growth - host_loss + 0.015 * laplacian(host * core), 0.0, 3.0)
        parasite = np.clip(parasite + parasite_growth - parasite_loss + 0.030 * laplacian(parasite), 0.0, 3.0)
        resource = np.clip(resource - resource_use, 0.0, 2.0)

    ratio = float(np.sum(host[core]) / max(np.sum(parasite[core]), 1e-12))
    return ratio, host - parasite


def main() -> None:
    scenarios = [("open_boundary", 0.0), ("weak_specificity", 0.35), ("strong_specificity", 0.75)]
    rows: list[dict[str, object]] = []
    frames: list[pd.DataFrame] = []
    for args in scenarios:
        row, frame = run(*args)
        rows.append(row)
        frames.append(frame)
    open_spatial_ratio, open_advantage = simulate_spatial_gate(0.0)
    strong_spatial_ratio, strong_advantage = simulate_spatial_gate(0.75)
    spatial_rows = [
        {"scenario": "open_boundary_2d", "specificity": 0.0, "host_parasite_ratio": open_spatial_ratio},
        {"scenario": "strong_specificity_2d", "specificity": 0.75, "host_parasite_ratio": strong_spatial_ratio},
    ]
    data = pd.concat(frames, ignore_index=True)
    out_dir = output_dir(__file__, "paper_10")
    data.to_csv(out_dir / "host_parasite_timeseries.csv", index=False)
    pd.DataFrame(rows).to_csv(out_dir / "parasitic_threshold_summary.csv", index=False)
    pd.DataFrame(spatial_rows).to_csv(out_dir / "spatial_boundary_gate_summary.csv", index=False)
    summary = {
        "paper": 10,
        "model": "host-parasite boundary specificity toy diagnostic with 2D boundary gate",
        "rows": rows,
        "spatial_rows": spatial_rows,
        "open_spatial_advantage": finite_summary(open_advantage),
        "strong_spatial_advantage": finite_summary(strong_advantage),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, axes = plt.subplots(2, 2, figsize=(12, 8), constrained_layout=True)
    for label, frame in data.groupby("scenario"):
        axes[0, 0].plot(frame["time"], frame["host"], lw=2, label=f"host {label}")
        axes[0, 0].plot(frame["time"], frame["parasite"], lw=1.6, ls="--", label=f"parasite {label}")
    labels = [str(row["scenario"]).replace("_", "\n") for row in rows]
    ratios = [float(row["host_parasite_ratio"]) for row in rows]
    axes[0, 1].bar(range(len(ratios)), ratios, color=["#b9574f" if r < 1.0 else "#4f8f5b" for r in ratios])
    axes[0, 1].axhline(1.0, color="black", lw=1, ls="--")
    axes[0, 1].set_xticks(range(len(ratios)))
    axes[0, 1].set_xticklabels(labels, fontsize=8)
    axes[0, 0].set_title("well-mixed trajectories")
    axes[0, 0].set_xlabel("time")
    axes[0, 0].set_ylabel("abundance proxy")
    axes[0, 0].legend(frameon=False, fontsize=7)
    axes[0, 1].set_title("boundary gate")
    axes[0, 1].set_ylabel("host / parasite")
    vmax = max(float(np.max(np.abs(open_advantage))), float(np.max(np.abs(strong_advantage))), 1e-6)
    im0 = axes[1, 0].imshow(open_advantage, origin="lower", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    axes[1, 0].set_title(f"2D open boundary ratio={open_spatial_ratio:.2f}")
    axes[1, 0].set_xlabel("x")
    axes[1, 0].set_ylabel("y")
    im1 = axes[1, 1].imshow(strong_advantage, origin="lower", cmap="coolwarm", vmin=-vmax, vmax=vmax)
    axes[1, 1].set_title(f"2D gated boundary ratio={strong_spatial_ratio:.2f}")
    axes[1, 1].set_xlabel("x")
    axes[1, 1].set_ylabel("y")
    fig.colorbar(im1, ax=[axes[1, 0], axes[1, 1]], fraction=0.046, pad=0.04, label="host minus parasite")
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
