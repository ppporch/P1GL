# P1GL — PDP-1 Graphics Library

## v0.8: text and reusable retained frames, November 19, 2026

Targets Bill Ezell's AM1 and improved Type 30 device with t30dpy.
G_PLOT, G_LINE, G_CIRCLE, G_TEXT, and retained-frame building/replay assembled
and executed successfully on Phillip's PiDP-1.
Phillip confirmed that the nine-cross calibration looks good on screen.

The original v0.4 assembly and documentation are preserved in original-v0.4/.
They describe the earlier prototype; the current contract is below.

## Install and run

Install alongside a working [Bill Ezell pidp1-mods](https://github.com/wjenh/pidp1-mods)
installation. P1GL is PDP-1 assembly, not native software for the Mac.

```sh
git clone https://github.com/ppporch/P1GL.git
cd P1GL
make PDP1_ROOT=/opt/pidp1-mods
```

With the PiDP-1 powered on, halt its current program before loading the demo:

```sh
/opt/pidp1-mods/bin/fastload -y build/frame_demo.rim
```

Open Bill's t30dpy/t30dpy3 display. No sense-switch changes are needed. The demo
replaces the current program in core; save any work first. Other build products
provide separate point, line, and circle tests. Build-generated binaries,
listings, screenshots and core snapshots are excluded from Git.

The `tools/live_*.py` helpers are development-session tools for Phillip's Pi and
known preceding demos; they are not general-purpose installers. Use the build
and loading commands above for a new installation.

## Build and test on the Pi

Requires am1 on PATH and the installed pidp1-mods CPU object for test-cpu.

```sh
make
make test-host
make test-cpu PDP1_ROOT=/opt/pidp1-mods
make test-lines PDP1_ROOT=/opt/pidp1-mods
make test-circles PDP1_ROOT=/opt/pidp1-mods
make test-frames PDP1_ROOT=/opt/pidp1-mods
```

Build products are in build/. `build/calibrate.rim` continuously draws nine
crosses; `build/calibrate-once.rim` draws once and halts. The five-point example
is `build/gplot_demo.rim`. CPU tests run in a separate process and do not load
the running emulator. No sense switches are used by these calibration programs.

## Calling G_PLOT

```text
        jda gplot
        0d512       // literal X value, not its address
        0d512       // literal Y value
```

Include src/gplot.am1 in the same bank. Coordinates are integers 0..1023;
X increases rightwards and Y upwards, with logical center (512,512).
The current Type 30 conversion cannot address pixel zero: logical zero explicitly
clamps to pixel one on either axis. Thus the distinct usable device positions are
1..1023. Bounds are a caller precondition; clipping is not implemented.

AC and IO are clobbered. Linkage is non-reentrant and requires writable code.
DPY uses synchronous completion and intensity field 2 (`dpy 200`, word 730207).
The device maps this intensity to protocol level 6. Coordinate conversion uses
one's-complement signed values in the high ten bits of AC/IO.
JSP replaces AC with its return address, so internal gcoord receives its input
through gc_value and returns the encoded coordinate in AC.

## Verification

- All 11 original host checks pass (nine function tests plus two unittest cases).
- The installed CPU object executed 45 calibration points and a 1,024-point
  sweep covering every logical coordinate on each axis. All coordinates and
  DPY words matched expectations; no overflow was reported.
- The running Type 30 device emitted the correct sequence for 194 complete
  captured frames (8,762 points received, including a partial frame).
- Mean live frame period: 20.62 ms over a four-second sample. This measures the
  frame counter rate, not maximum frame latency or the display client's frame rate.
- Phillip confirmed the screen appearance on November 19, 2026.

See docs/validation/cpu-results.json, docs/validation/live-results.json, and docs/verification.md.

## G_LINE

```text
        jda gline
        0d100       // literal X0
        0d200       // literal Y0
        0d700       // literal X1
        0d400       // literal Y1
```

Include src/gline.am1 and src/gplot.am1 in the same bank. Endpoint-inclusive
Bresenham matches reference/gline.py in all octants, with strict tie comparisons.
Caller guarantees integer endpoints 0..1023; clipping is not implemented.
AC/IO are clobbered; linkage is non-reentrant and requires writable code.

581 executed cases matched 153,017 reference points, including short slopes,
random long lines, endpoint reversals, axes, diagonals, zero-length lines,
and screen boundaries. The actual demo also passed a 32-page, 1,056-point CPU
check, including its application-only view transformation. These CPU tests use
immediate device completion and do not measure live display speed.

`build/line_demo.rim` cycles through 16 directions, then reverses their endpoints.
Each 33-point line is magnified 8x about the center, intentionally showing the
individual dots and integer stair steps. The view transformation is confined to
the demo: library coordinates and G_LINE remain unchanged. The live demo averaged
24.00 ms/frame across 125 frames over three seconds; this is a mean frame-counter
rate, not a maximum latency or client rendering rate. A Pi desktop screenshot
confirmed the dotted lines and expected phosphor trails. Phillip confirmed that the line test looks correct, following his earlier point
calibration confirmation.

See docs/validation/line-results.json, docs/validation/line-live-results.json and docs/G_LINE.md.

## G_CIRCLE

```text
        jda gcircle
        0d512       // literal center X
        0d512       // literal center Y
        0d100       // literal radius
```

Include src/gcircle.am1 and src/gplot.am1 in the same bank. Center coordinates
and radius must be integers 0..1023. Midpoint integer geometry emits each logical
symmetry point once and clips points outside the logical viewport before plotting.
Radius zero plots the center exactly once. The documented logical-zero device
alias still applies: distinct logical boundary points can share a device pixel.

277 executed CPU cases matched 143,151 plotted points, including 127 cases
requiring clipping. Four additional host checks verify symmetry, radial error,
axes, zero radius, clipping and invalid reference inputs. All earlier checks pass.
The exact retained-point demo passed an 11-page, 821-point CPU playback check,
with its buffer guard intact and fault flag zero.

`build/circle_demo.rim` cycles through four sizes, four clipped edges, two clipped
corners, and radius zero. A demo-only 8x view transform makes points easy to see.
Each page is generated once into a bounded 256-point raw-coordinate buffer and
replayed for refresh. A BBN millisecond clock paces the display at a nominal
22 ms interval. The live demo averaged 22.79 ms per refresh across 702 frames
in 16 seconds, including page changes. This is not a maximum latency guarantee;
page construction takes additional time. Screen capture shows the expected
circle. Phillip confirmed that the circle test looks correct.

See docs/G_CIRCLE.md, docs/validation/circle-results.json and docs/validation/circle-live-results.json.

## G_TEXT and retained frames

G_TEXT uses Bill's Type 33 generator and ASCII character shapes on the Type 30
display. Its four inline arguments are baseline X, baseline Y, size 0..3,
and the address of a NUL-terminated AM1 `ascii` string. Labels are placed in
logical screen coordinates; a size of 3 gives five-pixel dot spacing.
All printable ASCII is supported; other nonzero codes become question marks.
Whole glyphs that cross the viewport are omitted. Calls are limited to 256
characters and the string must be contained in the current memory bank.

Define P1GL_FRAME before including src/gplot.am1 to enable frame capture.
Include src/gframe.am1 and, for text, src/gtext.am1; build with
`-I/opt/pidp1-mods/Am1Includes` for Bill's font table. Geometry primitives need
no API changes. Between begin and end, point and text calls build a retained
scene without display I/O:

```text
        jda gframe_begin
        frame_buffer       // address of caller-reserved buffer
        0d512              // capacity in words
        jda gtext
        0d100
        0d800
        3
        caption            // caption, ascii "P1GL"
        jsp gframe_end
        jsp gframe_refresh // replay the saved scene; repeat as needed
```

The caller must reserve the buffer without overlapping code or data. Each point
uses two words and each character five. Refresh replays points, then text, using
absolute positions. Begin resets the scene; end restores immediate drawing.
A sticky fault prevents partial replay of an invalid frame; the next begin
clears it. The current API holds one scene descriptor and is not interrupt-safe
or double-buffered. See docs/G_FRAME.md and docs/G_TEXT.md.

`build/frame_demo.rim` combines readable labels, a circle, a radius line, and a
center point. It cycles through three saved scenes. Twenty-four executed
frame/text tests pass, checking 998 device transactions, all printable ASCII,
packed strings, clipping, exact buffer fits, overflow, empty frames, repeated
replay, reset and immediate drawing. Earlier point/line/circle tests pass too.
The CPU runner captures Type 33 commands; real rendering is verified separately
on the Pi. The screenshot shows clear labels and the expected geometry.

The final live sample averaged 22.94 ms across 436 refreshes in ten seconds;
the largest BBN-clock draw measurement was 22 ms. This is not a maximum frame
latency guarantee: page construction adds a gap, and host/client pacing can
vary. Timing is diagnostic; readable labels and geometric fidelity take priority
over a strict redraw threshold, following Phillip and Bill's feedback.
Phillip confirmed that the combined demo and its labels look good.

## Next milestone

Application graphics and interaction for Orbit Laboratory. View transforms in
the demos remain application code; a public transform API, interrupt-driven
refresh, and scene double buffering are not implemented yet.

## License and credits

Licensed under GPL-3.0; see LICENSE. Developed by Phillip Porch with Codex/ChatGPT
assistance. Bill Ezell's pidp1-mods provides AM1, the emulator/device support, and
the Type 33 ASCII character table, included from his installation rather than
vendored here. The RIM decoder and isolated CPU harness originated in Phillip's
SignalAnalysis project. See docs/verification.md and docs/validation/ for the
tested milestones and recorded results.
