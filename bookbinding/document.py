from collections import defaultdict
from reportlab.pdfgen.canvas import Canvas
from .knuth import wrap_paragraph
from .skeleton import Page, Chase, Line

inch = 72.

FONT_FACE = 'Times-Roman'
FONT_SIZE = 10.
LINE_HEIGHT = FONT_SIZE + 2.

PAGE_WIDTH = 6. * 72.
PAGE_HEIGHT = 9. * 72.

class Setter(object):
    pass

class Document(object):

    def __init__(self, font_face=FONT_FACE):
        self.font_face = font_face

    def format(self, story, top_margin, bottom_margin,
               inner_margin, outer_margin):

        p = Page(self, PAGE_WIDTH, PAGE_HEIGHT)
        c = Chase(p, top_margin, bottom_margin, inner_margin, outer_margin)

        canvas = Canvas(
            'book.pdf', pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        canvas.setFont(self.font_face, FONT_SIZE)
        self.canvas = canvas

        _widths = {}
        def width_of(string):
            w = _widths.get(string)
            if not w:
                w = canvas.stringWidth(string)
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
                    indent = FONT_SIZE
                else:
                    indent = 0.0
                end_line = wrap_paragraph(width_of, line, item, indent)
                line = end_line.next()
            else:
                line = line.need(item.height)
                line.graphics.append(item.draw)
                line = line.down(item.height)

        # Prevent a blank last page.
        while not line.graphics:
            line = line.previous

        self.pages = line.unroll_document()
        return self.pages

    def render(self, pages):
        canvas = self.canvas
        for page in pages:
            canvas.setFont(self.font_face, FONT_SIZE)
            for graphic in page.graphics:
                graphic(page, canvas)
            for chase in page.chases:
                for line in chase.lines:
                    if line.align == 'center':
                        s = u' '.join(line.words)
                        ww = canvas.stringWidth(s)
                        canvas.drawString(
                            line.chase.x + line.chase.width / 2. - ww / 2.,
                            line.ay(),
                            s,
                        )
                    for graphic in line.graphics:
                        graphic.draw(line, canvas)
            canvas.showPage()

        canvas.save()

class Paragraph(object):

    def __init__(self, text, style):
        self.text = text
        self.style = style

class Spacer(object):

    def __init__(self, *args):
        self.args = args
