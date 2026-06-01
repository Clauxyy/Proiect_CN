from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer
from MetBis import Ui_MainWindow
import numpy as np
from sympy import sympify, symbols, lambdify, nsolve
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.fisier_text = None
        self.a = None
        self.b = None
        self.functie = None
        self.x_anim = None
        self.y_anim = None
        self.cadru_curent = 0
        self.timer = QTimer()
        self.timer.setInterval(20)
        self.timer.timeout.connect(self._pas_animatie)

        self.fig_erori = Figure(tight_layout=True)
        self.canvas_erori = FigureCanvas(self.fig_erori)
        self.canvas_erori.setMinimumSize(300, 250)
        self.ui.verticalLayout_2.addWidget(self.canvas_erori)

        self.fig_anim = Figure(tight_layout=True)
        self.canvas_anim = FigureCanvas(self.fig_anim)
        self.canvas_anim.setMinimumSize(300, 250)
        self.ui.verticalLayout_3.addWidget(self.canvas_anim)

        self.fig_functie = Figure(tight_layout=True)
        self.canvas_functie = FigureCanvas(self.fig_functie)
        self.canvas_functie.setMinimumSize(600, 220)
        self.ui.verticalLayout_4.addWidget(self.canvas_functie)

        self.ui.Itereaza.clicked.connect(self.ruleaza)
        self.ui.Incarca.clicked.connect(self.citeste_fisier)
        self.ui.RadioIteratii.toggled.connect(self.actualizeaza_campuri)
        self.ui.RadioZecimale.toggled.connect(self.actualizeaza_campuri)
        self.ui.SalveazaGrafic.clicked.connect(self.salveaza_erori)
        self.ui.functiegraficbtn.clicked.connect(self.salveaza_functie)
        self.ui.START.clicked.connect(self.start_animatie)
        self.ui.STOP.clicked.connect(self.stop_animatie)
        self.ui.SalveazaAnim.clicked.connect(self.salveaza_animatie)

        self.actualizeaza_campuri()

    def actualizeaza_campuri(self):
        e_iter = self.ui.RadioIteratii.isChecked()
        e_zec = self.ui.RadioZecimale.isChecked()
        self.ui.TolerantaText.setVisible(e_iter)
        self.ui.TolerantaCamp.setVisible(e_iter)
        self.ui.ZecimaleText.setVisible(e_zec)
        self.ui.ZecimaleCamp.setVisible(e_zec)

    def citeste_fisier(self):
        cale, _ = QFileDialog.getOpenFileName(self, "Alege fisier", "", "Text Files (*.txt);;All Files (*)")
        if cale:
            with open(cale, "r", encoding="utf-8") as f:
                self.fisier_text = f.read().strip()

    def ruleaza(self):
        text = self.ui.FunctieCamp.text().strip()
        sursa = text if text else (self.fisier_text or "")
        self.functie = transforma_functie(sursa)
        if self.functie is None:
            self.ui.label_rez.setText("Functie invalida sau lipsa!")
            return
        try:
            a_raw = float(sympify(self.ui.ACamp.text().strip()))
            b_raw = float(sympify(self.ui.BCamp.text().strip()))
            self.a, self.b = sorted([a_raw, b_raw])
            if a_raw > b_raw:
                self.ui.ACamp.setText(str(self.a))
                self.ui.BCamp.setText(str(self.b))
                self.avertisment_interval = True
            else:
                self.avertisment_interval = False
        except Exception:
            self.ui.label_rez.setText("Interval invalid!")
            return
        if not self.ui.RadioIteratii.isChecked() and not self.ui.RadioZecimale.isChecked():
            self.ui.label_rez.setText("Alege un tip de precizie!")
            return
        nr_iteratii_max = None
        text_nr = self.ui.NrIteratiiCamp.text().strip()
        if text_nr:
            try:
                nr_iteratii_max = int(text_nr)
            except Exception:
                self.ui.label_rez.setText("Nr. iteratii invalid!")
                return
        epsilon = None
        nr_zecimale = None
        if self.ui.RadioIteratii.isChecked():
            try:
                epsilon = float(self.ui.TolerantaCamp.text().strip())
            except Exception:
                self.ui.label_rez.setText("Epsilon invalid!")
                return
        elif self.ui.RadioZecimale.isChecked():
            try:
                nr_zecimale = int(self.ui.ZecimaleCamp.text().strip())
            except Exception:
                self.ui.label_rez.setText("Nr. zecimale invalid!")
                return
        rezultat, erori_abs, erori_rel, nr_iter_folosit = self.bisectie(self.functie, self.a, self.b, nr_iteratii_max, epsilon, nr_zecimale )
        if rezultat is None:
            self.ui.label_rez.setText("NU SE POATE aplica bisectia (f(a)*f(b) >= 0)!")
            return
        avert = " | a > b — interval corectat automat" if getattr(self, "avertisment_interval", False) else ""
        rad_exacta = self.radacina_exacta(rezultat)
        linie_exacta = f"  |  radacina exacta: {rad_exacta:.10f}  |  eroare fata de exacta: {abs(rezultat - rad_exacta):.2e}" if rad_exacta is not None else ""
        if nr_zecimale:
            precizie_atinsa = len(erori_abs) > 0 and erori_abs[-1] < 10 ** (-(nr_zecimale + 1))
            mesaj = (f"Solutie bisectie: {rezultat:.{nr_zecimale + 2}f}  |  "f"{nr_iter_folosit} iteratii  |  " f"{nr_zecimale} zecimale {' garantate' if precizie_atinsa else '— nr iteratii insuficient'}"f"{linie_exacta}{avert}")
        elif epsilon:
            precizie_atinsa = len(erori_abs) > 0 and erori_abs[-1] < epsilon
            mesaj = (f"Solutie bisectie: {rezultat:.10f}  |  " f"{nr_iter_folosit} iteratii  |  " f"eroare finala: {erori_abs[-1]:.2e} {' < ε' if precizie_atinsa else '— nr iteratii insuficient'}" f"{linie_exacta}{avert}")
        else:
            mesaj = f"Solutie bisectie: {rezultat:.10f}  |  {nr_iter_folosit} iteratii{linie_exacta}"
        self.ui.label_rez.setText(mesaj)
        self.deseneaza_erori(erori_abs, erori_rel, nr_iter_folosit)
        self.deseneaza_functie()
        self.pregateste_animatie()

    def bisectie(self, f, a, b, nr_iteratii_max, epsilon, nr_zecimale):
        try:
            fa, fb = float(f(a)), float(f(b))
        except Exception:
            return None, None, None, 0
        if fa * fb >= 0:
            return None, None, None, 0

        tol_oprire = None
        if nr_zecimale is not None:
            tol_oprire = 10 ** (-(nr_zecimale + 1))
        elif epsilon is not None:
            tol_oprire = epsilon

        limita = nr_iteratii_max if nr_iteratii_max else 10000
        iteratii, erori_abs, erori_rel = [], [], []
        c = a
        for i in range(1, limita + 1):
            c = (a + b) / 2.0
            iteratii.append(c)
            if i > 1:
                err = abs(iteratii[-1] - iteratii[-2])
                erori_abs.append(err)
                if c != 0:
                    erori_rel.append(err / abs(c))
            fc = float(f(c))
            if fc == 0:
                break
            if tol_oprire is not None and (b - a) / 2.0 < tol_oprire:
                break
            if float(f(a)) * fc < 0:
                b = c
            else:
                a = c
        return c, erori_abs, erori_rel, len(iteratii)


    def radacina_exacta(self, c):
        try:
            x = symbols('x')
            text = self.ui.FunctieCamp.text().strip()
            sursa = text if text else (self.fisier_text or "")
            expr = sympify(sursa.strip())
            rad = float(nsolve(expr, x, c))
            return rad
        except Exception:
            return None

    def deseneaza_erori(self, erori_abs, erori_rel, nr_iter=None):
        self.fig_erori.clear()
        tip = self.ui.comboBox.currentText()
        if tip == "Ambele":
            ax1 = self.fig_erori.add_subplot(211)
            ax2 = self.fig_erori.add_subplot(212)
            if erori_abs:
                ax1.semilogy(range(1, len(erori_abs) + 1), erori_abs, color="#2196F3", lw=1.8)
            ax1.set_title(f"Eroare absoluta  ({nr_iter} iteratii)" if nr_iter else "Eroare absoluta", fontsize=9)
            ax1.set_xlabel("Iteratie", fontsize=8)
            ax1.grid(True, alpha=0.3)
            if erori_rel:
                ax2.semilogy(range(1, len(erori_rel) + 1), erori_rel, color="#F44336", lw=1.8)
            ax2.set_title("Eroare relativa", fontsize=9)
            ax2.set_xlabel("Iteratie", fontsize=8)
            ax2.grid(True, alpha=0.3)
        else:
            ax = self.fig_erori.add_subplot(111)
            date = erori_abs if tip == "Absoluta" else erori_rel
            culoare = "#2196F3" if tip == "Absoluta" else "#F44336"
            if date:
                ax.semilogy(range(1, len(date) + 1), date, color=culoare, lw=1.8)
            ax.set_title(f"Eroare {tip.lower()}  ({nr_iter} iteratii)" if nr_iter else f"Eroare {tip.lower()}")
            ax.set_xlabel("Iteratie")
            ax.grid(True, alpha=0.3)
        self.fig_erori.tight_layout()
        self.canvas_erori.draw()

    def deseneaza_functie(self):
        x = np.linspace(self.a, self.b, 500)
        try:
            y = self.functie(x).astype(float)
        except Exception:
            return
        self.fig_functie.clear()
        ax = self.fig_functie.add_subplot(111)
        ax.plot(x, y, color="#2196F3", lw=2, label="f(x)")
        ax.axhline(0, color="black", lw=0.8, ls="--")
        if self.a <= 0 <= self.b:
            ax.axvline(0, color="black", lw=0.8, ls="--")
        ax.set_title("Grafic functie")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)
        self.fig_functie.tight_layout()
        self.canvas_functie.draw()

    def pregateste_animatie(self):
        self.x_anim = np.linspace(self.a, self.b, 200)
        try:
            self.y_anim = self.functie(self.x_anim).astype(float)
        except Exception:
            self.x_anim = None

    def start_animatie(self):
        if self.x_anim is None:
            self.ui.label_rez.setText("Ruleaza mai intai bisectia!")
            return
        self.stop_animatie()
        self.cadru_curent = 0

        y_fin = self.y_anim[np.isfinite(self.y_anim)]
        if len(y_fin) == 0:
            return
        margin = max((y_fin.max() - y_fin.min()) * 0.1, 0.1)

        self.fig_anim.clear()
        self.ax_anim = self.fig_anim.add_subplot(111)
        self.ax_anim.set_xlim(self.x_anim[0], self.x_anim[-1])
        self.ax_anim.set_ylim(y_fin.min() - margin, y_fin.max() + margin)
        self.ax_anim.axhline(0, color="black", lw=0.8, ls="--")
        self.ax_anim.set_title("Animatie functie")
        self.ax_anim.set_xlabel("x")
        self.ax_anim.set_ylabel("f(x)")
        self.ax_anim.grid(True, alpha=0.3)
        self.linie_anim, = self.ax_anim.plot([], [], color="#2196F3", lw=2)
        self.fig_anim.tight_layout()
        self.canvas_anim.draw()
        self.timer.start()

    def _pas_animatie(self):
        if self.cadru_curent >= len(self.x_anim):
            self.timer.stop()
            return
        self.linie_anim.set_data(
            self.x_anim[:self.cadru_curent + 1],
            self.y_anim[:self.cadru_curent + 1]
        )
        self.canvas_anim.draw_idle()
        self.cadru_curent += 1

    def stop_animatie(self):
        self.timer.stop()

    def salveaza_animatie(self):
        if self.x_anim is None:
            self.ui.label_rez.setText("Nu exista animatie de salvat!")
            return
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza animatie", "animatie.gif", "GIF (*.gif)")
        if not cale:
            return
        import matplotlib.animation as manim
        self.fig_anim.clear()
        ax = self.fig_anim.add_subplot(111)
        y_fin = self.y_anim[np.isfinite(self.y_anim)]
        margin = max((y_fin.max() - y_fin.min()) * 0.1, 0.1)
        ax.set_xlim(self.x_anim[0], self.x_anim[-1])
        ax.set_ylim(y_fin.min() - margin, y_fin.max() + margin)
        ax.axhline(0, color="black", lw=0.8, ls="--")
        ax.set_title("Animatie functie")
        ax.set_xlabel("x")
        ax.set_ylabel("f(x)")
        ax.grid(True, alpha=0.3)
        linie, = ax.plot([], [], color="#2196F3", lw=2)
        def update(i):
            linie.set_data(self.x_anim[:i + 1], self.y_anim[:i + 1])
            return (linie,)
        anim = manim.FuncAnimation(self.fig_anim, update, frames=len(self.x_anim), interval=20, blit=True)
        try:
            anim.save(cale, writer="pillow", dpi=100)
            self.ui.label_rez.setText("Animatie salvata!")
        except Exception as e:
            self.ui.label_rez.setText(f"Eroare: {e}")
        self.canvas_anim.draw()

    def salveaza_erori(self):
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza grafic erori", "grafic_erori.png", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if cale:
            self.fig_erori.savefig(cale, dpi=150, bbox_inches="tight")
            self.ui.label_rez.setText("Grafic erori salvat!")

    def salveaza_functie(self):
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza grafic functie", "grafic_functie.png", "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if cale:
            self.fig_functie.savefig(cale, dpi=150, bbox_inches="tight")
            self.ui.label_rez.setText("Grafic functie salvat!")


def transforma_functie(f_str):
    try:
        x = symbols('x')
        expr = sympify(f_str.strip())
        if expr.free_symbols - {x}:
            return None
        return lambdify(x, expr, 'numpy')
    except Exception:
        return None