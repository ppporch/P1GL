"""P1GL G_LINE reference implementation. Coordinates are logical 0..1023.

The iterator is deliberately independent of PDP-1 Type 30 encoding.
All integer operations can be implemented using PDP-1 add/subtract/branch.
"""

MAX_COORD = 1023


def line_points(x0: int, y0: int, x1: int, y1: int):
    """Return endpoint-inclusive, 8-connected Bresenham pixels, all octants.

    Inputs must be integer coordinates inside the logical display viewport.
    No clipping is performed; rejecting invalid endpoints avoids accidental
    off-screen IOTs until the display driver is verified.
    """
    coords = (x0, y0, x1, y1)
    if any(type(v) is not int or not 0 <= v <= MAX_COORD for v in coords):
        raise ValueError('line endpoints must be integer coordinates 0..1023')
    dx = abs(x1 - x0)
    dy = abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx - dy
    points = []
    while True:
        points.append((x0, y0))
        if x0 == x1 and y0 == y1:
            return points
        e2 = 2 * err
        if e2 > -dy:
            err -= dy
            x0 += sx
        if e2 < dx:
            err += dx
            y0 += sy
