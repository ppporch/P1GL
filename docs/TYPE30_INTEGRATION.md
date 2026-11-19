> Historical v0.4 design note. See ../README.md and verification.md for the tested v0.5 point interface and current status.

# Type 30 integration decision — P1GL v0.4

## Fixed target

P1GL v1.0 targets **Bill Ezell's `pidp1-mods` implementation and `t30dpy` only**, with the AM1 assembler. No original DEC Type 30 compatibility layer is planned.

Upstream: https://github.com/wjenh/pidp1-mods

The upstream README explicitly describes a new Type 30/340 display subsystem, configurable aperture and origin options, lightpen support, and the recommendation to use `t30dpy` instead of `p7sim`. It also notes that the `dpy` coordinate reorigin option conflicts with the lightpen `sdb` IOT; the lightpen setting takes precedence when both are enabled. Accordingly, **coordinate mapping must be validated against the target configuration**, not assumed from a generic PDP-1 description.

## Layer separation

1. `G_PLOT_RAW` — machine-specific point output: AC/IO registers, display instruction, intensity/aperture behavior. Candidate code currently named `gplot`.
2. `G_COORD` — conversion from logical integer viewport 0..1023 to the exact Type 30 coordinate encoding used in Bill's configured emulator. **Not yet implemented.**
3. `G_LINE` — endpoint-inclusive Bresenham generator in logical coordinates; host reference exists, AM1 translation pending.
4. `G_FRAME` — repeated traversal of display commands for phosphor persistence; future module.

## Verification gate (do not skip)

- [ ] Obtain AM1 documentation and a working display example from the exact `pidp1-mods` revision in use.
- [ ] Check whether `dpy-i 4200` is valid AM1 syntax and the correct display IOT for desired intensity/aperture.
- [ ] Check AC/IO coordinate encoding and signedness, including positive and negative zero in ones'-complement arithmetic.
- [ ] Check `jda` return address semantics and indirect operand syntax.
- [ ] Check `t30dpy` configuration for origin shift, lightpen, and display settings.
- [ ] Assemble calibration program with AM1; record warnings and exact command.
- [ ] Execute in the matching emulator; confirm all calibration points appear in correct locations.
- [ ] Verify refresh rate and no flicker at intended point counts.

## Known limitations

The current `gplot.am1` is a **candidate only**; no assembly or emulator success is claimed. `gline.am1.plan` is a design note, not runnable code. Host tests validate the geometry algorithm but cannot validate AM1, Type 30 IOT behavior, or rendering speed.

## Recommended next work

Retrieve the actual AM1 grammar/examples and display test programs, then correct and assemble the low-level point driver before porting Bresenham to assembly. Preserve a hardware-independent host test suite to guard geometry against regressions.
