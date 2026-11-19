# Proposed P1GL API (draft)

Coordinates: unsigned 10-bit device space, 0..1023 in X and Y. Origin and axis direction to be verified against target display convention. Application-space transformations are separate.

- `G_INIT`: initialize software graphics state; does not assume a raster framebuffer.
- `G_PLOT(x,y)`: plot one point; device-driver boundary.
- `G_LINE(x0,y0,x1,y1)`: integer Bresenham line; clip or reject out-of-range coordinates per finalized contract.
- `G_CIRCLE(cx,cy,r)`: midpoint circle; points may require clipping.
- `G_CLEAR_FRAME`: reset retained display-command list, if that optional strategy is selected.
- `G_REFRESH`: replay the retained points/strokes for a persistence CRT, if selected.

Calling convention is not finalized: accumulator/IO register preservation, indirect addressing, return linkage, and argument storage require validation against the selected assembler/runtime.

## Test vectors
- Plot corners (0,0), (1023,0), (0,1023), (1023,1023), center (512,512).
- Lines: horizontal, vertical, 45 degrees, shallow, steep, reverse direction, degenerate point.
- Circles: radius 0, 1, 10, 100; edge clipping.
- Repeated refresh: assess flicker and density on actual hardware/emulation.
