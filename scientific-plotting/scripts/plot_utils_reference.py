#!/usr/bin/env python3
"""
Reference plotting utilities for publication-quality figures.

Adapted from an internal lab plotting utility and generalized for this skill.

This version keeps the importable helper functions and adds a CLI for common
single-panel plotting tasks from CSV/TSV tables.

Examples:
    python plot_utils_reference.py xy data.csv --x-col time --y-col signal \
        --xlabel "Time (s)" --ylabel "Signal (a.u.)" \
        --output-stem figures/signal --formats pdf,png

    python plot_utils_reference.py transmission spectrum.csv \
        --output-stem figures/transmission
"""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

try:
    import matplotlib.pyplot as plt
except Exception:
    plt = None

try:
    import pandas as pd
except Exception:
    pd = None

try:
    from cycler import cycler
except Exception:
    cycler = None

# Default plotting configuration, can be overridden by the user.
PLOT_CFG: Dict[str, object] = {
    "font_name": "Arial",
    "font_size": 7,
    "font_weight": "normal",
    "axes_linewidth": 0.5,
    "tick_length": 1.8,
    "tick_direction": "in",
    "marker_size": 10,
    "marker_edgecolor": "k",
    "marker_edgewidth": 0.15,
    "dpi": 450,
    "fig_width_cm": 12,
    "fig_height_cm": 6,
    "axes_rect": (0.15, 0.18, 0.82, 0.78),
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
    "linestyle": "-",
    "linewidth": 0.5,
    "grid": None,
    "gridlinestyle": "--",
    "gridlinewidth": 0.25,
    "gridcolor": "gray",
    "gridalpha": 0.5,
    "log_minor_subs": tuple(range(2, 10)),
    "log_minor_tick_length": 1.2,
    "log_minor_tick_width": 0.5,
    "log_minor_tick_color": "k",
    "log_minor_gridlinestyle": ":",
    "log_minor_gridlinewidth": 0.2,
    "log_minor_gridalpha": 0.5,
    "legend": False,
    "figure_facecolor": "none",
    "axes_facecolor": "none",
    "save_transparent": False,
    "bbox_inches": None,
    "pad_inches": 0.0,
    "pdf_fonttype": 42,
    "ps_fonttype": 42,
}


def require_runtime_dependencies() -> None:
    missing: List[str] = []
    if plt is None:
        missing.append("matplotlib")
    if pd is None:
        missing.append("pandas")
    if missing:
        joined = ", ".join(missing)
        raise SystemExit(
            f"Missing runtime dependencies: {joined}. "
            f"Install them before using this plotting script."
        )


def resolve_plot_cfg(overrides: Optional[dict] = None) -> Dict[str, object]:
    """Return a merged plot config without mutating the defaults."""
    cfg = dict(PLOT_CFG)
    if overrides:
        cfg.update(overrides)
    return cfg


def _cm2inch(w_cm: float, h_cm: float) -> Tuple[float, float]:
    """Convert centimeters to inches for figure sizing."""
    return w_cm / 2.54, h_cm / 2.54


def _apply_plot_style(cfg: dict) -> None:
    """Apply a consistent MATLAB-like style to matplotlib defaults."""
    require_runtime_dependencies()
    preferred_fonts: List[str] = []
    preferred_name = str(cfg.get("font_name", "Arial")).strip()
    if preferred_name:
        preferred_fonts.append(preferred_name)
    for fallback in ("Arial", "Helvetica", "DejaVu Sans"):
        if fallback not in preferred_fonts:
            preferred_fonts.append(fallback)
    params = {
        "font.family": "sans-serif",
        "font.sans-serif": preferred_fonts,
        "font.size": cfg["font_size"],
        "font.weight": cfg.get("font_weight", "normal"),
        "axes.linewidth": cfg["axes_linewidth"],
        "axes.edgecolor": "k",
        "axes.labelcolor": "k",
        "xtick.color": "k",
        "ytick.color": "k",
        "xtick.direction": cfg.get("tick_direction", "in"),
        "ytick.direction": cfg.get("tick_direction", "in"),
        "xtick.major.size": cfg["tick_length"],
        "ytick.major.size": cfg["tick_length"],
        "xtick.major.width": cfg["axes_linewidth"],
        "ytick.major.width": cfg["axes_linewidth"],
        "legend.frameon": False,
        "figure.facecolor": cfg.get("figure_facecolor", "none"),
        "axes.facecolor": cfg.get("axes_facecolor", "none"),
        "savefig.transparent": cfg.get("save_transparent", False),
        "axes.titlesize": cfg["font_size"],
        "axes.labelsize": cfg["font_size"],
        "xtick.labelsize": cfg["font_size"],
        "ytick.labelsize": cfg["font_size"],
        "legend.fontsize": cfg["font_size"],
        "savefig.dpi": cfg.get("dpi", 450),
        "pdf.fonttype": cfg.get("pdf_fonttype", 42),
        "ps.fonttype": cfg.get("ps_fonttype", 42),
        "lines.linewidth": cfg.get("linewidth", 0.5),
    }
    if "figure.constrained_layout.use" in plt.rcParams:
        params["figure.constrained_layout.use"] = False
    palette = cfg.get("palette")
    if cycler is not None and isinstance(palette, (list, tuple)) and palette:
        params["axes.prop_cycle"] = cycler(color=list(palette))
    plt.rcParams.update(params)


def _style_spines(ax: plt.Axes, cfg: dict) -> None:
    if not hasattr(ax, "spines"):
        return
    for spine in ax.spines.values():
        spine.set_linewidth(cfg["axes_linewidth"])
        spine.set_color("k")
        spine.set_visible(True)


def _style_log_ticks_and_grid(ax: plt.Axes, cfg: dict, *, grid: bool) -> None:
    from matplotlib.ticker import LogLocator, NullFormatter

    minor_subs = tuple(cfg.get("log_minor_subs", tuple(range(2, 10))))
    minor_color = cfg.get("log_minor_tick_color", "k")
    has_log_axis = False

    for axis_name, axis_obj, scale in (
        ("x", ax.xaxis, ax.get_xscale()),
        ("y", ax.yaxis, ax.get_yscale()),
    ):
        if scale != "log":
            continue
        has_log_axis = True
        axis_obj.set_minor_locator(LogLocator(base=10.0, subs=minor_subs))
        axis_obj.set_minor_formatter(NullFormatter())
        ax.tick_params(
            axis=axis_name,
            which="minor",
            direction=cfg.get("tick_direction", "in"),
            length=cfg.get("log_minor_tick_length", 1.2),
            width=cfg.get("log_minor_tick_width", 0.5),
            colors=minor_color,
        )
        if grid:
            ax.grid(
                True,
                axis=axis_name,
                which="minor",
                linestyle=cfg.get("log_minor_gridlinestyle", ":"),
                linewidth=cfg.get("log_minor_gridlinewidth", 0.2),
                color=cfg.get("gridcolor", "gray"),
                alpha=cfg.get("log_minor_gridalpha", 0.5),
            )
        else:
            ax.grid(False, axis=axis_name, which="minor")

    if not has_log_axis:
        return


def _has_log_axis(ax: plt.Axes) -> bool:
    return ax.get_xscale() == "log" or ax.get_yscale() == "log"


def style_axes(
    ax: plt.Axes,
    cfg: dict,
    *,
    grid: Optional[bool] = None,
    legend: Optional[bool] = None,
    title: Optional[str] = None,
) -> None:
    """Apply axis styling without changing limits or data."""
    require_runtime_dependencies()
    ax.minorticks_off()
    ax.tick_params(
        direction=cfg.get("tick_direction", "in"),
        length=cfg["tick_length"],
        width=cfg["axes_linewidth"],
        colors="k",
    )
    if hasattr(ax, "zaxis"):
        ax.zaxis.set_tick_params(
            direction=cfg.get("tick_direction", "in"),
            length=cfg["tick_length"],
            width=cfg["axes_linewidth"],
            colors="k",
        )
    _style_spines(ax, cfg)

    if grid is None:
        configured_grid = cfg.get("grid", None)
        if configured_grid is None:
            grid = _has_log_axis(ax)
        else:
            grid = bool(configured_grid)
    else:
        grid = bool(grid)
    if grid:
        ax.grid(
            True,
            which="major",
            linestyle=cfg["gridlinestyle"],
            linewidth=cfg["gridlinewidth"],
            color=cfg.get("gridcolor", "gray"),
            alpha=cfg.get("gridalpha", 0.5),
        )
    else:
        ax.grid(False, which="both")

    _style_log_ticks_and_grid(ax, cfg, grid=grid)

    if title is not None:
        ax.set_title(title)

    if legend is None:
        legend = bool(cfg.get("legend", False))
    if legend:
        handles, labels = ax.get_legend_handles_labels()
        if handles:
            ax.legend()
    else:
        leg = ax.get_legend()
        if leg is not None:
            leg.remove()


def create_figure(
    plot_config: Optional[dict] = None,
    *,
    size_cm: Optional[Tuple[float, float]] = None,
    axes_rect: Optional[Tuple[float, float, float, float]] = None,
    projection: Optional[str] = None,
) -> Tuple[plt.Figure, plt.Axes, Dict[str, object]]:
    """
    Create a figure with a fixed axes rectangle to keep output size consistent.
    """
    require_runtime_dependencies()
    cfg = resolve_plot_cfg(plot_config)
    _apply_plot_style(cfg)

    width_cm, height_cm = size_cm or (cfg["fig_width_cm"], cfg["fig_height_cm"])
    fig = plt.figure(figsize=_cm2inch(width_cm, height_cm), dpi=cfg.get("dpi", 450))
    fig.patch.set_facecolor(cfg.get("figure_facecolor", "none"))
    if cfg.get("figure_facecolor", "none") == "none":
        fig.patch.set_alpha(0)

    rect = axes_rect or cfg["axes_rect"]
    if projection:
        ax = fig.add_axes(rect, projection=projection)
    else:
        ax = fig.add_axes(rect)
    ax.set_facecolor(cfg.get("axes_facecolor", "none"))
    style_axes(ax, cfg, grid=cfg.get("grid"), legend=cfg.get("legend", False))
    return fig, ax, cfg


def add_axes(
    fig: plt.Figure,
    cfg: dict,
    rect: Optional[Tuple[float, float, float, float]] = None,
    *,
    projection: Optional[str] = None,
) -> plt.Axes:
    """Add a new axes with the same base style."""
    require_runtime_dependencies()
    rect = rect or cfg["axes_rect"]
    if projection:
        ax = fig.add_axes(rect, projection=projection)
    else:
        ax = fig.add_axes(rect)
    ax.set_facecolor(cfg.get("axes_facecolor", "none"))
    style_axes(ax, cfg, grid=cfg.get("grid"), legend=cfg.get("legend", False))
    return ax


def add_axes_grid(
    fig: plt.Figure,
    cfg: dict,
    rects: Sequence[Tuple[float, float, float, float]],
    *,
    projection: Optional[str] = None,
) -> List[plt.Axes]:
    """Create multiple axes with fixed rectangles for multi-panel layouts."""
    require_runtime_dependencies()
    axes: List[plt.Axes] = []
    for rect in rects:
        axes.append(add_axes(fig, cfg, rect, projection=projection))
    return axes


def style_colorbar(cbar: plt.colorbar.Colorbar, cfg: dict, *, label: Optional[str] = None) -> None:
    """Match colorbar styling to the main axes."""
    cbar.outline.set_linewidth(cfg["axes_linewidth"])
    cbar.ax.tick_params(
        direction=cfg.get("tick_direction", "in"),
        length=cfg["tick_length"],
        width=cfg["axes_linewidth"],
        colors="k",
    )
    if label is not None:
        cbar.set_label(label)


def add_colorbar(
    fig: plt.Figure,
    ax: plt.Axes,
    mappable,
    cfg: dict,
    *,
    label: Optional[str] = None,
    **kwargs,
) -> plt.colorbar.Colorbar:
    """Add a colorbar and apply consistent styling."""
    require_runtime_dependencies()
    cbar = fig.colorbar(mappable, ax=ax, **kwargs)
    style_colorbar(cbar, cfg, label=label)
    return cbar


