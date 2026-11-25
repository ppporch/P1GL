# Viewports and clipped lines

Include `gview.ac` alongside G_LINE, G_PLOT and G_FRAME. Enable the PDP-1
Type 10 multiply/divide option. All arguments and library code are in the
caller's field with ordinary addressing, as with G_LINE.

```text
        jda gview_set
        0d256; 0d256; 0d768; 0d768    // xmin, ymin, xmax, ymax

        jda gline_clip
        -0d80; 0d380; 0d900; 0d540    // x0, y0, x1, y1
```

The default viewport covers the full display, 0–1023 on each axis. Choose
inclusive bounds in that range. A zero-width or zero-height viewport is valid.
GVIEW_SET returns 0 on success or 1 on invalid bounds and preserves the previous
rectangle on error. The viewport persists across frames.

GLINE_CLIP accepts signed endpoints from −8191 to +8191. It intersects the
finite line segment with the viewport using exact fractional comparisons,
then rounds the clipped endpoints to the nearest pixel, with ties toward
the larger coordinate. It preserves drawing direction. If the visible result
is a single pixel, it draws a point. Entirely hidden lines emit no commands.
Both outcomes return 0. An endpoint outside the supported range sets the
usual G_FRAME argument fault (1). Other drawing faults propagate from G_LINE.

Call GLINE_CLIP for immediate drawing, while recording a frame, or while
building or replacing a retained drawing group. The [path API](G_PATHS.md) also uses the active viewport. The normal line, circle and text APIs retain their existing
coordinate rules, so a frame can mix clipped geometry with labels or a border.

Build and load the [viewport demo](../examples/viewport_demo.ac) to see a
diamond pass through all four edges of a retained rectangular border. It uses
the BBN clock for pacing. `make test-viewport` compares the CPU's display
lists with rational reference geometry and checks a complete 280-frame demo
cycle. The usual synchronous refresh and same-bank, non-reentrant rules apply.
