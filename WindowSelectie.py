from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from PyQt5.QtCore import Qt

from WindowBisectie import MainWindow as BisectieWindow
from WindowCoarda import MainWindow as CoardaWindow

class SelectionWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Metode Numerice - Alegere Metodă")
        self.setFixedSize(400, 300)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        title = QLabel("Alege metoda numerică:")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        btn_bisectie = QPushButton("Metoda Bisectiei")
        btn_bisectie.setFixedSize(250, 50)
        btn_bisectie.setStyleSheet("font-size: 14px;")
        btn_bisectie.clicked.connect(self.start_bisectie)
        layout.addWidget(btn_bisectie, alignment=Qt.AlignCenter)

        btn_coarda = QPushButton("Metoda Coardei")
        btn_coarda.setFixedSize(250, 50)
        btn_coarda.setStyleSheet("font-size: 14px;")
        btn_coarda.clicked.connect(self.start_coarda)
        layout.addWidget(btn_coarda, alignment=Qt.AlignCenter)

        btn_exit = QPushButton("Ieșire")
        btn_exit.setFixedSize(150, 40)
        btn_exit.clicked.connect(self.close)
        layout.addWidget(btn_exit, alignment=Qt.AlignCenter)

    def start_bisectie(self):
        self.hide()
        self.bisectie_window = BisectieWindow(selection_window=self)
        self.bisectie_window.show()

    def start_coarda(self):
        self.hide()
        self.coarda_window = CoardaWindow(selection_window=self)
        self.coarda_window.show()
