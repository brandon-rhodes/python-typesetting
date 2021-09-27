#!/usr/bin/env python3

from PySide2.QtWidgets import QApplication

from typesetting import composing as c
from typesetting.knuth import knuth_paragraph
from typesetting.skeleton import single_column_layout, unroll
from typesetting.writer_qt import QtWriter

actions = [
    (c.ragged_paragraph, [['body', """
In olden times when wishing still helped one, there lived a king
whose daughters were all beautiful, but the youngest was so beautiful
that the sun itself, which has seen so much, was astonished whenever
it shone in her face.  Close by the king's castle lay a great dark
forest, and under an old lime-tree in the forest was a well, and when
the day was very warm, the king's child went out into the forest and
sat down by the side of the cool fountain, and when she was bored she
took a golden ball, and threw it up on high and caught it, and this
ball was her favorite plaything.
"""]]),
]

PAGE_WIDTH = 6 * 72
PAGE_HEIGHT = 9 * 72
QApplication([])

from PySide2.QtGui import QFontDatabase
print(QFontDatabase().families())

writer = QtWriter('art.pdf', PAGE_WIDTH, PAGE_HEIGHT)
fonts = writer.get_fonts([
    ('body', 'Arial', 'Regular', 8),
])

inch = 72
INNER_MARGIN = 54.
OUTER_MARGIN = inch
BOTTOM_MARGIN = inch + 6.
TOP_MARGIN = inch - 6.

next_line = single_column_layout(
    PAGE_WIDTH, PAGE_HEIGHT,
    inner=INNER_MARGIN,
    outer=OUTER_MARGIN,
    top=TOP_MARGIN,
    bottom=BOTTOM_MARGIN,
)

d = writer
line = c.compose(actions, fonts, None, next_line)

lines = unroll(None, line)
lines = lines[1:]

def draw_text(fonts, line, writer, x, font_name, text):
    print(repr(text))
    font = fonts[font_name]
    writer.set_font(font)
    writer.draw_text(line.column.x + x,
                     line.column.y + line.y - font.descent,
                     text)

for line in lines:
    for graphic in line.graphics:
        function, *args = graphic
        print(repr(function))
        if function == 'draw_text':
            function = draw_text
        function(fonts, line, writer, *args)

writer.painter.end()

# doc = bb.Document()
# doc.format(story, 72., 72., 72., 72.)
# doc.render(doc.pages)
