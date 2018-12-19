from PySide2.QtGui import QFontDatabase


def get_fonts(painter, font_specs):
    fonts = {}
    for key, name, style, size in font_specs:
        qt_font = QFontDatabase().font(name, style, size)
        painter.setFont(qt_font)
        metrics = painter.fontMetrics()
        fonts[key] = Font(qt_font, metrics)
    return fonts

class Font(object):
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self.metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200
        self.descent = metrics.descent() * 72 / 1200
        self.height = metrics.height() * 72 / 1200
        self.leading = metrics.lineSpacing() * 72 / 1200 - self.height

    def width_of(self, text):
        return self.metrics.width(text) * 72 / 1200
