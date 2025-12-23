import sys, math, ast, requests, xml.etree.ElementTree as ET
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QComboBox, QStackedLayout, QTabWidget
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

# ================= THEMES =================
THEMES = {
    "dark": {"bg":"#0f172a","disp":"#020617","btn":"#1e293b","hover":"#334155","eq":"#22c55e","txt":"#f8fafc"},
    "light":{"bg":"#e5e7eb","disp":"#ffffff","btn":"#e5e7eb","hover":"#d1d5db","eq":"#16a34a","txt":"#020617"}
}

# ================= TCMB =================
def get_rates():
    try:
        root = ET.fromstring(
            requests.get("https://www.tcmb.gov.tr/kurlar/today.xml", timeout=5).content
        )
        r = {"TRY": 1.0}
        for c in root.findall("Currency"):
            v = c.findtext("ForexSelling")
            if v:
                r[c.attrib["CurrencyCode"]] = float(v.replace(",", "."))
        return r
    except:
        return {"TRY": 1.0}

# ================= UNITS =================
MASS = {"kg":1,"g":0.001,"mg":1e-6,"ton":1000,"lb":0.453592,"oz":0.0283495}
LENGTH = {"m":1,"cm":0.01,"mm":0.001,"km":1000,"inch":0.0254,"ft":0.3048,"mile":1609.34}
FORCE = {"N":1,"kgf":9.80665,"lbf":4.44822}
TIME = {"s":1,"min":60,"h":3600,"day":86400}

def convert_linear(v, f, t, table):
    return v * table[f] / table[t]

def convert_temp(v, f, t):
    if f == t: return v
    if f=="C" and t=="F": return v*9/5+32
    if f=="F" and t=="C": return (v-32)*5/9
    if f=="C" and t=="K": return v+273.15
    if f=="K" and t=="C": return v-273.15
    if f=="F" and t=="K": return (v-32)*5/9+273.15
    if f=="K" and t=="F": return (v-273.15)*9/5+32

# ================= SAFE EVAL =================
SAFE = {
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "sqrt": math.sqrt,
    "pi": math.pi
}

ALLOWED = (
    ast.Expression, ast.BinOp, ast.UnaryOp,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Pow,
    ast.USub, ast.Constant, ast.Call, ast.Name
)

def safe_eval(expr):
    tree = ast.parse(expr, mode="eval")
    for n in ast.walk(tree):
        if not isinstance(n, ALLOWED):
            raise ValueError
    return eval(compile(tree, "<safe>", "eval"), {"__builtins__": None}, SAFE)

