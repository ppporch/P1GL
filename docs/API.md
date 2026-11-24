# P1GL API — v0.10, Type 340

All inline arguments below are literal words. Code/data/list in one 4K bank,
ordinary memory mode; writable, non-reentrant linkage; AC/IO clobbered.
All primitives require gframe.am1 for recording and immediate-list ownership.

| Call | Inline arguments | Behavior |
|---|---|---|
| `jda gplot` | X, Y | Native point, true 0..1023 coordinates |
| `jda gline` | X0, Y0, X1, Y1 | Connected native vectors, exact endpoints |
| `jda gcircle` | CX, CY, radius | Midpoint points, clipped circumference |
| `jda gpolyline` | X/Y table, count, closed flag | Connected vectors clipped to the active viewport |
| `jda gtrace` | Y table, count, start X, X step | Equally spaced samples clipped to the active viewport |
| `jda gmarker` | X, Y, radius, shape | Plus, X, or diamond clipped to the active viewport |
| `jda gtext` | X, Y, size, ASCII address | Native Type 342 glyphs |
| `jda gvtext` | X, Y, size, ASCII address | Optional proportional stroke glyphs |
| `jda gframe_begin` | Buffer address, capacity words | Start a new retained list |
| `jsp gframe_end` | None | Finalize list, return gf_fault in AC |
| `jsp gframe_refresh` | None | Run completed list and wait, return gf_fault |

Coordinates are 0..1023 and Y increases upwards. Point/line endpoints and
circle center/radius bounds remain caller preconditions. Radius zero emits one
center point; circle clipping suppresses offscreen points. All circle symmetry
points are unique in logical/device space. Line rasterization is the native
340 rate multiplier, with segmentation as described in TYPE340.md.

Text scale 0..3 is 1,2,4,8 pixels. Native cursor advance is seven scaled units.
Strings are NUL-terminated AM1 ASCII, at most 256 characters, within the bank.
Whole glyphs and their cursor advance must fit; lower-case descenders are also
checked against the bottom edge. Out-of-repertoire codes and standalone caret/
grave accents become '?'. Invalid text arguments set fault 1.

Frame capacity includes one setup and two stop words, minimum three words.
Points cost two, each vector segment four plus one initial plotted endpoint,
and each character five. Buffer storage must be caller-reserved and nonoverlapping.
An overflow marks the entire retained list invalid; no partial replay occurs.
Immediate calls use safe bounded scratch-list chunks, not a different device.

See G_FRAME.md, G_TEXT.md and TYPE340.md. Type 30-era detailed documents and the
v0.8 implementation are historical; they do not define the v0.9 pixel contract.

Optional G_VTEXT uses the same baseline/string argument shape, but size scales
Hershey font units (nominal capitals 21 units high), rather than the native glyph
matrix. Code/strings/list stay in bank 0; read-only font data occupies a selectable
extended-memory bank, default 1. Whole glyphs are clipped by their full bounds.
All 95 printable ASCII glyphs are available, including standalone caret/grave.
See G_VTEXT.md. Native-only applications do not load the font bank.
