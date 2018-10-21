from PySide2.QtCore import QSizeF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase
from PySide2.QtWidgets import QApplication

from .knuth import wrap_paragraph
from .skeleton import Page, Chase, Line

#inch = 72
mm = 25.4 / 72

class Setter(object):
    pass

class Document(object):

    def __init__(self, page_width, page_height):
        self.page_width = page_width
        self.page_height = page_height

        QApplication(['my-q-application'])
        f = QFontDatabase.addApplicationFont('OldStandard-Regular.ttf')
        f = QFontDatabase.addApplicationFont('OldStandard-Italic.ttf')
        names = QFontDatabase.applicationFontFamilies(f)
        print(names)
        name = names[0]
        self.writer = QPdfWriter('book.pdf')
        self.writer.setPageSizeMM(QSizeF(page_width * mm, page_height * mm))
        self.painter = QPainter(self.writer)

        self.fonts = {}
        self.metrics = {}

        for name_and_args in [
            ('body-roman', name, u'Roman', 11),
            ('body-italic', name, u'Italic', 11),
        ]:
            name = name_and_args[0]
            font = QFontDatabase().font(*name_and_args[1:])
            self.fonts[name] = font
            self.painter.setFont(font)
            self.metrics[name] = self.painter.fontMetrics()

        self.painter.setFont(self.fonts['body-roman'])

    def format(self, story, top_margin, bottom_margin,
               inner_margin, outer_margin):

        p = Page(self, self.page_width, self.page_height)
        c = Chase(p, top_margin, bottom_margin, inner_margin, outer_margin)

        _font_caches = {}
        _cache = None

        def width_of(string):
            w = _cache.get(string)
            if w is None:
                w = _cache[string] = self.font_metrics.width(string)
            return w

        def switch_font(name):
            nonlocal _cache
            self.font_metrics = self.metrics[name]
            _cache = _font_caches.get(name)
            if _cache is None:
                _cache = _font_caches[name] = {}

        switch_font('body-roman')

        font_height_raw = self.font_metrics.height()
        line_height_raw = self.font_metrics.lineSpacing()
        line_height = line_height_raw * 72.0 / 1200

        line = Line(c)
        for item in story:
            if isinstance(item, Spacer):
                if not line.at_bottom(line_height):
                    line = line.next(line_height)
                if line.at_bottom(line_height):
                    line.graphics.append((asterisks, width_of))
                    line = line.next(line_height)
                    line = line.next(line_height)
                # if line.at_bottom():
                #     line = line.down(1)
                #     line.words = [u'*']
                #     line.align = 'center'
            elif isinstance(item, Paragraph):
                if item.style == 'indented-paragraph':
                    indent = font_height_raw
                else:
                    indent = 0.0
                line_lengths = [c.width * 1200 / 72]
                end_line = wrap_paragraph(switch_font, width_of, line_lengths,
                                          line, item.text, indent,
                                          line_height)
                if end_line is None:
                    break
                line = end_line.next(line_height)
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

        for i, page in enumerate(pages):
            if i:
                self.writer.newPage()
            for graphic in page.graphics:
                graphic(page, paint)
            for chase in page.chases:
                for line in chase.lines:
                    for graphic in line.graphics:
                        call = graphic[0]
                        args = graphic[1:]
                        #graphic.draw(line, paint)
                        call(paint, line, *args)

        paint.end()

class Paragraph(object):

    def __init__(self, text, style):
        self.text = text
        self.style = style

class Spacer(object):

    def __init__(self, *args):
        self.args = args

def asterisks(paint, line, width_of):
    y = line.ay()
    pt = 1200 / 72.0
    a = u'* * *'
    w = width_of(a)
    x = line.chase.x * pt + (line.chase.width * pt - w) / 2
    paint.drawText(x, y * pt, a)
