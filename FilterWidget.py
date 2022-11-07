from typing import Any

import numpy
import numpy as np
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
import os
import multiprocessing as mp
from multiprocessing import Pool
import threading

from ImageFilter import ImageFilter

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
        pix = QPixmap(self.img).scaledToWidth(SCALE_WIDTH)
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

        maskTable = QTableView()
        mask = filter.getMeanFilterMask(3)
        tableModel = TableModel(mask)
        tableModel.dataChanged.connect(self.refreshWeight)
        maskTable.setModel(tableModel)

        self.table = maskTable

        maskWeight = QLabel(f"가중치 합 : {np.sum(mask)}")
        self.weight = maskWeight
        maskTable.resizeColumnsToContents()

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
        resultData = filter.mean(3)
        resultPix = QPixmap.fromImage(resultData).scaledToWidth(SCALE_WIDTH)
        result.setPixmap(resultPix)
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
        cores = mp.cpu_count()

    def comboboxChanged(self):
        cb: QComboBox = self.cb
        filter: ImageFilter = self.filter
        table: QTableView = self.table

        table.setModel(TableModel(filter.getFilterTables(cb.currentText()), self.weight))

    def refreshWeight(self, topLeft, bottomRight):
        print(topLeft, bottomRight)


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
            return True

        return False

    def rowCount(self, index) -> int:  # noqa: N802
        return self.data.shape[0]

    def columnCount(self, index) -> int:  # noqa: N802
        return self.data.shape[1]

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        # flag = super().flags(index)
        # flag |= Qt.ItemFlag.ItemIsEditable
        # return flag  # type: ignore
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable