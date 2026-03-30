---
name: scientific-plotting
description: Create, restyle, and export publication-quality scientific figures from raw data or existing charts. Use when Codex needs to turn CSV or tabular results into a clean paper-ready plot, improve the styling of an existing figure, fix labels/fonts/spacing, standardize multi-panel layouts, or export plots as SVG, PDF, EPS, or PNG. Typical triggers include "make this figure cleaner for a paper", "improve the styling of this plot", "turn this data into a scientific plot", and Chinese requests such as "把这张图整理得更适合论文", "美化这张图", or "用这份数据画科研图".
---

# Scientific Plotting

## Overview

Produce standard, repeatable scientific figures that are easy to read at paper scale, conservative in styling, and straightforward to regenerate from code. Prefer the simplest plot that supports the scientific claim, then make typography, spacing, and export quality consistent.

## Workflow

### Inspect the task

Identify whether the user wants a new plot, a restyle of an existing figure, a multi-panel composition, or an export-only cleanup. Check the available inputs first: raw data, plotting code, notebook, raster image, or vector source.

If the user only provides an image, improve presentation conservatively and state that the underlying data cannot be recovered faithfully from pixels alone.

### Choose the figure form

Choose the smallest honest visual encoding that communicates the result. Use [references/figure-guidelines.md](references/figure-guidelines.md) for plot selection defaults, sizing targets, typography, and export rules.

Prefer Matplotlib for paper figures unless the repository already uses another plotting stack and consistency matters more than switching tools.

### Build or restyle

Start from [scripts/plot_utils_reference.py](scripts/plot_utils_reference.py) when the task needs a reusable helper module, a fixed-layout figure template, or a CLI that turns CSV and TSV tables into publication-style output.

Preserve the user's analysis unless they explicitly ask to change it. Improve presentation before changing aggregation, smoothing, normalization, statistics, or uncertainty display.

### Export

Export vector formats first. Save `pdf` and `png` at 450 ppi by default. Add `eps` or `svg` only when explicitly requested or required by a downstream workflow.

Before finishing, verify that labels are not clipped, panel spacing is even, line weights remain legible at journal size, and colors still separate clearly in grayscale or colorblind-safe viewing.

## House Rules

Keep one clear message per axis. Label variables and units explicitly. Avoid decorative effects, heavy grids, saturated colors, and unnecessary titles inside publication figures.

Use Arial or Helvetica by default, keep normal text at 7 pt, and default to a 12 cm x 6 cm canvas unless the task or venue requires another size. Do not add a title unless the user explicitly asks for one.

Prefer direct labels or compact legends. Use `0.5 pt` as the default data-line width, draw all four borders as explicit black spines at `0.5 pt`, keep tick marks inside the plotting box, and only add a light grid when the reader needs help estimating values.

For log-scale axes, enable minor ticks at `2..9 x 10^n`, hide minor tick labels, and use black minor ticks with length `1.2` and width `0.5`. Log plots should enable major+minor grid by default unless the task explicitly disables grid. Use `--` linestyle, `0.25` line width, and `0.5` alpha for the major grid; use `:` linestyle, `0.2` line width, `0.5` alpha, and `cfg_plot["gridcolor"]` or `gray` for the log minor grid.

Write x-axis and y-axis labels in sentence case by default: only the first word capitalized, unless a symbol, acronym, or unit needs its standard casing.

## Deliverables

Return reproducible code together with the exported figure files. State any assumptions that affect interpretation, especially units, normalization, smoothing, missing metadata, and chosen defaults.

If the request is underspecified, choose a conservative publication default and state it briefly instead of blocking on optional style questions.

## Resources

- Read [references/figure-guidelines.md](references/figure-guidelines.md) for detailed plotting standards, default sizes, export expectations, and a final review checklist.
- Reuse [scripts/plot_utils_reference.py](scripts/plot_utils_reference.py) as the primary reference script when a task benefits from a fixed-layout plotting helper or a direct CLI such as `xy` and `transmission`.
