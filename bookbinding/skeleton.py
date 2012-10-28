FONT_SIZE = 10.
LINE_HEIGHT = FONT_SIZE + 2.

class Page(object):

    def __init__(self, document, width, height, folio=1, previous=None):
        self.document = document
        self.width = width
        self.height = height
        self.folio = folio
        self.is_recto = (folio % 2 == 0)
        self.is_verso = (folio % 2 == 1)
        self.previous = previous

    def next(self):
        return Page(self.document, self.width, self.height, self.folio + 1, self)

class Chase(object):
    def __init__(self, page, top_margin, bottom_margin,
                 inner_margin, outer_margin):
        self.page = page
        self.top_margin = top_margin
        self.bottom_margin = bottom_margin
        self.inner_margin = inner_margin
        self.outer_margin = outer_margin

        self.height = page.height - top_margin - bottom_margin
        self.width = page.width - inner_margin - outer_margin

        self.x = inner_margin if page.is_recto else outer_margin

    def next(self):
        return Chase(self.page.next(), self.top_margin, self.bottom_margin,
                     self.inner_margin, self.outer_margin)

class Line(object):

    def __init__(self, chase, previous=None, y=None):
        if y is None:
            y = chase.height - LINE_HEIGHT
        self.chase = chase
        self.w = chase.width
        self.y = y
        self.previous = previous
        self.justify = None
        self.words = ()
        self.align = None

    def next(self):
        if not self.at_bottom():
            return self.down(1)
        else:
            next_chase = self.chase.next()
            return Line(next_chase, previous=self)

    def down(self, n):
        return Line(self.chase, previous=self, y=self.y - n * LINE_HEIGHT)

    def at_bottom(self):
        return self.y <= LINE_HEIGHT

    def ay(self):
        return self.chase.bottom_margin + self.y
