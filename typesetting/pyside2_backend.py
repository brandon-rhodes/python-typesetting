import os
from PySide2.QtGui import QFontDatabase

def get_fonts(painter, font_specs):
    fonts = {}
    database = QFontDatabase()
    for key, family, style, size in font_specs:
        weight = database.weight(family, style)
        qt_font = database.font(family, style, size)
        actual_family = qt_font.family()
        if weight == -1 or family != actual_family:
            print('Cannot find font: {!r} {!r}'.format(family, style))
            os._exit(1)
        painter.setFont(qt_font)
        metrics = painter.fontMetrics()
        fonts[key] = Font(qt_font, metrics)
    return fonts

class Font(object):
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self._qt_metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200
        self.descent = metrics.descent() * 72 / 1200
        self.height = metrics.height() * 72 / 1200
        self.leading = metrics.lineSpacing() * 72 / 1200 - self.height

    def width_of(self, text):
        return self._qt_metrics.width(text) * 72 / 1200
