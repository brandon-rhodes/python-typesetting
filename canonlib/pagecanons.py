
def diagonals(canvas, is_right=False):
    """Draw a diagonal across the page, and diagonals across the whole book."""

    canvas.saveState()
    w, h = canvas._pagesize
    if is_right:
        canvas.transform(-1., 0., 0., 1., w, 0.)

    canvas.line(0, 0, w, h)             # main diagonal
    canvas.line(0, 0, w, h / 2.)        # bottom half of cross-page diagonal
    canvas.line(w, h / 2., 0, h)        # top half of cross-page diagonal

    canvas.restoreState()

def van_de_graaf_rectangle(canvas):
    w, h = canvas._pagesize
    return w * 2./9., h * 2./9., w * 6./9., h * 6./9.

def van_de_graaf(canvas, is_right=False):
    """Draw the Van de Graaf canon construction on the ReportLab `canvas`."""

    w, h = canvas._pagesize

    diagonals(canvas, is_right)

    line = canvas.line
    canvas.saveState()
    if is_right:
        canvas.transform(-1., 0., 0., 1., w, 0.)

    # Next, we figure out where the diagonals intersect.

    ix = w * 2./3.
    iy = h * 2./3.

    # Draw a vertical from that point to the page top, and then
    # diagonals between its ends that cross over to the same vertical on
    # the opposite page.

    line(ix, iy, ix, h)
    line(ix, iy, w, (h + iy) / 2.)
    line(ix, h, w, (h + iy) / 2.)

    # Draw the actual content rectangle.

    canvas.rect(*van_de_graaf_rectangle(canvas))

    # All done.

    canvas.restoreState()
