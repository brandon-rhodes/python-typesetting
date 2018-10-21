"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

NONWORD = re.compile(r'(\W+)')
BREAKING_SPACE = re.compile(r'[ \n]+')
ZERO_WIDTH_BREAK = Glue(0, 0, 0)

def wrap_paragraph(width_of, line_lengths, line, text, indent,
                   line_height, # TODO: remove this one
):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    #space_width = width_of(u' ')
    space_width = width_of(u'm m') - width_of(u'mm')
    #space_width *= 0.9
    hyphen_width = width_of(u'-')

    # TODO: should do non-breaking spaces with glue as well
    space = Glue(space_width, space_width * .5, space_width * .3333)

    def word_boxes(word):
        if not word:
            return
        pieces = iter(hyphenate_word(word))
        piece = next(pieces)
        yield Box(width_of(piece), piece)
        for piece in pieces:
            yield Penalty(hyphen_width, 100)
            yield Box(width_of(piece), piece)

    def punctuation_boxes(punctuation):
        if not punctuation:
            return
        yield Box(width_of(punctuation), punctuation)
        if punctuation == u'-':
            yield ZERO_WIDTH_BREAK

    for string in BREAKING_SPACE.split(text):
        i = iter(NONWORD.split(string))
        word = next(i)
        olist.extend(word_boxes(word))
        for punctuation in i:
            olist.extend(word_boxes(punctuation))
            word = next(i)
            olist.extend(word_boxes(word))
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
        r = olist.compute_adjustment_ratio(start, breakpoint, 0,
                                           (line_lengths[0],))

        r = 1.0

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

        line.graphics.append((knuth_draw, xlist))
        line = line.next(line_height)
        start = breakpoint + 1

    return line.previous

def knuth_draw(paint, line, xlist):
    ay = line.ay()
    pt = 1200 / 72.0
    for x, text in xlist:
        paint.drawText(line.chase.x * pt + x, ay * pt, text)
