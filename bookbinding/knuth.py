"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

NONWORD = re.compile(r'(\W+)')
BREAKING_SPACE = re.compile(r'[ \n]+')
ZERO_WIDTH_BREAK = Glue(0, 0, 0)

def knuth_paragraph(
        actions, a, line, next_line,
                    # text,
                    # font_name, indent, temporary_indent,

        width_of, # (font, text)

        line_lengths,
        indent,
        first_indent,
        fonts_and_texts,

                    # switch_font, width_of, line_lengths,# line,
                    # fonts_and_texts,
                    # indent, first_indent,
                    # line_height, ascent
):
    #print(line_lengths)
    #print(indent)
    # line = next_line(line, 2, 10)
    # line.graphics.append((knuth_draw2, text))
    # return a + 1, line

# def wrap_paragraph(
#         # switch_font,
#         line,
#         next_line,
#         line_lengths,
#         width_of, # (font, text)
#         fonts_and_texts,
#         indent,
#         first_indent,
#         # line_height, ascent, # TODO: remove these
# ):

    olist = ObjectList()
    # olist.debug = True

    if first_indent:
        olist.append(Glue(first_indent, 0, 0))

    font = fonts_and_texts[0][0]

    # TODO: get rid of this since it changes with the font?  Compute
    # and pre-cache them in each metrics cache?
    space_width = width_of(font, u'm m') - width_of(font, u'mm')

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
                yield Box(width_of(font, punctuation), punctuation)
                if punctuation == u'-':
                    yield ZERO_WIDTH_BREAK
            if space:
                yield space_glue

    def word_boxes(word):
        pieces = iter(hyphenate_word(word))
        piece = next(pieces)
        yield Box(width_of(font, piece), piece)
        for piece in pieces:
            yield Penalty(width_of(font, u'-'), 100)
            yield Box(width_of(font, piece), piece)

    indented_lengths = [length - indent for length in line_lengths]

    for font, text in fonts_and_texts:
        #switch_font(font_name)
        olist.append(Box(0, font))  # special sentinel
        olist.extend(text_boxes(text))

    olist.add_closing_penalty()

    for tolerance in 1, 2, 3, 4:
        try:
            breaks = olist.compute_breakpoints(
                indented_lengths, tolerance=tolerance)
        except RuntimeError:
            pass
        else:
            break
    else:
        print('FAIL')  # TODO
        breaks = [0, len(olist) - 1]  # TODO

    assert breaks[0] == 0
    start = 0

    for i, breakpoint in enumerate(breaks[1:]):
        r = olist.compute_adjustment_ratio(start, breakpoint, i,
                                           indented_lengths)

        r = 1.0

        xlist = []
        x = 0
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                x += box.compute_width(r)
            elif box.is_box():
                if box.width:
                    xlist.append((x + indent, box.character))
                    x += box.width
                else:
                    xlist.append((None, box.character))

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width:
            xlist.append((x + indent, u'-'))

        print(xlist)
        line = next_line(line, 2, 10)  #TODO line_height, ascent
        line.graphics.append((knuth_draw2, xlist))
        start = breakpoint + 1

    return a + 1, line

def knuth_draw(fonts, painter, line, xlist):
    ay = line.ay()
    pt = 1200 / 72.0
    #painter.setFont(font)
    for x, text in xlist:
        if x is None:
            painter.setFont(fonts[text])
        else:
            painter.drawText(line.chase.x * pt + x, ay * pt, text)

def knuth_draw2(painter, line, xlist):
    pt = 1200 / 72.0
    for x, text in xlist:
        if x is None:
            pass # TODO: set font
        else:
            painter.drawText((line.column.x + x) * pt,
                             (line.column.y + line.y) * pt,
                             text)




    return
    ay = line.ay()
    pt = 1200 / 72.0
    #painter.setFont(font)
    for x, text in xlist:
        if x is None:
            painter.setFont(fonts[text])
        else:
            painter.drawText(line.chase.x * pt + x, ay * pt, text)
