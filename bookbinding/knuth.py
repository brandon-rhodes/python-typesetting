"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

NONWORD = re.compile(r'(\W+)')
BREAKING_SPACE = re.compile(r'[ \n]+')
ZERO_WIDTH_BREAK = Glue(0, 0, 0)

def wrap_paragraph(switch_font, width_of, line_lengths, line, text, indent,
                   line_height, # TODO: remove this one
):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    #space_width = width_of(u' ')
    # TODO: get rid of these since they change with the font?
    # Compute and pre-cache them in each metrics cache!
    space_width = width_of(u'm m') - width_of(u'mm')
    #space_width *= 0.9
    hyphen_width = width_of(u'-')

    # TODO: should do non-breaking spaces with glue as well
    space = Glue(space_width, space_width * .5, space_width * .3333)

    def text_boxes(text):
        for string in BREAKING_SPACE.split(text):
            i = iter(NONWORD.split(string))
            word = next(i)
            yield from word_boxes(word)
            for punctuation in i:
                yield from word_boxes(punctuation)
                word = next(i)
                yield from word_boxes(word)
            yield space

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

    #olist.append(Box(0, italic_font))
    olist.extend(text_boxes(text))
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
                if box.width == 0:
                    xlist.append((None, box.character))
                else:
                    xlist.append((x, box.character))
                    x += box.width

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width == hyphen_width:
            xlist.append((x, u'-'))

        line.graphics.append((knuth_draw, xlist))
        line = line.next(line_height)
        start = breakpoint + 1

    return line.previous

def knuth_draw(painter, line, xlist):
    ay = line.ay()
    pt = 1200 / 72.0
    #painter.setFont(font)
    for x, text in xlist:
        if x is None:
            painter.setFont(text)
        else:
            painter.drawText(line.chase.x * pt + x, ay * pt, text)
