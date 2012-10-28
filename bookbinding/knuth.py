"""Classes that support Knuth TeX-style paragraph breaking."""

from texlib.wrap import Box, Glue

class KnuthLine(object):
    """A graphic that knows how to draw a justified line of text."""

    def __init__(self, line):
        self.line = line

    def draw(self, canvas):
        ww = 0.
        line = self.line
        ay = line.ay()
        for thing in self.things:
            if isinstance(thing, Box):
                canvas.drawString(line.chase.x + ww, ay, thing.character)
                ww += canvas.stringWidth(thing.character)
            elif isinstance(thing, Glue):
                ww += thing.glue_width
