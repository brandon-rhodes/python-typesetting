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

        p = Page(self, 0)
        c = Chase(OUTER_MARGIN, BOTTOM_MARGIN,
                  PAGE_WIDTH - OUTER_MARGIN - INNER_MARGIN,
                  PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)
        p.cj += 1

        p.canvas.setFont('Roman', FONT_SIZE)

        line = Line(p, c)
        for item in story:
            if not item.__class__.__name__.endswith('Paragraph'):
                continue
            for s in [item.text]:
                p.canvas.drawString(c.x, line.ay(), s)
                line = line.next()
        p.canvas.save()

class Line(object):

    def __init__(self, page, chase, previous=None, dy=0):
        self.page = page
        self.chase = chase
        if previous is None:
            self.y = chase.h - LINE_HEIGHT - dy
        else:
            self.y = previous.y - dy

    def next(self):
        return Line(self.page, self.chase, self, LINE_HEIGHT)

    def ay(self):
        return self.chase.y + self.y
