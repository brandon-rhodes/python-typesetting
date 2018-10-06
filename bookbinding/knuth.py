"""Classes that support Knuth TeX-style paragraph breaking."""

from __future__ import print_function

from texlib.wrap import ObjectList, Box, Glue, Penalty
from .hyphenate import hyphenate_word

STRING_WIDTHS = {}

def wrap_paragraph(canvas, line, pp, indent):

    olist = ObjectList()
    # olist.debug = True

    if indent:
        olist.append(Glue(indent, 0, 0))

    space_width = canvas.stringWidth(u' ')
    hyphen_width = canvas.stringWidth(u'-')

    for word in pp.text.split():
        pieces = hyphenate_word(word)
        for piece in pieces:
            w = STRING_WIDTHS.get(piece)
            if w is None:
                w = STRING_WIDTHS[piece] = canvas.stringWidth(piece)
                if piece == 'sit':
                    print('sit1', canvas.stringWidth(piece))
            olist.append(Box(w, piece))
            #olist.append(Penalty(hyphen_width, 100))
            olist.append(Penalty(0.0, 100))
        olist.pop()
        olist.append(Glue(space_width, space_width * .5, space_width * .25))
    olist.pop()
    olist.add_closing_penalty()

    # for item in olist:
    #     print item

    line_lengths = [line.w]
    for tolerance in 1, 2, 3, 4:
        # try:
            breaks = olist.compute_breakpoints(
                line_lengths, tolerance=tolerance)
        # except RuntimeError:
        #     pass
        # else:
        #     break

    assert breaks[0] == 0
    start = 0
    # if 'Confederate' in pp.text:
    #     print breaks, len(olist)
    # if breaks[-1] != len(olist) - 1:
    #     breaks.append(len(olist) - 1)
    for breakpoint in breaks[1:]:
        keepers = []
        # print(olist[breakpoint-2:breakpoint+3])
        # if breakpoint != breaks[-1]:
        #     breakpoint -= 1
        #end =
        # while end > start and 'Glue' in type(olist[end-1]).__name__:
        #     end -= 1

        print(olist[start:breakpoint])
        print(olist[breakpoint])

        r = olist.compute_adjustment_ratio(start, breakpoint, 0, (line.w,))

        print('================', type(olist))

        W = 0
        X = 0
        for item in olist[start:breakpoint]:
            W += item.width
            #compute = getattr(item, 'compute_width', None)
            #X += compute(r) if compute else item.width
            if item.is_glue():
                Xinc = item.compute_width(r)
                X += Xinc
                print('glue', Xinc)
            else:
                print('box', item.__class__.__name__, item.width)
                X += item.width

        print('{:.2f} {:.2f} {:.2f}'.format(W, X, r))

        # if 'Confederate' in pp.text:
        #     print breakpoint, r
        X = 0

        for i in range(start, breakpoint):
            box = olist[i]
            if box.is_glue():
                box.final_width = box.compute_width(r)
                keepers.append(box)
                X += box.final_width
                print('glue', box.final_width)
            elif box.is_box():
                print('box')
                keepers.append(box)
                X += box.width

        print('X2 {:.2f}'.format(X))

        bbox = olist[breakpoint]
        if bbox.is_penalty() and bbox.width == hyphen_width:
            b = Box(hyphen_width, u'-')
            keepers.append(b)
        graphic = KnuthLine()
        graphic.things = keepers
        #print('LAST1:', graphic.things[-1])
        line.graphics.append(graphic)
        line = line.next()
        start = breakpoint + 1
        #start = breakpoint

    return line.previous

class KnuthLine(object):
    """A graphic that knows how to draw a justified line of text."""

    def __call__(self, line, canvas):
        ww = 0.
        ay = line.ay()
        #print('LAST2:', self.things[-1])
        for thing in self.things:
            if isinstance(thing, Box):
                canvas.drawString(line.chase.x + ww, ay, thing.character)
                wi = canvas.stringWidth(thing.character)
                ww += canvas.stringWidth(thing.character)
                if thing.character == 'sit':
                    print('sit2', canvas.stringWidth(thing.character))
            elif isinstance(thing, Glue):
                wi = thing.final_width
                ww += thing.final_width
            print(thing.__class__.__name__, wi)
        print('~~~~~~~~~~~~~~~~~~~~~~', ww)
