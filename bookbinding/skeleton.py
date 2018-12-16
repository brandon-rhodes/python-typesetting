
class OldPage(object):

    def __init__(self, document, width, height, folio=1, previous=None):
        self.document = document
        self.width = width
        self.height = height
        self.folio = folio
        self.is_recto = (folio % 2 == 1)
        self.is_verso = (folio % 2 == 0)
        self.previous = previous

    def next(self):
        return OldPage(self.document, self.width, self.height,
                    self.folio + 1, self)

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
        self.y = top_margin

        self.graphics = []

    def next(self):
        return Chase(self.page.next(), self.top_margin, self.bottom_margin,
                     self.inner_margin, self.outer_margin)

from collections import namedtuple

Font = namedtuple('Font', 'ascent descent height leading')

Page = namedtuple('Page', 'width height')
Column = namedtuple('Column', 'page id width height')
Line = namedtuple('Line', 'previous column y words')

class OldLine(object):

    def __init__(self, chase, y, previous=None):
        self.chase = chase
        self.w = chase.width
        self.y = y
        self.previous = previous
        self.justify = None
        self.words = ()
        self.align = None
        self.graphics = []

    def need(self, height):
        """Return `self` if at least `height` remains, else a new line."""
        asdf
        if height <= chase.height - self.y: #self.y:
            return self
        next_chase = self.chase.next()
        return OldLine(next_chase, previous=self)

    def next(self, line_height, ascent):
        # TODO: also accept ascent?
        if not self.at_bottom(line_height):
            return self.down(line_height)
        else:
            next_chase = self.chase.next()
            return OldLine(next_chase, previous=self, y=ascent)

    def down(self, line_height):
        return OldLine(self.chase, previous=self, y=self.y + line_height)

    def at_bottom(self, line_height):
        return self.y > self.chase.height - line_height

    def ay(self):
        return self.chase.top_margin + self.y

    def unroll_document(self):
        lines = old_unroll(self)
        pages = old_unroll(self.chase.page)

        lines.reverse()
        pages.reverse()

        for page in pages:
            page.chases = []
        for line in lines:
            chase = line.chase
            if chase not in chase.page.chases:
                chase.page.chases.append(chase)
            if not hasattr(chase, 'lines'):
                chase.lines = []
            line.chase.lines.append(line)
        return pages

def old_unroll(item):
    items = []
    while item:
        items.append(item)
        item = item.previous
    return items

def new_page():
    return Page(10, 34)

def next_column(column):
    page = new_page()
    id = column.id + 1 if column else 1
    return Column(page, id, 10, 34)

def next_line(line, leading, height):
    if line:
        column = line.column
        y = line.y + height + leading
        if y <= column.height:
            return Line(line, column, y, [])
    else:
        column = None
    return Line(line, next_column(column), height, [])

def unroll(start_line, end_line):
    lines = [end_line]
    while end_line is not start_line:
        end_line = end_line.previous
        lines.append(end_line)
    lines.reverse()
    return lines
