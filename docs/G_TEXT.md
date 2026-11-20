# G_TEXT — v0.9 Type 342

`jda gtext; X; Y; SIZE; STRING_ADDRESS` accepts AM1 ASCII packing, two nine-bit
characters per word, terminated by NUL. The string must fit in the current bank
and terminate within 256 characters. X/Y are logical baseline coordinates
0..1023; SIZE is 0..3. Invalid arguments or a missing terminator set gf_fault=1.

The hardware scale is 1<<SIZE: 1,2,4,8 pixels. It differs from the Type 33 size
mapping in v0.8. Cursor advance is seven scaled units. A complete glyph, its
final cursor advance and any lower-case descender must fit the screen or that
glyph is omitted. There is no line wrapping. Subsequent logical cursor positions
still advance for omitted glyphs. Lower-case g/j/p/q/y descend two scaled units.

Native Type 342 character groups replace the Type 33 bitmap generator. ASCII
conversion follows Bill's AM1 asciiToType340/type340Shift conventions in eval.c;
paired table entries hold a native character word and a descender marker. The
glyph shapes live in the display device, not in P1GL. Native letters, digits,
punctuation and alternate-set symbols are supported. Caret and grave accent
have hardware overstrike semantics rather than standalone glyphs, so this API
maps them to '?'; other unsupported nonzero codes also become '?'.

Each stored character group sets its absolute position, enters CHARACTER mode
at the desired scale with the dual charset enabled, emits shift/character/escape,
then restores default scale zero and POINT mode. The grouping is atomic for
buffer reservation and immediate scratch streaming. It does not depend on
previous glyph state or hardware autospacing. No Type 30/33 IOT is used.

This remains a native dot-matrix font, which can look dotted at large scales.
The separate G_VTEXT routine now supplies optional continuous-stroke letters.
It coexists with this compact hardware font; see G_VTEXT.md.

All calls require gframe.am1, writable non-reentrant linkage and same-bank data
in ordinary memory mode. AC/IO are clobbered. See TYPE340.md for verification
limits, and legacy/type30 for the earlier character implementation.