# ================= MAIN =================
class App(QWidget):
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.scientific_visible = False
        self.rates = get_rates()
        self.drag_pos = None
        self.init_ui()
        self.apply_theme()
        self.animate()

    # ===== WINDOW DRAG =====
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.drag_pos:
            self.move(self.pos() + event.globalPosition().toPoint() - self.drag_pos)
            self.drag_pos = event.globalPosition().toPoint()

    # ===== UI =====
    def init_ui(self):
        self.setFixedSize(380, 760)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.stack = QStackedLayout(self)

        # ===== CALCULATOR =====
        calc = QWidget()
        v = QVBoxLayout(calc)

        top = QHBoxLayout()
        for txt, cb in [
            ("🧪", self.toggle_scientific),
            ("💱", lambda: self.stack.setCurrentIndex(1)),
            ("📏", lambda: self.stack.setCurrentIndex(2)),
            ("🌙", self.toggle_theme),
            ("✕", self.close)
        ]:
            b = QPushButton(txt)
            b.clicked.connect(cb)
            top.addWidget(b)
        v.addLayout(top)

        self.display = QLineEdit("0")
        self.display.setFont(QFont("Segoe UI", 26))
        self.display.setAlignment(Qt.AlignRight)
        v.addWidget(self.display)

        # --- Scientific ---
        self.sci_widget = QWidget()
        sg = QGridLayout(self.sci_widget)
        for t,r,c in [
            ("sin(",0,0),("cos(",0,1),("tan(",0,2),
            ("sqrt(",1,0),("pi",1,1),("^",1,2)
        ]:
            b = QPushButton(t)
            b.clicked.connect(lambda _,x=t:self.add_text("**" if x=="^" else x))
            sg.addWidget(b,r,c)
        self.sci_widget.hide()
        v.addWidget(self.sci_widget)

        # --- Main keypad ---
        g = QGridLayout()
        for t,r,c in [
            ("7",0,0),("8",0,1),("9",0,2),("/",0,3),
            ("4",1,0),("5",1,1),("6",1,2),("*",1,3),
            ("1",2,0),("2",2,1),("3",2,2),("-",2,3),
            ("0",3,0),(".",3,1),("C",3,2),("+",3,3)
        ]:
            b = QPushButton(t)
            b.clicked.connect(lambda _,x=t:self.press(x))
            g.addWidget(b,r,c)

        self.eq = QPushButton("=")
        self.eq.clicked.connect(self.calculate)
        g.addWidget(self.eq,4,0,1,4)
        v.addLayout(g)

        # ===== FX =====
        fx = QWidget()
        fv = QVBoxLayout(fx)
        fv.addWidget(QPushButton("← Geri", clicked=lambda:self.stack.setCurrentIndex(0)))
        self.amount = QLineEdit()
        fv.addWidget(self.amount)
        self.fc = QComboBox()
        self.tc = QComboBox()
        for c in self.rates:
            self.fc.addItem(c)
            self.tc.addItem(c)
        row = QHBoxLayout()
        row.addWidget(self.fc); row.addWidget(QLabel("→")); row.addWidget(self.tc)
        fv.addLayout(row)
        fv.addWidget(QPushButton("Çevir", clicked=self.fx_calc))
        self.fx_res = QLabel()
        fv.addWidget(self.fx_res)

        # ===== UNIT =====
        unit = QWidget()
        uv = QVBoxLayout(unit)
        uv.addWidget(QPushButton("← Geri", clicked=lambda:self.stack.setCurrentIndex(0)))
        tabs = QTabWidget()

        def add_tab(name, table=None, temp=False):
            w = QWidget()
            l = QVBoxLayout(w)
            val = QLineEdit()
            l.addWidget(val)
            f = QComboBox()
            t = QComboBox()
            units = ["C","F","K"] if temp else table.keys()
            for u in units:
                f.addItem(u); t.addItem(u)
            r = QHBoxLayout()
            r.addWidget(f); r.addWidget(QLabel("→")); r.addWidget(t)
            l.addLayout(r)
            res = QLabel()
            l.addWidget(res)
            def do():
                try:
                    x = float(val.text())
                    out = convert_temp(x,f.currentText(),t.currentText()) if temp \
                          else convert_linear(x,f.currentText(),t.currentText(),table)
                    res.setText(f"Sonuç: {out:.4f}")
                except:
                    res.setText("Hatalı")
            l.addWidget(QPushButton("Çevir", clicked=do))
            tabs.addTab(w,name)

        add_tab("Kütle", MASS)
        add_tab("Uzunluk", LENGTH)
        add_tab("Kuvvet", FORCE)
        add_tab("Zaman", TIME)
        add_tab("Sıcaklık", temp=True)
        uv.addWidget(tabs)

        self.stack.addWidget(calc)
        self.stack.addWidget(fx)
        self.stack.addWidget(unit)

    # ===== FUNCTIONS =====
    def press(self, x):
        if x == "C":
            self.display.setText("0")
        else:
            self.add_text(x)

    def add_text(self, txt):
        self.display.setText(txt if self.display.text()=="0" else self.display.text()+txt)

    def calculate(self):
        try:
            self.display.setText(str(safe_eval(self.display.text())))
        except:
            self.display.setText("Error")

    def toggle_scientific(self):
        self.scientific_visible = not self.scientific_visible
        self.sci_widget.setVisible(self.scientific_visible)

    def fx_calc(self):
        try:
            a = float(self.amount.text())
            r = a * self.rates[self.fc.currentText()] / self.rates[self.tc.currentText()]
            self.fx_res.setText(f"Sonuç: {r:.2f}")
        except:
            self.fx_res.setText("Hata")

    def apply_theme(self):
        t = THEMES[self.theme]
        self.setStyleSheet(f"""
        QWidget{{background:{t['bg']};color:{t['txt']};}}
        QLineEdit{{background:{t['disp']};border-radius:12px;padding:8px;}}
        QPushButton{{background:{t['btn']};border-radius:14px;padding:10px;}}
        QPushButton:hover{{background:{t['hover']};}}
        """)
        self.eq.setStyleSheet(f"background:{t['eq']};color:white;")

    def toggle_theme(self):
        self.theme = "light" if self.theme=="dark" else "dark"
        self.apply_theme()

    def animate(self):
        self.setWindowOpacity(0)
        a = QPropertyAnimation(self, b"windowOpacity")
        a.setDuration(400)
        a.setStartValue(0)
        a.setEndValue(1)
        a.setEasingCurve(QEasingCurve.OutCubic)
        a.start()
        self.anim = a

# ================= RUN =================
app = QApplication(sys.argv)
w = App()
w.show()
sys.exit(app.exec())

