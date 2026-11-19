# P1GL implemented API — v0.8

- G_PLOT: `jda gplot` followed by X and Y literal values.
- G_LINE: `jda gline` followed by X0, Y0, X1, Y1 literal values.
- G_CIRCLE: `jda gcircle` followed by center X, center Y, radius literal values.
- G_TEXT: `jda gtext` followed by baseline X, Y, size 0..3, packed ASCII address.
- G_FRAME_BEGIN: `jda gframe_begin` followed by buffer address and capacity words.
- G_FRAME_END: `jsp gframe_end`.
- G_FRAME_REFRESH: `jsp gframe_refresh`.

Coordinates are integer logical values 0..1023. X increases rightwards, Y upwards;
(512,512) is the center. On the current Type 30 device, logical 0 clamps to pixel
1, so there are 1,023 distinct device positions per axis. Center/endpoint coordinates and radius bounds are caller preconditions.
G_CIRCLE clips generated circumference points to the viewport; G_LINE and G_PLOT
do not clip.

All routines clobber AC/IO, use writable code and scratch words, are non-reentrant,
and require caller and routines in the same 4K bank with ordinary memory mode.
The sample drivers explicitly disable extended addressing and sequence breaks.

G_LINE is endpoint-inclusive and matches the Python reference's tie rules.
The library always plots all generated points. The line demo's 8x magnification
is an application wrapper, not a change to the library coordinate contract.

G_CIRCLE emits each logical circumference point once, including the center once
for radius zero. Distinct logical 0/1 boundary points can still alias on the
current physical device. Line clipping remains future work. See G_TEXT.md and G_FRAME.md for implemented
text and retained-frame contracts. Define P1GL_FRAME before including gplot.am1
to enable recording between begin and end.
