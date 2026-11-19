# Architecture notes

The Type 30 is a point-plotting CRT, not a pixel-addressable raster screen. P1GL should not promise a screen-clear operation unless implemented by the surrounding display environment. Repeated plotting is required for persistent images.

Recommended separation:
1. Geometry routines: generate bounded coordinate pairs.
2. Hardware adapter: translate a coordinate pair to verified Type 30 instructions.
3. Optional display-list player: regenerate frames without recomputing geometry.

Avoid hardcoding a guessed PDP-1 instruction sequence. Verify coordinate word packing, display timing, coordinate polarity, and applicable assembler syntax before implementation.
