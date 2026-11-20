# Retained frames — v0.9 Type 340

The frame is now a native display program rather than a CPU replay of raw
Type 30 coordinate pairs and Type 33 glyph payloads. See TYPE340.md for encoding
and ownership details; the v0.8 document is under legacy/type30/docs/.

`jda gframe_begin; BUFFER_ADDRESS; CAPACITY_WORDS` resets fault and counts and
starts silent recording. The caller reserves nonoverlapping storage in the
same 4K bank. Capacity includes setup and stop, so the minimum is three words.
`jsp gframe_end` finalizes the list and restores immediate operation.
`jsp gframe_refresh` runs the list, waits for display completion and checks edge
status. End and refresh return gf_fault in AC.

Counts gf_points, gf_vectors and gf_chars describe recorded explicit points,
native vector segments and character groups. A line includes one explicit start
point, then bounded vector segments. Counts do not imply total displayed dots.
Frame size gf_used includes one setup, all commands, the POINT-to-PARAMETER word
and HALT. A single point takes two words, a vector segment four, a character five.
The private encoding is not a disk format or promised binary API.

Points, lines, circles and text retain call order. All complete command groups
leave POINT mode selected. Type 342 text changes scale and character mode,
then restores scale zero and POINT mode. Frame finalization explicitly leaves
POINT mode before HALT; tests catch mode errors and trailing/unbounded lists.

The descriptor is not stored in the buffer. One completed frame is active;
there is no double buffering, interrupt restart or concurrent construction.
Do not alter the list while active. The blocking refresh call guarantees the
device is stopped before it returns. New begin discards the prior descriptor.

Immediate calls use their own 64-word list and do not overwrite a retained list.
When necessary, completed groups are streamed as multiple display runs, with
completion checked before each scratch reuse. Nested primitives share one
outer operation, so circles do not issue a separate IOT for every point.

Faults are 1 invalid input, 2 buffer capacity, 3 lifecycle, 4 display edge status.
Faults are sticky until a new begin. A failed retained frame is never partly
replayed. The caller owns point/line input validity and memory allocation.
Code/data/list share one bank, ordinary memory mode; AC/IO clobbered, writable
non-reentrant linkage. See API.md for calls and TYPE340.md for test limits.
