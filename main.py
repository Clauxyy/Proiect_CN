import sys
from PyQt5.QtWidgets import QApplication

from WindowSelectie import SelectionWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    selection = SelectionWindow()
    selection.show()
    sys.exit(app.exec_())
