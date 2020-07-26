#!/usr/bin/env python

import argparse
import os
import sys

from typesetting.composing import (
    avoid_widows_and_orphans, centered_paragraph, ragged_paragraph,
    run, vspace,
)
from typesetting.knuth import knuth_paragraph
from typesetting.skeleton import single_column_layout, unroll
from typesetting.writer_qt import QtWriter

INCH = 72

def main(argv):
    parser = argparse.ArgumentParser(description='Generate slides')
    parser.parse_args(argv)

    os.chdir(os.path.dirname(__file__))

    actions = [
        (knuth_paragraph, 0, 0, [('bold', 'Steam'.strip())]),
    ]

    page_width = 8.5 * INCH
    page_height = 11 * INCH

    next_line = single_column_layout(page_width, page_height,
                                     INCH, INCH, INCH, INCH)

    writer = QtWriter(page_width, page_height)
    writer.load_font('../../fonts/OldStandard-Regular.ttf')
    writer.load_font('../../fonts/GenBasB.ttf')
    writer.load_font('../../fonts/GenBasR.ttf')

    fonts = writer.get_fonts([
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('old-standard', 'Old Standard TT', 'Regular', 12),
        ('roman', 'Gentium Basic', 'Regular', 12),
        ('roman-small', 'Gentium Basic', 'Regular', 4), #?
    ])

    # TODO: rename "run" to "compose"?
    end_line = run(actions, fonts, None, next_line)
    lines = unroll(None, end_line)[1:]  # TODO: handle None case better?

    # TODO: combine both kinds of verb into one?
    current_page = lines[0].column.page
    for line in lines:
        if line.column.page is not current_page:
            writer.new_page()
            current_page = line.column.page
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            function(fonts, line, writer, *args)

def draw_texts(fonts, line, writer, xlist):
    current_font_name = None
    for x, font_name, text in xlist:
        if font_name != current_font_name:
            font = fonts[font_name]
            writer.set_font(font)
            current_font_name = font_name
        writer.draw_text(line.column.x + x,
                         line.column.y + line.y - font.descent,
                         text)

if __name__ == '__main__':
    main(sys.argv[1:])
