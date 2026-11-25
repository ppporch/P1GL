# P1GL — PDP-1 Graphics Library

P1GL v0.10 draws through the **Type 340 display processor and Type 342 character
generator** in [Bill Ezell's pidp1-mods](https://github.com/wjenh/pidp1-mods).
It provides reusable AM1 routines for points, native vector lines, midpoint
circles, text, and retained display frames.

The CPU builds native display lists; the Type 340 fetches and executes them.
There are no Type 30 DPY or Type 33 character IOTs in the new backend.
Bill's t30dpy/t30dpy3 window displays both devices, so its window title can still
say “Type 30” while P1GL is using the Type 340.

## Build and run on the Pi

Requires a working pidp1-mods installation with AM1, Type 340/342 devices and
its display client. This is PDP-1 assembly, not native Mac software.

```sh
git clone https://github.com/ppporch/P1GL.git
cd P1GL
make PDP1_ROOT=/opt/pidp1-mods
```

Power on the PiDP-1, save any current work, and halt its program before loading:

```sh
/opt/pidp1-mods/bin/fastload -y build/frame_demo.rim
```

Open t30dpy or t30dpy3. No sense switches are used. The combined demo shows
“P1GL TYPE 340”, a full-resolution circle with a continuous radius line and a
frame number. It cycles through radii 96, 128 and 160. Separate programs are
`build/line_demo.rim`, `build/circle_demo.rim`, `build/gplot_demo.rim`, and
`build/calibrate.rim`. Loading replaces the current program in core.

## Library calls

Arguments are literal inline words, not addresses of coordinate variables:

```text
        jda gplot
        0d100; 0d200

        jda gline
        0d100; 0d200; 0d900; 0d700

        jda gcircle
        0d512; 0d512; 0d160

        jda gtext
        0d100; 0d840; 2; caption
```

`caption` is a NUL-terminated AM1 `ascii` string. Text size 0..3 selects native
scale 1, 2, 4 or 8. Labels use the Type 342 repertoire; standalone `^` and grave
accent are replaced by `?` rather than applying an accent over a preceding glyph.

Include `src/gplot.ac`, `src/gline.ac`, `src/gcircle.ac`, `src/gtext.ac`, and
`src/gframe.ac` as required. P1GL uses `.ac` for reusable code, demos, and calibration,
and `.ah` for definitions. All primitives need the frame module, including
immediate drawing. No external font-table include path is needed.

Coordinates are the full 0..1023 device range, with Y increasing upward.
Points and lines require valid endpoints; circles clip their circumference.
Lines use connected hardware-vector segments with components no larger than
127. Endpoints are exact; the intervening pixels use the Type 340 rate
multiplier rather than the old CPU Bresenham rasterization.

The current implementation places code, data and the display list in bank 0,
in ordinary memory mode. The optional vector font uses a separate memory bank. Calls clobber AC/IO and use non-reentrant writable linkage. See
[API](docs/API.md), [Type 340 migration](docs/TYPE340.md),
[frames](docs/G_FRAME.md), and [text](docs/G_TEXT.md).

## Optional vector-stroke text

`G_VTEXT` draws continuous Hershey strokes using native vectors, while `G_TEXT`
remains the compact native Type 342 option. The vector font supports all 95
printable ASCII characters, proportional spacing, lowercase and punctuation.

```text
        jda gvtext
        0d100; 0d600; 1; caption
```

X/Y are baseline coordinates; size 0..3 selects 1,2,4,8 font units, with a nominal
capital height of 21 units. Include src/gvtext.ac alongside the point, line and
frame modules. The font occupies 1,759 words in a separate memory bank (default
bank 1), and requires extended memory. Programs that do not include this module
load no font bank. Choose a free bank using P1GL_FONT_BANK; see
[vector-text documentation](docs/G_VTEXT.md).

After `make`, preview it on the powered-on, halted PiDP-1 with:

```sh
/opt/pidp1-mods/bin/fastload -y build/vector_text_demo.rim
```

It cycles through four pages of vector text and a native-font comparison. This
replaces the current program, so save current work first. Phillip confirmed that
the preview looks fantastic. All 24 new CPU test executions pass, covering 95
glyphs at four scales, font banks 1/3/15, clipping, read-only font data, restored
ordinary addressing, frame bounds and the exact demo. Previous graphics checks
continue to pass. Stroke text uses more list space and drawing time; it is an
optional choice rather than a replacement for native characters.

## Retained frames

```text
        jda gframe_begin
        frame_buffer
        0d2048             // caller-reserved words, including setup and stop
        // Drawing calls build the scene without starting the display.
        jsp gframe_end
        jsp gframe_refresh // replay; waits for device completion
```

Capacity includes one setup word and two termination words; it must be at least
three. Points take two words, vector segments four, and character groups five.
A sticky fault suppresses replay of an invalid frame; a new begin clears it.
Immediate primitives use a separate small scratch list and stream safe chunks,
leaving a completed retained scene intact. Lists are not modified while active.

The optional [retained groups and labels API](docs/G_RETAINED.md) lets a
program replace a bounded drawing group or update a fixed-width label between
refreshes. Labels support text and signed numbers with decimal places.
Build `build/retained_demo.rim` to try a moving marker and numeric readout.

The optional [viewport API](docs/G_VIEWPORT.md) clips signed line endpoints
to an inclusive rectangular drawing area. The viewport demo moves a diamond
across all four edges of a retained border.

The optional [transform API](docs/G_TRANSFORM.md) scales, rotates and
translates application coordinates. It can draw transformed lines through the
active viewport. The transform demo animates an arrow inside a fixed border.

The optional [vector curves API](docs/G_ARCS.md) draws circles, ellipses and
arcs as connected native vectors, with adjustable angular steps and viewport
clipping. The arc demo shows all three shapes.

The optional [path API](docs/G_PATHS.md) draws clipped polylines, evenly
spaced sample traces, and plus, X, or diamond markers. It keeps the beam in
vector mode across connected segments to reduce display-list size. Build
`build/path_demo.rim` to see the three calls together.

The optional [PENMENU adapter](docs/G_PENMENU.md) connects Bill's light-pen
menu library to retained and immediate drawing. Its demo lets the viewer's
left mouse button select a circle, ellipse or arc.

P1GL uses explicit Type 340 IOT numbers to avoid the shared drum instruction
names. Applications using named IOTs with the Type 23 drum should include Bill's
`TYPE340/type340alt.ah` and use the prefixed names.

## Validation and status

```sh
make test PDP1_ROOT=/opt/pidp1-mods
```

Tests execute assembled code on the installed PDP-1 CPU object, with PDP-1D
extensions disabled. They check all 1,024 coordinate values, 549 line cases,
277 circle cases, text at all four scales, clipping, immediate chunking, frame
lifecycle, exact fits and overflows, and the actual demo programs. Native-list
capture rejects Type 30/33 IOTs. The independent decoder checks command modes,
coordinates, vector endpoints, characters and bounds; it does not replace real
hardware rasterization, glyph rendering or timing tests.

The native combined demo runs on Phillip's PiDP-1 without display faults or
buffer overruns. Phillip confirmed that the full-resolution lines and circles
look much better. Its full-resolution sample averaged 37.88 ms per refresh,
with a largest sampled display draw of 46 ms. This draws substantially more
circle points than the earlier coarse preview. Readability and correct geometry
take priority over a strict redraw threshold. See [verification](docs/verification.md)
and [recorded results](docs/validation/).

Native character labels are still dot-matrix glyphs. Use optional G_VTEXT for
continuous stroke lettering. Menu and popup-keyboard integration remain future work.

The tested Type 30 v0.8 sources and tests remain under `legacy/type30/`; the
original unassembled v0.4 prototype remains under `original-v0.4/`. These are
historical references, not the default backend. Session-specific `tools/live_*`
helpers are not general installers; use the documented loader commands above.

## License and credits

MIT; see LICENSE. Phillip Porch directs the project, suggests features and
performs hardware/visual tests; ChatGPT/Codex writes and tests the implementation.
Bill Ezell's repository supplies AM1, the emulator, device support and integration
examples. SignalAnalysis supplied the RIM decoder and isolated CPU-test harness.
The optional Hershey font data has separate attribution and distribution terms;
see fonts/HERSHEY-NOTICE.txt and fonts/README.md.

## Embedding in an existing display engine

`src/vector_sink.ac` provides a non-owning vector-word emitter for applications
such as Signal Station that already manage their own display lists and interrupts.
The host supplies an AC-word sink, positions the beam, selects VECTOR mode and
unit scale, then calls `jsp p1gl_vector` with signed deltas and an optional END.
No P1GL frame manager, font bank, or device IOT is involved. See
[embedding API](docs/VECTOR-SINK.md). `make test-vector-sink` checks this component.
