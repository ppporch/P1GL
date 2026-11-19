# G_PLOT candidate interface (v0.2)

This is a **candidate implementation**, not yet assembled or tested in AM1.

## Calling sequence

```
        jda gplot
        xword
        yword
```

The two inline argument words are *values*, not pointers. The routine loads them
using the return-address pointer left in AC by JDA, increments that pointer twice,
loads X into AC and Y into IO, issues the display instruction, and returns after
the arguments. This follows Bill Ezell's published JDA inline-argument convention.

**Caveat:** This implementation is non-reentrant and stores arguments in global
scratch locations. It clobbers AC and IO. Do not use it from interrupt code.

## Coordinate contract (not yet finalized)

For this prototype, `xword` and `yword` are **raw Type 30 encoded words**.
A later `G_COORD` layer will expose application-friendly 0..1023 coordinates.
The ±020000 calibration constants are intentionally provisional.

## Open validation steps

1. Confirm the `dpy-i 4200` opcode/AM1 spelling and whether DPY consumes AC/IO.
2. Confirm AM1 accepts `jda`, `lac i`, `jmp i`, and source layout.
3. Confirm Type 30 coordinate alignment, intensity, and aperture.
4. Confirm cross-bank addressing behavior; prototype is single-bank only.
5. Assemble and run under the matching pidp1-mods emulator and `t30dpy`.
6. Verify points and phosphor persistence before optimizing refresh.

## Why this design

The low-level routine deliberately handles *one point only*. Lines, circles,
coordinate transforms, and retained frame lists are separate modules. This makes
it usable in both Signal Lab and Orbit Laboratory without pulling in unrelated code.

## References

- Bill Ezell, PiDP-1 discussion of JDA inline argument pattern (Jan 22, 2026):
  https://groups.google.com/g/pidp-1/c/mFqc1wEBfzI/m/6UWa9524AgAJ
- https://github.com/wjenh/pidp1-mods
