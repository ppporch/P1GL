# Polylines, sample traces, and markers

Include `gpath.am1` alongside G_VIEW, G_LINE, G_PLOT, and G_FRAME. These calls
use the active [viewport](G_VIEWPORT.md), which defaults to 0–1023 inclusive on
both axes. Enable Type 10 multiply/divide. Code, data, and tables must reside
in the current field with extended addressing off. Calls clobber AC and IO
and use writable, non-reentrant linkage.

```text
        jda gpolyline
        vertices; 4; 1                  // four X/Y pairs, closed

        jda gtrace
        samples; 0d64; 0d128; 0d12      // 64 Y values from X=128 in steps of 12

        jda gmarker
        0d512; 0d384; 0d16; 2          // diamond around (512, 384)
```

| Call | Inline arguments |
| --- | --- |
| `gpolyline` | Address of consecutive X/Y pairs, vertex count, closed flag (0 or 1) |
| `gtrace` | Address of consecutive Y values, sample count, starting X, signed X step |
| `gmarker` | Center X/Y, radius (0–1023), shape (0 plus, 1 X, 2 diamond) |

Source coordinates, generated coordinates, and the trace step must be in
−8191…8191. A zero count draws nothing. A one-vertex path or zero-radius marker
draws a point if visible. Closing a path with at least two vertices adds the
last-to-first edge. A trace supports either direction and a zero step.

Edges clip individually using the viewport's pixel rounding. A hidden edge
or a change in the clipped start position breaks the current visible run.
Batches hold up to 32 native vectors and return to POINT mode. This lets paths
draw immediately, record in a frame, or fit inside a retained group. A batch of
N native vectors takes N+3 words. Long edges can split into multiple native
vectors. Allow two words for each standalone point. Frame setup and termination
take three additional words. G_PATH includes and binds the vector sink to the frame writer.
Use that binding when including G_PATH.

Calls return the frame fault in AC, zero on success. An invalid argument
sets fault 1. Capacity errors use the normal G_FRAME fault 2. A fault suppresses
retained frame replay. Immediate mode can already have displayed earlier
batches when a later coordinate is invalid.

Build `build/path_demo.rim` for a closed border, a clipped sample trace, and
three markers. `make test-paths` checks assembled code and decoded native
lists. On a 19-edge trace the lists used 117 words with repeated G_LINE calls
and 25 with G_POLYLINE. The nominal Type 340 scan model estimates 3.035 ms and
1.280 ms respectively. These figures are for replay of the captured lists
and exclude CPU list construction, channel contention, and host scheduling.