def save_figure(
    fig: plt.Figure,
    path: Path,
    cfg: dict,
    *,
    dpi: Optional[int] = None,
    transparent: Optional[bool] = None,
    bbox_inches=None,
    pad_inches: Optional[float] = None,
) -> None:
    """Save figures with a fixed canvas size unless explicitly overridden."""
    if dpi is None:
        dpi = int(cfg.get("dpi", 450))
    if transparent is None:
        transparent = bool(cfg.get("save_transparent", False))
    if bbox_inches is None:
        bbox_inches = cfg.get("bbox_inches", None)
    if pad_inches is None:
        pad_inches = float(cfg.get("pad_inches", 0.0))
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(
        path,
        dpi=dpi,
        bbox_inches=bbox_inches,
        pad_inches=pad_inches,
        transparent=transparent,
    )


def save_figure_variants(
    fig: plt.Figure,
    output_stem: Path,
    cfg: dict,
    formats: Sequence[str],
) -> List[Path]:
    saved_paths: List[Path] = []
    for fmt in formats:
        path = output_stem.with_suffix(f".{fmt}")
        save_figure(fig, path, cfg)
        saved_paths.append(path)
    return saved_paths


def normalize_formats(formats: Sequence[str]) -> List[str]:
    normalized = [fmt.strip().lower() for fmt in formats if fmt and fmt.strip()]
    if not normalized:
        raise SystemExit("Pass at least one output format.")
    return normalized


def plot_transmission_spectrum(
    data: pd.DataFrame,
    save_path: Path,
    basename: str,
    title: Optional[str] = None,
    xscale: str = "linear",
    yscale: str = "linear",
    plot_config: dict | None = None,
    formats: Optional[Sequence[str]] = None,
    save_png: Optional[bool] = None,
    save_eps: Optional[bool] = None,
    save_pdf: Optional[bool] = None,
) -> List[Path]:
    """
    Generate and save a styled plot for transmission spectrum data.

    Defaults to `pdf` and `png` output. Legacy `save_png` / `save_eps` flags
    are still accepted for backward compatibility.
    """
    if formats is None:
        legacy_flags_specified = any(flag is not None for flag in (save_pdf, save_png, save_eps))
        if legacy_flags_specified:
            formats = []
            if save_pdf:
                formats.append("pdf")
            if save_png:
                formats.append("png")
            if save_eps:
                formats.append("eps")
        else:
            formats = ["pdf", "png"]

    normalized_formats = normalize_formats(formats)

    fig, ax, cfg = create_figure(plot_config)
    ax.plot(
        data["Wavelength"] * 1e9,
        data["Voltage"],
        linestyle=cfg["linestyle"],
        linewidth=cfg["linewidth"],
        color=cfg["palette"][0],
        label="Transmission",
    )
    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    if xscale == "linear":
        ax.ticklabel_format(style="plain", axis="x")
    ax.set_xlabel("Wavelength (nm)")
    ax.set_ylabel("Voltage (V)")
    style_axes(ax, cfg, grid=cfg.get("grid"), legend=cfg.get("legend", False), title=title)

    save_path.mkdir(parents=True, exist_ok=True)
    saved_paths = save_figure_variants(fig, save_path / basename, cfg, normalized_formats)

    plt.close(fig)
    logging.info("Saved plot '%s' to %s", basename, save_path.resolve())
    return saved_paths


def load_table(path: Path) -> pd.DataFrame:
    require_runtime_dependencies()
    return pd.read_csv(path, sep=None, engine="python", comment="#")


def normalize_output_stem(path_like: str) -> Path:
    path = Path(path_like)
    if path.suffix:
        return path.with_suffix("")
    return path


