"""Shared CDFD Part II runtime helpers for paper-local diagnostics.

The helpers keep the release scripts aligned with the public CDFL convention:
Phi is drive, C is constraint/resistance, S is responsive routing, and M_s is
retained structural memory. The functions are intentionally small and
paper-local; they are not a replacement for the public CDFD Runtime package.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np


EPS = 1e-12


def output_dir(script_file: str, paper_id: str) -> Path:
    """Return and create outputs/paper_XX for a supplementary script."""
    path = Path(script_file).resolve().parent.parent / "outputs" / paper_id
    path.mkdir(parents=True, exist_ok=True)
    return path


def laplacian(z: np.ndarray) -> np.ndarray:
    """Periodic five-point Laplacian used by the 2D toy diagnostics."""
    return (
        -4.0 * z
        + np.roll(z, 1, 0)
        + np.roll(z, -1, 0)
        + np.roll(z, 1, 1)
        + np.roll(z, -1, 1)
    )


def adaptive_ratio(phi: np.ndarray, constraint: np.ndarray, S: np.ndarray | float = 1.0, M_s: np.ndarray | float = 1.0) -> np.ndarray:
    """CDFL adaptive operating ratio Psi_s = (Phi / C) S M_s."""
    safe_constraint = np.maximum(np.abs(constraint), EPS)
    return (phi / safe_constraint) * S * M_s


def life_number(
    input_energy: float,
    sigma_e: float,
    sigma_p: float,
    tau_relax: float,
    stabilization: float,
    maintenance_energy: float = 1.0,
    S: float = 1.0,
    M_s: float = 1.0,
) -> float:
    """Tri-regime Life Number used by Papers 11-12."""
    denominator = max(stabilization * maintenance_energy, EPS)
    return float((input_energy * sigma_e * sigma_p * tau_relax / denominator) * S * M_s)


def bounded_adaptive_update(
    phi: np.ndarray,
    constraint: np.ndarray,
    S: np.ndarray,
    M_s: np.ndarray,
    dt: float,
    kappa_s: float,
    memory_decay: float,
    max_state: float = 100.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Apply a bounded CDFL S/M_s update and return Phi, S, M_s.

    Explicit toy models can explode when autocatalytic terms are left
    unbounded. This update clips rates and states so failure reflects modeled
    parameter choices rather than floating-point overflow.
    """
    psi = adaptive_ratio(phi, constraint, S, M_s)
    dM_s = np.clip(phi * S - memory_decay * M_s, -max_state, max_state)
    M_s = np.clip(M_s + dt * dM_s, 0.0, max_state)
    dS = np.clip(kappa_s * (psi - S), -max_state, max_state)
    S = np.clip(S + dt * dS, 0.01, max_state)
    phi = np.clip(phi, 0.0, max_state)
    return phi, S, M_s


def finite_summary(values: np.ndarray | list[float]) -> dict[str, float | bool]:
    """Compact finite-value audit for JSON summaries."""
    arr = np.asarray(values, dtype=float)
    finite = arr[np.isfinite(arr)]
    if finite.size == 0:
        return {"all_finite": False, "min": float("nan"), "max": float("nan"), "mean": float("nan")}
    return {
        "all_finite": bool(finite.size == arr.size),
        "min": float(np.min(finite)),
        "max": float(np.max(finite)),
        "mean": float(np.mean(finite)),
    }


def regime_from_value(value: float, low: float = 1.0, high: float = 2.0) -> str:
    """Shared release labels for decay, near-critical, and sustained regimes."""
    if value < low:
        return "decay_dominated"
    if value < high:
        return "near_critical"
    return "sustained"
