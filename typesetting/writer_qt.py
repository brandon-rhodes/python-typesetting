import atexit
import os
from PySide2.QtCore import QSizeF, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase

MM = 25.4 / 72
PT = 1200 / 72

class QtWriter(object):

    def __init__(self, path, width_pt, height_pt):
        self.writer = QPdfWriter(path)
        self.writer.setPageSizeMM(QSizeF(width_pt * MM, height_pt * MM))
        self.writer.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.painter = QPainter(self.writer)
        atexit.register(self.close)

    def close(self):
        if self.painter.isActive():
            self.painter.end()

    def load_font(self, path):
        QFontDatabase.addApplicationFont(path)

    def get_fonts(self, font_specs):
        fonts = {}
        database = QFontDatabase()
        for key, family, style, size in font_specs:
            weight = database.weight(family, style)
            qt_font = database.font(family, style, size)
            actual_family = qt_font.family()
            if weight == -1 or family != actual_family:
                print('Cannot find font: {!r} {!r}'.format(family, style))
                os._exit(1)
            self.painter.setFont(qt_font)
            metrics = self.painter.fontMetrics()
            fonts[key] = QtFont(qt_font, metrics)
        return fonts

    def new_page(self):
        self.writer.newPage()
        # if self.include_crop_marks:
        #     self.draw_crop_marks()

    def set_font(self, font):
        self.painter.setFont(font.qt_font)

    def draw_text(self, x_pt, y_pt, text):
        self.painter.drawText(x_pt * PT, y_pt * PT, text)

class QtFont(object):
    def __init__(self, qt_font, metrics):
        self.qt_font = qt_font
        self._qt_metrics = metrics
        self.ascent = metrics.ascent() * 72 / 1200
        self.descent = metrics.descent() * 72 / 1200
        self.height = metrics.height() * 72 / 1200
        self.leading = metrics.lineSpacing() * 72 / 1200 - self.height

    def width_of(self, text):
        return self._qt_metrics.width(text) * 72 / 1200


# class Writer(object):

#     def __init__(self, page_width, page_height, crop_margin_width=0):
#         self.page_width = page_width
#         self.page_height = page_height
#         self.margin_width = crop_margin_width
#         return

#         self.include_crop_marks = bool(crop_margin_width)
#         if self.include_crop_marks:
#             self.draw_crop_marks()

#     def draw_crop_marks(self):
#         pt = 1200 / 72.0
#         m = self.margin_width * pt
#         offset = 9 * pt
#         weight = 0.25
#         painter = self.painter

#         if m < 9:
#             return
#         pen = QPen(Qt.black, weight, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
#         painter.setPen(pen)

#         w = self.page_width * pt
#         h = self.page_height * pt

#         for x in 0, w:
#             painter.drawLine(QPoint(x, -m), QPoint(x, -offset))
#             painter.drawLine(QPoint(x, h + m), QPoint(x, h + offset))
#         for y in 0, h:
#             painter.drawLine(QPoint(-m, y), QPoint(-offset, y))
#             painter.drawLine(QPoint(w + m, y), QPoint(w + offset, y))
