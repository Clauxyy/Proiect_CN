from LogicBisectie import transforma_functie
from PyQt5.QtWidgets import QMainWindow,QApplication
from UI_Metoda_Bisectiei import Ui_MainWindow

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
       

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.Itereaza.clicked.connect(self.verificaf)
    def verificaf(self):
        text = self.ui.FunctieCamp.text()
        expr = transforma_functie(text)
        if expr is None:
            self.ui.label_rez.setText("Functie invalida!")
            self.ui.label_rez.setStyleSheet("color: red; font-size: 16px; font-weight: bold;")
        else:
            self.ui.label_rez.setText('')
            
            
            
            
            
            
            
            
            
            
app = QApplication([])
window = MainWindow()
window.show()
app.exec_()