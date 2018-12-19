
from .skeleton import unroll

def run(actions, fonts, line, next_line):
    a = 0
    while a < len(actions):
        a, line = call_action(actions, a, fonts, line, next_line)
    return line

def call_action(actions, a, fonts, line, next_line):
    action, *args = actions[a]
    return action(actions, a, fonts, line, next_line, *args)

def blank_line(actions, a, fonts, line, next_line, graphic):
    line2 = next_line(line, 2, 10)
    if line2.column is not line.column:
        line2 = next_line(line, 9999999, 0)
    return a + 1, line2

def section_break(actions, a, fonts, line, next_line, graphic):
    at_top = line is None
    a1 = a + 1
    if at_top:
        return a1, line

    at_bottom = a1 == len(actions)
    if at_bottom:
        return a1, line

    line2 = next_line(line, 2, 10)  # TODO: fix hard-coded values

    if line2.column is not line.column:
        line2.graphics.append(graphic)
        line3 = next_line(line2, 2, 10)
        return a1, line3

    a2, line3 = call_action(actions, a1, fonts, line2, next_line)
    # if line3 is line2:
    #     return a2, line3
    lines = unroll(line2, line3)
    assert line2 is lines[0]
    if line2.column is lines[1].column:
        return a2, line3

    line3 = next_line(line2, 2, 10)
    line3.graphics.append(graphic)
    if line3.column is line.column:
        line4 = next_line(line3, 99999999, 0)
    else:
        line4 = next_line(line3, 2, 10)
        if line4.column is not line3.column:
            line4 = next_line(line3, 99999999, 0)
    return a1, line4

def section_title(actions, a, fonts, line, next_line):
    a1 = a + 1
    if a1 == len(actions):
        return a1, line

    a2, title_line = call_action(actions, a1, fonts, line, next_line)
    a3, following_line = call_action(actions, a2, fonts, title_line, next_line)
    lines1 = unroll(line, title_line)
    lines2 = unroll(title_line, following_line)
    first_line_of_title = lines1[1]
    line_after_title = lines2[1]
    if first_line_of_title.column is line_after_title.column:
        return a3, following_line

    # Otherwise, move the title to the top of the next column.
    def next_line2(line2, leading, height):
        if line2 is line:
            leading = 9999999
        return next_line(line2, leading, height)

    a2, title_line = call_action(actions, a1, fonts, line, next_line2)
    return a2, title_line

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
        if (line2.column.id, line2.y) in skips:
            line2 = next_line(line, 99999, height)
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

def ragged_paragraph(actions, a, fonts, line, next_line, fonts_and_texts):
    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)
    line = next_line(line, leading, height)

    for font_name, text in fonts_and_texts:
        font = fonts[font_name]
        line.graphics.append((draw_text, font_name, text))

    return a + 1, line

def draw_text(fonts, line, painter, font_name, text):
    pt = 1200 / 72.0
    font = fonts[font_name]
    painter.setFont(font.qt_font)
    painter.drawText((line.column.x) * pt,
                     (line.column.y + line.y - font.descent) * pt,
                     text)
