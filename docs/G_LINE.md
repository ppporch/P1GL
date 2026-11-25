# G_LINE — v0.9 Type 340 vectors

`jda gline; X0; Y0; X1; Y1` accepts literal integer endpoints 0..1023. Endpoints
must be valid; general line clipping is not implemented. Radius-zero/degenerate
lines plot their one point once. All calls require gframe.ac and gplot.ac,
non-reentrant writable same-bank linkage in ordinary addressing mode; AC/IO
are clobbered.

The initial point is plotted explicitly. An integer Bresenham walk chooses
segment endpoints after at most 127 major-axis steps and at the final endpoint.
Each component is therefore representable in the native seven-bit vector field.
Each segment positions the invisible start, enters VECTOR, draws a visible
signed displacement with END, then restores POINT mode. Adjacent segments share
an exact endpoint and there is no arbitrary scaling of device coordinates.

The hardware rate multiplier draws the intermediate pixels continuously at
scale zero. Those samples need not match the old CPU Bresenham sequence. The
contract is exact geometric endpoints and connected native segments. No Type 30
point-by-point IOT loop remains. A 1,023-pixel major-axis line needs nine vector
segments, not 1,024 CPU point-display calls.

Tests execute 549 line cases: short slopes in every octant, zero length, long
axes/diagonals, random endpoints and reversals. Each bounded segment endpoint
matches the chosen reference geometry; lists are structurally decoded and the
real device is inspected separately. Pixel timing and hardware rate-multiplier
stepping are not reimplemented by the structural test decoder.
