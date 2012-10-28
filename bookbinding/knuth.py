"""Classes that support Knuth TeX-style paragraph breaking."""

from texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

STRING_WIDTHS = {}

def wrap_paragraph(canvas, line, pp, indent):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    space_width = canvas.stringWidth(u' ')
    hyphen_width = canvas.stringWidth(u'-')

    for word in pp.text.split():
        pieces = hyphenate_word(word)
        for piece in pieces:
            w = STRING_WIDTHS.get(piece)
            if w is None:
                w = STRING_WIDTHS[piece] = canvas.stringWidth(piece)
            olist.append(Box(w, piece))
            olist.append(Penalty(hyphen_width, 100))
        olist.pop()
        olist.append(Glue(space_width, space_width * .5, space_width * .25))
    olist.pop()
    olist.add_closing_penalty()

    # for item in olist:
    #     print item

    line_lengths = [line.w]
    for tolerance in 1, 2, 3, 4:
        try:
            breaks = olist.compute_breakpoints(
                line_lengths, tolerance=tolerance)
        except RuntimeError:
            pass
        else:
            break

    start = 0
    n = 0
    # if 'Confederate' in pp.text:
    #     print breaks, len(olist)
    # if breaks[-1] != len(olist) - 1:
    #     breaks.append(len(olist) - 1)
    for breakpoint in breaks[1:]:
        keepers = []
        r = olist.compute_adjustment_ratio(start, breakpoint, 0, (line.w,))
        # if 'Confederate' in pp.text:
        #     print breakpoint, r
        n += 1
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                box.glue_width = box.compute_width(r)
                keepers.append(box)
            elif box.is_box():
                keepers.append(box)
        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width == hyphen_width:
            b = Box(hyphen_width, u'-')
            keepers.append(b)
        line = line.next()
        graphic = KnuthLine(line)
        graphic.things = keepers
        line.graphics.append(graphic)
        start = breakpoint + 1

    return line

class KnuthLine(object):
    """A graphic that knows how to draw a justified line of text."""

    def __init__(self, line):
        self.line = line

    def draw(self, canvas):
        ww = 0.
        line = self.line
        ay = line.ay()
        for thing in self.things:
            if isinstance(thing, Box):
                canvas.drawString(line.chase.x + ww, ay, thing.character)
                ww += canvas.stringWidth(thing.character)
            elif isinstance(thing, Glue):
                ww += thing.glue_width
