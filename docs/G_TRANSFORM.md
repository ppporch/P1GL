# Application coordinates and transforms

Include `gtransform.ac` with G_VIEWPORT, G_LINE, G_PLOT and G_FRAME. Enable the
PDP-1 Type 10 multiply/divide option. The module uses ordinary same-field
addressing and non-reentrant scratch, like the other drawing modules.

```text
        // Center (512,512), quarter-turn, full X scale and half Y scale.
        jda gtransform_set
        0d512; 0d512; 0d64; 0d1024; 0d512

        // Draw a local horizontal line as a device-space vertical line.
        jda gline_transform
        -0d80; 0; 0d80; 0
```

The transform first scales along the local axes, then rotates counterclockwise
and finally translates. The default is the identity. A transform stays in effect
across frames until replaced. The regular graphics calls use device coordinates.

| Argument | Units and range |
| --- | --- |
| Translation X/Y | Signed pixels, −1023 through +1023 |
| Angle | 0–255, one full turn divided into 256 steps |
| Scale X/Y | Signed Q10, −4096 through +4096. 1024 means 1×. Negative scale mirrors and zero collapses an axis. |
| Local X/Y | Signed integers, −1023 through +1023 |

## Entry points

- `gtransform_set` takes translation X, translation Y, angle, scale X and scale
  Y. It returns AC=0 on success or AC=1 on invalid inputs. An invalid request
  preserves the active transform.
- `gtransform_point` takes local X and Y. It returns AC=0 on success and places
  the signed device coordinates in `gtransform_x` and `gtransform_y`. These may
  be outside the display. Invalid input returns AC=1 and preserves both result
  words. For outlines with shared vertices, transform each vertex once and call
  `gline_clip` on the resulting edges.
- `gline_transform` takes four local endpoint coordinates and clips the result
  against the active viewport. It returns the usual drawing fault in AC and
  sets G_FRAME's argument fault for out-of-range local coordinates. It works
  in immediate mode, a retained frame or a retained drawing group.

The sine table and matrix coefficients use Q10. Coefficients and resulting
coordinates round to the nearest representable value with ties toward the
larger coordinate. The calculation keeps both fractional products until
their sum is rounded. Viewport clipping operates on the resulting integer
endpoints. Angles 0, 64, 128 and 192 give exact cardinal rotations at unit scale.

The [demo](../examples/transform_demo.ac) rotates, scales and moves an arrow
across a retained border. It uses the BBN clock for pacing. Run
`make test-transform` to compare point and line results against the reference
and check every frame of one turn.
