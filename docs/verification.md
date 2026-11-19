# Verification record — November 19, 2026

P1GL v0.5 point milestone passed assembly, isolated CPU execution, live Type 30
output capture, and Phillip's visual inspection.

Target: pdp1, installed checkout 035c84a. Isolated work directory:
/tmp/p1gl-first-test-20261119/P1GL. No repository source files were changed on the Pi.

Before live loading, the CPU was powered on and halted, with no enabled
breakpoints, watches, or sticky single-step state. All 65,536 core words and
register state were saved in:
/tmp/p1gl-first-test-20261119/P1GL/build/snapshots/20261119T194102Z/.
This is a diagnostic core/register snapshot, not a full device-state checkpoint.
Drum and Microtape images were not modified by calibration.

The original candidate required AM1 source/directive fixes, literal inline
arguments, verified display encoding and synchronous completion. Execution tests
also caught an internal JSP linkage bug before any live calibration was loaded.

The current build uses the installed /usr/local/bin/am1, SHA256:
b849e838fe35664ceeb6238b06ad9540da03567172d8a537147d1ee9d1472ac7.
Installed Type 30 device IOT_7.so SHA256:
8f3bdea8dc2d4b903b9d0b6f77482ea1214feb09405fda25d218cf4b99be6060.
Installed Type30Display/IOT_7.c matches the local reference, SHA256:
d1e1d6687f8b0da57d386174c9fdcf538220e4b864c13fa50b0683a8341d8f3f.

CPU runner intercepts IOT 7 with immediate completion: its timing is not a
Type 30 timing measurement. The subsequent live capture exercises the real
installed device and display-output path. Neither replaces visual inspection;
Phillip separately confirmed that the screen looks good.

The calibration remained running for inspection, with t30dpy opened on the Pi's
X11 desktop. No sense-switch changes were required.

Other documents in this directory originated with v0.4; see README.md for the
current G_PLOT contract and original-v0.4/ for preserved prototype documents.

## v0.6 line milestone

See G_LINE.md and validation/line-results.json for the 581-case, 153,017-point
executed geometry comparison and the 32-page actual-demo check. All original
host and point CPU tests were rerun and passed after the line changes.
Long-case batches were reduced to eight lines to fit the CPU runner's
2,000,000-cycle execution bound; the earlier interruptions were runner-budget
failures, not evidence of an infinite loop in G_LINE.

During this work the installed repository advanced externally to 4f2b775.
The assembler was copied into the isolated build folder to avoid transient
replacement during tests. Its SHA256 stayed identical to that listed above.
The isolated plot_runner SHA256 was
8e55c371d94c4b7c75dc931ed13228e4437796be5482b57d554026aa2ce2e833.

Before switching, tools/live_lines.py verified the running calibration's first
32 instruction/data words against its assembled image, then halted and saved
core/registers. Snapshot:
/tmp/p1gl-first-test-20261119/P1GL/build/snapshots/20261119T195107Z-lines/.
The line demo remains running with mean refresh 24.00 ms over three seconds.
The screen capture confirms dotted lines and phosphor trails. Phillip subsequently confirmed the line screen looks correct.

## v0.7 circle milestone

All original host checks, point CPU tests, and line CPU tests passed again.
Four new host circle tests passed. Executed circle checks passed 277 cases and
143,151 points, including 127 clipped cases. Eleven demo pages and 821 cached
points passed replay verification, with no overflow, fault, or buffer overrun.

Before switching, live_circles.py verified the first sixteen immutable words of
the running line demo, halted it, and saved all core and register state in:
/tmp/p1gl-first-test-20261119/P1GL/build/snapshots/20261119T200056Z-circles/.
Drum and tape images were not modified. The circle demo enables the BBN clock
without clock interrupts and remains running for inspection.

Live observation: 702 frames in 16.00008 seconds, mean 22.7921 ms, zero fault,
intact 0123456 buffer guard. Screen capture shows a symmetric dotted circle.
This average includes page transitions, but is not a worst-case latency bound.
Phillip confirmed the circle display looks correct.

## v0.8 text and retained frames

The previous circle demo was visually confirmed by Phillip. New G_TEXT and frame
modules pass 24 executed tests covering 998 IOT transactions, including all
printable ASCII. All earlier host, point, line and circle checks passed with the
extended event-capture runner. The optimized character replay passed the same
24 tests with unchanged expected transactions; no geometry code changed.

The circle demo was identified by its immutable instruction prefix, halted and
snapshotted before loading the combined demo. Snapshot:
/tmp/p1gl-first-test-20261119/P1GL/build/snapshots/20261119T201455Z-frames/.
The first text replay copied glyph payloads each refresh and measured mean
26.1782 ms with a 29 ms largest BBN-clock draw observation. Direct replay avoids
that copy. Before reloading, the running demo's instruction prefix was checked;
the relocated LAC [02000] constant reference was checked semantically as well.
Snapshot:
/tmp/p1gl-first-test-20261119/P1GL/build/snapshots/20261119T201659Z-frames/.

Final live sample: 436 frames in 10.00005 seconds, mean 22.9359 ms; sampled
largest draw duration 22 ms. Program fault and frame fault are zero; the buffer
guard remains 0123456. Scene building adds time between pages and the recorded
draw maximum is not a full frame-latency bound. Drum/tape images were unchanged.
Screen capture shows readable P1GL GRAPHICS / FRAME 1 labels with a circle,
radius line and center point. Phillip confirmed the combined demo and labels look good. Timing is diagnostic; clarity and correctness are the priority per
Phillip and Bill's latest guidance.
