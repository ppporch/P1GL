# G_CIRCLE — v0.7, November 19, 2026

Call `jda gcircle` followed by three literal words: center X, center Y, radius.
All three must be integers 0..1023. Return resumes after the three arguments.
Caller and library reside in the same bank, in ordinary memory mode. AC/IO are
clobbered. Work words and return linkage are non-reentrant and require writable
code. G_PLOT is required. Do not interrupt a P1GL operation with another call.

## Geometry and clipping

Start x=radius, y=0, d=1-radius. While y<=x, emit the distinct eightfold symmetry
points about the center. Axis and diagonal duplicates are suppressed; radius
zero therefore emits the center once. Increment y. If d<0, add 2*y+1 to d;
otherwise decrement x and add 2*(y-x)+1. Only integer add/subtract, shifts and
branches are used; no multiply, divide, square root, or floating point.

Generated coordinates outside 0..1023 are dropped before G_PLOT. This is point
clipping: the remaining circumference is drawn without a closing edge at the
viewport boundary. Centers and radii outside the input contract are unsupported;
the assembly does not validate them. Intermediate coordinates and decision terms
fit signed 18-bit arithmetic throughout the supported domain.

G_PLOT maps logical zero to device pixel one. Consequently logical duplicate
suppression does not guarantee physically distinct pixels for points involving
logical 0 and 1 near an edge. It does prevent repeated axis and diagonal points
caused by the usual eightfold symmetry expansion.

## Tests

Four host geometry tests independently check reflection and coordinate-swap
symmetry, uniqueness, radial error <=0.5 pixel, axes, zero radius, viewport
bounds, and reference input rejection. Full symmetry is checked before clipping
for radii 0..128; large clipped cases include radius 1023.

`make test-circles` assembles and executes 277 cases on the isolated PDP-1 CPU
object, with extensions disabled and immediate Type 30 completion. All 143,151
emitted display points and instruction words match the Python reference after
the documented device zero mapping. 127 cases require viewport clipping.
The CPU test is not a device-timing measurement.

The actual demo is also executed with DEMO_CPU_TEST: pacing IOTs omitted, one
refresh per page, halt after the final page. All 11 pages and 821 output points
match the expected view transform and replay order. The buffer guard remains
0123456, the fault flag stays zero, and the frame count reaches eleven.

## Display demo

The four full circles have logical radii 8, 16, 24, and 32. Remaining pages show
left/right/top/bottom clipping, two clipped corners, and the radius-zero point.
A demo-only transform magnifies offsets from each circle center by eight.
Each page is generated once into a buffer of at most 256 raw coordinate pairs;
replay uses synchronous DPY directly. This separates circle calculation from
refresh without adding a public retained-scene API to the library yet.

The BBN clock is enabled without its interrupt bits and supplies nominal 22 ms
refresh pacing. The clock's 60,000 ms rollover is accounted for in the polling
loop. The isolated demo CPU test skips this timing code; the live test exercises
it. Pages are shown for sixty refreshes. Rebuilding a page adds a brief gap.

Live result: 702 frames in 16.00008 seconds, mean 22.7921 ms, no reported fault,
intact buffer guard. This is average frame-counter rate, not worst-case latency
or the t30dpy client frame rate. Screen capture shows a symmetric dotted circle.
Phillip confirmed that the circle screen looks correct, following the earlier
point and line confirmations. No sense switches are used.
