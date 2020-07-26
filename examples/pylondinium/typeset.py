#!/usr/bin/env python

import argparse
import os
import sys
from copy import deepcopy
from textwrap import dedent

import PySide2.QtSvg
from PySide2.QtWidgets import QApplication

from typesetting.composing import (
    avoid_widows_and_orphans, centered_paragraph, ragged_paragraph,
    run, vskip,
)
from typesetting.knuth import knuth_paragraph
from typesetting.skeleton import single_column_layout, unroll
from typesetting.writer_qt import QtWriter

def main(argv):
    parser = argparse.ArgumentParser(description='Generate slides')
    parser.parse_args(argv)

    os.chdir(os.path.dirname(__file__))

    factor = 72 / 4

    QApplication([])
    w = writer = QtWriter('slides.pdf', 16 * factor, 9 * factor)
    w.load_font('../../fonts/OldStandard-Regular.ttf')
    w.load_font('../../fonts/GenBasB.ttf')
    w.load_font('../../fonts/GenBasR.ttf')

    fonts = w.get_fonts([
        ('bold', 'Gentium Basic', 'Bold', 12),
        ('old-standard', 'Old Standard TT', 'Regular', 12),
        ('roman', 'Gentium Basic', 'Regular', 12),
        ('roman-small', 'Gentium Basic', 'Regular', 4), #?
        ('typewriter', 'Courier', 'Regular', 9),
    ])
    fonts['typewriter'].leading = 0

    simple_slide = make_simple_slide_function(fonts, w)
    code_slide = make_code_slide_function(fonts, w)

    narrow_line = slide_layout(0.5)

    lotr = [
        (knuth_paragraph, 0, 0, [('roman', """

        and all but Hobbits would find them exceedingly dull.
        Hobbits delighted in such things, if they were accurate: they
        liked to have books filled with things that they already knew,
        set out fair and square with no contradictions.

        """.strip())]),
        (vskip, 8),
        (knuth_paragraph, 0, 0, [('bold', """
        2. Concerning Pipe-weed
        """.strip())]),
        (vskip, 2),
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
    w.painter.drawPixmap(1200, 100, 1200 * n, 1196 * n, pm)

    s('τέχνη', 'craft / art')

    w.new_page()
    center_formula(w, 'logo.svg')

    s('markup language', '', 'plain text → document')

    with open('sample.tex') as f:
        code = f.read()
    code = code.split('\n', 1)[1].rsplit('\n', 2)[0]
    code_slide(code)

    w.new_page()
    center_formula(w, 'sample.svg', 20)

    s('The book’s lessons', 'on how to type .tex files',
      'were a small course in typography')
    c('Mr.~Baggins', 'Mrs.~Cotton')
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

    w.new_page()
    center_formula(w, 'formula.svg')

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

    w.new_page()
    center_formula(w, 'sample.svg', 20)

    s('The output of TeX was beautiful!',
      'But it was difficult to control.',
      '',
      'Once you set up the parameters,',
      'layout proceeded largely outside',
      'of your control')

    w.new_page()
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    w.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    s('Backing up a tractor and trailers', 'is an open problem in AI')
    s('“Fuzzy Knowledge-Based Control', 'for Backing Multi-Trailer Systems”',
      '', 'Andri Riid, Jaakko Ketola, Ennu Rüstern')
    s('Trailers are difficult to back up',
      'because the input — the motion of the tractor —',
      'has an increasingly distant relationship',
      'to the motion of the nth trailer')

    w.new_page()
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    w.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    s('Trying to control TeX', 'sometimes felt similar')
    s('Idea:')
    s('What if instead of typesetting',
      '“systems” that we merely configure',
      '',
      'there were a typesetting “library”',
      'that left the programmer in control?')
    s('Recently,', 'I realized that typesetting',
      'and printing a book from Python', 'was coming within reach!')
    s('Print-on-demand', '', 'PDF → custom hardcover')
    s('Real hardcover!', '', '• Casebound', '• Smyth sewn')

    n = 5
    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212228.jpg')
    w.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('Technology', '',
      'MetaFont → TrueType, OpenType',
      'Macro language → Markdown, RST',
      'Paragraph layout → Andrew Kuchling’s texlib',
      'DVI → PDF')

    s('', 'But what would I print?', '', '', '')
    s('', '', 'My grandfather’s essays', '', '')
    s('', '', '', 'And I would write the typesetting myself', '')
    s('', '', '', 'And I would write the typesetting myself', '— in Python!')

    s('Hwæt!', '', '')
    s('Hwæt!', '', 'Re-implementing TeX')
    s('Hwæt!', '', 'What would I do differently?')

    simple_slide('I chose a specific first goal')
    simple_slide('Different width columns?', 'Not supported in TeX')
    s('As TeX breaks a paragraph into lines',
      'it doesn’t even know what page',
      'the paragraph will land on')
    simple_slide('paragraph → lines',
                 'is a separate step from',
                 'lines → pages')
    simple_slide('My idea: the paragraph should ask for more space',
                 'as it needs it, so it learns about any width',
                 'change when it crosses to a new column')
    s('Plan', '', '1. Find a library for rendering PDF',
      '2. Invent a new page layout engine')

    w.new_page()
    lay_out_paragraph(fonts, w, [
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

    w.new_page()
    lay_out_paragraph(fonts, w, [
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

    s('What API should the layout',
      'engine use to call each action?')
    s('Let’s start by asking:',
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

    simple_slide('Problem:', 'Headings')
    s('A heading is supposed to sit atop',
      'the content of which it is the head')
    s('')
    run_and_draw(lotr, fonts, None, narrow_line, writer)
    s('Q: What if there’s no room',
      'beneath the heading?')
    s('A: Typographic disaster')
    s('')
    run_and_draw(lotr2, fonts, None, narrow_line, writer)
    s('The heading needs to move', 'itself to the next column')
    code_slide('''
    # Can the Heading simply check whether
    # there is room for a line beneath it?

    if y + 2 * (leading + height) > column.height:
        column = next_column(column)
        y = 0
    ''')
    simple_slide('But checking for a free line',
                 'won’t, alas, always work')
    simple_slide('Why?', '', 'Because a paragraphs might not choose',
                 'to use the final line of a column!')
    s('“widows and orphans”')
    simple_slide('A single-line paragraph might deign',
                 'to remain at the bottom of the page')

    s('')
    run_and_draw(lotr3, fonts, None, narrow_line, writer)
    simple_slide('But a multi-line paragraph will',
                 'refuse to leave its opening line alone —',
                 'will refuse to leave it an “orphan”')
    w.new_page()
    run_and_draw(lotr, fonts, None, narrow_line, writer)
    w.new_page()
    run_and_draw(lotr2, fonts, None, narrow_line, writer)
    simple_slide('How can the heading predict',
                 'whether it will be stranded alone?',
                 '',
                 '',
                 '',
                 '')
    simple_slide('How can the heading predict',
                 'whether it will be stranded alone?',
                 '',
                 '(a) Know everything about paragraphs',
                 '',
                 '')
    simple_slide('How can the heading predict',
                 'whether it will be stranded alone?',
                 '',
                 '(a) Know everything about paragraphs',
                 '— or —',
                 '(b) Ask next action to lay itself out speculatively')
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
      'as we discard them')
    s('Actions now need a new argument:',
      'the most recently laid out line')
    c('''
               ↓
    paragraph(line, column, y, next_column, ...):
    ''')
    s('But look!')
    c('''
                      ↓     ↓
    paragraph(line, column, y, next_column, ...)

    # What does a line know?         ↓    ↓
    Line = NamedTuple(…, 'previous column y graphics')
    ''')
    c('''
    paragraph(line, next_column, ...)
    ''')
    s('Designing our return value',
      'wound up eliminating two', 'of our input arguments',
      '', 'Always look for chances to simplify',
      'as you proceed with a design')
    s('Also nice:', 'Symmetry!')
    c('''
    # The Line becomes a common currency that is
    # both our argument and our return value:

    def paragraph(line, next_column, ...):
        ...
        return last_line_of_paragraph
    ''')

    s('But:',
      '(a) How will the heading action', 'invoke the action that follows?',
      '', '(b) How it will tell the engine', 'that the following action',
      'is already laid out?')
    s('Special callable?', 'Exception?', 'Coroutine?')
    c(sample_actions)
    c('''
    def heading(actions, a, line, next_column, …):
        …
        return a + 2, line_n
    ''')
    s('Incrementing and returning the `a` index',
      'lets an action invoke as many subsequent',
      'actions as it needs to')

    # The spammish repetition.

    s('Stepping back, I looked askance at',
      'the amount of repetition in my code')
    symmetrical = '''
    # opinionated
    def heading(actions, a, line, next_column, …):
        … return a + 2, line2
    def section(actions, a, line, next_column, …):
        … return a + 3, line2

    # simple
    def paragraph(actions, a, line, next_column, …):
        … return a + 1, line2
    def center_text(actions, a, line, next_column, …):
        … return a + 1, line2
    '''
    c(symmetrical)
    s('For “opinionated” actions',
      'that care about what follows',
      'it’s necessary to pass',
      '`action` and `a`')
    s('But simple actions ignore them!')
    c(symmetrical)
    s('How can I eliminate `actions` and `a`',
      'from simple actions that don’t need them?')
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
    s('DRY')
    s('And what did I decide?')
    s('I decided', 'to repeat myself')
    c(symmetrical)
    s('Why?', 'Symmetry')
    c(symmetrical)
    s('When I return to code', 'months and years later',
      'I re-learn by re-reading')
    s('Given a stack of functions',
      'that do exactly the same thing,',
      'if ½ of them use one convention',
      'and ½ use another —')
    s('— then I now have twice',
      'the number of conventions to re-learn,',
      'and only half the number of examples',
      'of each to learn from!')
    s('I chose verbose symmetry', 'over asymmetric brevity')
    s('As a reader,',
      'I need routines',
      'that behave the same',
      'to look the same')
    c(symmetrical)

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
      'paragraph() had a hidden inner routine',
      'that did the actual paragraph layout')
    s('What if you just wanted', 'to call the simple part?')
    c('''
    def paragraph(…, no_widows=True, no_orphans=True):
        …
    ''')
    s('But Boolean switches are often',
      'a hint that we have coupled what could',
      'actually be two different routines')
    s('Composition » Coupling')
    c('''
    actions = [
        (heading, '1. Concerning Hobbits'),
        (paragraph, 'Hobbits are an unobtrusive…'),
    ]
    ''')
    c('''
    actions = [
        (avoid_widows_and_orphans,),
        (paragraph, 'Hobbits are an unobtrusive…'),
    ]
    ''')
    s('Avoiding an orphan?', '', 'Easy!')
    c('''
       A            B
    ┌─────┐      ┌─────┐
    │  .  │      │  .  │
    │  .  │      │  .  │
    │ ----│      │     │
    └─────┘      └─────┘
    ┌─────┐      ┌─────┐
    │-----│      │ ----│
    │---  │      │-----│
    │     │      │---  │
    └─────┘      └─────┘
    ''')
    c('''
    # Before calling the paragraph, simply:

    column = next_column(column)
    y = 0
    ''')
    s('Avoiding a widow?', '')
    s('Nearly impossible')
    c('''
       A            B
    ┌─────┐      ┌─────┐
    │ ----│      │ ----│
    │-----│      │-----│
    │-----│      │     │ ←
    └─────┘      └─────┘
    ┌─────┐      ┌─────┐
    │---  │      │-----│
    │     │      │---  │
    │     │      │     │
    └─────┘      └─────┘
    ''')

    s('How would we ever convince a paragraph',
      'to move to the next column early?')
    c('''
    # Each time the paragraph needs another line:

    leading = …
    height = …
    if y + leading + height > column.height:
        # ask for another column

    # How would we influence this choice?
    ''')
    s('Lie about the value of `y`?', '',
      'Provide a fake column height?')
    s('We are looking desperately',
      'for parameters to tweak because',
      'we’re standing outside of the code',
      'that makes the decision')

    w.new_page()
    pm = PySide2.QtGui.QPixmap('two-trailers.png')
    w.painter.drawPixmap(1200, 500, 2000, 2000, pm)

    s('Outside', '', 'Is that really where we want to be',
      'during a crucial decision?')
    s('No')
    s('When code is making a crucial decision —')
    s('You want to be', 'in the room where it happens')
    s('Right now, the paragraph only consults us',
      'when it needs a whole new column',
      '',
      'next_column()')
    c('''
    def next_line(line, leading, height):
        column = line.column
        y = y + leading + height
        if y > line.column.height:
             column = next_column(line.column)
             y = height
        return Line(line, column, y, [])
    ''')
    c('''
    # What if the paragraph calls back not only
    # when it *thinks* it needs a next_column()
    # but every time it needs a next_line()?

    def paragraph(…, next_line, …):
        …
    ''')
    s('Then, the widow-orphan logic',
      'can subvert the paragraph’s normal decision',
      'simply by passing a custom next_line()!')
    c('''
    def avoid_widows_and_orphans(…, next_line, …):

        def fancy_next_line(…):
            # A wrapper around next_line() that jumps
            # to the next column early!

        paragraph(..., fancy_next_line, ...)
    ''')

    s('Success!')
    s('Did you catch why', 'this was a success?')
    s('The fancy_next_line() wrapper is so simple',
      'because we avoided premature Object Orientation!')
    c('''
    # What if instead of just passing next_line()
    # we were passing a whole Layout object?

    def paragraph(..., line, layout, ...):
        line2 = layout.next_line(line)
    ''')
    s('How would you make an object’s',
      'next_line() method return a different value?')
    s('Monkey patching?',
      'An Adapter class?',
      'Gang of Four Decorator?')
    s('In Object Orientation, customizing a verb',
      'can require trundling out an entire design pattern')
    s('But if you pass callables —',
      'if you treat your verbs as first class citizens —',
      'a simple inline wrapper can put you',
      'in the room where it happens')
    s('Lessons', '',
      'Start verbose, simplify later',
      'Value symmetry over special cases',
      'Avoid premature Object Orientation',
      'Let verbs be first-class citizens')

    s('I plan on releasing my “typesetting”',
      'Python library later this summer — but you',
      'can already watch my progress on GitHub:',
      '',
      'github.com/brandon-rhodes/python-typesetting')

    n = 5

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212228.jpg')
    w.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('Sure Print and Design', 'Toronto, Canada', '',
      'Will print runs of only 2 books!')

    s('328 hardcover pages')

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212247.jpg')
    w.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('')
    pm = PySide2.QtGui.QPixmap('IMG_20190611_212354.jpg')
    w.painter.drawPixmap(800, 100, 640 * n, 480 * n, pm)

    s('Thank you very much!', '', '', '@brandon_rhodes')

def slide_layout(narrow=0):
    factor = 72 / 4
    margin = (1 + narrow) * factor
    return single_column_layout(
        16 * factor, 9 * factor,
        margin, margin, margin, margin,
    )

def center_formula(writer, path, formula_scale=32):
    r = PySide2.QtSvg.QSvgRenderer(path)
    b = r.viewBox()
    w = b.width() * formula_scale
    h = b.height() * formula_scale
    x = (writer.painter.device().width() - w) // 2
    y = (writer.painter.device().height() - h) // 2
    b2 = PySide2.QtCore.QRect(x, y, w, h)
    r.render(writer.painter, b2)

def lay_out_paragraph(fonts, writer, actions):
    next_line = slide_layout()
    run_and_draw_centered(actions, fonts, None, next_line, writer)

def make_simple_slide_function(fonts, writer):
    def simple_slide(*texts):
        if 'PyLondinium' not in texts:  # awkward special case: title slide
            writer.new_page()
        next_line = slide_layout()
        actions = [
            (centered_paragraph, [('roman', text)])
            for text in texts
        ]
        run_and_draw_centered(actions, fonts, None, next_line, writer)
    return simple_slide

def make_code_slide_function(fonts, writer):
    def code_slide(*texts):
        writer.new_page()
        text = '\n'.join(texts)
        text = dedent(text.rstrip()).strip('\n')
        next_line = slide_layout()
        actions = [
            (ragged_paragraph, [('typewriter', line)])
            for line in text.splitlines()
        ]
        run_and_draw_centered(actions, fonts, None, next_line, writer)
    return code_slide

def progressive_slide(f, *texts):
    texts = list(texts)
    for i in range(len(texts)):
        if texts[i]:
            f(*texts[:i+1] + [''] * (len(texts) - i))

def run_and_draw(actions, fonts, line, next_line, writer):
    line2 = run(actions, fonts, line, next_line)
    lines = unroll(line, line2)
    page = None
    for line in lines[1:]:
        if page is not None and page is not line.column.page:
            break
        page = line.column.page
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'draw_text':
                function = draw_text
            elif function == 'texts':
                function = draw_texts
            function(fonts, line, writer, *args)
    return line

def run_and_draw_centered(actions, fonts, line, next_line, writer):
    line2 = run(actions, fonts, line, next_line)
    lines = unroll(line, line2)
    page = None
    assert lines[0] is None

    y = lines[-1].y
    offset = (lines[1].column.height - y) / 2
    for line in lines[1:]:
        if page is not None and page is not line.column.page:
            break
        page = line.column.page
        line = line._replace(y = line.y + offset)
        for graphic in line.graphics:
            function, *args = graphic
            if function == 'draw_text':
                function = draw_text
            elif function == 'texts':
                function = draw_texts
            else:
                raise ValueError(function)
            function(fonts, line, writer, *args)
    return line

def draw_text(fonts, line, writer, x, font_name, text):
    font = fonts[font_name]
    writer.set_font(font)
    writer.draw_text(line.column.x + x,
                     line.column.y + line.y - font.descent,
                     text)

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
