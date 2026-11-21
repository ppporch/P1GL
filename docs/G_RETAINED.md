# Retained drawing groups and labels

Build a frame once, then replace individual drawing groups or update fixed-width
native Type 342 labels. Refresh still uses G_FRAME's synchronous scan. Update
between scans, from the main program, with ordinary same-bank addressing.

Define `P1GL_RETAINED` before including `gframe.am1`. Include `gretained.am1`
as well as the usual G_FRAME, G_TEXT and G_PLOT modules. Applications using the
default G_FRAME build do not allocate the new routines or state. See
[the demo](../examples/retained_demo.am1) for a complete program.

## Drawing groups

```text
        jda gframe_begin
        scene; 0d400
        // Draw static geometry here.
        jda ggroup_define
        marker; 0d24
        jda gline
        0d410; 0d550; 0d440; 0d580
        jsp ggroup_end
        jsp gframe_end

        // Later, replace the marker while keeping the same frame.
        jda ggroup_replace
        marker; scratch
        jda gline
        0d420; 0d550; 0d450; 0d580
        jsp ggroup_end
        jsp gframe_refresh
```

`marker` is a caller-owned three-word handle initialized with `0; 0; 0`.
The slot capacity is in display words and is reserved inside the frame. A
shorter group fills its remaining words with invisible POINT commands.
Groups are flat. Close a group before defining another group, defining a
label or ending the frame.

Replacement scratch must hold the full slot and be disjoint from the frame,
handles, code and other live data. You can reuse one scratch area for
successive replacements. Check AC after opening the replacement, then issue
drawing calls and close it. Closing returns the drawing fault in AC. If the
replacement exceeds its slot or drawing fails, the previous frame remains
ready to refresh with its original group. As with the ordinary frame API, stay
within the geometry bounds of the individual primitives.

## Updatable labels

```text
        // While constructing the frame, outside any group.
        jda glabel_define
        reading; 0d10; 0d440; 0d330; 2

        // After gframe_end, between refreshes.
        jda glabel_text
        reading; message
        jda glabel_number
        reading; -0d125; 2
```

`reading` is another three-word handle initialized to zero. The label
starts blank and uses five display words per cell. Width is 1–32 cells.
X, Y and size are passed as with G_TEXT. Y must be at least 16 to allow
descenders and every cell must fit on the screen.

G_LABEL_TEXT accepts NUL-terminated AM1 packed ASCII, aligns it left
and fills the remaining cells with spaces. G_LABEL_NUMBER takes a signed
18-bit one's-complement integer and 0–5 decimal places. It aligns the result
right, including the sign and decimal point. The example above displays
`-1.25`. Zero has no minus sign. Updates check the fit before writing and
change only native glyph words, so neighboring geometry and label positions
stay fixed. This API uses G_TEXT's native character repertoire.

## Faults and lifetime

AC is zero on success. A nonzero return is a G_FRAME fault code (1 invalid
arguments, 2 capacity, 3 lifecycle). A failed definition also sets the
active frame's fault. A failed update of a completed frame preserves the last
valid contents. G_FRAME’s primitive counters describe the initial frame build. Call `ggroup_end` for each successfully opened group, even
when one of its drawing calls failed.

Treat handles as opaque. A new `gframe_begin` invalidates the previous
frame's handles. Reuse their storage by defining them again. The library uses
a one-word generation counter, so discard old handles before the counter
wraps. Calls are non-reentrant. Use the normal drawing calls inside a group
and keep handles and scratch outside display buffers.
