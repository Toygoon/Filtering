from typing import Any

import numpy
import qimage2ndarray
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *

from ImageFilter import ImageFilter

SCALE_WIDTH: int = 300
WIN_HEIGHT: int = 1000
WIN_WIDTH: int = 400

class FilterWidget(QWidget):
    def __init__(self, main: QMainWindow = None, img=None):
        super(FilterWidget, self).__init__(main)
        self.main = main
        self.img = img

        self.initComponents()

    def initComponents(self):
        self.main.resize(WIN_HEIGHT, WIN_WIDTH)

        layout = QGridLayout()
        filter = ImageFilter(self.img)

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
        filterCombobox.addItems(set(filter.getFilterNames().values()))
        filterBox.addWidget(filterCombobox)
        groupFilters.setLayout(filterBox)

        groupMask = QGroupBox("마스크")
        maskBox = QVBoxLayout()
        maskBox.setAlignment(Qt.AlignCenter)
        maskTable = QTableView()
        maskTable.setModel(TableModel(filter.getMeanFilterMask(3)))
        # maskTable.setFixedSize(maskTable.horizontalHeader().length() + maskTable.verticalHeader().width(),
        #                        maskTable.verticalHeader().length() + maskTable.horizontalHeader().height())
        maskTable.resizeColumnsToContents()
        maskBox.addWidget(maskTable)
        groupMask.setLayout(maskBox)

        groupResult = QGroupBox("적용 결과")
        resultBox = QVBoxLayout()
        resultBox.setAlignment(Qt.AlignCenter)
        result = QLabel(self)
        resultData = filter.mean(3)
        resultPix = QPixmap.fromImage(qimage2ndarray.array2qimage(resultData, normalize=False)).scaledToWidth(SCALE_WIDTH)
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


class TableModel(QAbstractTableModel):
    def __init__(self, data: numpy.ndarray) -> None:
        super().__init__()
        self.data = data.tolist()

    def data(self, index: QModelIndex, role: int) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            return self.data[index.row()][index.column()]
        if role == Qt.ItemDataRole.EditRole:
            return self.data[index.row()][index.column()]  # pragma: no cover
        return None

    def rowCount(self, index) -> int:  # noqa: N802
        return len(self.data)

    def columnCount(self, index) -> int:  # noqa: N802
        return len(self.data[0])

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flag = super().flags(index)
        flag |= Qt.ItemFlag.ItemIsEditable
        return flag  # type: ignore
