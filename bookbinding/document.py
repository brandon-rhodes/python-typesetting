from PySide2.QtCore import QSizeF, Qt, QPoint, QMarginsF
from PySide2.QtGui import QPainter, QPdfWriter, QFontDatabase, QPen
from PySide2.QtWidgets import QApplication

#inch = 72
mm = 25.4 / 72

class Document(object):

    def __init__(self, page_width, page_height):
        self.page_width = page_width
        self.page_height = page_height

        QApplication(['my-q-application'])
        f = QFontDatabase.addApplicationFont('OldStandard-Regular.ttf')
        f = QFontDatabase.addApplicationFont('OldStandard-Italic.ttf')
        f = QFontDatabase.addApplicationFont('OldStandard-Bold.ttf')
        names = QFontDatabase.applicationFontFamilies(f)
        print(names)
        self.writer = QPdfWriter('book.pdf')
        self.writer.setPageSizeMM(QSizeF(page_width * mm, page_height * mm))
        self.writer.setPageMargins(QMarginsF(0, 0, 0, 0))
        self.painter = QPainter(self.writer)

def mark_chase(painter, chase):
    pt = 1200 / 72.0
    P = QPen(Qt.black, pt, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
    painter.setPen(P)

    x, y = chase.x * pt, chase.y * pt
    w = chase.width * pt
    h = chase.height * pt

    painter.drawPolyline([
        QPoint(x, y),
        QPoint(x + w, y),
        QPoint(x + w, y + h),
        QPoint(x, y + h),
        QPoint(x, y),
    ])
