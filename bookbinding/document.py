from reportlab.pdfgen import canvas

inch = 72.

FONT_SIZE = 10.
LINE_HEIGHT = FONT_SIZE + 2.

PAGE_WIDTH = 6. * 72.
PAGE_HEIGHT = 9. * 72.

INNER_MARGIN = 54.
OUTER_MARGIN = inch
BOTTOM_MARGIN = inch + 6.
TOP_MARGIN = inch - 6.

class Setter(object):
    pass

class Page(object):

    def __init__(self, document, ci):
        self.document = document
        self.ci = self.cj = ci
        self.canvas = canvas.Canvas('book.pdf',
                                    pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

class Chase(object):
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

class Document(object):

    def format(self, story):

        pages = []
        chases = []

        p = Page(self, 0)
        pages.append(p)
        c = Chase(OUTER_MARGIN, BOTTOM_MARGIN,
                  PAGE_WIDTH - OUTER_MARGIN - INNER_MARGIN,
                  PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)
        chases.append(c)
        p.cj += 1

        p.canvas.setFont('Roman', FONT_SIZE)

        y = c.h - LINE_HEIGHT
        for item in story:
            if not item.__class__.__name__.endswith('Paragraph'):
                continue
            lines = [item.text]
            for line in lines:
                p.canvas.drawString(c.x, y, line)
                y -= LINE_HEIGHT
        p.canvas.save()
