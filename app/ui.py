from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.windowTitle("Hypnos")
        self.setGeometry(100, 100, 800, 600)
        self.move(QApplication.desktop().screen().rect().center() - self.rect().center())
        self.setWindowIcon(QIcon("../assets/Hypnos-icon.png"))

