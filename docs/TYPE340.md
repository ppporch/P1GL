# Type 340 migration — v0.9

The new default backend emits native Type 340 display programs. It no longer
replays CPU Type 30 DPY calls or Type 33 character commands. The same t30dpy
client continues to show the result; its name does not identify which device
produced the display commands.

## What changed

- All 1,024 positions on each axis are distinct, including coordinate zero.
- Lines are connected native vectors. A CPU Bresenham walk chooses boundaries
  every 127 major-axis steps and at the endpoint, ensuring legal components and
  exact endpoint coordinates. The hardware determines the intermediate pixels;
  they are not promised to match the old Bresenham pixels one for one.
- Circles keep the tested midpoint geometry and clipping. Their points are
  recorded into native POINT-mode commands, without a CPU IOT per displayed dot.
- Text uses Type 342 character commands and native scales 1, 2, 4, 8. The ASCII
  conversion follows Bill's AM1 mapping. Accent commands are not standalone
  printable glyphs, so caret/grave accent are replaced by question marks.
- Frames are native display lists. The point/text split-buffer layout is gone.
  Setup and termination consume three words, points two, each native vector
  segment four, and characters five. P1GL_FRAME is no longer required.

All complete primitive command groups enter and leave POINT mode. Before HALT,
a nonvisible point-mode word changes to PARAMETER mode; HALT is then meaningful.
The tests explicitly decode these mode changes. An empty completed list is valid.

## Ownership and errors

`gframe_begin` validates its same-bank buffer and resets sticky faults.
`gframe_end` appends the nonvisible escape and HALT, and marks the list ready.
`gframe_refresh` starts DLA and waits for DSS before returning. Vertical and
horizontal edge flags are checked; fault 4 reports a device edge error.
The CPU never overwrites a list while the display is reading it.

Outside a frame build, nested primitives share a private 64-word scratch list.
When a complete group will not fit, the CPU appends termination, runs and waits,
and restarts the scratch list before appending that group. Thus even large
immediate circles do not need a large private framebuffer. A completed retained
list remains separate and may be refreshed after immediate drawing.

The descriptor and linkage are not reentrant. Code, variables and lists reside
in one 4K bank, ordinary addressing mode. Interrupt-driven refresh and
concurrent scene construction need a later ownership/API design; they are not
silently enabled by this migration.

Faults are 1 invalid arguments, 2 capacity, 3 lifecycle, 4 device edge status.
A fault suppresses later replay until a new begin resets it. As with the earlier
API, valid point/line endpoints and valid circle center/radius are caller
preconditions; generated circumference points are clipped before submission.

## Drum name conflicts

Bill's TYPE340/IMPORTANT.md warns that Type 340 and Type 23 drum include files
share instruction names. P1GL avoids those names entirely and emits explicit
IOTs 015, 0217, 0417 and 01017 for display start/status. It does not issue drum
IOTs. Applications using named definitions should use type340alt.ah and the
`t340...` prefixed names alongside the drum's prefixed names.

## Verification limits

CPU tests capture native lists at DLA and model immediate completion. An
independent Python decoder validates parameter/point/vector/character modes,
stop words, bounds, exact line endpoints, text codes and point geometry. It is
not a second implementation of the real 340 rate multiplier, glyph drawing,
HSC cycle stealing, timing, light pen or interrupts. Live tests and screenshot
inspection verify actual device execution separately.

The coarse native preview measured a largest sampled draw of 8 ms. After
Phillip requested solid circles, the demo switched from magnified sparse points
to every midpoint-circle pixel: radii 96, 128, 160. The full-resolution lists are
1,199, 1,563 and 1,923 words, safely inside their 2,048-word buffer. Its recorded
mean refresh was 37.88 ms, sampled largest draw 46 ms, no fault or guard damage.
The redraw observations are not hard latency bounds or client frame rates.
Phillip confirmed that the full-resolution lines and circles look much better.

Bill's PENMENU and PENKBD libraries target this device and may be useful for a
later interactive application; they are not part of this initial migration.
