#!/usr/bin/env python

from __future__ import print_function

import argparse
import os
import sys
from copy import deepcopy
from textwrap import dedent

import PySide2
import PySide2.QtSvg

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

    os.chdir(os.path.dirname(__file__))

    factor = 72 / 4  # TODO: have Document pull from layout instead?
    d = Document(16 * factor, 9 * factor)

    fonts = get_fonts(d.painter, [
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('roman', 'Gentium Basic', 'Roman', 12),
        ('roman-small', 'Gentium Basic', 'Roman', 4), #?
        ('typewriter', 'Courier', 'Roman', 11),
        #('typewriter', 'Inconsolata', 'Roman', 10),
        #('typewriter', 'Ubuntu Mono', 'Roman', 10),
    ])

    simple_slide = make_simple_slide_function(fonts, d)
    code_slide = make_code_slide_function(fonts, d)

    #next_line = slide_layout()
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

    # Slides

    s = simple_slide
    s('Letterpress')
    s('In the distant past,',
      'books and journals were',
      'typeset by hand')
    s('But as machines replaced humans,',
      'mathematics journals became so ugly that',
      'Donald Knuth could no longer bear to publish')
    s('TeX Typesetting System')
    s('τέχνη', 'craftsmanship / art')
    s('The Good', '',
      '1. Fonts',
      '2. Keyboard',
      '3. Math formulas',
      '4. Paragraph line breaking')

    s('1. Fonts',
      '',
      '“MetaFont”',
      'algorithmic',
      'vectors',
    )

    # next_line = slide_layout()
    # actions = [
    #     (centered_paragraph, [('roman', 'this very summer')]),
    #     (centered_paragraph, [('roman-small', 'this very summer')]),
    # ]
    # run_and_draw_centered(actions, fonts, None, next_line, d.painter)
    # d.new_page()

    # vector fonts: won!
    # fonts change shape as size changes (can show?)

    s('2. Keyboard',
      '',
      'Learning to type .tex files',
      'was a small course in typography')
    s('- – — −')
    s('Hobbit-lore', '1158–60', 'Stick to your plan—your whole plan', '−𝜋')
    code_slide('Hobbit-lore',
               '1158--60',
               'Stick to your plan---your whole plan',
               r'$-\pi$')
    code_slide("``No secrets between us, Frodo''",
               'Mr.~Baggins',
               r"N\'umenor",
               r'Nazg\^ul')

    s('3. Math formulas')
    with open('formula.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    center_formula(d, 'formula.svg')
    d.new_page()

    s('MathJax')

    s('4. Paragraph line breaking')

    # (show that "War" looked bad)

    # paragraphs: beautiful
    # boxes and glue -> dynamic programming

    # page layout

    # why?
    # different input forms
    # real language rather than macro language
    # (show what a macro language is)
    # (mention backslash?)
    # be in control

    # Paragraph layout: can it simply return its decision, given "width"?
    # No, because next column might be different width.
    # So it needs a way to ask for new pages/columns as it goes along.
    # And it will do something like:

    simple_slide('I wanted to improve upon TeX')
    simple_slide('(text, width) → paragraph',
                 '(paragraph, height) → page')
    simple_slide('Different width columns?', 'Not supported in TeX')
    simple_slide('My idea: paragraph that asks',
                 'for more space as it needs it,'
                 'so we know when it has filled one',
                 'column and moves to the next')
# by having paragraph ask for more columns as it needed them.
# lay_out_paragraph(width, height, y, ...)
# Column = NamedTuple(..., 'width, height')
# lay_out_paragraph(column, y, ...)
# each time you need a line:
# height = ... # compute space needed
# if y + height > column.height:
#     # ask for another column
# How do we do that?
# layout.next_column() OR column.next() OR next_column(column)
# lay_out_paragraph(column, y, next_column, ...)
# Why? To avoid Premature Object Orientation!
# Looking at options:
# layout.next_column() OR column.next() OR next_column(column)
# ask WHY?
# What necessity requires the verb you need
# to be attached to a noun?
# Unless the answer is, "because you can't avoid it", skip it.
# So my arguments are coming together
# lay_out_paragraph(column, y, next_column, ...)
# What about the return value?
# Can the routine simply draw on the page when it's done?
# No!
# Because we need speculation.
# ... (put existing slides here that show what headings need to do) ...
# How will the heading work?
# :add heading to column
# :ask paragraph to lay itself out
# :if paragraph's first line's column != column:
# :    remove the paragraph
# :    remove ourselves
# :    column = next_column()
# :    re-add heading
# :    re-add paragraph
# How?
# generators?
# iterators?
# lists of lists?
# linked list!
# Column = NamedTuple(..., 'width, height')
# Line = NamedTuple(..., 'previous_line column y')

#                    col5     col6    col6    col6
#                    line9 ← line1 ← line2 ← line3
#  col5     col5  <  HEADING  P1       P2      P3
#  line7 ← line8 <
#                    col6     col6    col6    col6
#                    line1 ← line2 ← line3 ← line4
#                    HEADING  P1      P2      P3
# We can run any number
# of speculative layout steps
# and when we keep one, Python
# decrements the refcounts
# and discards all the rest!
# so we have a linked list
# we need to pass it so that callee can add to it.
# lay_out_paragraph(column, y, line, next_column, ...)
# simplify / eliminate redundnancy / something? yes! simplify!
# lay_out_paragraph(xxxx column, xxx y, line, next_column, ...)
# because line already has them
# lay_out_paragraph(line, next_column, ...)
# yay
# SYMMMETRY: we started out passing one thing returning another
# but now we are passed a `line` and later we return a different `line`
# Line = NamedTuple(..., 'previous_line column y')
# so we now know how to return speculative layout.
# But how does the heading invoke the paragraph to make it do layout?
# Reality: markdown or rst → list of calls
# actions = [
#     (chapter_title, 'Intro'),
#     (paragraph, 'hobbits'),
#     (heading, '1. title'),
#     (paragraph, 'hobbits'),
#     (paragraph, 'hobbits'),
#     (heading, '2. on pipe-weed'),
#     (paragraph, 'hobbits'),
#     ...
# ]
# decision: pass in list and index
#   lay_out_paragraph(actions, a, ...)
# could try to hide it, but.
# so the paragraph lays out its content and is done.
# but the heading asks the following paragraph to work too.
# how can it return finished work?
# return a + i; can either do its own work, or return several subseq.
# `return line_n, a+1`
# so how does our arg list look
# lay_out_paragraph(actions, a, line, next_column, ...)
# even though half our routines are going to ignore `actions`
# and return `a+1`
# arg list is long because it's general
# it handles the case where you have to call n subseq steps
# idea: maybe make an EXCEPTION for simple layout routines
# that aren't going to look at `actions` and always return `a+1`
# 1990s: would have introspected arguments magic!
# 2000s: would have registered simple and complex
# 2010s: would have defined decorator to convert
# @simple
# could be:
# def simple(callable):
#     def wrapper(actions, a, line, next_column, *args):
#         line2 = callable(line, next_column, *args)
#         return a + 1, line2
#     return wrapper
# what did I decide?
# NO NO NO
# Keep all the routines the same
# The very simplest routine
# single_line(actions, a, line, next_column, ...)
#     ...
#     return a + 1, line2
# why?
# because I learn my code by re-reading
# if I have 5 sophisticated routines
# and 5 simple ones,
# and I give the simple ones an exception,
# 1. I now have two calling conventions rather than one
# 2. I only have half the number of examples of each one
# A single calling convention brings SYMMETRY
# (show "how heading works") <- (what?)
# BONUS ROUND
# inside para: multi calls to inner p. Looks like heading!
# so, shouldn't this be its own action in the list?
# BUT: needs to subvert LAST line. How? Twiddle?
# Fake params? Fake column? That's like a framework?
# NO-
# All these routines have the same logic. Over and over. [show logic?]
# That routine is going to be making a decision you want to control.
# Where do you want to be when a big decision is made.
# WHERE DO YOU WANT TO BE?
# In the room where it happens...
# I had been imagining:
# single_line(actions, a, line, next_column, ...)
#     ...
#     column2 = next_column(line.column)
# but what I really wanted was to take control away:
# single_line(actions, a, line, next_line, ...)
#     ...
#     line2 = next_line(leading=2, height=12)
# so you can subvert it
# (TODO: look up how I actually do this. How does it work?)
# And why are we able to do that?
# Becuase of avoiding Premature OO!
# Otherwise it would be difficult to replace one method of an object;
# would have to use Gang of Four Decorator, or monkeypatching, or worse.
# If you pass an object and need to live override a method
# you are in trouble.
# But if you pass a callable and need to tweak it?
# Very easy!
# End with showing photos of book.

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

    # so, linked list
    # line.y
    # so we no longer need to pass in y or column
    # so code started to look like:
    # (have code that combines leading, height, next_column, line)
    # and it always looks like that
    # idea: instead of next_column(), could we put this logic in next_line()?
    # so how do you find what next thing is?
    # of other alternatives, chose to pass array and index.
    # and have them pass back new index so they don't throw away layout.
    # and in case they were nondeterministic.
    # so, rule: if you lay out next element, keep the result.
    # show example list of items, and what array/a would be passed, returned.
    # TEMPTATION: special call convention for "simple" routines
    # that don't look at next.
    # (actions, a, fonts, line, next_line, ...)
    # could: introspect? register? decorate?
    # BUT: symmetry is more important than brevity. (and than DRY?)
    # Makes hard case harder to be unusual?
    #  .................................................................................................................................
    # TEMPTATION: Premature Object Orientation
    # want to add next() to line instead of having next_line()
    # TODO: how do we motivate wanting to control next_line() decision?
    # do we use wanting to separate out avoid_widows_and_orphans()
    # instead of having switch because:
    # Composition is better than Configuration(?)Switches(?)
    # (^^^ [farther up] show 2 different ways para would look in actions list)
    # Isn't widow/orphan like heading logic but without a heading?
    # It's a transform applied to a paragraph.
    # If we decide, "orphan", then we need to push to next page.
    # How do we control where its next line goes?
    # Alternatives: fake line; fake column height; fake page height.
    # All of these are frameworky!
    # You are adjusting inputs trying to control output.

    # "Fuzzy Knowledge-Based Control for Backing Multi-Trailer Systems"
    # Andri Riid , Jaakko Ketola , Ennu Rüstern

    import PySide2
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    d.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    # What if instead of setting up, I provided my own next_line()?
    # 1. it was right decision to pass as argument!
    # 2. it was right decision to not make it a method
    # ways to override a method:
    # monkey patching; decorator, which requires spinning up whole other class.
    # we would have to create entire object just to intercept one method!
    # instead, we kept it decoupled,
    # so we can just return wrapped next_line().
    # (^^ linked list: "Try it both ways")

    # when a crucial decision is made, where do you want to be?
    simple_slide('I want to be', 'in the room where it happens')

    # pm = PySide2.QtGui.QPixmap('two-trailers.png')
    # d.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    # resisted Premature OO
    # next_line() was bare and decoupled and easy to control
    # show code (# The room where it happens)
    # easier to write tests for this simple function

    # the right track:
    # when I adjusted for headings,
    # and was able to separate orphan/widow for free!

    # give my father a hardback with his father's memories
    # photo of book

    # Lessons:
    # ...
    # The Right Track

    d.painter.end()

def slide_layout(narrow=0):
    factor = 72 / 4
    margin = (1 + narrow) * factor
    return single_column_layout(
        16 * factor, 9 * factor,
        margin, margin, margin, margin,
    )

def center_formula(d, path):
    formula_scale = 32
    r = PySide2.QtSvg.QSvgRenderer(path)
    b = r.viewBox()
    w = b.width() * formula_scale
    h = b.height() * formula_scale
    x = (d.painter.device().width() - w) // 2
    y = (d.painter.device().height() - h) // 2
    b2 = PySide2.QtCore.QRect(x, y, w, h)
    r.render(d.painter, b2)

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
    def code_slide(*texts):
        text = '\n'.join(texts)
        text = dedent(text.rstrip()).strip('\n')
        next_line = slide_layout()
        actions = [
            (ragged_paragraph, [('typewriter', line)])
            for line in text.splitlines()
        ]
        run_and_draw_centered(actions, fonts, None, next_line, d.painter)
        d.new_page()
    return code_slide

def progressive_slide(f, *texts):
    texts = list(texts)
    i = len(texts) - 1
    while i > -1:
        if texts[i]:
            f(*texts)
            texts[i] = ''
        i -= 1

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
