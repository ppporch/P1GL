# Non-owning native vector emitter

This adapter integrates P1GL with an application that already owns list memory,
refresh scheduling and interrupts. Define P1GL_VECTOR_EMIT before including
src/vector_sink.ac. The macro consumes one native word in AC and may clobber
AC/IO; it is responsible for buffer bounds and any extended-memory store.
The emitter itself performs no device IOT and starts/stops no display.

Call `jsp p1gl_vector` after setting:

- p1gl_vdx and p1gl_vdy: signed one's-complement displacement -1023..1023.
- p1gl_vtail: zero to stay in VECTOR, or T_END/0400000 to return to PARAMETER.

The beam must already be positioned, with VECTOR mode selected at scale zero.
On return p1gl_vfault is zero for success or one for invalid arguments, and
p1gl_vcount is the number of emitted words. Inputs are unchanged. Negative zero
is accepted. Invalid input emits no partial path. Buffer failure handling belongs
to the sink and application. A zero displacement still emits one word so an END
request can change mode correctly; hardware draws no zero-length vector.

Components are bounded to 127. Axial paths use greedy 127-unit pieces; other
paths split integer halves, using a four-level private stack and preserving the
total displacement. At most sixteen words are required in the supported domain.
END is set only on the final word. Intermediate integer split points may differ
slightly from ideal fractional positions; this is native pixel-grid geometry,
not a promise of an identical Bresenham raster. Signal Station preserves every
original sample endpoint when using this emitter.

Code, inputs and scratch share one memory bank with ordinary addressing mode
and DAP return linkage; unlike the standalone frame manager the bank need not
be bank 0. Scratch is private to this routine and non-reentrant. An independent
ISR may interrupt it if the ISR preserves AC/IO/addressing/overflow state and
does not call this emitter or reuse its scratch.

Executed tests cover 4,496 signed displacements, an AC-clobbering sink, bounds,
sign, connected endpoints, exact total movement, final END placement, axis
chunk counts, and five invalid inputs. The largest tested path uses fifteen
words; the documented bound is conservatively sixteen. The largest measured
split-endpoint perpendicular deviation in that set is 1.311 pixels. Hardware
rasterization and live timing are tested separately by consuming applications.

SignalAnalysis vendors only this module, type340.ah and the GPL license so its
standalone source package remains self-contained. It binds the sink to its
existing inactive-buffer writer, keeping the sequence-break refresh protocol.
