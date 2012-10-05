from reportlab.pdfgen.canvas import Canvas

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

    def __init__(self, document, folio=0, previous=None):
        self.document = document
        self.folio = folio
        self.previous = previous

    def next(self):
        return Page(self.document, self.folio + 1, self)

class Chase(object):
    def __init__(self, page, x, y, w, h):
        self.page = page
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def next(self):
        return Chase(self.page.next(), self.x, self.y, self.w, self.h)

class Document(object):

    def format(self, story):

        p = Page(self, 0)
        c = Chase(p, OUTER_MARGIN, BOTTOM_MARGIN,
                  PAGE_WIDTH - OUTER_MARGIN - INNER_MARGIN,
                  PAGE_HEIGHT - TOP_MARGIN - BOTTOM_MARGIN)

        line = Line(p, c)
        for item in story:
            if not item.__class__.__name__.endswith('Paragraph'):
                continue
            for s in [item.text]:
                line.text = s
                line = line.next()
                line.text = 'THE END'

        lines = []
        while line:
            lines.append(line)
            line = line.previous

        lines.reverse()

        canvas = Canvas(
            'book.pdf', pagesize=(PAGE_WIDTH, PAGE_HEIGHT))

        canvas.setFont('Roman', FONT_SIZE)

        page = None
        for line in lines:
            if line.page is not page:
                canvas.showPage()
                page = line.page
            canvas.drawString(c.x, line.ay(), line.text)

        canvas.save()

class Line(object):

    def __init__(self, page, chase, previous=None, dy=0):
        self.page = page
        self.chase = chase
        self.previous = previous
        if previous is None:
            self.y = chase.h - LINE_HEIGHT - dy
        else:
            self.y = previous.y - dy

    def next(self):
        if self.y > LINE_HEIGHT:
            return Line(self.page, self.chase, self, LINE_HEIGHT)
        else:
            chase = self.chase.next()
            line = Line(chase.page, chase, self)
            line.y = chase.h - LINE_HEIGHT
            return line

    def ay(self):
        return self.chase.y + self.y
