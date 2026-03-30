# Figure Guidelines

## Contents

- Plot selection
- Canvas and sizing
- Typography
- Lines, markers, and color
- Axes, ticks, legends, and annotations
- Multi-panel layout
- Export and reproducibility
- Final review checklist

## Plot selection

- Use a line plot with uncertainty bands or error bars for ordered x-values, time series, or dose-response curves.
- Use a scatter plot for pairwise relationships; add a fit or guide only when it supports the argument.
- Use a bar chart only for a small number of discrete categories and when absolute level matters. For estimated means or effects, prefer points with intervals.
- Use a box plot, violin plot, swarm plot, or histogram for distributions; choose the least stylized option that still reveals the distribution shape.
- Use a heatmap only when the matrix structure matters. Label the colorbar clearly and control the displayed range deliberately.
- Avoid dual y-axes unless the user explicitly asks for them and the comparison cannot be expressed another way.

## Canvas and sizing

- Default canvas size: 12 cm x 6 cm unless the task or journal template requires another size.
- Default single-column width: 85 mm or 3.35 in.
- Default one-and-a-half-column width: 120 mm to 130 mm or 4.7 in to 5.1 in.
- Default double-column width: 178 mm or 7.0 in.
- Default height: roughly 55% to 70% of the width unless the data demands a different aspect ratio.
- Keep outer whitespace tight. Use constrained layout or a deliberate manual layout instead of a loose default canvas.
- Share axes across comparable panels when it reduces duplicate labels and improves comparison.

## Typography

- Use Arial or Helvetica by default. Fall back to another sans-serif only when those are unavailable in the runtime environment.
- Use one font family across axes labels, ticks, legends, and annotations.
- Default to 7 pt text at the final printed size unless the venue requires a larger minimum.
- Write x-axis and y-axis labels in sentence case: capitalize only the first word unless a symbol, acronym, or unit requires its conventional casing.
- Include physical units in parentheses, for example `Current (mA)` or `Time (s)`.
- Use math formatting only for symbols, variables, and equations that actually need it.
- Avoid figure titles by default. Add a title only when the user explicitly asks for one. Let the caption carry the narrative.

## Lines, markers, and color

- Default plotted data line width: 0.5 pt.
- Default plotting-box spine width: 0.5 pt on all four sides.
- Only increase line width when the user explicitly asks for stronger emphasis or a venue requires heavier strokes.
- Default marker size: 4 pt to 6 pt.
- Default error bar cap size: 2 pt to 3 pt.
- Limit distinct hues to roughly 4 to 6 in one panel unless the task truly needs more.
- Prefer a colorblind-safe palette built around blue, orange, green, red, purple, and gray.
- Use alpha only to manage overplotting or uncertainty fills; do not wash out primary data as a default style.
- Ensure the figure still works in grayscale when color is not essential to interpretation.

## Axes, ticks, legends, and annotations

- Start the y-axis at zero for bars unless a truncated baseline is essential and clearly justified.
- Keep major ticks sparse enough that labels do not collide; 4 to 6 major ticks per axis is a good default.
- Format numbers simply and avoid unnecessary decimal precision.
- Draw all four sides of the plotting box as explicit black spines at `0.5 pt`. Do not rely on hidden or theme-dependent defaults.
- Draw tick marks inward so they remain inside the plotting box by default.
- Use a light grid only when it helps the reader estimate values; keep it behind the data.
- Prefer direct labels when there are only a few series. If a legend is needed, remove the frame and keep wording short.
- Keep annotations short, aligned, and outside dense data regions when possible.

## Log-scale axes

- When an axis uses log scale, enable minor ticks at `2..9 x 10^n`.
- When an axis uses log scale, enable the major and minor grid by default unless the task explicitly disables grid.
- Style the log major grid with `--` linestyle, `0.25` line width, `0.5` alpha, and `cfg_plot["gridcolor"]` when available, otherwise `gray`.
- Hide minor tick labels on log axes.
- Style log-axis minor ticks in black with length `1.2` and width `0.5`.
- If the plot grid is enabled, also enable the minor grid for log axes with `:` linestyle, `0.2` line width, `0.5` alpha, and `cfg_plot["gridcolor"]` when available, otherwise `gray`.

## Multi-panel layout

- Align panel edges and keep gutter spacing consistent.
- Reuse identical axis limits for comparable panels unless there is a strong reason not to.
- Place panel labels such as `(a)`, `(b)`, and `(c)` in a consistent location, usually near the top-left margin of each panel.
- Avoid repeating identical axis labels on every shared panel; keep only the labels that add information.
- Use a common legend for grouped panels when that reduces duplication.

## Export and reproducibility

- Save `pdf` and `png` by default.
- Save raster output at 450 ppi by default.
- Save `eps` or `svg` only when the user explicitly asks for it or a downstream workflow needs it.
- Keep text editable in vector exports when possible. In Matplotlib, use `pdf.fonttype = 42`, `ps.fonttype = 42`, and `svg.fonttype = none`.
- Keep the plotting code deterministic. Set a random seed whenever jitter, simulation, subsampling, or randomized layout is involved.
- Preserve the raw data, the plotting script, and the exported outputs together whenever the repository structure allows it.
- Avoid hand-editing vector output unless the user explicitly asks for illustration work outside the plotting code.

## Final review checklist

- Does the figure still read clearly at journal column width?
- Are axis labels, units, legend labels, and annotations complete?
- Are spacing, clipping, and alignment clean?
- Does the color encoding remain interpretable for grayscale or colorblind viewing?
- Is the uncertainty or statistical summary presented honestly and explicitly?
- Are the exported formats the ones the user or publisher actually needs?
