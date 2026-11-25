# G_CIRCLE — v0.9 Type 340 points

`jda gcircle; CX; CY; RADIUS` accepts literal integers 0..1023, as a caller
precondition. It uses the midpoint recurrence and distinct eightfold symmetry
points established in v0.7. Generated points outside the viewport are discarded;
clipping leaves a circumference arc, not a closing edge. Radius zero emits its
center once. All 1,024 device coordinates are distinct on this backend.

Each visible logical point becomes two native POINT-mode words. In a retained
frame these are recorded once and replayed by the display processor. In immediate
mode the frame module streams bounded scratch chunks and waits before reusing
them. The CPU does not issue one display IOT per point. There is no native circle
instruction: the midpoint geometry still determines the actual circle points.

The full-resolution combined demo uses actual radii 96,128,160, removing the
old magnification gaps. The standalone circle demo also exercises clipped edges,
corners and radius zero. Tests compare 277 circles, including screen edges, corners and large radii, point for point against the independent reference.

Code/data/list occupy one bank in ordinary addressing mode; require gplot.ac
and gframe.ac, writable non-reentrant linkage, and clobber AC/IO. A retained
buffer still needs enough words for its scene. Large immediate circles do not
require a private full-circle buffer because safe chunks are streamed.

The real Type 340 executes point positioning, drawing and list fetch timing;
CPU test capture deliberately does not emulate those timings. See TYPE340.md
and recorded validation data for live observations and their limits.
