
from bookbinding.skeleton import Column, Line2 as Line, Font, Page2 as Page

def next_page(page):
    return Page(10, 34)

def next_column(column):
    page = next_page(column.page if column else None)
    return Column(page, 10, 34)

def next_line(font, line):
    if line:
        column = line.column
        y = line.y + font.height + font.leading
        if y <= column.height:
            return Line(line, column, y, [])
    else:
        column = None
    return Line(line, next_column(column), font.height, [])

def test_line_positions():
    f = Font(8, 2, 10, 2)
    l1 = next_line(f, None)
    l2 = next_line(f, l1)
    l3 = next_line(f, l2)
    l4 = next_line(f, l3)

    p = Page(10, 34)
    c = Column(p, 10, 34)
    assert l1 == Line(None, c, 10, [])
    assert l2 == Line(l1, c, 22, [])
    assert l3 == Line(l2, c, 34, [])
    assert l4 == Line(l3, c, 10, [])
