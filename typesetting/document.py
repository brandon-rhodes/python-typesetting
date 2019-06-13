from PySide2.QtCore import QSizeF, Qt, QPoint, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase, QPen
from PySide2.QtWidgets import QApplication

#inch = 72
mm = 25.4 / 72

class Document(object):

    def __init__(self, page_width, page_height, crop_margin_width=0):
        self.page_width = page_width
        self.page_height = page_height
        self.margin_width = crop_margin_width
        self.include_crop_marks = bool(crop_margin_width)

        QApplication(['my-q-application'])
        f = QFontDatabase.addApplicationFont('OldStandard-Regular.ttf')
        f = QFontDatabase.addApplicationFont('OldStandard-Italic.ttf')
        f = QFontDatabase.addApplicationFont('OldStandard-Bold.ttf')
        f = QFontDatabase.addApplicationFont('fonts/Inconsolata-Regular.ttf')
        f = QFontDatabase.addApplicationFont('fonts/UbuntuMono-R.ttf')
        f = QFontDatabase.addApplicationFont('../../fonts/GenBasB.ttf')
        f = QFontDatabase.addApplicationFont('../../fonts/GenBasR.ttf')
        #f = QFontDatabase.addApplicationFont('../../fonts/Inconsolata-Regular.ttf')
        print(f)
        names = QFontDatabase.applicationFontFamilies(f)
        print(names)
        self.writer = QPdfWriter('book.pdf')
        size = QSizeF((2 * crop_margin_width + page_width) * mm,
                      (2 * crop_margin_width + page_height) * mm)
        self.writer.setPageSizeMM(size)
        margins = QMarginsF(crop_margin_width, crop_margin_width,
                            crop_margin_width, crop_margin_width)
        self.writer.setPageMargins(margins)
        self.painter = QPainter(self.writer)
        if self.include_crop_marks:
            self.draw_crop_marks()

    def new_page(self):
        self.writer.newPage()
        if self.include_crop_marks:
            self.draw_crop_marks()

    def draw_crop_marks(self):
        pt = 1200 / 72.0
        m = self.margin_width * pt
        offset = 9 * pt
        weight = 0.25
        painter = self.painter

        if m < 9:
            return
        pen = QPen(Qt.black, weight, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)

        w = self.page_width * pt
        h = self.page_height * pt

        for x in 0, w:
            painter.drawLine(QPoint(x, -m), QPoint(x, -offset))
            painter.drawLine(QPoint(x, h + m), QPoint(x, h + offset))
        for y in 0, h:
            painter.drawLine(QPoint(-m, y), QPoint(-offset, y))
            painter.drawLine(QPoint(w + m, y), QPoint(w + offset, y))
