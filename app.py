from PyQt6.QtWidgets import QApplication, QWidget, QMainWindow, QPushButton

import sys


class MainWindow(QMainWindow):
    def __init__(self):
        # QMainWindow 호출
        super().__init__()

        # Window 이름 설정
        self.setWindowTitle('Filtering')

        # 버튼 생성
        button = QPushButton('Button')
        # View에 버튼 추가
        self.setCentralWidget(button)


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
