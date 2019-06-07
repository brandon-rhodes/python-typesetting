import sys
from .skeleton import Line, unroll

def run(actions, fonts, line, next_line):
    a = 0
    while a < len(actions):
        a, line = call_action(actions, a, fonts, line, next_line)
    return line

def call_action(actions, a, fonts, line, next_line):
    action, *args = actions[a]
    return action(actions, a, fonts, line, next_line, *args)

def add_leading(line, next_line, leading=9999999):
    """Add `leading` to the leading of the first line after `line`."""
    def next_line2(line2, leading2, height):
        if line2 is line:
            leading2 = leading
        return next_line(line2, leading2, height)
    return next_line2

def new_page(actions, a, fonts, line, next_line):
    if line is None:
        return a + 1, line
    def next_line2(line2, leading, height):
        if line2 is line:
            leading = 9999999
        return next_line(line2, leading, height)
    return call_action(actions, a + 1, fonts, line, next_line2)

def new_recto_page(actions, a, fonts, line, next_line):
    if line is None:
        return a + 1, line
    if line.column.id % 2:
        line = next_line(line, 9999999, 0)
    return new_page(actions, a, fonts, line, next_line)

def blank_line(actions, a, fonts, line, next_line, graphic):
    line2 = next_line(line, 2, 10)
    if line2.column is not line.column:
        line2 = next_line(line, 9999999, 0)  # TODO: bad solution
    return a + 1, line2

def wrap_graphic(original_graphic, original_line):
    # TODO: this is a bit wonky; simplify
    def graphic(fonts, line, painter, *args):
        return original_graphic[0](fonts, original_line, painter, *args)
    call_and_args = list(original_graphic)
    call_and_args[0] = graphic
    return tuple(call_and_args)

def space_before_and_after(actions, a, fonts, line, next_line, above, below):
    def next_line2(line2, leading, height):
        if line2 is line:
            leading = above
        return next_line(line2, leading, height)

    a2, line2 = call_action(actions, a + 1, fonts, line, next_line2)

    if below:
        line2 = Line(
            previous=line2.previous,
            column=line2.column,
            y=line2.y + below,
            graphics=[wrap_graphic(g, line2) for g in line2.graphics],
        )

    return a2, line2

def section_break(actions, a, fonts, line, next_line,
                  font_name, graphic):
    font = fonts[font_name]
    leading = font.leading
    height = font.height

    at_top = line is None
    a1 = a + 1
    if at_top:
        return a1, line

    at_bottom = a1 == len(actions)
    if at_bottom:
        return a1, line

    # Add a blank line.
    line2 = next_line(line, leading, height)

    if line2.column is not line.column:
        # Our attempt to add a blank line pushed us to the next page.
        # Instead, use the line for the graphic.
        line2.graphics.append(graphic)
        line3 = next_line(line2, leading, height)
        return a1, line3

    # See what the following content does after the blank line.
    a2, line3 = call_action(actions, a1, fonts, line2, next_line)
    lines = unroll(line2, line3)
    assert line2 is lines[0]
    if line2.column is lines[1].column:
        # A simple blank line works! The following content (at least its
        # first line) stayed here on the same page.
        return a2, line3

    # A blank line pushed the following content to the next page. Add a
    # separator graphic.
    line3 = next_line(line2, leading, height)
    line3.graphics.append(graphic)

    if line3.column is not line.column:
        # The separator landed on the next page! To avoid the extra
        # blank line at the bottom of the column, rebuild atop `line`,
        # and put a blank line after the separator instead.
        line2 = next_line(line, 9999999, height)
        line2.graphics.append(graphic)
        line3 = next_line(line2, leading, height)
        return a1, line3

    # Re-run the following content, forcing it on to the next page.
    a = add_leading(line3, next_line)
    return call_action(actions, a1, fonts, line3, a)

def section_title(actions, a, fonts, line, next_line):
    """Move the next action on to the same page as the action that follows."""
    a1 = a + 1
    if a1 == len(actions):
        return a1, line

    a2, title_line = call_action(actions, a1, fonts, line, next_line)
    if title_line is line:
        die('The action:', actions[a],
            'expects to be followed by an action that generates at least one'
            ' line, but the actions that followed:', actions[a1:a2],
            'did not generate a line.')

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

    unwrapped_lines = split_texts_into_lines(fonts_and_texts)
    wrapped_lines = wrap_long_lines(fonts, unwrapped_lines, line.column.width)

    for tuples in wrapped_lines:
        #print(tuples)
        line = next_line(line, leading, height)
        x = 0
        for font_name, text, width in tuples:
            line.graphics.append((draw_text, x, font_name, text))
            x += width

    return a + 1, line

def centered_paragraph(actions, a, fonts, line, next_line, fonts_and_texts):
    # Just like a ragged paragraph, but with different x's. TODO: can
    # probably be refectored to share more code; but can they shared
    # more code without making them both more complicated?
    leading = max(fonts[name].leading for name, text in fonts_and_texts)
    height = max(fonts[name].height for name, text in fonts_and_texts)

    unwrapped_lines = split_texts_into_lines(fonts_and_texts)
    wrapped_lines = wrap_long_lines(fonts, unwrapped_lines, line.column.width)

    for tuples in wrapped_lines:
        #print(tuples)
        line = next_line(line, leading, height)
        content_width = sum(width for font_name, text, width in tuples)
        x = (line.column.width - content_width) / 2.0
        for font_name, text, width in tuples:
            line.graphics.append((draw_text, x, font_name, text))
            x += width

    return a + 1, line

def wrap_long_lines(fonts, lines, width):
    return [list(wrap_long_line(fonts, line, width)) for line in lines]

def wrap_long_line(fonts, texts_and_fonts, width):
    #line = []
    x = 0
    for font_name, text in texts_and_fonts:
        # if line:
        #     pass
        width = fonts[font_name].width_of(text)
        yield font_name, text, width
    #yield line

def split_texts_into_lines(fonts_and_texts):
    line = []
    for font_name, text in fonts_and_texts:
        pieces = text.split('\n')
        if pieces[0]:
            line.append((font_name, pieces[0]))
        for piece in pieces[1:]:
            yield line
            line = []
            if piece:
                line.append((font_name, piece))
    yield line

# def wrap_lines(lines_of_fonts_and_texts):

def draw_text(fonts, line, painter, x, font_name, text):
    pt = 1200 / 72.0
    font = fonts[font_name]
    painter.setFont(font.qt_font)
    painter.drawText((line.column.x + x) * pt,
                     (line.column.y + line.y - font.descent) * pt,
                     text)

def die(*args):
    strings = []
    for arg in args:
        if not isinstance(arg, str):
            arg = '\n\n{}\n\n'.format(arg)
        strings.append(arg)
    print('Composing error - ' + ''.join(strings), file=sys.stderr)
    sys.exit(1)
