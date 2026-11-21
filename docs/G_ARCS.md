# Vector circles, ellipses, and arcs

Include `garc.am1` with G_TRANSFORM, G_VIEWPORT, G_LINE, G_PLOT and G_FRAME.
The curves share the Q10 sine table and fixed-point helpers with G_TRANSFORM
and require the Type 10 multiply/divide option. They draw in device
coordinates and respect the active viewport. Calls preserve the current
transform and viewport.

```text
        jda gcircle_vector
        0d250; 0d512; 0d80; 0d8     // cx, cy, radius, step

        jda gellipse_vector
        0d512; 0d512; 0d140; 0d80; 0d8
                                   // cx, cy, rx, ry, step

        jda garc
        0d800; 0d512; 0d100; 0d80; 0d64; -0d96; 0d8
                                   // cx, cy, rx, ry, start, sweep, step
```

Centers accept signed coordinates from −1023 to +1023. Radii accept 0–1023.
Angles use 256 units per turn. Angle 0 starts on the positive X axis and
angle 64 is at the top. Start accepts 0–255 and sweep accepts −256 to +256.
Positive sweeps go counterclockwise and negative sweeps go clockwise. Full
circle and ellipse calls start at zero and sweep one turn. A zero sweep
draws a point at the start angle if that point is visible.

Step accepts 1–64 and gives the maximum angular distance between neighboring
vertices. Smaller steps produce smoother curves and require more display
words. For example, step 8 gives 32 chords on a full turn before clipping.
The last chord always reaches the requested endpoint, including when the step
doesn't divide the sweep. Consecutive vertices that round to the same pixel
are skipped. A curve that collapses to a point draws it once.

The routine draws connected chords with native Type 340 vectors. Each chord is
clipped independently, so the viewport can leave separate visible sections.
The existing midpoint circle routine remains available for point rendering.

Call the curve entries in immediate mode, inside a retained frame or while
recording a retained drawing group. AC returns the usual drawing fault.
Invalid parameters set the argument fault (1) before drawing any part of
the curve. Allow up to 256 chords for a full turn at step 1. A short visible
chord takes six display words with the current G_LINE implementation.
Longer chords can need additional native segments.

The [arc demo](../examples/arc_demo.am1) shows a circle, an ellipse, and two
clockwise arcs that cross the viewport's right edge. `make test-arcs` checks
the executed display lists against reference geometry.
