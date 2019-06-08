#!/usr/bin/env python

from __future__ import print_function

import argparse
import sys
from copy import deepcopy
from textwrap import dedent

from typesetting.composing import (
    avoid_widows_and_orphans, centered_paragraph, ragged_paragraph,
    run, space_before_and_after,
)
from typesetting.document import Document
from typesetting.knuth import knuth_paragraph
from typesetting.pyside2_backend import get_fonts
from typesetting.skeleton import single_column_layout, unroll

def main(argv):
    parser = argparse.ArgumentParser(description='Generate slides')
    parser.parse_args(argv)

    factor = 72 / 4  # TODO: have Document pull from layout instead?
    d = Document(16 * factor, 9 * factor)

    fonts = get_fonts(d.painter, [
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('roman', 'Gentium Basic', 'Roman', 12),
        ('typewriter', 'Courier', 'Roman', 11),
        #('typewriter', 'Inconsolata', 'Roman', 10),
        #('typewriter', 'Ubuntu Mono', 'Roman', 10),
    ])

    simple_slide = make_simple_slide_function(fonts, d)
    code_slide = make_code_slide_function(fonts, d)

    next_line = slide_layout()
    narrow_line = slide_layout(0.5)

    lotr = [
        (knuth_paragraph, 0, 0, [('roman', """

        and all but Hobbits would find them exceedingly dull.
        Hobbits delighted in such things, if they were accurate: they
        liked to have books filled with things that they already knew,
        set out fair and square with no contradictions.

        """.strip())]),
        (space_before_and_after, 8, 2),
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
    lotr2 = deepcopy(lotr)
    lotr2[-1:-1] = [(avoid_widows_and_orphans,)]
    lotr3 = deepcopy(lotr)
    lotr3[-1][3][0] = ('roman', 'There is another astonishing thing.')

    code_slide('''
    y = line.y + need_y
    if y > column.height:
        page = next_page()
        y = 0
    ''')

    simple_slide('Problem:', 'Headings')

    run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    d.new_page()

    simple_slide('Q: What if there were no text', 'below the heading?')

    run_and_draw(lotr2, fonts, None, narrow_line, d.painter)
    d.new_page()

    code_slide('''
    # Q: Can the Heading simply
    #    leave extra space?

    y = line.y + need_y + extra_y
    if y > column.height:
        page = next_page()
        y = 0
    ''')

    simple_slide('A: No')

    simple_slide('Why?', 'Widows and orphans')

    run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    d.new_page()

    simple_slide('A 1-line paragraph would', 'follow the heading',
                 'without complaint')

    run_and_draw(lotr3, fonts, None, narrow_line, d.painter)
    d.new_page()

    simple_slide('But a several-line paragraph will',
                 'bump its opening line to the next page,',
                 'leaving the heading stranded')

    run_and_draw(lotr2, fonts, None, narrow_line, d.painter)
    d.new_page()

    simple_slide('How can the heading predict',
                 'when it will be stranded alone?',
                 '',
                 '1. Know everything about paragraphs',
                 '',
                 '')

    simple_slide('How can the heading predict',
                 'when it will be stranded alone?',
                 '',
                 '(a) Know everything about paragraphs',
                 '— or —',
                 '(b) Ask next item to lay itself out speculatively')

    simple_slide('Heading algorithm', '',
                 '1. Add heading to this page',
                 '2. Run the following paragraph',
                 '3. Is its first line on the same page? Done!',
                 '4. If not? Remove paragraph & heading',
                 '5. Move heading to next page instead',
                 '6. Lay the paragraph out again!')

    simple_slide('Consequence #1', '', 'Layout and drawing',
                 'need to be separate steps')

    simple_slide('Consequence #2', '', 'The output of the layout step',
                 'needs to be easy to discard')

    simple_slide('I want to be', 'in the room where it happens')

    d.painter.end()

def slide_layout(narrow=0):
    factor = 72 / 4
    margin = (1 + narrow) * factor
    return single_column_layout(
        16 * factor, 9 * factor,
        margin, margin, margin, margin,
    )

def make_simple_slide_function(fonts, d):
    def simple_slide(*texts):
        next_line = slide_layout()
        actions = [
            (centered_paragraph, [('roman', text)])
            for text in texts
        ]
        run_and_draw_centered(actions, fonts, None, next_line, d.painter)
        d.new_page()
    return simple_slide

def make_code_slide_function(fonts, d):
    def code_slide(text):
        text = dedent(text.rstrip()).strip('\n')
        next_line = slide_layout()
        actions = [
            (ragged_paragraph, [('typewriter', line)])
            for line in text.splitlines()
        ]
        run_and_draw_centered(actions, fonts, None, next_line, d.painter)
        d.new_page()
    return code_slide

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

def run_and_draw_centered(actions, fonts, line, next_line, painter):
    line2 = run(actions, fonts, line, next_line)
    lines = unroll(line, line2)
    page = None
    assert lines[0] is None
    assert lines[1].column.page is lines[-1].column.page
    y = lines[-1].y
    offset = (lines[1].column.height - y) / 2
    for line in lines[1:]:
        if page is not None and page is not line.column.page:
            break
        page = line.column.page
        for graphic in line.graphics:
            function, *args = graphic
            line = line._replace(y = line.y + offset)
            function(fonts, line, painter, *args)
    return line

if __name__ == '__main__':
    main(sys.argv[1:])
