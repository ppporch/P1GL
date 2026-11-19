# Verification checklist

## Before calling the assembly runnable
1. Check AM1 source directives (`org`, `end`) and labels against Bill's local documentation.
2. Check Type 30 `dpy-i` syntax, display mode, AC/IO operand mapping and intensity.
3. Check actual display coordinate width, range, and alignment; the current ±8192 test values are provisional.
4. Confirm signed one's-complement encoding of coordinate words.
5. Confirm whether a device-ready wait or pacing is required and whether tight-loop refresh is appropriate.
6. Assemble with the installed AM1 and inspect diagnostics.
7. Run under Bill's `t30dpy`, checking all nine points and their orientation.
8. Capture a screenshot and adjust scaling/refresh.

## Host-side tests
Run `python3 tests/test_coordinates.py` from the project root.

## Design note
`G_PLOT` should have a documented calling convention, clobber list, and no dependency on Orbit Laboratory or Signal Lab. Prefer a small core library and optional higher-level modules.
