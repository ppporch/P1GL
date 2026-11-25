# G_VTEXT — optional continuous-stroke text, v0.10

`jda gvtext; X; Y; SIZE; STRING_ADDRESS` draws a NUL-terminated AM1 ASCII string
as native Type 340 vectors. It supports all 95 printable ASCII characters,
including lowercase and punctuation. Unsupported nonzero codes become '?'.
The string must be in bank 0 and terminate within 256 characters.

X/Y are baseline coordinates 0..1023. SIZE 0..3 multiplies font units by 1,2,4,8.
The nominal capital height is 21 font units, so these are roughly 21,42,84,168
pixels high. This is a different size convention from native G_TEXT. Glyphs have
proportional advances from their original left/right bearings. Descenders and
other outlying strokes are included in each glyph's bounding box.

Every stroke becomes one or more connected scale-zero Type 340 vectors. The
hardware draws intermediate pixels continuously. Pen lifts do not connect
unrelated strokes; single-vertex strokes are preserved as points. Larger
segments use G_LINE's bounded native-vector segmentation. Whole glyphs crossing
any viewport edge are omitted, while the logical cursor advances normally.

## Integration

Include gplot.ac, gline.ac, gframe.ac and gvtext.am1. Native gtext.ac is
needed only if the program also wants native Type 342 labels. Drawing follows
the usual P1GL ownership rules: build silently between gframe_begin/end, then
refresh; outside a build, immediate scratch lists are safely streamed.

Code, strings, variables and display lists remain in bank 0. The font occupies
1,759 words in a separate read-only extended-memory bank, default bank 1,
starting at 0100. Extended memory must be enabled. Select a free bank before
including gvtext.ac, for example:

```text
#define P1GL_FONT_BANK 3
#include "../src/gvtext.ac"
```

The valid range is banks 1..15; hexadecimal 0xf names bank 15 unambiguously.
Do not place other application data over the font's allocation. Each font fetch
briefly enables extended addressing and restores ordinary mode before calling
other routines. The generated include returns assembly to bank 0. Tests verify
font banks 1,3,15 and read-only contents.

Existing native-only programs do not include the font module and load no extra
bank. The standard frame_demo.rim was checked to remain entirely in bank 0.
G_TEXT remains the compact native-font option. G_VTEXT consumes more list memory
and can take longer to construct/draw; it is an optional quality/scale choice.
All calls clobber AC/IO, use writable non-reentrant linkage and share P1GL faults.
Invalid text inputs set fault 1; frame overflow sets fault 2 and suppresses replay.

## Font data and regeneration

The bundled face is Hershey `futural.jhf`, from
https://github.com/kamalmostafa/hershey-fonts at commit
1356bf2f83d380fcef68c887e88675eb9d445d86. Only font data is used; no library or
application code from that repository is included. Required acknowledgments
and distribution terms are retained in fonts/HERSHEY-NOTICE.txt.

`python3 tools/generate_vfont.py` regenerates generated/vector-font.ac and its
provenance JSON. The packed format is P1GL's own, not the prohibited NTIS format.
Metadata records hold a far pointer, advance, and four bounds; vertex words
hold coordinates and pen-lift/end markers. Source data remains bundled for
reproducible geometry comparisons.

## Verification and demo

`make test-vector-text` executes the actual assembled code through the isolated
PDP-1 CPU runner, captures native lists and checks source-font geometry. Twenty-
four executions cover all 95 glyphs at all four scales, mixed case, punctuation,
clipping, zero coordinates, empty/odd/even strings, retained replay, immediate
streaming, overflow, bad input, length limits and alternate font banks. All
5,122 emitted vectors match expected source geometry and segmentation. Font
memory stays unchanged and ordinary addressing is restored. The structural
model does not replace real beam/timing tests.

`build/vector_text_demo.rim` cycles through four retained scenes: title text,
uppercase, lowercase, and digits/punctuation. All show a large vector P1GL title
and native Type 342 comparison. Scene sizes are 1,854,1,524,1,680,1,440 words,
inside a 2,048-word buffer. The real Pi test has no program/frame fault or guard
damage, and font data stays unchanged. Its 14-second frame-counter sample
averaged 42.81 ms including scene construction; this is not a worst-case latency
or client frame-rate guarantee. Phillip confirmed that the preview looks
fantastic. See docs/validation/vector-text-results.json and the live record.
