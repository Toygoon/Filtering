from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *


class FilterWidget(QWidget):
    def __init__(self, main: QMainWindow = None, img=None):
        super(FilterWidget, self).__init__(main)
        self.main = main
        self.img = img

        self.initComponents()

    def initComponents(self):
        self.main.resize(700, 400)

        layout = QGridLayout()

        groupOriginal = QGroupBox("원본 이미지")
        originalBox = QVBoxLayout()
        originalBox.setAlignment(Qt.AlignCenter)
        label = QLabel(self)
        pix = QPixmap(self.img).scaledToWidth(300)
        label.setPixmap(pix)
        originalBox.addWidget(label)
        groupOriginal.setLayout(originalBox)

        groupFilters = QGroupBox("필터 선택")

        layout.addWidget(groupOriginal, 0, 0, 3, 1)
        layout.addWidget(groupFilters, 0, 1, 1, 1)

        self.setLayout(layout)