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
        ('old-standard', 'Old Standard TT', 'Roman', 12),
        ('roman', 'Gentium Basic', 'Roman', 12),
        ('roman-small', 'Gentium Basic', 'Roman', 4), #?
        ('typewriter', 'Courier', 'Roman', 9),
        #('typewriter', 'Inconsolata', 'Roman', 10),
        #('typewriter', 'Ubuntu Mono', 'Roman', 9),
    ])
    fonts['typewriter'].leading = 0

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

    s('The book’s lessons', 'in how to type .tex files',
      'were a small course in typography')
    code_slide('Mr.~Baggins')
    code_slide('Mrs.~Cotton')
    s('- – — −')
    s('Hobbit-lore', '1158–60', 'Stick to your plan—your whole plan', '−𝜋')
    code_slide('Hobbit-lore',
               '1158--60',
               'Stick to your plan---your whole plan',
               r'$-\pi$')
    s('Math typesetting')
    s('The real reason for TeX:', '',
      'When math journals stopped paying',
      'for professionals to set type by hand,',
      'math papers looked so ugly that',
      'Knuth could no longer publish')
    s('So he took an entire year off to invent TeX')

    with open('formula.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    d.new_page()
    center_formula(d, 'formula.svg')

    s('Paragraphs')
    s('TeX represents the words of a paragraph',
      'as fixed-width “boxes” separated by stretchy “glue”')
    c('┌───┐  ┌──┐  ┌─────┐  ┌───┐  ┌──┐  ┌─────┐',
      '└───┘←→└──┘←→└─────┘←→└───┘←→└──┘←→└─────┘')
    s('A paragraph with n positions',
      'at which the text could be split into lines',
      'can be laid out in 2ⁿ different ways', '',
      'How could we ever find the optimium layout?')
    s('Dynamic programming!')
    s('TeX finds the optimal solution',
      'for breaking each paragraph into lines',
      '',
      'O(n²) worse case, usually O(n)',
      '(n = number of possible breaks)')

    with open('sample.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    d.new_page()
    center_formula(d, 'sample.svg', 20)

    s('The output of TeX was beautiful!',
      'But it was difficult to control.',
      '',
      'Once you set up the parameters,',
      'layout proceeded largely outside'
      'of your control')

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

    d.new_page()
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    d.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    s('What if instead of typesetting systems',
      'there were a typesetting library',
      'that invited the programmer',
      'inside its decisions?')
    s('2012', '', 'I realized that typesetting',
      'and printing a book', 'was now within reach!')

    s('The pieces were now in place')

    s('Print-on-demand', '', 'PDF → custom hardcover')
    s('Real hardcover!', '', '• Casebound', '• Smyth sewn')

    n = 5
    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212228.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('Technology', '',
      'MetaFont → TrueType, OpenType',
      'Macro language → Markdown, RST',
      'Paragraph layout → Andrew Kuchling’s texlib',
      'DVI → PDF')

    s('', 'But what would I print?', '', '', '')
    s('', '', 'My grandfather’s essays', '', '')
    s('', '', '', 'Wrote the typesetting myself', '')
    s('', '', '', 'Wrote the typesetting myself', '— in Python!')

    s('Hwæt!', '', '', '', '')
    s('Hwæt!', '', 'What would I do differently?')

    simple_slide('I chose a specific first goal')
    simple_slide('Different width columns?', 'Not supported in TeX')
    s('As a paragraph is broken into lines',
      'you don’t even know what page',
      'the paragraph will land on')
    simple_slide('paragraph → lines',
                 'is a separate step from',
                 'lines → pages')
    simple_slide('My idea: the paragraph should ask for more space',
                 'as it needs it, so it learns about any width',
                 'change when it crosses to a new column')
    s('Plan', '', '1. Find a library for rendering PDF',
      '2. Write a new page layout engine')

    d.new_page()
    lay_out_paragraph(fonts, d, [
        (centered_paragraph, [
            ('roman', 'ReportLab'),
        ]),
        (centered_paragraph, [('roman', '')]),
        (centered_paragraph, [
            ('old-standard', 'He was named for two Revolutionary W'),
            ('old-standard', 'ar heroes'),
        ]),
    ])

    s('Was there an alternative?')

    d.new_page()
    lay_out_paragraph(fonts, d, [
        (centered_paragraph, [
            ('roman', 'ReportLab'),
        ]),
        (centered_paragraph, [('roman', '')]),
        (centered_paragraph, [
            ('old-standard', 'He was named for two Revolutionary W'),
            ('old-standard', 'ar heroes'),
        ]),
        (centered_paragraph, [('roman', '')]),
        (centered_paragraph, [
            ('roman', 'Qt'),
        ]),
        (centered_paragraph, [('roman', '')]),
        (centered_paragraph, [
            ('old-standard', 'He was named for two Revolutionary War heroes'),
        ]),
    ])

    s('Input: list of typesetting actions')

    sample_actions = '''
    # Input (Markdown, RST, etc) produces:
    actions = [
        (title, 'Prologue'),
        (heading, '1. Concerning Hobbits'),
        (paragraph, 'Hobbits are an unobtrusive…'),
        (paragraph, 'For they are a little people…'),
        (heading, '2. Concerning Pipe-weed'),
        (paragraph, 'There is another astonishing…'),
    ]
    '''
    c(sample_actions)

    s('What API should the engine',
      'and the actions use to cooperate?')
    s('Let’s start by asking:'
      'what information does',
      'an action need?')

    code_slide('''
    Column = NamedTuple(…, 'width height')
    paragraph(column, y, ...)
    ''')
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
    def paragraph(column, y, ...):
        column2 = column.next()

    def paragraph(column, y, layout, ...):
        column2 = layout.next_column(column)

    def paragraph(column, y, next_column, ...):
        column2 = next_column(column)
    ''')
    simple_slide('A: Pass a plain callable!')
    code_slide('''
    def paragraph(column, y, next_column, ...):
        column2 = next_column(column)
    ''')
    s('Why?')
    s('To avoid', 'premature', 'Object Orientation')
    progressive_slide(
        s,
        '“Premature optimization is the root of all evil”',
        '— Donald Knuth',
    )
    simple_slide('Premature Object Orientation:',
                 '',
                 'attaching a verb to a noun',
                 "when you don’t need to yet")
    simple_slide('Symptom:',
                 '',
                 'Passing an object',
                 'on which a function will',
                 'only ever call a single method')
    code_slide('''
    def paragraph(column, y, layout, ...):
        column2 = layout.next_column(column)
    ''')
    simple_slide('Premature Object Orientation',
                 'couples code that needs only a verb',
                 'to all the implementation details of the noun')
    code_slide('''
    def paragraph(column, y, next_column, ...):
        column2 = next_column(column)
    ''')
    code_slide('''
    # So now I had a rough plan for action inputs:

    def paragraph(column, y, next_column, ...):
        column2 = next_column(column)

    # What would an action return?
    ''')

    # What output will the paragraph return?

    simple_slide('Can the paragraph',
                 'simply go ahead and draw',
                 'on the output device?')
    simple_slide('No')
    # TODO Make "Headings" faster?
    # TODO Always first tell, THEN show "if there isn't room the heading gets stranded"
    simple_slide('Problem:', 'Headings')
    s('A heading is supposed to sit atop',
      'the content of which it is the head')
    s('')
    run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    s('Q: What if there’s no room',
      'beneath the heading?')
    s('A: Typographic disaster')
    s('')
    d.new_page()
    run_and_draw(lotr2, fonts, None, narrow_line, d.painter)
    s('The heading needs to move', 'itself to the next column')
    code_slide('''
    # Can the Heading simply check whether
    # there is room for a line beneath it?

    if y + 2 * (leading + height) > column.height:
        column = next_column(column)
        y = 0
    ''')
    simple_slide('No. No, it can’t.')
    simple_slide('Why?', '', 'Because a paragraphs might not choose',
                 'to use the final line of a column!')
    s('“widows and orphans”')
    simple_slide('A single-line paragraph might deign',
                 'to remain at the bottom of the page')
    # d.new_page()
    # run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    s('')
    run_and_draw(lotr3, fonts, None, narrow_line, d.painter)
    simple_slide('But a several-line paragraph will',
                 'refuse to leave its opening line alone')
    d.new_page()
    run_and_draw(lotr2, fonts, None, narrow_line, d.painter)
    simple_slide('How can the heading predict',
                 'when it will be stranded alone?',
                 '',
                 '',
                 '',
                 '')
    simple_slide('How can the heading predict',
                 'when it will be stranded alone?',
                 '',
                 '(a) Know everything about paragraphs',
                 '',
                 '')
    simple_slide('How can the heading predict',
                 'when it will be stranded alone?',
                 '',
                 '(a) Know everything about paragraphs',
                 '— or —',
                 '(b) Ask next item to lay itself out speculatively')
    s('But this is going to require', '“undo” — the ability to back up')
    c('''
    # Heading

    def heading(...):
        add itself to document
        add the following paragraph to the document
        if there is content beneath heading:
            return
        undo the paragraph
        undo the heading
        start over on next page
    ''')
    simple_slide('Consequence #1', '', 'Layout needs to return',
                 'an intermediate data structure',
                 'that the caller can inspect')
    simple_slide('', 'Consequence #2', '', 'The intermediate data',
                 'needs to be easy to discard')

    s('Iterators?', 'Generators?', 'Lists of lists?', 'Trees?')
    progressive_slide(s, 'A:', 'Linked list')
    code_slide('''
    Column = NamedTuple(… 'width height')
    Line = NamedTuple(…, 'previous column y graphics')

    c1 = Column(…)
    line1 = Line(None, c1, 0, [])
    line2 = Line(line1, c1, 14, [])
    line3 = Line(line2, c1, 28, [])
    ''')
    c('''
    ┌────┐   ┌────┐
    │line│ ← │line│
    └────┘   └────┘
    ''')
    c('''
                      ┌────┐   ┌────┐   ┌────┐
                      │line│ ← │line│ ← │line│ A
    ┌────┐   ┌────┐ ↙ └────┘   └────┘   └────┘
    │line│ ← │line│
    └────┘   └────┘ ↖ ┌────┐   ┌────┐   ┌────┐
                      │line│ ← │line│ ← │line│ B
                      └────┘   └────┘   └────┘
    ''')

    s('A linked list lets us extend the document',
      'with any number of speculative layouts,',
      'which Python automatically disposes of',
      'when we’re done')
    s('We now need a new argument:',
      'the most recently laid out line')
    c('''
               ↓
    paragraph(line, column, y, next_column, ...):
    ''')
    s('But look!')
    c('''
                      ↓     ↓
    paragraph(line, column, y, next_column, ...)

    # But what is a line?            ↓    ↓
    Line = NamedTuple(…, 'previous column y graphics')
    ''')
    c('''
    paragraph(line, next_column, ...)
    ''')
    s('Designing our return value',
      'wound up eliminating two', 'of our input arguments',
      '', 'Always look for chances to simplify',
      'after designing a new part of your system')
    s('Also nice:', 'Symmetry!')
    c('''
    # The Line becomes a common currency that is
    # both our argument and our return value:

    def paragraph(line, next_column, ...):
        ...
        return last_line_of_paragraph
    ''')

    s('We now have a scheme whereby paragraphs can plan',
      'their layout without writing to the PDF yet',
      '',
      'But how will the heading’s code find',
      'and invoke the paragraph that follows it?')
    # d.new_page()
    # run_and_draw(lotr, fonts, None, narrow_line, d.painter)
    # d.new_page()
    # run_and_draw(lotr2, fonts, None, narrow_line, d.painter)  #?
    s('Well: what drives the layout process?')

    # TODO
    s('Q:', 'How can the heading signal', 'that it needs the next item?')
    s('Special callable?', 'Exception?', 'Coroutine?')
    s('This is a prototype.', 'I’m learning the problem.',
      'Let’s just do the easiest possible thing.')
    c(sample_actions)
    c('''
    def heading(actions, a, line, next_column, …):
        …
        return heading_line
    ''')
    # TODO: shorten
    s('Q:', 'But wait!', 'Why throw out', 'the paragraph’s work?')
    c('''
    def heading(actions, a, line, next_column, …):
        …
        return heading_line
        # - OR -
        return last_line_of_next_paragraph
    ''')
    # Should I show the heading logic? Or does that come later?
    s('But won’t the paragraph be printed again',
      'when the engine itself calls the next item?')
    c('''
    def heading(actions, a, line, next_column, …):
        …
        # Let’s also return the next index
        # that the engine should render!
        return a + 2, last_line
    ''')

    # The spammish repetition.

    s('Stepping back, I looked askance',
      'at the repetition in my code')
    # TODO Call them "opinionated actions"
    c('''
    # Some routines actually use `actions` and `a`:
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    # But many ignored `actions` and returned `a + 1`:
    def paragraph(actions, a, line, next_column, …):
        … return a + 1, line2
    def center_text(actions, a, line, next_column, …):
        … return a + 1, line2
    ''')
    s('How can I eliminate `actions` and `a`',
      'from innocent routines that don’t need them?')
    s('DRY')
    s('“Don’t Repeat Yourself”', '', 'I suddenly',
      'heard the call', 'of distant decades')
    s('1990s', '', 'Introspect each function to learn',
      'if it takes `actions` and `a` or not!')
    c('''
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    def paragraph(line, next_column, …):
        … return line2
    def center_text(line, next_column, …):
        … return line2
    ''')
    s('Early 2000s', '', 'Special registry for functions',
      'that don’t need `actions` and `a`')
    s('Late 2000s', '', 'A decorator for functions',
      'that don’t need `actions` and `a`')
    c('''
    def simple(function):
        def wrapper(actions, a, line, next_col, *args):
            line2 = function(line, next_col, *args)
            return a + 1, line2
        return wrapper
    ''')
    c('''
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    @simple
    def paragraph(line, next_column, …):
        … return line2
    @simple
    def center_text(line, next_column, …):
        … return line2
    ''')
    s('And what did I decide?')
    s('Symmetry')
    c('''
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    def paragraph(actions, a, line, next_column, …):
        … return a + 1, line2
    def center_text(actions, a, line, next_column, …):
        … return a + 1, line2
    ''')
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
    s('In summary:', 'I decided against DRY', 'and simply repeated myself')
    c('''
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    def paragraph(actions, a, line, next_column, …):
        … return a + 1, line2
    def center_text(actions, a, line, next_column, …):
        … return a + 1, line2
    ''')

    # (show "how heading works") <- (what?)

    s('We’re ready for a final design step!')
    s('widows', 'and', 'orphans')
    s('How does that look in code?')
    c('''
    def paragraph(…):
        lay out paragraph
        if it stranded an orphan at the page bottom:
            try again
        if it stranded a widow at the page top:
            try again
    ''')
    s('Inside of its widow-orphan logic,',
      'paragraph() will have an inner routine',
      'that does the actual paragraph layout')
    # TODO: clean up justification
    s('What if you just want the simple part?')
    s('In the old days,',  'I would have parametrized')
    c('''
    def paragraph(…, no_widows=True, no_orphans=True):
        …
    ''')
    s('But —', '', 'This looks a lot', 'like our heading logic')
    c('''
    if the heading is alone at bottom of column:
        try again

    if this paragraph creates an orphan:
        try again
    ''')
    c('''
    actions = [
        (heading, '1. Concerning Hobbits'),
        (paragraph, 'Hobbits are an unobtrusive…'),
    ]
    ''')
    s('What if, instead of widow-orphan logic',
      'being coupled to the paragraph() routine,',
      'it lived outside and could be composed',
      'with the paragraph?')
    c('''
    actions = [
        (avoid_widows_and_orphans,),
        (paragraph, 'Hobbits are an unobtrusive…'),
    ]
    ''')
    s('Composition » Coupling+Configuration')
    s('Problem:', '', 'To avoid a widow, the paragraph needs',
      'to move to the second column early',
      '', 'How will we convince it to do that?')
    c('''
    # Each time the paragraph needs another line:
    leading = …
    height = …
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

    def paragraph(…, next_column, …):
        …
        if y + leading + height > column.height:
             …
    ''')
    c('''
    # Let's change that up.

    def paragraph(…, next_line, …):
        …
    ''')
    # TODO move this up and admit I had already factored it out
    # but now wanted to be inside
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
    def avoid_widows_and_orphans(…, next_line, …):

        def fancy_next_line(…):
            # A wrapper that makes its own decisions!

        # Call the paragraph with fancy_next_line()
    ''')
    s('Did you catch the win?')
    s('The simple wrapper would not have worked',
      'if we had not avoided premature Object Orientation!')
    s('A function is easy to wrap!', '',
      'A method? Hard!')
    s('Monkey patching?',
      'An Adapter class?',
      'Gang of Four Decorator?')
    s('In Object Orientation, customizing a verb',
      'can require trundling out an entire design pattern')
    s('But if you pass functions —',
      'if you treat verbs as first class citizens —',
      'a simple wrapper can put you',
      'in the room where it happens')
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

    s('Sure Print and Design', 'Toronto, Canada', '',
      'Supported run of only 2 books!')

    s('328 hardcover pages')

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212247.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212354.jpg')
    d.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('I’ll be releasing the “typesetting” Python library',
      'at the end of the month — follow me on Twitter',
      'if you’re interested in following along')

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

def lay_out_paragraph(fonts, d, actions):
    next_line = slide_layout()
    run_and_draw_centered(actions, fonts, None, next_line, d.painter)

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
        #print(line.graphics)
        line = line._replace(y = line.y + offset)
        for graphic in line.graphics:
            function, *args = graphic
            function(fonts, line, painter, *args)
    return line

if __name__ == '__main__':
    main(sys.argv[1:])
