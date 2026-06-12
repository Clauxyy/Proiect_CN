from PyQt5.QtWidgets import QMainWindow, QFileDialog
from PyQt5.QtCore import QTimer
from MetCoarda import Ui_MainWindow
import numpy as np
from sympy import sympify, symbols, lambdify, nsolve
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class MainWindow(QMainWindow):
    def __init__(self, selection_window=None):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.selection_window = selection_window
        self.a = None
        self.b = None
        self.functie = None
        self.f_str = None
        self.x_aprox = []
        self.puncte_fix = []
        self.curent_index = 0
        self.timer = QTimer()
        self.timer.setInterval(500)
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
        self.ui.clearbtn.clicked.connect(self.sterge_functie)
        self.ui.RadioIteratii.toggled.connect(self.actualizeaza_campuri)
        self.ui.RadioZecimale.toggled.connect(self.actualizeaza_campuri)
        self.ui.SalveazaGrafic.clicked.connect(self.salveaza_erori)
        self.ui.functiegraficbtn.clicked.connect(self.salveaza_functie)
        self.ui.START.clicked.connect(self.start_animatie)
        self.ui.STOP.clicked.connect(self.stop_animatie)
        self.ui.SalveazaAnim.clicked.connect(self.salveaza_animatie)

        self.actualizeaza_campuri()

    def closeEvent(self, event):
        if self.selection_window is not None:
            self.selection_window.show()
        event.accept()

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
                continut = f.read().strip()
                self.ui.FunctieCamp.setText(continut)

    def sterge_functie(self):
        """Buton de clear pentru câmpul funcţiei"""
        self.ui.FunctieCamp.clear()
        self.ui.ACamp.clear()
        self.ui.BCamp.clear()
        self.ui.NrIteratiiCamp.clear()
        self.ui.ZecimaleCamp.clear()
        self.ui.TolerantaCamp.clear()

    def ruleaza(self):
        text = self.ui.FunctieCamp.text().strip()
        sursa = text
        self.functie = transforma_functie(sursa)
        self.f_str = sursa
        if self.functie is None:
            self.ui.label_rez.setText("Functie invalida sau lipsa!")
            return

        try:
            a_raw = float(sympify(self.ui.ACamp.text().strip()))
            b_raw = float(sympify(self.ui.BCamp.text().strip()))
        except Exception:
            self.ui.label_rez.setText("Interval invalid!")
            return

        if a_raw > b_raw:
            self.ui.label_rez.setText("Eroare: a trebuie să fie mai mic decât b!")
            return

        self.a, self.b = a_raw, b_raw

        if not self.ui.RadioIteratii.isChecked() and not self.ui.RadioZecimale.isChecked():
            self.ui.label_rez.setText("Alege un tip de precizie!")
            return

        nr_iteratii_max = None
        text_nr = self.ui.NrIteratiiCamp.text().strip()
        if text_nr:
            try:
                if int(text_nr) <= 0:
                    raise Exception
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

        try:
            rezultat, erori_abs, erori_rel, nr_iter, aproximari, puncte_fix = self.coarda(
                self.functie, self.a, self.b, nr_iteratii_max, epsilon, nr_zecimale
            )
        except Exception as e:
            self.ui.label_rez.setText(f"Eroare în metoda coardei: {str(e)}")
            return

        if rezultat is None:
            self.ui.label_rez.setText("NU SE POATE aplica metoda coardei (f(a)*f(b) >= 0)!")
            return

        self.x_aprox = aproximari
        self.puncte_fix = puncte_fix

        rad_exacta = self.radacina_exacta(rezultat)
        linie_exacta = f"  |  radacina exacta: {rad_exacta:.10f}  |  eroare fata de exacta: {abs(rezultat - rad_exacta):.2e}" if rad_exacta is not None else ""

        if nr_zecimale:
            precizie_atinsa = len(erori_abs) > 0 and erori_abs[-1] < 10 ** (-(nr_zecimale + 1))
            mesaj = (f"Solutie coarda: {rezultat:.{nr_zecimale + 2}f}  |  "
                     f"{nr_iter} iteratii  |  {nr_zecimale} zecimale "
                     f"{'garantate' if precizie_atinsa else '— nr iteratii insuficient'}"
                     f"{linie_exacta}")
        elif epsilon:
            precizie_atinsa = len(erori_abs) > 0 and erori_abs[-1] < epsilon
            mesaj = (f"Solutie coarda: {rezultat:.10f}  |  "
                     f"{nr_iter} iteratii  |  eroare finala: {erori_abs[-1]:.2e} "
                     f"{'< ε' if precizie_atinsa else '— nr iteratii insuficient'}"
                     f"{linie_exacta}")
        else:
            mesaj = f"Solutie coarda: {rezultat:.10f}  |  {nr_iter} iteratii{linie_exacta}"

        self.ui.label_rez.setText(mesaj)
        self.deseneaza_erori(erori_abs, erori_rel, nr_iter)
        self.deseneaza_functie()

    def coarda(self, f, a, b, nr_iter_max, epsilon, nr_zecimale):
        """
        Metoda coardei cu punct fix = b, pornind din a.
        Formula: x_{n+1} = x_n - f(x_n)*(x_n - b)/(f(x_n)-f(b))
        """
        try:
            fa = float(f(a))
            fb = float(f(b))
        except Exception:
            return None, None, None, 0, [], []

        if fa * fb >= 0:
            return None, None, None, 0, [], []

        tol_oprire = None
        if nr_zecimale is not None:
            tol_oprire = 10 ** (-(nr_zecimale + 1))
        elif epsilon is not None:
            tol_oprire = epsilon

        limita = nr_iter_max if nr_iter_max else 10000

        fix = b
        f_fix = fb
        x_curr = a
        aproximari = [x_curr]
        puncte_fix = [fix] * (limita + 1)
        erori_abs = []
        erori_rel = []

        for i in range(1, limita + 1):
            fx = f(x_curr)
            if abs(fx - f_fix) < 1e-15:
                break
            x_next = x_curr - fx * (x_curr - fix) / (fx - f_fix)
            aproximari.append(x_next)
            puncte_fix[i] = fix

            err_abs = abs(x_next - x_curr)
            erori_abs.append(err_abs)
            if abs(x_next) > 1e-12:
                erori_rel.append(err_abs / abs(x_next))
            else:
                erori_rel.append(err_abs)

            if tol_oprire is not None and err_abs < tol_oprire:
                break
            if abs(f(x_next)) < 1e-15:
                break

            x_curr = x_next

        puncte_fix = puncte_fix[:len(aproximari)]
        nr_iter = len(aproximari) - 1
        c = aproximari[-1]
        return c, erori_abs, erori_rel, nr_iter, aproximari, puncte_fix

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
        if self.a is None or self.b is None or self.functie is None:
            return
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

    def start_animatie(self):
        if not self.x_aprox or len(self.x_aprox) < 2 or not self.puncte_fix:
            self.ui.label_rez.setText("Ruleaza mai intai metoda coardei!")
            return
        self.stop_animatie()
        self.curent_index = 0

        self.fig_anim.clear()
        self.ax_anim = self.fig_anim.add_subplot(111)

        x_vals = np.linspace(self.a, self.b, 500)
        y_vals = self.functie(x_vals)
        self.ax_anim.plot(x_vals, y_vals, 'b-', linewidth=2, label='f(x)')
        self.ax_anim.axhline(0, color='k', linestyle='--', linewidth=0.8)
        self.ax_anim.axvline(0, color='k', linestyle='--', linewidth=0.8)
        self.ax_anim.set_xlim(self.a, self.b)
        ymin = min(y_vals.min(), 0) - 0.2 * abs(y_vals.min())
        ymax = max(y_vals.max(), 0) + 0.2 * abs(y_vals.max())
        self.ax_anim.set_ylim(ymin, ymax)
        self.ax_anim.set_title("Metoda Coardei - Animație (punct fix b)")
        self.ax_anim.set_xlabel("x")
        self.ax_anim.set_ylabel("f(x)")
        self.ax_anim.grid(True, alpha=0.3)
        self.ax_anim.legend()

        self.punct_curent, = self.ax_anim.plot([], [], 'ro', markersize=8, label='x_n')
        self.coarda_line, = self.ax_anim.plot([], [], 'g--', linewidth=1.5, label='coarda')
        self.text_annot = self.ax_anim.annotate('', xy=(0, 0), xytext=(10, 10),
                                                textcoords='offset points',
                                                fontsize=10, color='red')

        self.fig_anim.tight_layout()
        self.canvas_anim.draw()
        self.timer.start()

    def _pas_animatie(self):
        if self.curent_index >= len(self.x_aprox):
            self.timer.stop()
            sol = self.x_aprox[-1]
            self.text_annot.set_text(f"Soluție: {sol:.6f}")
            self.canvas_anim.draw_idle()
            return

        x_n = self.x_aprox[self.curent_index]
        f_n = self.functie(x_n)
        fix = self.puncte_fix[self.curent_index]
        f_fix = self.functie(fix)

        self.punct_curent.set_data([x_n], [f_n])
        self.coarda_line.set_data([x_n, fix], [f_n, f_fix])
        self.text_annot.set_text(f"n={self.curent_index}, x={x_n:.6f}, fix=b={fix:.3f}")
        self.text_annot.set_position((x_n, f_n))

        self.canvas_anim.draw_idle()
        self.curent_index += 1

    def stop_animatie(self):
        self.timer.stop()

    def salveaza_animatie(self):
        if not self.x_aprox or not self.puncte_fix:
            self.ui.label_rez.setText("Nu exista animatie de salvat!")
            return
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza animatie", "animatie_coarda.gif", "GIF (*.gif)")
        if not cale:
            return
        import matplotlib.animation as manim
        fig_anim_save = Figure(tight_layout=True)
        ax_save = fig_anim_save.add_subplot(111)
        x_vals = np.linspace(self.a, self.b, 500)
        y_vals = self.functie(x_vals)
        ax_save.plot(x_vals, y_vals, 'b-', linewidth=2)
        ax_save.axhline(0, color='k', linestyle='--')
        ax_save.axvline(0, color='k', linestyle='--')
        ax_save.set_xlim(self.a, self.b)
        ymin = min(y_vals.min(), 0) - 0.2 * abs(y_vals.min())
        ymax = max(y_vals.max(), 0) + 0.2 * abs(y_vals.max())
        ax_save.set_ylim(ymin, ymax)
        ax_save.grid(True, alpha=0.3)
        punct, = ax_save.plot([], [], 'ro', markersize=8)
        coarda_line, = ax_save.plot([], [], 'g--', linewidth=1.5)
        text_anim = ax_save.annotate('', xy=(0, 0), xytext=(10, 10), textcoords='offset points')

        def update(frame):
            x_n = self.x_aprox[frame]
            f_n = self.functie(x_n)
            fix = self.puncte_fix[frame]
            punct.set_data([x_n], [f_n])
            coarda_line.set_data([x_n, fix], [f_n, self.functie(fix)])
            text_anim.set_text(f"n={frame}, x={x_n:.6f}, fix=b={fix:.3f}")
            text_anim.set_position((x_n, f_n))
            return punct, coarda_line, text_anim

        anim = manim.FuncAnimation(fig_anim_save, update, frames=len(self.x_aprox), interval=500, blit=False)
        try:
            anim.save(cale, writer="pillow", dpi=100)
            self.ui.label_rez.setText("Animatie salvata!")
        except Exception as e:
            self.ui.label_rez.setText(f"Eroare: {e}")
        finally:
            import matplotlib.pyplot as plt
            plt.close(fig_anim_save)

    def salveaza_erori(self):
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza grafic erori", "grafic_erori.png",
                                              "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
        if cale:
            self.fig_erori.savefig(cale, dpi=150, bbox_inches="tight")
            self.ui.label_rez.setText("Grafic erori salvat!")

    def salveaza_functie(self):
        cale, _ = QFileDialog.getSaveFileName(self, "Salveaza grafic functie", "grafic_functie.png",
                                              "PNG (*.png);;PDF (*.pdf);;SVG (*.svg)")
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