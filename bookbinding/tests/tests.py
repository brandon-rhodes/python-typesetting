
from ..skeleton import Column, Line, Page, unroll, next_line
from ..composing import avoid_widows_and_orphans, run, section_title

def make_paragraph(actions, a, fonts, line, next_line, leading, height, n):
    for i in range(n):
        line = next_line(line, leading, height)
    return a + 1, line

def test_line_positions():
    l1 = next_line(None, 2, 10)
    l2 = next_line(l1, 2, 10)
    l3 = next_line(l2, 2, 10)
    l4 = next_line(l3, 2, 10)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c1, 34, [])
    assert l4 == Line(l3, c2, 10, [])

def test_nice_paragraph():
    # It produces neither an orphan nor a widow.
    l1 = next_line(None, 2, 10)
    #l3 = avoid_widows_and_orphans(l1, next_line, make_paragraph, 2, 10, 2)
    l3 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 2),
    ], None, l1, next_line)
    l2 = l3.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c1, 34, [])

def test_orphan():
    # A simple situation: an orphan that can be avoided by not using the
    # final line of the starting column.

    l1 = next_line(None, 2, 10)
    l2 = next_line(l1, 2, 10)

    l5 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 3),
    ], None, l2, next_line)
    l2, l3, l4 = unroll(l2, l5.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c2, 34, [])

def test_widow():
    # Another simple situation: a widow that can be avoided by not using
    # the final line of the starting column.
    l1 = None

    l5 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 4),
    ], None, l1, next_line)
    l1, l2, l3, l4 = unroll(l1, l5.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l2 == Line(l1, c1, 10, [])
    assert l3 == Line(l2, c1, 22, [])
    assert l4 == Line(l3, c2, 10, [])
    assert l5 == Line(l4, c2, 22, [])

def test_widow_after_full_page():
    # A widow that can be avoided by not using the final line of the
    # second column of a 3-column paragraph.
    l0 = None

    l7 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 7),
    ], None, l0, next_line)
    l0, l1, l2, l3, l4, l5, l6 = unroll(l0, l7.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    c3 = Column(p, 3, 0, 0, 10, 34)
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
    l1 = next_line(None, 2, 10)
    l2 = next_line(l1, 2, 10)

    l4 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 2),
    ], None, l2, next_line)
    l3 = l4.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])

def test_orphan_then_full_page_then_widow():
    # A 3-column paragraph offering both an orphan and a window, that
    # needs a 1-line bump to fix both (and become a 2-column paragraph).
    l1 = next_line(None, 2, 10)
    l2 = next_line(l1, 2, 10)

    l7 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 5),
    ], None, l2, next_line)
    l2, l3, l4, l5, l6 = unroll(l2, l7.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    c3 = Column(p, 3, 0, 0, 10, 34)
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
    l1 = next_line(None, 2, 10)

    l4 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 3),
    ], None, l1, next_line)
    l1, l2, l3 = unroll(l1, l4.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c2, 10, [])
    assert l3 == Line(l2, c2, 22, [])
    assert l4 == Line(l3, c2, 34, [])

def test_orphan_whose_fix_creates_widow():
    # Another situation that needs two rounds: an orphan that can be
    # fixed by bumping the final line to the next column, that then
    # creates a widow.
    l1 = next_line(None, 2, 10)
    l2 = next_line(l1, 2, 10)

    l6 = run([
        (avoid_widows_and_orphans,),
        (make_paragraph, 2, 10, 4),
    ], None, l2, next_line)
    l2, l3, l4, l5 = unroll(l2, l6.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    c3 = Column(p, 3, 0, 0, 10, 34)
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
    assert l5 == Line(l4, c3, 10, [])
    assert l6 == Line(l5, c3, 22, [])

def test_widow_that_cannot_be_fixed():
    # What if the next page's columns are narrower, so trying to push
    # one line to the next page in fact fills the page and creates a
    # widow all over again?  Then the algorithm should give up and
    # return the original paragraph.

    state = 0
    def stateful_make_paragraph(actions, a, fonts, line, next_line,
                                leading, height):
        nonlocal state
        n = 6 if state else 4
        state = 1
        return make_paragraph(actions, a, fonts, line, next_line, leading, height, n)

    l4 = run([
        (avoid_widows_and_orphans,),
        (stateful_make_paragraph, 2, 10),
    ], None, None, next_line)
    l0, l1, l2, l3 = unroll(None, l4.previous)

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c1, 34, [])
    assert l4 == Line(l3, c2, 10, [])

# def section_title2(#actions, a,
#         line, next_line, title):
#     # What if we use "yield"?
#     title_line = next_line(line, 2, 10)
#     # if a + 1 == len(actions):
#     #     return a + 1, line2
#     #return a + 1, line2
#     lines = yield title_line
#     # next_action, *args = actions[a + 1]
#     # a2, line3 = next_action(actions, a + 1, line2, next_line, *args)
#     # lines = unroll(line2, line3)

#     # If we are in the same column as the following content, declare
#     # victory.
#     if lines[0].column is lines[1].column:
#         return # a2, line3

#     # Try moving this title to the top of the next column.
#     title_line2 = next_line(line, 9999999, 10)
#     # a2b, line3b = next_action(actions, a + 1, line2b, next_line, *args)
#     # linesb = unroll(line2b, line3b)
#     lines2 = yield title_line2
#     if lines2[0].column is lines2[1].column:
#         return # a2b, line3b

#     # We were still separated from our content?  Give up and keep
#     # ourselves on our original page.
#     #return a2, line3
#     yield title_line

def test_title_without_anything_after_it():
    actions = [
        (section_title, 'font', 'Title'),
    ]
    line = run(actions, None, None, next_line)
    assert line.previous is None

def test_title_with_stuff_after_it():
    # A title followed by a happy paragraph should stay in place.
    actions = [
        (section_title, 'font', 'Title'),
        (make_paragraph, 2, 10, 1),
    ]
    line = run(actions, None, None, next_line)
    assert line.previous.previous is None
    return

def test_title_without_enough_room():
    actions = [
        (make_paragraph, 2, 10, 2),
        (section_title, 'font', 'Title'),
        (make_paragraph, 2, 10, 1),
    ]
    l4 = run(actions, None, None, next_line)
    l3 = l4.previous
    l2 = l3.previous
    l1 = l2.previous

    p = Page(10, 34)
    c1 = Column(p, 1, 0, 0, 10, 34)
    c2 = Column(p, 2, 0, 0, 10, 34)
    assert l1 == Line(None, c1, 10, [])
    assert l2 == Line(l1, c1, 22, [])
    assert l3 == Line(l2, c2, 10, [])
    assert l4 == Line(l3, c2, 22, [])