def parse_tuple_floats(raw: Optional[str], expected_len: int, label: str) -> Optional[Tuple[float, ...]]:
    if raw is None:
        return None
    parts = [item.strip() for item in raw.split(",") if item.strip()]
    if len(parts) != expected_len:
        raise SystemExit(f"{label} must have exactly {expected_len} comma-separated values.")
    try:
        return tuple(float(item) for item in parts)
    except ValueError as exc:
        raise SystemExit(f"{label} must contain numeric values only.") from exc


def load_config_overrides(config_path: Optional[str]) -> dict:
    if not config_path:
        return {}
    path = Path(config_path)
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON config file: {path}") from exc
    if not isinstance(content, dict):
        raise SystemExit("Config file must contain a JSON object at the top level.")
    return content


def format_default_axis_label(raw: str) -> str:
    text = " ".join(raw.strip().replace("_", " ").split())
    if not text:
        return text
    for idx, char in enumerate(text):
        if char.isalpha():
            return f"{text[:idx]}{char.upper()}{text[idx + 1:]}"
    return text


def apply_cli_overrides(args: argparse.Namespace) -> dict:
    overrides = load_config_overrides(getattr(args, "config", None))
    if getattr(args, "font_name", None):
        overrides["font_name"] = args.font_name
    if getattr(args, "font_size", None) is not None:
        overrides["font_size"] = args.font_size
    if getattr(args, "linewidth", None) is not None:
        overrides["linewidth"] = args.linewidth
    if getattr(args, "grid", False):
        overrides["grid"] = True
    if getattr(args, "legend", False):
        overrides["legend"] = True
    if getattr(args, "transparent", False):
        overrides["save_transparent"] = True
    return overrides


