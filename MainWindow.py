import sys

import qdarktheme
from PyQt5.QtCore import QDir
from PyQt5.QtGui import QFontDatabase, QFont
from PyQt5.QtWidgets import *

from FilterWidget import FilterWidget


class MainWindow(QMainWindow):
    def __init__(self):
        # QMainWindow 호출
        super().__init__()

        self.layout = None
        self.widget = None
        self.img = None

        self.initComponents()

    def initComponents(self):
        # Window 이름 설정
        self.setWindowTitle('Filtering')

        # Window 크기 설정
        self.resize(500, 500)

        # Window가 중간에 위치하도록 설정
        frame = self.frameGeometry()
        center = QDesktopWidget().availableGeometry().center()
        frame.moveCenter(center)

        # MenuBar 생성
        self.initMenuBar()

        # StyleSheet 로드
        self.setStyleSheet(qdarktheme.load_stylesheet())

        # 파일 불러오기 부분
        self.imgLoadLayout()

        # 파일 드래그 설정
        self.setAcceptDrops(True)

        # Window 출력
        self.show()

    def initMenuBar(self):
        # MenuBar 생성
        menu = self.menuBar()
        menu.setNativeMenuBar(False)

        # MenuBar 요소 추가
        openAction = QAction('파일 열기', self)
        openAction.setShortcut('Ctrl+O')
        openAction.triggered.connect(self.fileLoad)

        exitAction = QAction('종료', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(qApp.quit)

        fileMenu = menu.addMenu('파일')
        fileMenu.addAction(openAction)
        fileMenu.addAction(exitAction)

    def imgLoadLayout(self):
        # 불러오기 버튼
        loadButton = QPushButton('클릭하여 불러오기\n\n\n혹은 이미지를 드래그')
        loadButton.clicked.connect(self.fileLoad)
        loadButton.setFlat(True)

        self.setCentralWidget(loadButton)

    def mainLayout(self):
        self.layout = QGridLayout()

        self.widget = QWidget()
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        loadButton = QPushButton('불러오기')
        loadButton.setFlat(True)

        self.layout.addWidget(loadButton, 0, 0)

    def fileLoad(self):
        # 파일 열기 기능
        file = QFileDialog.getOpenFileName(self, caption='파일 열기', directory=QDir.homePath(),
                                           filter='이미지 파일 (*.jpg *.gif *.png)')
        self.processFile(file[0])

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        # TODO : 이미지 파일만 골라내기
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for f in files:
            self.processFile(f)

    def processFile(self, img: str):
        if len(img) < 1:
            # 파일이 불러와지지 않은 경우
            print('User canceled importing images')
            return False

        self.setCentralWidget(FilterWidget(self, img))


if __name__ == '__main__':
    # Application 초기화
    app = QApplication(sys.argv)

    # 폰트 적용
    font = QFontDatabase()
    font.addApplicationFont('./fonts/NanumGothic.ttf')
    app.setFont(QFont('NanumGothic', 10))

    # Window 호출
    window = MainWindow()
    window.show()

    # 종료시 앱도 종료하도록 설정
    sys.exit(app.exec())
