from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase, QPen


def get_fonts(doc, font_specs):
    #d = Document(PAGE_WIDTH, PAGE_HEIGHT)
    fonts = {}
    for key, name, roi, size in font_specs:
        font = QFontDatabase().font(name, roi, size)
        doc.painter.setFont(font)
        metrics = doc.painter.fontMetrics()
        fonts[key] = Font(metrics)
    return fonts

class Font(object):
    def __init__(self, metrics):
        self.metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200
        self.height = metrics.height() * 72 / 1200
        self.leading = metrics.lineSpacing() * 72 / 1200 - self.height

    def width_of(self, text):
        return 3
