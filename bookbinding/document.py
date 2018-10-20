from PySide2.QtGui import QPdfWriter, QFontDatabase
from PySide2.QtWidgets import QApplication
from PySide2.QtGui import QPainter

from .knuth import wrap_paragraph
from .skeleton import Page, Chase, Line

inch = 72.

FONT_FACE = 'Times-Roman'
FONT_SIZE = 10.
LINE_HEIGHT = FONT_SIZE + 2.

PAGE_WIDTH = 6. * 1200
PAGE_HEIGHT = 9. * 1200

class Setter(object):
    pass

class Document(object):

    def __init__(self):
        QApplication()
        f = QFontDatabase.addApplicationFont('OldStandard-Regular.ttf')
        names = QFontDatabase.applicationFontFamilies(f)
        name = names[0]
        font = QFontDatabase().font(name, u'regular', 10)
        self.writer = QPdfWriter('book.pdf')
        self.painter = QPainter(self.writer)
        self.painter.setFont(font)
        self.font = font
        self.font_metrics = self.painter.fontMetrics()

    def format(self, story, top_margin, bottom_margin,
               inner_margin, outer_margin):

        p = Page(self, PAGE_WIDTH, PAGE_HEIGHT)
        c = Chase(p, top_margin, bottom_margin, inner_margin, outer_margin)

        _widths = {}
        def width_of(string):
            w = _widths.get(string)
            if not w:
                w = self.font_metrics.width(string)
                _widths[string] = w
            return w

        line = Line(c)
        for item in story:
            if isinstance(item, Spacer):
                if not line.at_bottom():
                    line = line.next()
                # if line.at_bottom():
                #     line = line.next()
                #     line.words = [u'*']
                #     line.align = 'center'
                # line = line.next()
                # if line.at_bottom():
                #     line = line.down(1)
                #     line.words = [u'*']
                #     line.align = 'center'
            elif isinstance(item, Paragraph):
                if item.style == 'indented-paragraph':
                    indent = FONT_SIZE * 1200 / 72
                else:
                    indent = 0.0
                line_lengths = [c.width]
                end_line = wrap_paragraph(width_of, line_lengths,
                                          line, item, indent)
                if end_line is None:
                    break
                line = end_line.next()
            else:
                line = line.need(item.height)
                line.graphics.append(item.draw)
                line = line.down(item.height)

        # Prevent a blank last page.
        while line.previous and not line.graphics:
            line = line.previous

        self.pages = line.unroll_document()
        return self.pages

    def render(self, pages):
        paint = self.painter
        #paint.setFont(self.font)

        for page in pages[:1]:
            for graphic in page.graphics:
                graphic(page, paint)
            for chase in page.chases:
                for line in chase.lines:
                    for graphic in line.graphics:
                        graphic.draw(line, paint)

        paint.end()

        # w.newPage()?

class Paragraph(object):

    def __init__(self, text, style):
        self.text = text
        self.style = style

class Spacer(object):

    def __init__(self, *args):
        self.args = args
