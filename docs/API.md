# P1GL API — v0.9, Type 340

All inline arguments below are literal words. Code/data/list in one 4K bank,
ordinary memory mode; writable, non-reentrant linkage; AC/IO clobbered.
All primitives require gframe.am1 for recording and immediate-list ownership.

| Call | Inline arguments | Behavior |
|---|---|---|
| `jda gplot` | X, Y | Native point, true 0..1023 coordinates |
| `jda gline` | X0, Y0, X1, Y1 | Connected native vectors, exact endpoints |
| `jda gcircle` | CX, CY, radius | Midpoint points, clipped circumference |
| `jda gtext` | X, Y, size, ASCII address | Native Type 342 glyphs |
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
