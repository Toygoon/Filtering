import cv2
import numpy
import numpy as np
import qimage2ndarray
from PIL import ImageQt
from PyQt5.QtCore import Qt, QAbstractTableModel, QModelIndex, QRunnable, QThreadPool, QDir
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from numpy.random.mtrand import randint

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

        self.imgArray = None
        self.filter: ImageFilter = None
        self.cb: QComboBox = None
        self.weight: QLabel = None
        self.table: QTableView = None
        self.before: QLabel = None
        self.result: QLabel = None

        self.initComponents()
        self.initMenuBar()

    def initMenuBar(self):
        self.main.menuBar().clear()
        menu = self.main.menuBar()
        menu.setNativeMenuBar(False)

        # MenuBar 요소 추가
        openAction = QAction('파일 열기', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.main.fileLoad)

        saveAction = QAction('파일 열기', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.triggered.connect(self.saveImg)

        exitAction = QAction('종료', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        fileMenu = menu.addMenu('파일')
        fileMenu.addAction(openAction)
        fileMenu.addAction(saveAction)
        fileMenu.addAction(exitAction)

        # Tools
        noiseAction = QAction('노이즈 생성', self)
        noiseAction.triggered.connect(self.saltPepper)
        toolMenu = menu.addMenu('도구')
        toolMenu.addAction(noiseAction)

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
            qimage2ndarray.array2qimage(filter.img, normalize=False)).scaledToWidth(
            SCALE_WIDTH)
        label.setPixmap(pix)
        self.before = label
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
        saveButton = QPushButton("파일 저장")
        saveButton.clicked.connect(self.saveImg)
        buttonBox.addWidget(saveButton)
        buttonWidget.setLayout(buttonBox)

        layout.addWidget(groupOriginal, 0, 0, 3, 1)
        layout.addWidget(groupFilters, 0, 1, 1, 1)
        layout.addWidget(groupMask, 1, 1, 2, 1)
        layout.addWidget(groupResult, 0, 2, 3, 1)
        layout.addWidget(buttonWidget, 3, 2, 1, 1)

        self.setLayout(layout)

    def saltPepper(self):
        # TODO : 이미지를 필터에도 적용
        noise = cv2.imread(self.img, cv2.IMREAD_GRAYSCALE)
        H, W = noise.shape
        salt = int(H * W * 0.1)
        for i in range(salt):
            row = int(randint(99999, size=1) % H)
            col = int(randint(9999, size=1) % W)
            noise[row][col] = 255 if randint(99999, size=1) % 2 == 1 else 0

        self.before.setPixmap(QPixmap(qimage2ndarray.array2qimage(noise).scaledToWidth(SCALE_WIDTH)))

    def applyFilter(self):
        pool = QThreadPool.globalInstance()

        loading = LoadingThread(loading_screen=LoadingScreen(parent=self, description_text="", dot_animation=True))
        runnable = Runnable(self, loading)
        pool.start(runnable)

    def saveImg(self):
        img = ImageQt.fromqpixmap(self.result.pixmap())
        file, _ = QFileDialog.getSaveFileName(parent=self, caption='이미지 파일 저장', directory=QDir.homePath(),
                                              filter='이미지 파일 (*.png)')

        if len(file) < 1:
            print('User canceled saving images')
            return False

        img.save(file)

    def comboboxChanged(self):
        cb: QComboBox = self.cb
        filter: ImageFilter = self.filter
        table: QTableView = self.table

        text = cb.currentText()
        mask = None

        if text.lower() == 'custom':
            custom, ok = QInputDialog.getText(self, '크기 입력', '입력 (3*3이면 3 입력) : ')
            try:
                custom = int(custom)
            except ValueError:
                return False

            if ok is False:
                return False

            mask = np.ones((custom, custom))

        else:
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
        # self.filter.img = self.widget.before.pixmap()

        self.loading.start()

        if self.text == 'Median Filter':
            data = self.filter.median()
        else:
            self.filter.mask = self.mask
            data = self.filter.convolution()

        self.result.setPixmap(QPixmap.fromImage(data).scaledToWidth(SCALE_WIDTH))

        self.loading.stop()
