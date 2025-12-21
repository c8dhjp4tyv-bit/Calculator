import sys
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QPushButton, QLineEdit, QLabel, QHBoxLayout
)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PySide6.QtGui import QFont

# ---------------- THEMES ----------------
THEMES = {
    "dark": {
        "window": "#0f172a",
        "card": "#111827",
        "display": "#020617",
        "btn": "#1e293b",
        "btn_hover": "#334155",
        "op": "#f59e0b",
        "eq": "#22c55e",
        "text": "#f8fafc"
    },
    "light": {
        "window": "#e5e7eb",
        "card": "#f9fafb",
        "display": "#ffffff",
        "btn": "#e5e7eb",
        "btn_hover": "#d1d5db",
        "op": "#f59e0b",
        "eq": "#16a34a",
        "text": "#020617"
    }
}

# ---------------- LANGUAGE ----------------
LANGS = ["en", "tr", "de", "fr"]

TEXT = {
    "en": "Calculator",
    "tr": "Hesap Makinesi",
    "de": "Rechner",
    "fr": "Calculatrice"
}

# ---------------- MAIN APP ----------------
class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.theme = "dark"
        self.lang = "tr"
        self.init_ui()
        self.apply_theme(animated=False)
        self.animate_start()

    # ---------- UI ----------
    def init_ui(self):
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setFixedSize(360, 520)

        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(20, 20, 20, 20)

        # Title bar
        top = QHBoxLayout()
        self.title = QLabel(TEXT[self.lang])
        self.title.setFont(QFont("Segoe UI", 11, QFont.Bold))

        self.lang_btn = QPushButton("🌐")
        self.lang_btn.setFixedWidth(32)
        self.lang_btn.clicked.connect(self.toggle_language)

        self.theme_btn = QPushButton("🌙")
        self.theme_btn.setFixedWidth(32)
        self.theme_btn.clicked.connect(self.toggle_theme)

        close = QPushButton("✕")
        close.clicked.connect(self.close)

        top.addWidget(self.title)
        top.addStretch()
        top.addWidget(self.lang_btn)
        top.addWidget(self.theme_btn)
        top.addWidget(close)
        self.root.addLayout(top)

        # Display
        self.display = QLineEdit()
        self.display.setFont(QFont("Segoe UI", 26))
        self.display.setAlignment(Qt.AlignRight)
        self.display.setFixedHeight(60)
        self.root.addWidget(self.display)

        # Buttons
        grid = QGridLayout()
        self.buttons = []

        layout = [
            ("7",0,0),("8",0,1),("9",0,2),("/",0,3),
            ("4",1,0),("5",1,1),("6",1,2),("*",1,3),
            ("1",2,0),("2",2,1),("3",2,2),("-",2,3),
            ("0",3,0),(".",3,1),("C",3,2),("+",3,3)
        ]

        for t,r,c in layout:
            btn = QPushButton(t)
            btn.setFont(QFont("Segoe UI", 14))
            btn.clicked.connect(lambda _,x=t: self.press(x))
            grid.addWidget(btn,r,c)
            self.buttons.append(btn)

        self.eq = QPushButton("=")
        self.eq.setFont(QFont("Segoe UI", 18))
        self.eq.clicked.connect(self.calculate)
        grid.addWidget(self.eq,4,0,1,4)

        self.root.addLayout(grid)

    # ---------- LOGIC ----------
    def press(self, v):
        if v == "C":
            self.display.clear()
        else:
            self.display.insert(v)

    def calculate(self):
        try:
            self.display.setText(str(eval(self.display.text())))
        except:
            self.display.setText("Error")

    # ---------- LANGUAGE ----------
    def toggle_language(self):
        i = LANGS.index(self.lang)
        self.lang = LANGS[(i + 1) % len(LANGS)]
        self.title.setText(TEXT[self.lang])

    # ---------- THEME ----------
    def apply_theme(self, animated=True):
        t = THEMES[self.theme]

        style = f"""
        QWidget {{
            background:{t['window']};
            color:{t['text']};
        }}
        QLineEdit {{
            background:{t['display']};
            border-radius:12px;
            padding:8px;
        }}
        QPushButton {{
            background:{t['btn']};
            border-radius:14px;
            padding:10px;
        }}
        QPushButton:hover {{
            background:{t['btn_hover']};
        }}
        """

        self.setStyleSheet(style)
        self.eq.setStyleSheet(f"""
            background:{t['eq']};
            color:white;
            border-radius:18px;
            padding:14px;
        """)

    def toggle_theme(self):
        self.theme = "light" if self.theme == "dark" else "dark"
        self.apply_theme()

    # ---------- ANIMATION ----------
    def animate_start(self):
        self.setWindowOpacity(0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(600)
        anim.setStartValue(0)
        anim.setEndValue(1)
        anim.setEasingCurve(QEasingCurve.OutCubic)
        anim.start()
        self.anim = anim

# ---------------- RUN ----------------
app = QApplication(sys.argv)
w = Calculator()
w.show()
sys.exit(app.exec())
