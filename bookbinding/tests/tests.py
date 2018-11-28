
from bookbinding.skeleton import Column, Line2 as Line, Font, Page2 as Page

def next_page(page):
    return Page(page, 10, 34)

def next_column(column):
    page = next_page(column.page if column else None)
    return Column(column, page, 10, 34)

def next_line(font, line):
    column = next_column(line.column if line else None)
    return Line(None, column, font.height, [])

def test_line_positions():
    f = Font(8, 2, 10, 2)
    l1 = next_line(f, None)
    l2 = next_line(f, l1)

    p1 = Page(None, 10, 34)
    c1 = Column(None, p1, 10, 34)
    p2 = Page(p1, 10, 34)
    c2 = Column(c1, p2, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(None, c2, 10, [])
