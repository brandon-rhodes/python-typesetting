#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys

from typesetting.composing import run
from typesetting.document import Document
from typesetting.knuth import knuth_paragraph
from typesetting.pyside2_backend import get_fonts
from typesetting.skeleton import single_column_layout, unroll

def main(argv):
    parser = argparse.ArgumentParser(description='Generate slides')
    parser.parse_args(argv)

    factor = 72 / 4
    d = Document(16 * factor, 9 * factor)

    fonts = get_fonts(d.painter, [
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('roman', 'Gentium Basic', 'Roman', 12),
        ('typewriter', 'Courier', 'Roman', 12),
    ])

    margin = 1 * factor
    next_line = single_column_layout(16 * factor, 9 * factor,
                                  margin, margin, margin, margin)

    actions = [
        (knuth_paragraph, 0, 0, [('roman', """

        Hobbits delighted in such things, if they were accurate: they
        liked to have books filled with things that they already knew,
        set out fair and square with no contradictions.

        """.strip())]),
        (knuth_paragraph, 0, 0, [('bold', """
        2. Concerning Pipe-weed
        """.strip())]),
        (knuth_paragraph, 0, 0, [('roman', """

        There is another astonishing thing about Hobbits of old that
        must be mentioned, an astonishing habit: they imbibed or
        inhaled, through pipes of clay or wood, the smoke of the burning
        leaves of a herb, which they called pipe-weed or leaf.

        """.strip())]),
    ]
    run_and_draw(actions, fonts, None, next_line, d.painter)

    d.painter.end()

def run_and_draw(actions, fonts, line, next_line, painter):
    line2 = run(actions, fonts, line, next_line)
    lines = unroll(line, line2)
    page = None
    for line in lines[1:]:
        if page is not None and page is not line.column.page:
            break
        page = line.column.page
        for graphic in line.graphics:
            function, *args = graphic
            function(fonts, line, painter, *args)
    return line

if __name__ == '__main__':
    main(sys.argv[1:])
