import sys

from PyQt5.QtWidgets import QApplication, QMainWindow

from ui import MainWindow
from logic import SleepSessionManager

def main():
    app = QApplication(sys.argv)

    session_manager = SleepSessionManager()

    window = MainWindow(session_manager)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()