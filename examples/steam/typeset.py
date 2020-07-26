#!/usr/bin/env python

import argparse
import os
import sys

from PySide2.QtWidgets import QApplication

from typesetting.composing import (
    avoid_widows_and_orphans, centered_paragraph,
    run, section_break, vspace,
)
from typesetting.knuth import knuth_paragraph
from typesetting.skeleton import single_column_layout, unroll
from typesetting.writer_qt import QtWriter

INCH = 72
INDENT = INCH / 4

def main(argv):
    parser = argparse.ArgumentParser(description='Generate slides')
    parser.parse_args(argv)

    os.chdir(os.path.dirname(__file__))

    with open('steam.txt') as f:
        essay_text = f.read()

    page_width = 5 * INCH
    page_height = 8 * INCH

    next_line = single_column_layout(
        page_width, page_height,
        1.0 * INCH, 1.0 * INCH, 0.8 * INCH, 0.8 * INCH,
    )

    my_break = section_break, 'roman', ('texts', [(0, 'roman', '* * *')])

    actions = [
        (centered_paragraph, [('roman', ' ')]),
        (vspace, INCH),
        (centered_paragraph, [('bold', 'Steam')]),
        my_break,
        (centered_paragraph, [('roman', 'J. Elmer Rhodes, Jr.')]),
        (centered_paragraph, [('roman', '(1920–1995)')]),
        (vspace, INCH * 3/4),
    ]

    actions.extend(parse_essay(essay_text, my_break))

    QApplication([])
    writer = QtWriter('book.pdf', page_width, page_height)
    writer.load_font('../../fonts/OldStandard-Regular.ttf')
    writer.load_font('../../fonts/GenBasB.ttf')
    writer.load_font('../../fonts/GenBasI.ttf')
    writer.load_font('../../fonts/GenBasR.ttf')

    fonts = writer.get_fonts([
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('italic', 'Gentium Basic', 'Italic', 12),
        ('old-standard', 'Old Standard TT', 'Regular', 12),
        ('roman', 'Gentium Basic', 'Regular', 12),
        ('roman-small', 'Gentium Basic', 'Regular', 4), #?
    ])

    # TODO: rename "run" to "compose"?
    end_line = run(actions, fonts, None, next_line)
    lines = unroll(None, end_line)[1:]  # TODO: handle None case better?

    current_page = lines[0].column.page
    page_no = 1

    for line in lines:
        if line.column.page is not current_page:
            current_page = line.column.page
            writer.new_page()
            page_no += 1
            decorate(current_page, page_no, fonts, writer)
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'texts':
                function = draw_texts
            function(fonts, line, writer, *args)

def parse_essay(text, my_break):
    sections = text.strip().split('\n\n\n')
    for i, section in enumerate(sections):
        if i:
            yield my_break
        section = section.strip()
        paragraphs = section.split('\n\n')
        for j, paragraph in enumerate(paragraphs):
            indent = INDENT if j else 0
            yield avoid_widows_and_orphans,
            yield knuth_paragraph, 0, indent, [('roman', paragraph.strip())]

def decorate(page, page_no, fonts, writer):
    font = fonts['roman']
    text = str(page_no)
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = page.height - INCH * 2/3

    writer.set_font(font)
    writer.draw_text(x, y, text)

    font = fonts['italic']
    text = 'Steam'
    width = font.width_of(text)
    x = (page.width - width) / 2
    y = INCH * 3/4

    writer.set_font(font)
    writer.draw_text(x, y, text)

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
