# Short native vector optimization

G_LINE now bypasses the CPU Bresenham pixel walk when both absolute
displacements are at most 127. It emits the same starting point and single
native vector as before, with the same exact endpoint and frame lifecycle.
Zero-length lines remain point-only; larger lines retain the original path.

The complete P1GL suite passes, including native graphics, frames, banked
vector fonts and vector sinks. Orbit Laboratory uses the fast path for its
short outline, text and trajectory segments. This does not change Type 340
hardware scan time; it reduces CPU list-construction work.

The frame module also exposes two optional embedding hooks, exercised by Orbit
Laboratory's PENMENU integration. `P1GL_DISPLAY_ENTRY` supplies a full constant
address for an application-owned display-list wrapper; it overrides **all**
frame/scratch scan addresses, so it is intended for applications using retained
frames exclusively. `P1GL_POLL_HOOK` expands inside the display-completion wait;
a polling routine may read a light-pen hit and resume the device, but must not
modify an active list. Neither hook changes the default library behavior.
Both must be defined before including gframe.am1. Orbit dispatches the saved
pen event only after refresh returns. The full default P1GL suite passes with
the hooks absent; Orbit's production-loop tests exercise the wrapper and hook.
