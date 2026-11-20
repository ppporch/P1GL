# Current status — v0.9 Type 340

The default backend is now native Type 340/342; see TYPE340.md. The records below
are chronological and older milestones describe their historical devices.

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

## v0.9 native Type 340 migration

The backend now emits parameter, point, vector and character commands and uses
explicit IOT 015/0217/0417/01017. No Type 30 or Type 33 device calls are accepted
by the native CPU test runner. Native vectors preserve exact endpoints; hardware
samples replace the former CPU Bresenham pixels. Circles preserve midpoint
points and clipping, including true coordinate zero. Text uses Type 342 scale
and repertoire; its look and spacing differ from the old Type 33 bitmap labels.

The structural decoder and real CPU execute coordinate, vector, circle, text,
frame, ownership and buffer cases, including all three actual demo programs.
The initial test caught the required POINT-to-PARAMETER transition before HALT.
CPU capture models completion immediately, so real device execution remains a
separate required check, not an implication of the model tests.

The Pi had a different program running when the loader first checked it. No
replacement occurred until Phillip explicitly approved saving and replacing it.
Its core/register diagnostic snapshot is:
/tmp/p1gl-type340-20261119/P1GL/build/snapshots/20261120T025023Z-type340/.
These are UTC-stamped paths; the test occurred November 19 in America/Chicago.
A coarse native preview ran with no faults and sampled draw maximum 8 ms.

Phillip then asked to remove the dotted geometry appearance. The combined demo
was changed to full-resolution circles (96,128,160) and continuous native vector
radius lines. Before reloading, the known coarse demo was identified and saved:
/tmp/p1gl-type340-20261119/P1GL/build/snapshots/20261120T025328Z-type340/.
Live sample: 264 frames in 10.00008 seconds, mean 37.8791 ms; largest sampled
BBN draw duration 46 ms; program/frame faults zero, buffer guard 0123456 intact.
The largest list is 1,923 words in a 2,048-word buffer. No drum/tape image changed.
Phillip confirmed that the lines and circles look much better. Quality takes
priority over a hard redraw threshold, per Phillip and Bill's guidance.

The display client still says t30dpy3; it presents the Type 340 output as well.
Native labels remain dot matrices. An optional vector-stroke font was discussed
and is a separate next feature, not part of this migration.

The tested v0.8 source/tests are preserved under legacy/type30. The native
Type 340 migration is the v0.9 default backend.

Final clean build and `make test` passed in a separate directory:
/tmp/p1gl-type340-final-20261119/P1GL/.
Eleven host function checks passed. Native CPU verification completed 381 test
executions covering 549 lines, 277 circles and all 1,024 coordinate values;
6,860 captured display lists contained 329,199 native words. All default demo
programs assembled. Frame, line and circle demo drivers were executed to their
CPU-test termination as well as checking their library primitives.

Installed Type 340 device IOT_15.so SHA256:
24132d492e12f9909e1b68e8350956eeb82f80a24f5d5723f435ab4d8d4f50ed.
Installed type340emu.c SHA256:
6d29e2d61dba33872f00ec7e8b9d55a690275c4fd03f230d8dfc9248846a5f14.
See docs/validation/type340-results.json and type340-live-results.json.
