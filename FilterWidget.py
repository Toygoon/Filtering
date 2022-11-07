from typing import Any

import cv2
import numpy
import numpy as np
import qimage2ndarray
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QThread, QRunnable, QThreadPool
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from ImageFilter import ImageFilter
from LoadingScreen import LoadingScreen, LoadingThread

SCALE_WIDTH: int = 300
WIN_HEIGHT: int = 1000
WIN_WIDTH: int = 400


class FilterWidget(QWidget):
    def __init__(self, main=None, img=None):
        super(FilterWidget, self).__init__(main)
        self.main: QMainWindow = main
        self.img: str = img

        self.filter: ImageFilter = None
        self.cb: QComboBox = None
        self.weight: QLabel = None
        self.table: QTableView = None
        self.result: QLabel = None

        self.initComponents()

    def initComponents(self):
        self.main.resize(WIN_HEIGHT, WIN_WIDTH)

        layout = QGridLayout()
        filter = ImageFilter(self.img)
        self.filter = filter

        groupOriginal = QGroupBox("원본 이미지")
        originalBox = QVBoxLayout()
        originalBox.setAlignment(Qt.AlignCenter)
        label = QLabel(self)
        pix = QPixmap(
            qimage2ndarray.array2qimage(cv2.imread(self.img, cv2.IMREAD_GRAYSCALE), normalize=False)).scaledToWidth(
            SCALE_WIDTH)
        label.setPixmap(pix)
        originalBox.addWidget(label)
        groupOriginal.setLayout(originalBox)

        groupFilters = QGroupBox("필터 선택")
        filterBox = QVBoxLayout()
        filterBox.setAlignment(Qt.AlignCenter)
        filterCombobox = QComboBox()
        filterCombobox.addItems(filter.getFilterNames().values())
        filterCombobox.currentIndexChanged.connect(self.comboboxChanged)
        self.cb = filterCombobox
        filterBox.addWidget(filterCombobox)
        groupFilters.setLayout(filterBox)

        groupMask = QGroupBox("마스크")

        maskBox = QVBoxLayout()
        maskBox.setAlignment(Qt.AlignCenter)

        mask = filter.getMeanFilterMask(3)
        maskWeight = QLabel(f"가중치 합 : {np.sum(mask)}")
        self.weight = maskWeight

        maskTable = QTableView()
        tableModel = TableModel(mask, self.weight)
        maskTable.setModel(tableModel)
        maskTable.resizeColumnsToContents()

        self.table = maskTable

        applyButton = QPushButton('필터 적용')
        applyButton.clicked.connect(self.applyFilter)

        maskBox.addWidget(maskTable)
        maskBox.addWidget(maskWeight)
        maskBox.addWidget(applyButton)
        groupMask.setLayout(maskBox)

        groupResult = QGroupBox("적용 결과")
        resultBox = QVBoxLayout()
        resultBox.setAlignment(Qt.AlignCenter)
        result = QLabel(self)
        self.result = result
        result.setPixmap(pix)
        resultBox.addWidget(result)
        groupResult.setLayout(resultBox)

        buttonWidget = QWidget()
        buttonBox = QHBoxLayout()
        buttonBox.setAlignment(Qt.AlignRight)
        backButton = QPushButton("돌아가기")
        saveButton = QPushButton("저장")
        buttonBox.addWidget(backButton)
        buttonBox.addWidget(saveButton)
        buttonWidget.setLayout(buttonBox)

        layout.addWidget(groupOriginal, 0, 0, 3, 1)
        layout.addWidget(groupFilters, 0, 1, 1, 1)
        layout.addWidget(groupMask, 1, 1, 2, 1)
        layout.addWidget(groupResult, 0, 2, 3, 1)
        layout.addWidget(buttonWidget, 3, 2, 1, 1)

        self.setLayout(layout)

    def applyFilter(self):
        pool = QThreadPool.globalInstance()
        loading = LoadingThread(loading_screen=LoadingScreen(parent=self, description_text="", dot_animation=True))
        runnable = Runnable(self, loading)
        pool.start(runnable)

    def comboboxChanged(self):
        cb: QComboBox = self.cb
        filter: ImageFilter = self.filter
        table: QTableView = self.table

        text = cb.currentText()

        mask = filter.getFilterTables(text)
        table.setModel(TableModel(mask, self.weight))
        self.weight.setText("가중치 합 : {:.2f}".format(float(np.sum(mask))))
        table.resizeColumnsToContents()

        if text == 'Median Filter':
            table.setEnabled(False)
            self.weight.setText(f"가중치 합 : X")
        else:
            table.setEnabled(True)


class TableModel(QAbstractTableModel):
    def __init__(self, data: numpy.ndarray, weight: QLabel) -> None:
        super().__init__()
        self.data = data
        self.weight = weight

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole or role == Qt.EditRole:
                value = self.data[index.row(), index.column()]
                return str("{:.3f}".format(value))

    def setData(self, index, value, role):
        if role == Qt.EditRole:
            try:
                value = float(value)
            except ValueError:
                return False
            self.data[index.row(), index.column()] = value
            self.weight.setText("가중치 합 : {:.2f}".format(np.sum(self.data)))
            return True

        return False

    def rowCount(self, index) -> int:  # noqa: N802
        return self.data.shape[0]

    def columnCount(self, index) -> int:  # noqa: N802
        return self.data.shape[1]

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable


class Runnable(QRunnable):
    def __init__(self, widget, loading):
        super().__init__()
        self.widget: FilterWidget = widget
        self.filter: ImageFilter = widget.filter
        self.text: str = widget.cb.currentText()
        self.mask: numpy.ndarray = widget.table.model().data
        self.result: QLabel = widget.result
        self.loading: LoadingThread = loading

    def run(self):
        data = None

        self.loading.start()

        if self.text == 'Median Filter':
            data = self.filter.median()
        else:
            self.filter.mask = self.mask
            data = self.filter.convolution()

        self.result.setPixmap(QPixmap.fromImage(data).scaledToWidth(SCALE_WIDTH))

        self.loading.stop()
