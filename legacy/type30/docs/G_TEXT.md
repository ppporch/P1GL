# G_TEXT — v0.8

`jda gtext` takes four inline literal arguments: X, Y, SIZE, STRING_ADDRESS.
X/Y are bottom-left baseline coordinates 0..1023; SIZE is 0..3. Text is AM1
`ascii "..."` packing, two nine-bit characters per word, ending at the first
NUL. The string must lie in the same bank and terminate within 256 characters.
Bank crossing, bad input coordinates/size, or a nonterminated 256-character
limit sets gf_fault=1. Printable ASCII 32..126 is drawn; any other nonzero code
is replaced by '?'. ASCII NUL always terminates.

The Type 33 dot spacing is 2+SIZE. Glyphs span four spacings horizontally and
six vertically, and the cursor advances 6*(2+SIZE)+2 per character. X increases
to the right; glyph rows increase Y from the baseline. A glyph crossing the
right/top viewport edge is omitted as a whole; text does not wrap. Unsupported
input positions are rejected rather than sent to the device. G_PLOT's logical
zero-to-one device mapping also applies to text origin coordinates.

Font data is Bill Ezell's Am1Includes/SYMGEN/ascchars.ac, included directly from
pidp1-mods so no copy of his table is maintained here. Configure AM1's include
search with -I/opt/pidp1-mods/Am1Includes. Requires gplot.am1/gcoord and gframe.am1.
Compile with P1GL_FRAME for integrated geometry capture. All calls use writable,
non-reentrant same-bank code in ordinary memory mode and clobber AC/IO.

The glyph is positioned explicitly using SDB at intensity field 2. GLF sets size
without autospacing; GPL and GPR each wait for completion. This avoids inherited
character format/spacing state. Labels use the real Type 33 matrix timing, not
one CPU DPY per text dot. When recording, the five-word glyph payload is saved;
the string and font table need not be read again during refresh.

CPU tests check odd/even packing, empty strings, unsupported codes, invalid size,
string length, whole-glyph clipping, exact edge placement, and all printable
characters against Bill's actual font words. They also verify immediate labels
and retained labels in combination with points. Live screenshot inspection shows
clear P1GL GRAPHICS and FRAME 1 labels; Phillip confirmed that the combined demo and labels look good.
