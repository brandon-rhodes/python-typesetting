from reportlab.pdfgen.canvas import Canvas
from .knuth import wrap_paragraph
from .skeleton import Page, Chase, Line

inch = 72.

FONT_SIZE = 10.

PAGE_WIDTH = 6. * 72.
PAGE_HEIGHT = 9. * 72.

INNER_MARGIN = 54.
OUTER_MARGIN = inch
BOTTOM_MARGIN = inch + 6.
TOP_MARGIN = inch - 6.

class Setter(object):
    pass

class Document(object):

    def format(self, story):

        p = Page(self, PAGE_WIDTH, PAGE_HEIGHT)
        c = Chase(p, TOP_MARGIN, BOTTOM_MARGIN, INNER_MARGIN, OUTER_MARGIN)

        canvas = Canvas(
            'book.pdf', pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        canvas.setFont('Roman', FONT_SIZE)

        line = Line(c)
        line.text = u'foo'
        for item in story:
            if item.__class__.__name__ == 'Spacer':
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
                for s in [item.text]:
                    if item.style == 'indented-paragraph':
                        indent = FONT_SIZE
                    else:
                        indent = 0.0
                    line = wrap_paragraph(canvas, line, item, indent)

        pages = line.unroll_document()

        for page in pages:
          canvas.showPage()
          canvas.setFont('Roman', FONT_SIZE)
          for chase in page.chases:
           for line in chase.lines:
            if line.align == 'center':
                s = u' '.join(line.words)
                ww = canvas.stringWidth(s)
                canvas.drawString(line.chase.x + line.chase.width / 2. - ww / 2.,
                                  line.ay(), s)
            for graphic in line.graphics:
                graphic.draw(canvas)

        canvas.save()

class Paragraph(object):

    def __init__(self, text, style):
        self.text = text
        self.style = style

class Spacer(object):

    def __init__(self, *args):
        self.args = args
