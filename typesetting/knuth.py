"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

import re
from .vendored.texlib_wrap import ObjectList, Box, Glue, Penalty
from .vendored.hyphenate import hyphenate_word

_zero_width_break = Glue(0, 0, 0)

def knuth_paragraph(actions, a, fonts, line, next_line,
                    indent, first_indent, fonts_and_texts):

    font_name = fonts_and_texts[0][0]
    font = fonts[font_name]
    width_of = font.width_of

    # Design simplification: if any line will require extra leading,
    # then all lines are spaced farther apart.
    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

    line = next_line(line, leading, height)
    line_lengths = [line.column.width]  # TODO: support interesting shapes

    if first_indent is True:
        first_indent = font.height

    olist = ObjectList()
    # olist.debug = True

    if first_indent:
        olist.append(Glue(first_indent, 0, 0))

    # TODO: get rid of this since it changes with the font?  Compute
    # and pre-cache them in each metrics cache?
    space_width = width_of('m m') - width_of('mm')

    # TODO: should do non-breaking spaces with glue as well
    space_glue = Glue(space_width, space_width * .5, space_width * .3333)

    indented_lengths = [length - indent for length in line_lengths]

    for font_name, text in fonts_and_texts:
        font = fonts[font_name]
        width_of = font.width_of
        boxes = break_text_into_boxes(text, font_name, width_of, space_glue)
        olist.extend(boxes)

    if olist[-1] is space_glue:
        olist.pop()             # ignore trailing whitespace

    olist.add_closing_penalty()

    for tolerance in 1, 2, 3, 4, 5, 6, 7:  # TODO: went to 7 to avoid errors
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

    font = 'body-roman'

    for i, breakpoint in enumerate(breaks[1:]):
        r = olist.compute_adjustment_ratio(start, breakpoint, i,
                                           indented_lengths)

        #r = 1.0

        xlist = []
        x = 0
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                x += box.compute_width(r)
            elif box.is_box():
                font_name, text = box.content
                xlist.append((x + indent, font_name, text))
                x += box.width

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width:
            xlist.append((x + indent, font_name, '-'))

        line.graphics.append(('knuth_boxes', xlist))
        line = next_line(line, leading, height)
        start = breakpoint + 1

    return a + 1, line.previous

# Regular expression that scans text for control codes, words, punction,
# and runs of contiguous space.  If it works correctly, any possible
# string will consist entirely of contiguous matches of this regular
# expression.
_text_findall = re.compile(r'([\u00a0]?)(\w*)([^\u00a0\w\s]*)([ \n]*)').findall

def break_text_into_boxes(text, font_name, width_of, space_glue):
    #print(repr(text))
    for control_code, word, punctuation, space in _text_findall(text):
        #print((control_code, word, punctuation, space))
        if control_code:
            if control_code == '\u00a0':
                yield Penalty(0, 1000)
                yield space_glue
            else:
                print('Unsupported control code: %r' % control_code)
        if word:
            strings = hyphenate_word(word)
            if punctuation:
                strings[-1] += punctuation
            for i, string in enumerate(strings):
                if i:
                    yield Penalty(width_of('-'), 100)
                yield Box(width_of(string), (font_name, string))
        elif punctuation:
            yield Box(width_of(punctuation), (font_name, punctuation))
        if punctuation == '-':
            yield _zero_width_break
        if space:
            yield space_glue