def plot_xy_table(
    data: pd.DataFrame,
    *,
    x_col: str,
    y_col: str,
    output_stem: Path,
    kind: str = "line",
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    title: Optional[str] = None,
    label: Optional[str] = None,
    xscale: str = "linear",
    yscale: str = "linear",
    plot_config: Optional[dict] = None,
    size_cm: Optional[Tuple[float, float]] = None,
    axes_rect: Optional[Tuple[float, float, float, float]] = None,
    formats: Sequence[str] = ("pdf", "png"),
) -> List[Path]:
    if x_col not in data.columns:
        raise SystemExit(f"Column not found: {x_col}")
    if y_col not in data.columns:
        raise SystemExit(f"Column not found: {y_col}")

    fig, ax, cfg = create_figure(plot_config, size_cm=size_cm, axes_rect=axes_rect)
    x = data[x_col]
    y = data[y_col]

    if kind == "line":
        ax.plot(x, y, linestyle=cfg["linestyle"], linewidth=cfg["linewidth"], label=label)
    elif kind == "scatter":
        ax.scatter(
            x,
            y,
            s=cfg.get("marker_size", 10),
            edgecolors=cfg.get("marker_edgecolor", "k"),
            linewidths=cfg.get("marker_edgewidth", 0.15),
            color=cfg["palette"][0],
            label=label,
        )
    elif kind == "bar":
        ax.bar(x, y, color=cfg["palette"][0], label=label)
    else:
        raise SystemExit(f"Unsupported plot kind: {kind}")

    ax.set_xscale(xscale)
    ax.set_yscale(yscale)
    ax.set_xlabel(xlabel if xlabel is not None else format_default_axis_label(x_col))
    ax.set_ylabel(ylabel if ylabel is not None else format_default_axis_label(y_col))
    style_axes(
        ax,
        cfg,
        grid=cfg.get("grid"),
        legend=bool(label) or cfg.get("legend", False),
        title=title,
    )
    saved_paths = save_figure_variants(fig, output_stem, cfg, formats)
    plt.close(fig)
    return saved_paths


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Reference scientific plotting utilities with a CLI.",
    )
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--config", help="Optional JSON file with plot config overrides")
    common.add_argument("--font-name", help="Override font family")
    common.add_argument("--font-size", type=float, help="Override font size")
    common.add_argument("--linewidth", type=float, help="Override line width")
    common.add_argument("--grid", action="store_true", help="Enable grid")
    common.add_argument("--legend", action="store_true", help="Enable legend")
    common.add_argument("--transparent", action="store_true", help="Save with transparent background")
    common.add_argument(
        "--size-cm",
        help="Figure size as width_cm,height_cm",
    )
    common.add_argument(
        "--axes-rect",
        help="Axes rectangle as left,bottom,width,height in figure fractions",
    )
    common.add_argument(
        "--formats",
        default="pdf,png",
        help="Comma-separated output formats",
    )
    common.add_argument(
        "--xscale",
        choices=("linear", "log"),
        default="linear",
        help="Scale for x-axis",
    )
    common.add_argument(
        "--yscale",
        choices=("linear", "log"),
        default="linear",
        help="Scale for y-axis",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    xy = subparsers.add_parser("xy", parents=[common], help="Plot generic x/y data from a table")
    xy.add_argument("input", help="CSV or TSV file")
    xy.add_argument("--x-col", required=True, help="Column name for x")
    xy.add_argument("--y-col", required=True, help="Column name for y")
    xy.add_argument(
        "--kind",
        choices=("line", "scatter", "bar"),
        default="line",
        help="Plot kind",
    )
    xy.add_argument("--xlabel", help="Optional x-axis label")
    xy.add_argument("--ylabel", help="Optional y-axis label")
    xy.add_argument("--title", help="Optional figure title")
    xy.add_argument("--label", help="Optional series label")
    xy.add_argument("--output-stem", required=True, help="Output path without extension")

    transmission = subparsers.add_parser(
        "transmission",
        parents=[common],
        help="Plot a transmission spectrum from Wavelength and Voltage columns",
    )
    transmission.add_argument("input", help="CSV or TSV file")
    transmission.add_argument("--title", help="Optional figure title")
    transmission.add_argument("--output-stem", required=True, help="Output path without extension")

    return parser


def parse_formats(raw: str) -> List[str]:
    return normalize_formats(raw.split(","))


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    overrides = apply_cli_overrides(args)
    size_cm = parse_tuple_floats(getattr(args, "size_cm", None), 2, "--size-cm")
    axes_rect = parse_tuple_floats(getattr(args, "axes_rect", None), 4, "--axes-rect")
    formats = parse_formats(args.formats)

    require_runtime_dependencies()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if args.command == "xy":
        data = load_table(Path(args.input))
        saved_paths = plot_xy_table(
            data,
            x_col=args.x_col,
            y_col=args.y_col,
            output_stem=normalize_output_stem(args.output_stem),
            kind=args.kind,
            xlabel=args.xlabel,
            ylabel=args.ylabel,
            title=args.title,
            label=args.label,
            xscale=args.xscale,
            yscale=args.yscale,
            plot_config=overrides,
            size_cm=size_cm,
            axes_rect=axes_rect,
            formats=formats,
        )
        for path in saved_paths:
            print(path)
        return

    if args.command == "transmission":
        data = load_table(Path(args.input))
        if "Wavelength" not in data.columns or "Voltage" not in data.columns:
            raise SystemExit(
                "Transmission mode requires columns named 'Wavelength' and 'Voltage'."
            )
        output_stem = normalize_output_stem(args.output_stem)
        fig, ax, cfg = create_figure(overrides, size_cm=size_cm, axes_rect=axes_rect)
        ax.plot(
            data["Wavelength"] * 1e9,
            data["Voltage"],
            linestyle=cfg["linestyle"],
            linewidth=cfg["linewidth"],
            color=cfg["palette"][0],
            label="Transmission",
        )
        ax.set_xscale(args.xscale)
        ax.set_yscale(args.yscale)
        if args.xscale == "linear":
            ax.ticklabel_format(style="plain", axis="x")
        ax.set_xlabel("Wavelength (nm)")
        ax.set_ylabel("Voltage (V)")
        style_axes(ax, cfg, grid=cfg.get("grid"), legend=cfg.get("legend", False), title=args.title)
        saved_paths = save_figure_variants(fig, output_stem, cfg, formats)
        plt.close(fig)
        for path in saved_paths:
            print(path)
        return

    raise SystemExit(f"Unknown command: {args.command}")


if __name__ == "__main__":
    main()
