
from bookbinding.skeleton import Column, Line2 as Line, Font, Page2 as Page

def new_page():
    return Page(10, 34)

def next_column(column):
    page = new_page()
    return Column(page, 10, 34)

def next_line(line, height, leading):
    if line:
        column = line.column
        y = line.y + height + leading
        if y <= column.height:
            return Line(line, column, y, [])
    else:
        column = None
    return Line(line, next_column(column), height, [])

def test_line_positions():
    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)
    l3 = next_line(l2, 10, 2)
    l4 = next_line(l3, 10, 2)

    p = Page(10, 34)
    c = Column(p, 10, 34)
    assert l1 == Line(None, c, 10, [])
    assert l2 == Line(l1, c, 22, [])
    assert l3 == Line(l2, c, 34, [])
    assert l4 == Line(l3, c, 10, [])
    assert l1.column is l2.column is l3.column
    assert l3.column is not l4.column

def make_paragraph(line, next_line, height, leading, n):
    for i in range(n):
        line = next_line(line, height, leading)
    return line

def unroll(start_line, end_line):
    lines = [end_line]
    while end_line is not start_line:
        end_line = end_line.previous
        lines.append(end_line)
    lines.reverse()
    return lines

def skip_lines(next_line, line_numbers):
    X

def avoid_widows_and_orphans(line, next_line, callable, *args):
    end_line = callable(line, next_line, *args)
    lines = unroll(line, end_line)

    # Single-line paragraphs produce neither widows nor orphans.
    if len(lines) <= 2:
        return end_line

    # Avoid orphans by moving paragraph to top of next column.
    if (lines[0].column is lines[1].column # TODO: what if lines[0] is None?
        and lines[1].column is not lines[2].column):
        dy = lines[1].y - lines[0].y
        line = next_line(line, dy, 0)
        end_line = callable(line, next_line, *args)

    return end_line
    #if line.end_line 

def test_avoids_orphan():
    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)
    l5 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 3)

    l4 = l5.previous
    l3 = l4.previous
    lwat = l3.previous
    assert lwat.previous is l2

    p = Page(10, 34)
    c = Column(p, 10, 34)
    assert l2 == Line(l1, c, 22, [])
    assert l3 == Line(lwat, c, 10, [])
    assert l4 == Line(l3, c, 22, [])
    assert l5 == Line(l4, c, 34, [])


