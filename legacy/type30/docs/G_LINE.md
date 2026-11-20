# G_LINE — v0.6, November 19, 2026

Call with JDA and four inline literal logical coordinates, X0, Y0, X1, Y1.
Return resumes after all four values. The routine plots the starting point,
then advances integer Bresenham state until the final point has also been plotted.
Both endpoint coordinates must be in 0..1023. Coordinates outside that range
are a caller error; no clipping or rejection code is present in this first version.
G_PLOT's documented zero-to-one device mapping applies to each emitted point.

The error algorithm is identical to reference/gline.py: dx and dy are absolute
endpoint differences, err=dx-dy, e2=2*err. Advance X when e2>-dy and Y when e2<dx.
The same saved e2 is used for both decisions even if X changed err. Zero is
canonicalized before the strict Y sign comparison to avoid dependence on
negative-zero representation. Maximum magnitudes fit signed 18-bit arithmetic.

Same-bank JDA linkage, writable inline arguments in the internal point call,
and saved return/work words make the implementation non-reentrant. AC/IO and
library scratch words are clobbered. Do not call from an interrupt that can
interrupt another P1GL call. Interrupt preservation is the application's job.

## Verification

`make test-lines` generates and assembles 73 isolated batches with the installed
AM1, then executes them through the PDP-1 CPU object with extensions disabled.
581 cases and 153,017 points matched the independent Python geometry reference,
after the documented device-zero clamp. The runner captures actual AC/IO and
instruction words at IOT 7; unexpected devices, instruction mismatches, CPU
cycle-limit overruns and overflow are failures.

The actual line demo is additionally assembled with DEMO_CPU_TEST: one frame
per page, halt after 32 pages. All 1,056 points match the expected 8x view transform.
The source library is unchanged by that demo-only magnification wrapper.

The live test saved our previous calibration's halted core and register state,
loaded line_demo.rim, and measured 125 frames over 3.00003 seconds: mean 24.0002 ms.
Screen capture showed the expected dotted line, stair steps, and earlier-page
phosphor trails. No sense switches are used. Phillip subsequently confirmed that the line display looks correct, following
his earlier point calibration confirmation.

This is point-by-point drawing. A full 1,024-point line cannot achieve the same
refresh time as the 33-point demo. A later sampling/performance design must be
explicit about point spacing, preserved endpoints, and numerical accuracy.
