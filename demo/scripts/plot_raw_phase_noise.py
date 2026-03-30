#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


PLOT_CFG = {
    "font_name": "Arial",
    "font_size": 7,
    "axes_linewidth": 0.5,
    "tick_length": 1.8,
    "tick_direction": "in",
    "dpi": 450,
    "fig_width_cm": 12,
    "fig_height_cm": 6,
    "palette": [
        "#9B2629",
        "#C1DCF3",
        "#C99D1F",
        "#4E5969",
        "#2166AC",
        "#4393C3",
        "#92C5DE",
        "#F4A582",
        "#D6604D",
        "#B2182B",
    ],
    "gridcolor": "gray",
}


def cm_to_inch(width_cm: float, height_cm: float) -> tuple[float, float]:
    return width_cm / 2.54, height_cm / 2.54


def load_phase_noise(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, comment="#")


def style_axes(ax: plt.Axes) -> None:
    for spine in ax.spines.values():
        spine.set_linewidth(PLOT_CFG["axes_linewidth"])
        spine.set_color("k")
        spine.set_visible(True)

    ax.tick_params(
        axis="both",
        which="major",
        direction=PLOT_CFG["tick_direction"],
        length=PLOT_CFG["tick_length"],
        width=PLOT_CFG["axes_linewidth"],
        colors="k",
    )
    ax.tick_params(
        axis="both",
        which="minor",
        direction=PLOT_CFG["tick_direction"],
        length=1.2,
        width=0.5,
        colors="k",
    )
    ax.grid(True, which="major", linestyle="--", linewidth=0.25, color=PLOT_CFG["gridcolor"], alpha=0.5)
    ax.grid(True, which="minor", linestyle=":", linewidth=0.2, color=PLOT_CFG["gridcolor"], alpha=0.5)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    data_dir = root / "data"
    output_dir = root / "output"
    output_dir.mkdir(parents=True, exist_ok=True)

    plt.rcParams.update(
        {
            "font.family": "sans-serif",
            "font.sans-serif": [PLOT_CFG["font_name"], "Helvetica", "DejaVu Sans"],
            "font.size": PLOT_CFG["font_size"],
            "axes.linewidth": PLOT_CFG["axes_linewidth"],
            "xtick.direction": PLOT_CFG["tick_direction"],
            "ytick.direction": PLOT_CFG["tick_direction"],
            "xtick.major.size": PLOT_CFG["tick_length"],
            "ytick.major.size": PLOT_CFG["tick_length"],
            "xtick.major.width": PLOT_CFG["axes_linewidth"],
            "ytick.major.width": PLOT_CFG["axes_linewidth"],
            "legend.frameon": False,
            "savefig.dpi": PLOT_CFG["dpi"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "lines.linewidth": 0.5,
        }
    )

    files = [
        ("RIO laser", data_dir / "riolaser_phasenoise.csv", PLOT_CFG["palette"][0]),
        ("TOPTICA laser", data_dir / "topticalaser_phasenoise.csv", PLOT_CFG["palette"][4]),
    ]

    fig, ax = plt.subplots(figsize=cm_to_inch(PLOT_CFG["fig_width_cm"], PLOT_CFG["fig_height_cm"]))

    for label, path, color in files:
        df = load_phase_noise(path)
        ax.plot(
            df["offset_Hz"],
            df["phase_noise_raw_dBc_per_Hz"],
            color=color,
            label=label,
        )

    ax.set_xscale("log")
    ax.set_xlim(1e1, 1e8)
    ax.set_xlabel("Offset frequency (Hz)")
    ax.set_ylabel("Phase noise (dBc/Hz)")
    style_axes(ax)
    ax.legend(loc="best", handlelength=2.8)

    fig.tight_layout()

    output_stem = output_dir / "raw_phase_noise"
    fig.savefig(output_stem.with_suffix(".pdf"), dpi=PLOT_CFG["dpi"])
    fig.savefig(output_stem.with_suffix(".png"), dpi=PLOT_CFG["dpi"])
    plt.close(fig)


if __name__ == "__main__":
    main()
