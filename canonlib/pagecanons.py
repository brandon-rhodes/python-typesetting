
def van_de_graaf_rectangle(canvas):
    w, h = canvas._pagesize
    return w * 2./9., h * 2./9., w * 6./9., h * 6./9.

def van_de_graaf(canvas, is_right):
    """Draw the Van de Graaf canon construction on the ReportLab `canvas`."""

    canvas.saveState()
    canvas.setLineWidth(0.5)
    line = canvas.line
    w, h = canvas._pagesize

    if is_right:
        canvas.transform(-1., 0., 0., 1., w, 0.)

    # First we draw a diagonal from the lower outer corner to the top
    # inner corner, then a pair of diagonals across the whole opened
    # book, from each corner to its opposite.

    line(0, 0, w, h)             # main diagonal
    line(0, 0, w, h / 2.)        # bottom half of cross-page diagonal
    line(w, h / 2., 0, h)        # top half of cross-page diagonal

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
