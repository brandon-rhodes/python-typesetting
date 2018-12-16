from PySide2.QtCore import QSizeF, Qt, QPoint, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase, QPen
from PySide2.QtWidgets import QApplication

#from .knuth import wrap_paragraph
#from .knuth import knuth_paragraph
from .skeleton import OldPage as Page, Chase, OldLine as Line

#inch = 72
mm = 25.4 / 72

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
        self.writer.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.painter = QPainter(self.writer)

        self.fonts = {}
        self.metrics = {}

        for name_and_args in [
            ('chapter-title-roman', name, u'Roman', 18),
            ('section-title-roman', name, u'Roman', 14),
            ('body-roman', name, u'Roman', 11),
            ('body-italic', name, u'Italic', 11),
        ]:
            name = name_and_args[0]
            font = QFontDatabase().font(*name_and_args[1:])
            self.painter.setFont(font)
            metrics = self.painter.fontMetrics()
            self.fonts[name] = font
            self.metrics[name] = metrics

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
        ascent = self.font_metrics.ascent() * 72.0 / 1200

        line = Line(c, ascent)
        for item in story:
            if isinstance(item, Spacer):
                if not line.at_bottom(line_height):
                    line = line.next(line_height, ascent)
                if line.at_bottom(line_height):
                    line.graphics.append((asterisks, width_of))
                    line = line.next(line_height, ascent)
                    line = line.next(line_height, ascent)
                # if line.at_bottom():
                #     line = line.down(1)
                #     line.words = [u'*']
                #     line.align = 'center'
            elif isinstance(item, Paragraph):
                paragraph = item
                first_indent = item.first_indent
                if first_indent is True:
                    first_indent = font_height_raw
                line_lengths = [c.width * 1200 / 72]
                pieces = item.text.split('<i>')
                fonts_and_texts = [(paragraph.font_name, pieces[0])]
                for piece in pieces[1:]:
                    p2 = piece.split('</i>')
                    fonts_and_texts.append(('body-italic', p2[0]))
                    fonts_and_texts.append(('body-roman', p2[1]))
                end_line = wrap_paragraph(switch_font, width_of, line_lengths,
                                          line, fonts_and_texts,
                                          item.indent, first_indent,
                                          line_height, ascent)
                if end_line is None:
                    break
                line = end_line.next(line_height, ascent)
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
        page_graphics = flatten_graphics(pages, self.painter, self.fonts)
        return render(self.painter, self.writer, page_graphics)

def flatten_graphics(pages, painter, fonts):
    page_graphics = []

    for page in pages:
        graphics = []
        for chase in page.chases:
            graphics.append((mark_chase, painter, chase))
            for line in chase.lines:
                for graphic in line.graphics:
                    call, *args = graphic
                    graphics.append((call, fonts, painter, line) + tuple(args))
        page_graphics.append(graphics)

    return page_graphics

def render(painter, writer, page_graphics):
    #paint.setFont(self.font)

    for i, graphics in enumerate(page_graphics):
        if i:
            writer.newPage()
        for call, *args in graphics:
            call(*args)
    painter.end()

class Paragraph(object):

    def __init__(self, text, font_name, indent=0, first_indent=0,
                 margin_top=0.0, margin_bottom=0.0):
        self.text = text
        self.font_name = font_name
        self.indent = indent
        self.first_indent = first_indent
        self.margin_top = margin_top
        self.margin_bottom = margin_bottom

class Spacer(object):

    def __init__(self, *args):
        self.args = args

def asterisks(fonts, paint, line, width_of):
    # TODO: font?
    y = line.ay()
    pt = 1200 / 72.0
    a = u'* * *'
    w = width_of(a)
    x = line.chase.x * pt + (line.chase.width * pt - w) / 2
    paint.drawText(x, y * pt, a)

def mark_chase(painter, chase):
    pt = 1200 / 72.0
    P = QPen(Qt.black, pt, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(P)

    x, y = chase.x * pt, chase.y * pt
    w = chase.width * pt
    h = chase.height * pt

    painter.drawPolyline([
        QPoint(x, y),
        QPoint(x + w, y),
        QPoint(x + w, y + h),
        QPoint(x, y + h),
        QPoint(x, y),
    ])
