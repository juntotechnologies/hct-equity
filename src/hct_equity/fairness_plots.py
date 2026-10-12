"""Figures for notebook 02. Each title carries the synthetic-data note."""

import math

import matplotlib.pyplot as plt
import pandas as pd

from hct_equity.config import Columns, FairnessPlot
from hct_equity.fairness import MODEL_LABEL

PANEL_COLUMNS = 3
REFERENCE_LABELS = {"all": "Treat all", "none": "Treat none"}


def plot_calibration(deciles: pd.DataFrame, columns: Columns, style: FairnessPlot, note: str) -> plt.Figure:
    """Predicted vs Kaplan-Meier observed risk by decile; one line per group."""
    fig, ax = plt.subplots(figsize=(7, 6))
    ax.plot([0, 1], [0, 1], color=style.reference_color, linestyle="--", linewidth=1, label="Perfect calibration")
    groups = deciles.groupby(columns.group)
    for (name, part), color, marker in zip(groups, style.group_colors, style.group_markers, strict=False):
        ax.plot(part["predicted"], part["observed"], color=color, marker=marker, markersize=6, linewidth=2, label=name)
    ax.set(xlabel="Predicted risk by horizon", ylabel="Observed risk (Kaplan-Meier)", xlim=(0, 1), ylim=(0, 1))
    ax.set_title(f"Calibration by race group (out-of-fold, risk deciles)\n{note}", fontsize=10)
    ax.grid(alpha=0.3)
    ax.legend(fontsize=8, frameon=False)
    fig.tight_layout()
    return fig


def plot_dca_panel(ax: plt.Axes, part: pd.DataFrame, style: FairnessPlot) -> None:
    colors = {MODEL_LABEL: style.model_color, "all": style.reference_color, "none": style.treat_none_color}
    widths = {MODEL_LABEL: 2.0, "all": 1.5, "none": 1.0}
    for model, curve in part.groupby("model"):
        label = REFERENCE_LABELS.get(model, model)
        ax.plot(curve["threshold"], curve["net_benefit"], color=colors[model], linewidth=widths[model], label=label)
    ax.grid(alpha=0.3)


def plot_dca_by_group(dca: pd.DataFrame, columns: Columns, style: FairnessPlot, note: str) -> plt.Figure:
    """Net benefit vs threshold probability; one panel per group, shared axes."""
    groups = dca.groupby(columns.group)
    rows = math.ceil(groups.ngroups / PANEL_COLUMNS)
    fig, axes = plt.subplots(rows, PANEL_COLUMNS, figsize=(12, 3.6 * rows), sharex=True, sharey=True, squeeze=False)
    for ax, (name, part) in zip(axes.flat, groups, strict=False):
        plot_dca_panel(ax, part, style)
        ax.set_title(name, fontsize=10)
    for ax in axes.flat[groups.ngroups :]:
        ax.set_visible(False)
    top = dca.loc[dca["model"] == "all", "net_benefit"].max()
    axes[0, 0].set_ylim(-0.05, top + 0.05)
    axes[0, 0].legend(fontsize=8, frameon=False)
    fig.supxlabel("Threshold probability")
    fig.supylabel("Net benefit")
    fig.suptitle(f"Net benefit by race group (out-of-fold Cox model)\n{note}", fontsize=11)
    fig.tight_layout()
    return fig
