"""
Global stylesheet for AgriPOS desktop app
"""

SIDEBAR_STYLE = """
    QWidget#sidebar {
        background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
            stop:0 #0f172a, stop:0.6 #1e1b4b, stop:1 #064e3b);
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    QPushButton#nav_btn {
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 12px;
        padding: 12px 14px;
        text-align: left;
        font-size: 15px;
        font-weight: 600;
    }
    QPushButton#nav_btn:hover {
        background: rgba(255,255,255,0.08);
        color: #ffffff;
    }
    QPushButton#nav_btn:checked {
        background: rgba(16,185,129,0.20);
        color: #6ee7b7;
        border: 1px solid rgba(16,185,129,0.30);
        font-weight: 700;
    }
    QLabel#logo_title {
        color: #ffffff;
        font-size: 18px;
        font-weight: 700;
    }
    QLabel#logo_sub {
        color: #94a3b8;
        font-size: 12px;
    }
    QLabel#user_name {
        color: #ffffff;
        font-size: 14px;
        font-weight: 700;
    }
    QLabel#user_role {
        color: #94a3b8;
        font-size: 12px;
    }
    QPushButton#logout_btn {
        background: transparent;
        color: #94a3b8;
        border: none;
        border-radius: 8px;
        padding: 8px 12px;
        text-align: left;
        font-size: 13px;
    }
    QPushButton#logout_btn:hover {
        background: rgba(239,68,68,0.10);
        color: #f87171;
    }
"""

MAIN_STYLE = """
    QMainWindow, QWidget#main_area {
        background: #f8fafc;
    }
    QWidget#page_container {
        background: #f8fafc;
    }
"""

CARD_STYLE = """
    QFrame#card {
        background: #ffffff;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
    }
"""

TABLE_STYLE = """
    QTableWidget {
        background: #ffffff;
        border: none;
        border-radius: 0px;
        gridline-color: #f1f5f9;
        selection-background-color: #eff6ff;
        selection-color: #1e40af;
        font-size: 14px;
        outline: none;
    }
    QTableWidget::item {
        padding: 10px 14px;
        border-bottom: 1px solid #f1f5f9;
        color: #334155;
    }
    QTableWidget::item:selected {
        background: #eff6ff;
        color: #1e40af;
    }
    QHeaderView::section {
        background: #f8fafc;
        color: #64748b;
        font-size: 13px;
        font-weight: 700;
        padding: 10px 12px;
        border: none;
        border-bottom: 2px solid #e2e8f0;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    QScrollBar:vertical {
        width: 6px;
        background: transparent;
    }
    QScrollBar::handle:vertical {
        background: #cbd5e1;
        border-radius: 3px;
        min-height: 30px;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0;
    }
"""

INPUT_STYLE = """
    QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 14px;
        color: #1e293b;
        selection-background-color: #d1fae5;
    }
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus {
        border-color: #10b981;
        background: #f0fdf4;
    }
    QComboBox::drop-down {
        border: none;
        width: 24px;
    }
    QComboBox::down-arrow {
        width: 12px;
        height: 12px;
    }
    QComboBox QAbstractItemView {
        border: 1.5px solid #e2e8f0;
        border-radius: 8px;
        background: #ffffff;
        selection-background-color: #d1fae5;
        selection-color: #065f46;
    }
    QTextEdit {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
        color: #1e293b;
    }
    QTextEdit:focus {
        border-color: #10b981;
        background: #f0fdf4;
    }
"""

BUTTON_PRIMARY = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #10b981, stop:1 #0d9488);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #059669, stop:1 #0f766e);
    }
    QPushButton:pressed {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #047857, stop:1 #0d6b6b);
    }
    QPushButton:disabled {
        background: #94a3b8;
    }
"""

BUTTON_SECONDARY = """
    QPushButton {
        background: #ffffff;
        color: #475569;
        border: 1.5px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 500;
    }
    QPushButton:hover {
        background: #f8fafc;
        border-color: #cbd5e1;
    }
    QPushButton:pressed {
        background: #f1f5f9;
    }
"""

BUTTON_DANGER = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #ef4444, stop:1 #dc2626);
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 13px;
        font-weight: 600;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #dc2626, stop:1 #b91c1c);
    }
    QPushButton:pressed {
        background: #991b1b;
    }
"""

NUMPAD_STYLE = """
    QPushButton#numpad_btn {
        background: #ffffff;
        color: #1e293b;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        font-size: 20px;
        font-weight: 600;
        min-width: 70px;
        min-height: 60px;
    }
    QPushButton#numpad_btn:hover {
        background: #f0fdf4;
        border-color: #10b981;
        color: #065f46;
    }
    QPushButton#numpad_btn:pressed {
        background: #d1fae5;
    }
    QPushButton#numpad_clear {
        background: #fff7ed;
        color: #ea580c;
        border: 1.5px solid #fed7aa;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 700;
        min-width: 70px;
        min-height: 60px;
    }
    QPushButton#numpad_clear:hover {
        background: #ffedd5;
    }
    QPushButton#numpad_del {
        background: #fff1f2;
        color: #e11d48;
        border: 1.5px solid #fecdd3;
        border-radius: 12px;
        font-size: 18px;
        font-weight: 700;
        min-width: 70px;
        min-height: 60px;
    }
    QPushButton#numpad_del:hover {
        background: #ffe4e6;
    }
"""

CHECKOUT_BTN_STYLE = """
    QPushButton {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #10b981, stop:1 #0d9488);
        color: #ffffff;
        border: none;
        border-radius: 14px;
        font-size: 18px;
        font-weight: 700;
        padding: 16px;
    }
    QPushButton:hover {
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 #059669, stop:1 #0f766e);
    }
    QPushButton:pressed {
        background: #047857;
    }
    QPushButton:disabled {
        background: #cbd5e1;
        color: #94a3b8;
    }
"""

PRODUCT_CARD_STYLE = """
    QFrame#product_card {
        background: #ffffff;
        border-radius: 14px;
        border: 1.5px solid #e2e8f0;
    }
    QFrame#product_card:hover {
        border-color: #10b981;
        background: #f0fdf4;
    }
"""

DIALOG_STYLE = """
    QDialog {
        background: #ffffff;
        border-radius: 16px;
    }
    QLabel#dialog_title {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
    }
"""
