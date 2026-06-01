import sys
from PyQt5.QtWidgets import QApplication
from WindowBisectie import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MWindow = MainWindow()
    MWindow.show()
    sys.exit(app.exec_())
