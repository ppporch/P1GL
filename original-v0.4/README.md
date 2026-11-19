# P1GL — PDP-1 Graphics Library

## Milestone 1: Type 30 calibration (draft)

A standalone graphics library intended for PDP-1 programs, initially targeting Bill Ezell's PiDP-1 Mods environment and AM1 assembler.

### Current contents
- `src/calibrate.am1`: first candidate calibration program, plots nine reference points repeatedly.
- `tests/test_coordinates.py`: verified host-side PDP-1 one's-complement coordinate encoding tests.
- `docs/verification.md`: outstanding machine-specific checks and test procedure.

**Status:** The assembly is a candidate, **not yet assembled or executed**. Do not treat it as validated AM1 source. The coordinate scaling, `dpy-i 4200` mode, assembler directives, and source load procedure need verification against the installed AM1 and Type 30 examples.

### Roadmap
1. Confirm AM1 syntax and Type 30 coordinate encoding; assemble and run calibration.
2. Extract a callable `G_PLOT` primitive.
3. Add Bresenham `G_LINE` and midpoint `G_CIRCLE`.
4. Add example programs and API documentation.

### References
- https://github.com/wjenh/pidp1-mods
- https://obsolescence.dev/pidp1-mods.html

## Milestone 1.1 — G_PLOT candidate (v0.2)
- `src/gplot.am1`: non-reentrant JDA/inline-argument point plot routine.
- `examples/gplot_demo.am1`: five-point calibration driver; append the routine
  into the same source until the AM1 include/build conventions are confirmed.
- `docs/G_PLOT.md`: calling convention, caveats, verification checklist.
- `tests/test_gplot_contract.py`: host-side static contract checks.

**Still unverified:** AM1 assembly, actual DPY mode, coordinate scaling, and emulator execution.

## Milestone 1.2 — G_LINE reference (v0.3)

- `reference/gline.py`: endpoint-inclusive, all-octant Bresenham algorithm.
- `tests/test_gline.py`: octants, reverse symmetry, edge cases and invalid coordinates.
- `docs/G_LINE.md`: interface contract and AM1 porting gates.
- `src/gline.am1.plan`: assembly implementation plan, **not runnable assembly**.

The logical-coordinate API and the earlier G_PLOT hardware-word prototype are not yet compatible; a verified conversion layer is required. No AM1 compilation or emulator execution has been performed.

## v0.4 integration update (2026-11-19)

**Scope frozen:** Bill Ezell's improved Type 30 / `t30dpy` and AM1 exclusively. See `docs/TYPE30_INTEGRATION.md` for the interface boundaries and hardware verification gate. Extended host-side tests cover all eight line octants, endpoint reversal, full-screen lines, and geometric error bounds. The AM1 driver remains provisional until assembled and executed against Bill's matching emulator.
