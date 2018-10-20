"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

NONWORD = re.compile(r'(\W+)')

def wrap_paragraph(width_of, line_lengths, line, pp, indent):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    space_width = width_of(u' ')
    hyphen_width = width_of(u'-')
    space = Glue(space_width, space_width * .5, space_width * .3333)

    for string in pp.text.split():
        i = iter(NONWORD.split(string))
        for word in i:
            if word:
                pieces = hyphenate_word(word)
                for piece in pieces:
                    olist.append(Box(width_of(piece), piece))
                    olist.append(Penalty(hyphen_width, 100))
                olist.pop()
            punctuation = next(i, None)
            if punctuation is not None:
                olist.append(Box(width_of(punctuation), punctuation))
                if punctuation == u'-':
                    olist.append(Glue(0, 0, 0))
        olist.append(space)
    olist.pop()
    olist.add_closing_penalty()

    for tolerance in 1, 2, 3, 4:
        try:
            breaks = olist.compute_breakpoints(
                line_lengths, tolerance=tolerance)
        except RuntimeError:
            pass
        else:
            break
    else:
        breaks = [0, len(olist) - 1]  # TODO

    assert breaks[0] == 0
    start = 0

    for breakpoint in breaks[1:]:
        r = olist.compute_adjustment_ratio(start, breakpoint, 0, (line.w,))

        xlist = []
        x = 0
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                x += box.compute_width(r)
            elif box.is_box():
                xlist.append((x, box.character))
                x += box.width

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width == hyphen_width:
            xlist.append((x, u'-'))

        line.graphics.append(KnuthLine(xlist))
        line = line.next()
        start = breakpoint + 1

    return line.previous

class KnuthLine(object):
    """A graphic that knows how to draw a justified line of text."""

    def __init__(self, xlist):
        self.xlist = xlist

    def draw(self, line, paint):
        ay = line.ay()
        for x, text in self.xlist:
            paint.drawText(line.chase.x + x, ay, text)
