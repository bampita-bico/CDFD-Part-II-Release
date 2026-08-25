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


def source_mix_diagnostic() -> pd.DataFrame:
    scenarios = [
        ("terrestrial_synthesis", 1.0, 0.0, 0.60, 0.70, 0.40, "local synthesis with moderate retention"),
        ("meteoritic_pulse_unretained", 0.2, 1.4, 0.20, 0.35, 0.80, "exogenous pulse without localization"),
        ("meteoritic_seed_retained", 0.5, 0.8, 0.75, 0.65, 0.50, "delivered organics retained in a boundary"),
        ("mixed_source_surface_trap", 0.8, 0.5, 0.85, 0.80, 0.45, "local plus exogenous feedstock trapped at a surface"),
        ("high_feedstock_overload", 0.7, 1.5, 0.70, 0.70, 1.80, "feedstock enrichment with damaging overload"),
    ]
    rows = []
    for label, terrestrial, exogenous, retention, coupling, damage, note in scenarios:
        raw_pool = terrestrial + exogenous
        retained_pool = retention * raw_pool
        functional_score = retained_pool * coupling / (1.0 + damage)
        rows.append(
            {
                "scenario": label,
                "terrestrial_feedstock": terrestrial,
                "exogenous_feedstock": exogenous,
                "raw_pool": raw_pool,
                "retention_factor": retention,
                "retained_pool": retained_pool,
                "coupling_factor": coupling,
                "damage_load": damage,
                "functional_score": functional_score,
                "interpretation": note,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    pattern = aromatic_stabilization(5.0)
    chiral = chirality_breaking()
    source_mix = source_mix_diagnostic()
    out_dir = Path(__file__).resolve().parent.parent / "outputs" / "paper_07"
    out_dir.mkdir(parents=True, exist_ok=True)
    pattern.to_csv(out_dir / "aromatic_stability_timeseries.csv", index=False)
    chiral.to_csv(out_dir / "chirality_timeseries.csv", index=False)
    source_mix.to_csv(out_dir / "aromatic_source_mix.csv", index=False)
    best_source_row = source_mix.loc[source_mix["functional_score"].idxmax()]
    summary_rows = [
        {"metric": "final_aliphatic_pattern", "value": float(pattern["aliphatic"].iloc[-1])},
        {"metric": "final_aromatic_pattern", "value": float(pattern["aromatic"].iloc[-1])},
        {"metric": "initial_left", "value": float(chiral["left"].iloc[0])},
        {"metric": "initial_right", "value": float(chiral["right"].iloc[0])},
        {"metric": "final_left", "value": float(chiral["left"].iloc[-1])},
        {"metric": "final_right", "value": float(chiral["right"].iloc[-1])},
        {"metric": "best_source_mix_score", "value": float(best_source_row["functional_score"])},
    ]
    pd.DataFrame(summary_rows).to_csv(out_dir / "aromatic_chirality_summary.csv", index=False)
    summary = {
        "paper": 7,
        "model": "aromatic stability, chiral amplification, and aromatic source-mix diagnostic",
        "provenance_guardrail": "source supply is upstream of retention and coupling; exogenous delivery is not itself a Life Number gate",
        "best_source_mix": best_source_row.to_dict(),
        "summary_rows": summary_rows,
        "source_mix_rows": source_mix.to_dict(orient="records"),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    fig, axes = plt.subplots(1, 3, figsize=(14.3, 6.6), constrained_layout=True)
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
    labels = [label.replace("_", "\n") for label in source_mix["scenario"]]
    scores = source_mix["functional_score"].to_numpy()
    colors = ["#4f8f5b" if score == scores.max() else "#7a9cc6" for score in scores]
    axes[2].bar(np.arange(len(scores)), scores, color=colors)
    axes[2].set_xticks(np.arange(len(scores)))
    axes[2].set_xticklabels(labels, fontsize=7)
    axes[2].set_title("aromatic source mix")
    axes[2].set_ylabel("retained functional score")
    fig.savefig(out_dir / "aromatic_chirality_stability.png", dpi=220)
    plt.close(fig)
    print("=" * 70)
    print("CDFD OOL Paper 7: Aromatic Stabilization and Homochirality")
    print("=" * 70)
    for row in summary_rows:
        print(f"  {row['metric']:<28} {row['value']:.3f}")
    print(f"  {'best_source_mix':<28} {best_source_row['scenario']}")
    print("  Figure: outputs/paper_07/aromatic_chirality_stability.png")
    print("=" * 70)


if __name__ == "__main__":
    main()
