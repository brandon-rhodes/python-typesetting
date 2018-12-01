
from bookbinding.skeleton import Column, Line2 as Line, Page2 as Page

def new_page():
    return Page(10, 34)

def next_column(column):
    page = new_page()
    id = column.id + 1 if column else 1
    return Column(page, id, 10, 34)

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
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c1, 34, [])
    assert l4 == Line(l3, c2, 10, [])

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

def avoid_widows_and_orphans(line, next_line, add_paragraph, *args):
    end_line = add_paragraph(line, next_line, *args)
    lines = unroll(line, end_line)

    # Single-line paragraphs produce neither widows nor orphans.
    if len(lines) == 2:
        return end_line

    def orphaned(): return lines[1].column is not lines[2].column
    def widowed(): return lines[-2].column is not lines[-1].column

    def next_line2(line, height, leading):
        line2 = next_line(line, height, leading)
        if (line2.column.id, line2.y) in skips:
            line2 = next_line(line, height, leading + 99999)
        return line2

    skips = set()

    if orphaned():
        skips.add((lines[1].column.id, lines[1].y))
    elif widowed():
        skips.add((lines[-2].column.id, lines[-2].y))

    if skips:
        end_line = add_paragraph(line, next_line2, *args)
        #lines = unroll(line, end_line2)

    return end_line
    #if line.end_line

def test_avoids_orphan():
    # A simple situation: an orphan that can be avoided by not using the
    # final line of the starting column.

    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)

    l5 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 3)
    l4 = l5.previous
    l3 = l4.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c2, 34, [])

def test_avoids_widow():
    # Another simple situation: a widow that can be avoided by not using
    # the final line of the starting chase.
    l1 = None

    l5 = avoid_widows_and_orphans(l1, next_line, make_paragraph, 10, 2, 4)
    l4 = l5.previous
    l3 = l4.previous
    l2 = l3.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l2 == Line(l1, c1, 10, [])
    assert l3 == Line(l2, c1, 22, [])
    assert l4 == Line(l3, c2, 10, [])
    assert l5 == Line(l4, c2, 22, [])
