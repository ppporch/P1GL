# Type 340 light-pen menus

P1GL's adapter connects retained or immediate drawing to Bill Ezell's
`Am1Includes/PENMENU` library in pidp1-mods. Use a configuration with extended
memory, the Type 340 and Type 342, and the BBN clock. For the viewer, the left
mouse button is the light pen.

Declare a menu using Bill's `PM_BAR` macros, then include `gpenmenu.ah` before
`gframe.am1`. The demo uses direct buttons. Use PENMENU's own declaration and
action rules for dropdown menus and submenus.

```text
#define PM_BAR(L,B) B(circle,"Circle",1) B(ellipse,"Ellipse",2)
#include "../src/gpenmenu.ah"

        // Ordinary addressing, application CPU code in field 0.
        jsp gpen_init
        // Build and end a frame using the usual G_FRAME calls.
        jsp gframe_refresh
        jsp gpen_service  // AC = declared action, or zero

        // Include gpenmenu.am1 with the other field-0 P1GL modules.
        // At a free address in field 1:
#include "../src/gpenmenu-list.ac"

        // At a free address in field 2:
#include <PENMENU/penmenu.ac>
        constants
```

The application places the code and list using its normal AM1 bank and origin
directives. Set `P1GL_PEN_LIST_BANK` to 0 or 1 if needed. Set
`P1GL_PEN_CODE_BANK` to the extended field containing PENMENU's CPU code
(default 2). Reserve space for the list and library in those fields. The
adapter defines the menu return and G_FRAME hooks, so omit other definitions
for those hooks in the same build.

- `gpen_init` enables the clock and initializes PENMENU before the first scan.
- G_FRAME displays the menu, then jumps to the frame or immediate scratch
  buffer selected for that scan. During the scan it reads each light-pen hit
  and resumes the device.
- `gpen_service` consumes the latest saved hit and ticks PENMENU's idle timer.
  Call it after a completed scan and dispatch its AC result. A zero result
  needs no action. When drawing immediate primitives, service after each
  primitive whose hit you want to handle. Only the latest hit since the prior
  service is kept.

Call these entries from the main program with EEM off. The adapter is
non-reentrant and edits menu words only between scans. PENMENU handles
debouncing, including BBN clock wrap. Release for at least 250 ms between
presses on the same button with the default timing.

```sh
make AM1=/opt/pidp1-mods/bin/am1 build/penmenu_demo.rim test-penmenu
# Save your current work and halt the PiDP-1 before loading.
/opt/pidp1-mods/bin/fastload -y build/penmenu_demo.rim
```

Click **Circle**, **Ellipse**, or **Arc** at the top. The test uses the actual
PENMENU code and simulates a device hit, pause and resume. It checks action
delivery, held presses across clock wrap, off-menu hits, and routing to
different retained buffers and to immediate drawing.
