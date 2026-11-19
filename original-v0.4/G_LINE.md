# G_LINE — design and validated reference, v0.3

## Contract

`G_LINE(x0,y0,x1,y1)` draws both endpoints in logical 10-bit coordinates (0..1023). In v0.3 the caller must supply endpoints inside the viewport; clipping is reserved for a later module. Zero-length lines plot exactly one point. No floating point or multiplication is required.

## Algorithm

Use the symmetric all-octant Bresenham algorithm from `reference/gline.py`. The error value is `dx-dy`; each step doubles it (a single addition) and conditionally updates X and/or Y. The maximum error magnitude stays small enough for signed 18-bit one's-complement arithmetic at this viewport size. Conditional comparisons require careful handling of signed zero in PDP-1 assembly.

## Hardware interface

The final AM1 routine will call G_PLOT once for each logical point. **Important:** the existing `gplot.am1` prototype expects pre-encoded Type 30 words, while this reference accepts unsigned logical coordinates. We must finalize and test the coordinate transform before wiring the two routines together. Do not treat `gplot.am1` as a production ABI yet.

## AM1 integration gate

1. Verify AM1 source syntax, JDA argument/return semantics, indirect-address and increment instructions from Bill's docs/examples.
2. Verify Type 30 DPY operand, X/Y register ordering, signed coordinate scaling, and refresh behavior.
3. Implement logical-to-device transform; document AC/IO clobbers and reentrancy.
4. Port tested Bresenham reference into `gline.am1`, run assembler and debugger, then compare plotted points with reference vectors.

The repository source was not available for local cloning in this session. **No PDP-1 assembly execution or display verification is claimed.**
