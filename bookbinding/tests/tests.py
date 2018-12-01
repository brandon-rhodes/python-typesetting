
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
    original_end_line = end_line = add_paragraph(line, next_line, *args)
    lines = unroll(line, end_line)

    # Single-line paragraphs produce neither widows nor orphans.
    if len(lines) == 2:
        return end_line

    def reflow():
        nonlocal end_line, lines
        end_line = add_paragraph(line, fancy_next_line, *args)
        lines = unroll(line, end_line)

    def is_orphan():
        return lines[1].column is not lines[2].column

    def fix_orphan():
        skips.add((lines[1].column.id, lines[1].y))
        reflow()

    def is_widow():
        return lines[-2].column is not lines[-1].column

    def fix_widow():
        nonlocal end_line, lines
        skips.add((lines[-2].column.id, lines[-2].y))
        reflow()

    def fancy_next_line(line, height, leading):
        line2 = next_line(line, height, leading)
        while (line2.column.id, line2.y) in skips:
            line2 = next_line(line, height, leading + 99999)
        return line2

    skips = set()

    if is_orphan():
        fix_orphan()
        if is_widow():
            fix_widow()
    elif is_widow():
        fix_widow()
        if is_orphan():
            fix_orphan()

        # if is_orphan() or is_widow():
        #     return original_end_line
    return end_line

def test_orphan():
    # A simple situation: an orphan that can be avoided by not using the
    # final line of the starting column.

    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)

    l5 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 3)
    l2, l3, l4 = unroll(l2, l5.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c2, 34, [])

def test_widow():
    # Another simple situation: a widow that can be avoided by not using
    # the final line of the starting column.
    l1 = None

    l5 = avoid_widows_and_orphans(l1, next_line, make_paragraph, 10, 2, 4)
    l1, l2, l3, l4 = unroll(l1, l5.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l2 == Line(l1, c1, 10, [])
    assert l3 == Line(l2, c1, 22, [])
    assert l4 == Line(l3, c2, 10, [])
    assert l5 == Line(l4, c2, 22, [])

def test_widow_after_full_page():
    # A widow that can be avoided by not using the final line of the
    # second column of a 3-column paragraph.
    l0 = None

    l7 = avoid_widows_and_orphans(l0, next_line, make_paragraph, 10, 2, 7)
    l0, l1, l2, l3, l4, l5, l6 = unroll(l0, l7.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    c3 = Column(p, 3, 10, 34)
    assert l1 == Line(l0, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c1, 34, [])
    assert l4 == Line(l3, c2, 10, [])
    assert l5 == Line(l4, c2, 22, [])
    assert l6 == Line(l5, c3, 10, [])
    assert l7 == Line(l6, c3, 22, [])

def test_orphan_plus_widow():
    # A two-line paragraph straddling the end of a column, that has both
    # an orphan and a widow but only needs a 1-line bump to fix both.
    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)

    l4 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 2)
    l3 = l4.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])

def test_orphan_then_full_page_then_widow():
    # A 3-column paragraph offering both an orphan and a window, that
    # needs a 1-line bump to fix both (and become a 2-column paragraph).
    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)

    l7 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 5)
    l2, l3, l4, l5, l6 = unroll(l2, l7.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    c3 = Column(p, 3, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c2, 34, [])
    assert l6 == Line(l5, c3, 10, [])
    assert l7 == Line(l6, c3, 22, [])

def test_widow_whose_fix_creates_orphan():
    # Situation that needs two rounds: a widow that can be fixed by
    # bumping one line from the column, that then creates an orphan
    # requiring a second line to be bumped.
    l1 = next_line(None, 10, 2)

    l4 = avoid_widows_and_orphans(l1, next_line, make_paragraph, 10, 2, 3)
    l1, l2, l3 = unroll(l1, l4.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c2, 10, [])
    assert l3 == Line(l2, c2, 22, [])
    assert l4 == Line(l3, c2, 34, [])

def test_orphan_whose_fix_creates_widow():
    # Another situation that needs two rounds: an orphan that can be
    # fixed by bumping the final line to the next column, that then
    # creates a widow.
    l1 = next_line(None, 10, 2)
    l2 = next_line(l1, 10, 2)

    l6 = avoid_widows_and_orphans(l2, next_line, make_paragraph, 10, 2, 4)
    l2, l3, l4, l5 = unroll(l2, l6.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 10, 34)
    c2 = Column(p, 2, 10, 34)
    c3 = Column(p, 3, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c3, 10, [])
    assert l6 == Line(l5, c3, 22, [])
