"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

NONWORD = re.compile(r'(\W+)')
BREAKING_SPACE = re.compile(r'[ \n]+')
ZERO_WIDTH_BREAK = Glue(0, 0, 0)

def wrap_paragraph(switch_font, width_of, line_lengths, line,
                   fonts_and_texts,
                   indent,
                   line_height, # TODO: remove this one
):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    # TODO: get rid of this since it changesd with the font?  Compute
    # and pre-cache them in each metrics cache?
    space_width = width_of(u'm m') - width_of(u'mm')

    # TODO: should do non-breaking spaces with glue as well
    space_glue = Glue(space_width, space_width * .5, space_width * .3333)

    findall = re.compile(r'([\xa0]?)(\w*)([^\xa0\w\s]*)([ \n]*)').findall

    def text_boxes(text):
        for control_code, word, punctuation, space in findall(text):
            if control_code:
                if control_code == '\xa0':
                    yield space_glue
                    yield Penalty(0, 999999)
                else:
                    print('Unsupported control code: %r' % control_code)
            if word:
                yield from word_boxes(word)
            if punctuation:
                yield Box(width_of(punctuation), punctuation)
                if punctuation == u'-':
                    yield ZERO_WIDTH_BREAK
            if space:
                yield space_glue

    def word_boxes(word):
        pieces = iter(hyphenate_word(word))
        piece = next(pieces)
        yield Box(width_of(piece), piece)
        for piece in pieces:
            yield Penalty(width_of(u'-'), 100)
            yield Box(width_of(piece), piece)

    for font_name, text in fonts_and_texts:
        switch_font(font_name)
        olist.append(Box(0, font_name))  # special sentinel
        olist.extend(text_boxes(text))

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
                if box.width:
                    xlist.append((x, box.character))
                    x += box.width
                else:
                    xlist.append((None, box.character))

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width:
            xlist.append((x, u'-'))

        line.graphics.append((knuth_draw, xlist))
        line = line.next(line_height)
        start = breakpoint + 1

    return line.previous

def knuth_draw(fonts, painter, line, xlist):
    ay = line.ay()
    pt = 1200 / 72.0
    #painter.setFont(font)
    for x, text in xlist:
        if x is None:
            painter.setFont(fonts[text])
        else:
            painter.drawText(line.chase.x * pt + x, ay * pt, text)
