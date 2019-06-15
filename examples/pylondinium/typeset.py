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
        ('typewriter', 'Courier', 'Roman', 9),
        #('typewriter', 'Inconsolata', 'Roman', 10),
        #('typewriter', 'Ubuntu Mono', 'Roman', 9),
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
    c = code_slide

    s('Typesetting with Python', '', '', '', '@brandon_rhodes',
      '2019 June 16', 'PyLondinium')

    s('')
    pm = PySide2.QtGui.QPixmap('tex-and-metafont-book.jpg')
    n = 2
    d.painter.drawPixmap(1200, 100, 1200 * n, 1196 * n, pm)

    s('τέχνη', 'craft / art')

    d.new_page()
    center_formula(d, 'logo.svg')

    s('markup language', '', 'plain text → document')

    with open('sample.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    d.new_page()
    center_formula(d, 'sample.svg', 20)

    s('math typesetting')
    s('When math journals stopped paying for',
      'professional typesetters, papers looked so',
      'ugly that Knuth could no longer publish')
    s('He took an entire year off to invent TeX')

    with open('formula.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    d.new_page()
    center_formula(d, 'formula.svg')

    s('Eventually I got the opportunity to use TeX', '', '', '')
    s('', 'I disliked LaTeX so I wrote my own macros', '', '')
    s('', 'I learned TeX’s strengths', 'but also its limitations')
    s('', '', 'Which made me dream', 'of writing a replacement')
    s('(decades pass)')
    s('Print-on-demand', '', '', '', '')
    s('', 'PDF → custom hardcover', '', '', '')
    s('', 'Real hardcover: casebound, Smyth sewn', '', '', '')

    n = 5
    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212228.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('', '', 'My grandfather’s essays', '', '')
    s('', '', '', 'Wrote the typesetting myself', '')
    s('', '', '', 'Wrote the typesetting myself', '— in Python!')

    s('What was wrong with TeX?')
    s('Text + parameters → TeX → PDF')
    s('“Framework”')

    d.new_page()
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    d.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    s('Backing up a tractor and trailers', 'is an open problem in AI')
    s('“Fuzzy Knowledge-Based Control', 'for Backing Multi-Trailer Systems”',
      '', 'Andri Riid, Jaakko Ketola, Ennu Rüstern')
    s('Trailers are difficult to back up',
      'because the input — the motion of the tractor —',
      'has an increasingly distant relationship',
      'to the motion of the nth trailer')
    s('Example: TeX paragraph layout')



    s('Goal:', '', 'I wanted to turn my grandfather’s',
      'essays about family history and his own',
      'childhood in 1920s Birmingham, Alabama,',
      'into a printed hardcover book')
    s('Letterpress')
    s('In the distant past,',
      'books and journals were',
      'typeset by hand')
    s('But as machines replaced humans,',
      'mathematics journals became so ugly that',
      'Donald Knuth could no longer bear to publish')
    s('“TeX” Typesetting System')

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

    s('MathJax')

    s('4. Paragraph line breaking')

    # (show that "War" looked bad)

    s('Boxes and glue (and penalties)')
    s('• Boxes have a fixed width',
      '• Glue can shrink, stretch to fix the line length',
      '• But glue incurs “badness” if shrinks, stretches',
      '• You can break the line wherever there is glue',
      '• But you incur “badness” where there’s a penalty',
      '• Taking a penalty can also add length to the line')
    s('Can also configure:',
      '• More badness for 2 taking penalties in row',
      '• More badness for shrinking then stretching',
      '• More badness for a very short last line')
    progressive_slide(s, 'Isn’t that bizarre?',
                      '',
                      'It’s a classic framework')
    s('Boxes = text',
      'Glue = space between words',
      'Penalty = non-breaking space',
      'Penalty w/length = hyphenation',
      'Two penalties in a row = stacked hyphens')
    s('Despite a paragraph having 2ⁿ possible layouts,',
      'Knuth can find the optimal solution to boxes-and-glue',
      'in O(n²) worse case and usually close to O(n)!')
    s('How?', '', 'Dynamic programming!', '',
      '(I’ll bet you thought it only existed',
      'to provide programming interview questions!)')
    s('Result: *beautiful* paragraphs')

    s('But', '', 'TeX had a clunky macro language',
      'No support for modern markup languages',
      'Deep limitations in page layout')

    simple_slide('I wanted to improve upon TeX')
    simple_slide('(text, width) → paragraph',
                 '(paragraph, height) → page')
    simple_slide('Different width columns?', 'Not supported in TeX')
    simple_slide('My idea: paragraph layout that',
                 'asks for more space as it needs it,'
                 'so we know when it has filled one',
                 'column and moves to the next')
    code_slide('Column = NamedTuple(width, height)',
               'lay_out_paragraph(column, y, ...)')
    code_slide('''
    # Each time the paragraph needs another line:
    leading = 2pt
    height = 12pt
    if y + leading + height > column.height:
        # ask for another column
    ''')

    # How do we ask for more columns?

    simple_slide('Q: How do we ask for another column?')
    code_slide('''
    def lay_out_paragraph(column, y, ...):
        column2 = column.next()

    def lay_out_paragraph(column, y, layout, ...):
        column2 = layout.next_column(column)

    def lay_out_paragraph(column, y, next_column, ...):
        column2 = next_column(column)
    ''')
    simple_slide('A: Pass a plain callable!')
    code_slide('''
    def lay_out_paragraph(column, y, next_column, ...):
        column2 = next_column(column)
    ''')
    simple_slide('Why? To avoid', 'Premature Object Orientation')
    simple_slide('Premature Object Orientation:',
                 'attaching a verb to a noun',
                 "when you needn't")
    simple_slide('Symptom:',
                 'An object argument',
                 'on which you only call',
                 'a single method')
    simple_slide('Premature Object Orientation',
                 'couples code that needs only a verb',
                 'to all the implementation details of the noun')
    code_slide('''
    # So we now have a rough plan for our inputs:

    def lay_out_paragraph(column, y, next_column, ...):
        column2 = next_column(column)

    # What will we return?
    ''')

    # What output will the paragraph return?

    simple_slide('Can the paragraph',
                 'simply go ahead and draw',
                 'on the output device?')
    simple_slide('No')
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
                 '5. Place heading on the next page instead',
                 '6. Lay the paragraph out again!')

    simple_slide('Consequence #1', '', 'Layout and drawing',
                 'need to be separate steps')
    simple_slide('Consequence #2', '', 'The output of the layout step',
                 'needs to be easy to discard')

    # How will the heading work?
    # :add heading to column
    # :ask paragraph to lay itself out
    # :if paragraph's first line's column != column:
    # :    remove the paragraph
    # :    remove ourselves
    # :    column = next_column()
    # :    re-add heading
    # :    re-add paragraph

    s('Generators?', 'Iterators?', 'Lists of lists?')
    progressive_slide(s, 'A:', 'Linked list')
    code_slide('''
    Column = NamedTuple(..., 'width height')
    Line = NamedTuple(..., 'previous column y graphics')

    c1 = Column(...)
    line1 = Line(None, c1, 0, [])
    line2 = Line(line1, c1, 14, [])
    line3 = Line(line2, c1, 28, [])
    ''')
    # TODO:
    #                    col5     col6    col6    col6
    #                    line9 ← line1 ← line2 ← line3
    #  col5     col5  <  HEADING  P1       P2      P3
    #  line7 ← line8 <
    #                    col6     col6    col6    col6
    #                    line1 ← line2 ← line3 ← line4
    #                    HEADING  P1      P2      P3
    s('A linked list lets us attach any number',
      'of speculative layouts to the document so far,',
      'and automatically disposes of the layouts',
      'that we do not wind up keeping')
    s('Consequence: to return a',
      'new head for the linked list,',
      'we will need the current head')
    c('lay_out_paragraph(line, column, y, next_column, ...):')
    s('But wait!', 'We can eliminate common variables')
    c('''
    lay_out_paragraph(line, column, y, next_column, ...)

    # But what is a line?
    Line = NamedTuple(..., 'previous column y graphics')
    ''')
    s('That’s nice!', '', 'Designing our return value',
      'wound up eliminating two', 'of our input arguments',
      '', 'Always look for chances to simplify',
      'after designing a new part of your system')
    c('''
    lay_out_paragraph(line, next_column, ...)
    ''')
    s('Also nice:', 'Symmetry!')
    c('''
    # The Line becomes a common currency that is
    # both our argument and our return value:

    def lay_out_paragraph(line, next_column, ...):
        ...
        return last_line
    ''')

    s('So', '', 'We now have a scheme where a paragraph',
      'can lay itself out speculatively',
      'instead of immediately printing ink', '',
      'But how will the heading invoke it?')
    run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    run_and_draw(lotr2, fonts, None, narrow_line, d.painter)  #?
    s('Well: what drives the layout process?')
    c('''
    # Input (Markdown, RST, etc) produces:
    actions = [
        (title, 'Prologue'),
        (heading, '1. Concerning Hobbits'),
        (paragraph, 'Hobbits are an unobtrusive...'),
        (paragraph, 'For they are a little people...'),
        (heading, '2. Concerning Pipe-weed'),
        (paragraph, 'There is another astonishing...'),
    ]
    ''')
    s('Q:', 'How can the heading see', 'the paragraph that follows?')
    s('A:', 'Easiest thing?', 'Just pass in the list')
    c('''
    def lay_out_heading(actions, a, line, next_column, ...):
        ...
        return last_line
    ''')
    s('Q:', 'But wait!', 'Which last_line should', 'the heading return?')
    c('''
    def lay_out_heading(actions, a, line, next_column, ...):
        ...
        return last_line  # <- Is this the heading line?
                          #    Or the paragraph's last line?
    ''')
    # Should I show the heading logic? Or does that come later?
    s('If, to decide its own location,', 'the heading goes ahead and asks',
      'the following paragraph to lay itself out,',
      'shouldn’t we keep that work instead',
      'of throwing it away?')
    s('But how can the heading tell the engine,',
      '“I am returning the output of 2 items',
      'instead of just my own?”')
    c('''
    def lay_out_heading(actions, a, line, next_column, ...):
        ...
        return a + 2, last_line  # New return value: index!
    ''')

    # The spammish repetition.

    s('Stepping back, I looked askance',
      'at the repetition in my code')
    c('''
    # Some routines use `actions` and `a`:
    def heading(actions, a, line, next_column, ...):
        ... return a + 2, line_n
    def section(actions, a, line, next_column, ...):
        ... return a + 3, line_n

    # But many ignored `actions` and returned `a + 1`:
    def paragraph(actions, a, line, next_column, ...):
        ... return a + 1, line_n
    def centered_text(actions, a, line, next_column, ...):
        ... return a + 1, line_2
    def horizontal_rule(actions, a, line, next_column, ...):
        ... return a + 1, line_2
    ''')
    s('DRY')
    s('“Don’t Repeat Yourself”', '', 'And suddenly',
      'I heard the call', 'of other decades')
    s('How can I eliminate `actions` and `a`',
      'from innocent routines that don’t need them?')
    s('1990s', '', 'Introspect each function to learn',
      'if it takes `actions` and `a` or not!')
    s('Magic!')
    c('''
    def heading(actions, a, line, next_column, ...):
        ... return a + 2, line_n
    def section(actions, a, line, next_column, ...):
        ... return a + 3, line_n

    def paragraph(line, next_column, ...):
        ... return line_n
    def centered_text(line, next_column, ...):
        ... return line_2
    def horizontal_rule(line, next_column, ...):
        ... return line_2
    ''')
    s('Early 2000s', '', 'Special registry for functions',
      'that don’t need `actions` and `a`')
    s('Late 2000s', '', 'A decorator for functions',
      'that don’t need `actions` and `a`')
    c('''
    def simple(function):
        def wrapper(actions, a, line, next_column, *args):
            line2 = callable(line, next_column, *args)
            return a + 1, line2
        return wrapper
    ''')
    c('''
    def heading(actions, a, line, next_column, ...):
        ... return a + 2, line_n
    def section(actions, a, line, next_column, ...):
        ... return a + 3, line_n

    @simple
    def paragraph(line, next_column, ...):
        ... return line_n
    @simple
    def centered_text(line, next_column, ...):
        ... return line_2
    def horizontal_rule(line, next_column, ...):
        ... return line_2
    ''')
    s('And what did I decide?')
    s('Symmetry')
    s('When I return to code,', 'I learn by re-reading')
    s('Given a stack of functions',
      'that do exactly the same thing,',
      'if ½ of them use one convention',
      'and ½ use another —')
    s('— then I now have twice',
      'the number of conventions to re-learn,',
      'and only half the number of examples',
      'of each to learn from!')
    s('I chose verbose symmetry', 'over obscure complexity')
    s('As a reader,',
      'I need routines',
      'that behave the same',
      'to look the same')
    c('''
    # Some routines use `actions` and `a`:
    def heading(actions, a, line, next_column, ...):
        ... return a + 2, line_n
    def section(actions, a, line, next_column, ...):
        ... return a + 3, line_n

    # But many ignored `actions` and returned `a + 1`:
    def paragraph(actions, a, line, next_column, ...):
        ... return a + 1, line_n
    def centered_text(actions, a, line, next_column, ...):
        ... return a + 1, line_2
    def horizontal_rule(actions, a, line, next_column, ...):
        ... return a + 1, line_2
    ''')

    # (show "how heading works") <- (what?)

    s('BONUS ROUND')
    s('widows', 'and', 'orphans')
    s('How does that look in code?')
    c('''
    def paragraph(...):
        lay out paragraph
        if it creates an orphan:
            adjust, and try again
        if it creates a widow:
            adjust, and try again
    ''')
    s('So paragraph() hides an inner routine',
      'that does simple paragraph layout',
      'inside of widow-orphan logic')
    s('What if you just want the simple part?')
    s('Parametrize?')
    c('''
    def paragraph(..., no_widows=True, no_orphans=True):
        lay out paragraph
        if no_widows and it creates an orphan:
            adjust, and try again
        if no_orphans and it creates a widow:
            adjust, and try again
    ''')
    c('But —', '', 'This looks a lot', 'like our heading logic')
    c('''
    if it creates an orphan:
        adjust, and try again

    if heading is alone at bottom of column:
        adjust, and try again
    ''')
    c('''
    actions = [
        (heading, '1. Concerning Hobbits'),
        (paragraph, 'Hobbits are an unobtrusive...'),
    ]
    ''')
    s('What if, instead of widow-orphan logic',
      'being coupled to the paragraph() routine,',
      'it lived outside and could be composed',
      'with the paragraph?')
    c('''
    actions = [
        (avoid_widows_and_orphans,),
        (paragraph, 'Hobbits are an unobtrusive...'),
    ]
    ''')
    s('Composition » Coupling+Configuration')
    s('Problem:', '', 'To avoid a widow, the paragraph needs',
      'to move to the second column early',
      '', 'How will we convince it to do that?')
    c('''
    # Each time the paragraph needs another line:
    leading = ...
    height = ...
    if y + leading + height > column.height:
        # ask for another column
    ''')
    s('Provide an inflated y value, fix later?',
      'Provide a fake column with a smaller height?',
      '?')
    s('This feels a lot like a framework', '',
      'It feels we are looking desperately for levers',
      'because we are standing on the outside',
      'of the crucial decision we need to control')
    s('Where do you want to be during a crucial decision?', '',
      'On the outside, desperatly adjusting configuration?')
    s('You want to be', 'in the room where it happens')
    c('''
    # Previously, layout routines only consulted
    # us when they needed a new column, but handled
    # lines themselves:

    def paragraph(..., next_column, ...):
        ...
        if y + leading + height > column.height:
             ...
    ''')
    c('''
    # Let's change that up.

    def paragraph(..., next_line, ...):
        ...
    ''')
    c('''
    def next_line(line, leading, height):
        column = line.column
        y = y + leading + height
        if y > line.column.height:
             column = next_column(line.column)
             y = height
        return Line(line, column, y, [])
    ''')
    s('Then, all the widow-orphan', 'logic has to do is —')
    c('''
    def avoid_widows_and_orphans(..., next_line, ...):

        def fancy_next_line(...):
            # A wrapper that makes its own decisions!

        # Call the paragraph with fancy_next_line()
    ''')
    s('Did you catch the win?')
    s('The simple wrapper would not have worked',
      'if we had not avoided Premature Object Orientation!')
    s('Function `f()` is easy to wrap!', '',
      'Object `obj` with a method `m()`',
      'is not so easy to control')
    s('Monkey patching?',
      'An Adapter class?',
      'Gang of Four Decorator?')
    s('In Object Orientation, customizing a verb',
      'can require an entire design pattern')
    s('But if you pass functions —',
      'if you treat verbs as first class citizens —',
      'a simple wrapper function can put you',
      'inside of the room where it happens')
    s('This design makes me', '', '— happy —')
    s('When simplifications appear',
      'in several places I wasn’t expecting them',
      'I feel that design is going in the right',
      'direction')

    s('Lessons', '',
      'Start verbose, simplify later',
      'Value symmetry over special cases',
      'Let verbs be first-class citizens',
      'Avoid premature Object Orientation')

    # photos of book

    n = 5

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212228.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212247.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212354.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('Thank you very much!', '', '', '@brandon_rhodes')

    # (^^ linked list: "Try it both ways")

    # give my father a hardback with his father's memories
    # photo of book

    d.painter.end()

def slide_layout(narrow=0):
    factor = 72 / 4
    margin = (1 + narrow) * factor
    return single_column_layout(
        16 * factor, 9 * factor,
        margin, margin, margin, margin,
    )

def center_formula(d, path, formula_scale=32):
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
        if 'PyLondinium' not in texts:  # awkward special case: title slide
            d.new_page()
        next_line = slide_layout()
        actions = [
            (centered_paragraph, [('roman', text)])
            for text in texts
        ]
        run_and_draw_centered(actions, fonts, None, next_line, d.painter)
    return simple_slide

def make_code_slide_function(fonts, d):
    def code_slide(*texts):
        d.new_page()
        text = '\n'.join(texts)
        text = dedent(text.rstrip()).strip('\n')
        next_line = slide_layout()
        actions = [
            (ragged_paragraph, [('typewriter', line)])
            for line in text.splitlines()
        ]
        run_and_draw_centered(actions, fonts, None, next_line, d.painter)
    return code_slide

def progressive_slide(f, *texts):
    texts = list(texts)
    for i in range(len(texts)):
        if texts[i]:
            f(*texts[:i+1] + [''] * (len(texts) - i))
    # i = len(texts) - 1
    # while i > -1:
    #     if texts[i]:
    #         f(*texts)
    #         texts[i] = ''
    #     i -= 1

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
    #assert lines[1].column.page is lines[-1].column.page
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
