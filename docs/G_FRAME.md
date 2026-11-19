# Retained display frames — v0.8

Compile with P1GL_FRAME defined before including gplot.am1; include gframe.am1.
The optional branch in G_PLOT records its converted coordinates during a build,
so existing G_LINE and G_CIRCLE calls automatically participate. Ordinary builds
without this definition retain their original immediate behavior and do not
require the frame module. With the module, calls outside a build are immediate.

## Calls

- `jda gframe_begin; BUFFER_ADDRESS; CAPACITY_WORDS`: clear the current scene and
  its fault, set the recording mode, and initialize a caller-owned buffer.
- `jsp gframe_end`: finish recording, restore immediate drawing, return gf_fault
  in AC. No display I/O occurs.
- `jsp gframe_refresh`: replay the completed scene; return gf_fault in AC.

Arguments are literal inline words. The buffer must be reserved in the same
4K bank without overlapping program/data. Capacity is positive and the entire
buffer must fit in addresses 0..07777. Range checks prevent bank crossing;
allocation ownership and overlap are the caller's responsibility.

The descriptor is held in library work words, not in a serializable file header.
Only one scene descriptor is active. There is no interrupt locking, simultaneous
producer/consumer operation, or buffer swapping in this first version. All P1GL
calls require writable code, ordinary memory mode, and non-reentrant same-bank
linkage, and clobber AC/IO.

## Storage and replay

Points consume two words each and characters five. Points grow from the low end
of the buffer and characters from the high end. Before every append the two
frontiers are checked; a failed append sets a sticky fault without writing past
the available space. The private character layout is format, raw Y, raw X,
left bitmap, right bitmap. It is not a public file format.

Refresh outputs all points first, then characters in their original text-call
order. Everything has an absolute position; text placement does not depend on
hardware autospacing state. As on a persistence CRT, refresh does not instantly
clear earlier phosphor traces. Beginning a new scene changes future replay, not
existing phosphor decay. The application decides its refresh schedule.

Point replay is a tight synchronous Type 30 DPY loop. Text uses Bill's Type 33
GLF, Type 30 SDB positioning, synchronous GPL, then synchronous GPR. Character
payloads are read directly from the frame, avoiding a copy on every refresh.

## Faults

- 0: success.
- 1: invalid buffer or G_TEXT argument/string limit.
- 2: insufficient frame space.
- 3: refresh called before end.

Any fault suppresses the entire frame's subsequent refresh. Begin clears the
fault and all counts, allowing recovery with a new valid scene. Previously
recorded partial data is not displayed. Outside a build, immediate drawing is
not globally disabled by a prior frame fault.

## Verification

Twenty-four CPU-executed tests verify 998 IOT transactions, including silent
building, exact-fit mixed scenes, repeated replay, point/text overflow, omitted
partial frames, refresh during build, bad buffers, recovery, immediate drawing,
text packing, all printable ASCII and the actual combined demo. Memory guards
remain intact. IOT capture does not emulate Type 33 timing or its rendered dots.
Live device operation and screenshot inspection verify those separately.

The combined demo contains 82, 110, or 134 retained points and twenty characters,
using at most 368 of its 512 buffer words. It uses a demo-only 8x magnification
for geometry; labels remain in screen coordinates. The BBN clock supplies nominal
22 ms pacing, with its 60,000 ms rollover handled. Scene construction occurs
between pages and can add a short delay.

An initial copying implementation measured mean 26.18 ms, largest sampled draw
29 ms. Direct character replay preserves the exact output transaction sequence
and measured mean 22.94 ms, largest sampled draw 22 ms. These are observations,
not hard bounds or client frame-rate measurements. Readability and correct
geometry take priority over enforcing a strict refresh target.
