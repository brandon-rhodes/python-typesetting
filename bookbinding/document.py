from reportlab.pdfgen.canvas import Canvas
from .hyphenate import hyphenate_word
from .skeleton import Page, Chase, Line
from texlib.wrap import ObjectList, Box, Glue, Penalty

import re

inch = 72.

FONT_SIZE = 10.

PAGE_WIDTH = 6. * 72.
PAGE_HEIGHT = 9. * 72.

INNER_MARGIN = 54.
OUTER_MARGIN = inch
BOTTOM_MARGIN = inch + 6.
TOP_MARGIN = inch - 6.

class Setter(object):
    pass

class Document(object):

    def format(self, story):

        p = Page(self, PAGE_WIDTH, PAGE_HEIGHT)
        c = Chase(p, TOP_MARGIN, BOTTOM_MARGIN, INNER_MARGIN, OUTER_MARGIN)

        canvas = Canvas(
            'book.pdf', pagesize=(PAGE_WIDTH, PAGE_HEIGHT))
        canvas.setFont('Roman', FONT_SIZE)

        line = Line(c)
        line.text = u'foo'
        for item in story:
            if item.__class__.__name__ == 'Spacer':
                if not line.at_bottom():
                    line = line.next()
                # if line.at_bottom():
                #     line = line.next()
                #     line.words = [u'*']
                #     line.align = 'center'
                # line = line.next()
                # if line.at_bottom():
                #     line = line.down(1)
                #     line.words = [u'*']
                #     line.align = 'center'
            elif isinstance(item, Paragraph):
                for s in [item.text]:
                    #line = wrap_paragraph(canvas, line, item)
                    line = wrap_paragraph_knuth(canvas, line, item)

        lines = []
        while line:
            lines.append(line)
            line = line.previous

        lines.reverse()

        page = None
        for line in lines:
            if line.chase.page is not page:
                canvas.showPage()
                canvas.setFont('Roman', FONT_SIZE)
                page = line.chase.page
            if line.justify:
                ww = canvas.stringWidth(u''.join(line.words))
                space = (line.w - line.indent - ww) / (len(line.words) - 1)
                x = 0
                for word in line.words:
                    canvas.drawString(line.chase.x + x + line.indent, line.ay(),
                                      word)
                    x += space + canvas.stringWidth(word)
            elif line.align == 'center':
                s = u' '.join(line.words)
                ww = canvas.stringWidth(s)
                canvas.drawString(line.chase.x + line.chase.width / 2. - ww / 2.,
                                  line.ay(), s)
            elif hasattr(line, 'things'):
                ww = 0.
                ay = line.ay()
                for thing in line.things:
                    if isinstance(thing, Box):
                        canvas.drawString(line.chase.x + ww, ay, thing.character)
                        ww += canvas.stringWidth(thing.character)
                    elif isinstance(thing, Glue):
                        ww += thing.glue_width

        canvas.save()

def wrap_paragraph(canvas, line, pp):
    words = pp.text.split()
    indent = FONT_SIZE if pp.style.startswith('indented') else 0
    width = line.w - indent
    while words:
        i = 2
        el = u' '.join(words[:i])
        while canvas.stringWidth(el) < width:
            if i >= len(words):
                break
            el += u' ' + words[i]
            i += 1
        else:
            i -= 1
        line = line.next()
        line.words = words[:i]
        line.justify = i < len(words)
        line.indent = indent
        words = words[i:]
        indent, width = 0, line.w
    return line

wordre = re.compile('(\w+)')
STRING_WIDTHS = {}

def wrap_paragraph_knuth(canvas, line, pp):

    olist = ObjectList()
    # olist.debug = True

    if pp.style == 'indented-paragraph':
        olist.append(Glue(FONT_SIZE, 0, 0))

    space_width = canvas.stringWidth(u' ')
    hyphen_width = canvas.stringWidth(u'-')

    for word in pp.text.split():
        pieces = hyphenate_word(word)
        for piece in pieces:
            w = STRING_WIDTHS.get(piece)
            if w is None:
                w = STRING_WIDTHS[piece] = canvas.stringWidth(piece)
            olist.append(Box(w, piece))
            olist.append(Penalty(hyphen_width, 100))
        olist.pop()
        olist.append(Glue(space_width, space_width * .5, space_width * .25))
    olist.pop()
    olist.add_closing_penalty()

    # for item in olist:
    #     print item

    line_lengths = [line.w]
    for tolerance in 1, 2, 3, 4:
        try:
            breaks = olist.compute_breakpoints(
                line_lengths, tolerance=tolerance)
        except RuntimeError:
            pass
        else:
            break

    start = 0
    n = 0
    # if 'Confederate' in pp.text:
    #     print breaks, len(olist)
    # if breaks[-1] != len(olist) - 1:
    #     breaks.append(len(olist) - 1)
    for breakpoint in breaks[1:]:
        keepers = []
        r = olist.compute_adjustment_ratio(start, breakpoint, 0, (line.w,))
        # if 'Confederate' in pp.text:
        #     print breakpoint, r
        n += 1
        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                box.glue_width = box.compute_width(r)
                keepers.append(box)
            elif box.is_box():
                keepers.append(box)
        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width == hyphen_width:
            b = Box(hyphen_width, u'-')
            keepers.append(b)
        line = line.next()
        line.things = keepers
        start = breakpoint + 1

    return line

class Paragraph(object):

    def __init__(self, text, style):
        self.text = text
        self.style = style

class Spacer(object):

    def __init__(self, *args):
        self.args = args
