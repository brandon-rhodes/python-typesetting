
from .skeleton import unroll

def run(actions, fonts, line, next_line):
    a = 0
    while a < len(actions):
        a, line = call_action(actions, a, fonts, line, next_line)
    return line

def call_action(actions, a, fonts, line, next_line):
    action, *args = actions[a]
    return action(actions, a, fonts, line, next_line, *args)

def section_title(actions, a, fonts, line, next_line, title):
    line2 = next_line(line, 2, 10)
    if a + 1 == len(actions):
        return a + 1, line2
    a2, line3 = call_action(actions, a + 1, fonts, line2, next_line)
    lines = unroll(line2, line3)

    # If we are in the same column as the following content, declare
    # victory.
    if lines[0].column is lines[1].column:
        return a2, line3

    # Try moving this title to the top of the next column.
    line2b = next_line(line, 9999999, 10)
    a2b, line3b = call_action(actions, a + 1, fonts, line2b, next_line)
    linesb = unroll(line2b, line3b)
    if linesb[0].column is linesb[1].column:
        return a2b, line3b

    # We were still separated from our content?  Give up and keep
    # ourselves on our original page.
    return a2, line3

def avoid_widows_and_orphans(actions, a, fonts, line, next_line):
    a2, end_line = call_action(actions, a + 1, fonts, line, next_line)
    lines = unroll(line, end_line)

    # Single-line paragraphs produce neither widows nor orphans.
    if len(lines) == 2:
        return a2, end_line  # TODO: untested

    original_a2 = a2
    original_end_line = end_line

    def reflow():
        nonlocal end_line, lines
        a2, end_line = call_action(actions, a + 1, fonts, line, fancy_next_line)
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

    def fancy_next_line(line, leading, height):
        line2 = next_line(line, leading, height)
        while (line2.column.id, line2.y) in skips:
            line2 = next_line(line, leading + 99999, height)
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

    if is_orphan() or is_widow():
        return original_a2, original_end_line

    return a2, end_line
