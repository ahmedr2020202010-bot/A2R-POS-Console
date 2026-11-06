# theme.py
# ملف التصميم الشامل (QSS) للبرنامج ليعطي شكلاً حديثاً واحترافياً (Modern Dark Theme)

GLOBAL_QSS = """
/* الأساسيات */
QMainWindow, QDialog, QWidget {
    background-color: #080E17;
    color: #FFFFFF;
    font-family: 'Segoe UI', Arial;
}

/* الكروت والإطارات */
QFrame {
    background-color: #121E2E;
    border: 1px solid #1E2E42;
    border-radius: 8px;
}

/* النصوص العادية */
QLabel {
    border: none;
    background: transparent;
}

/* الأزرار الأساسية */
QPushButton {
    background-color: #0284C7;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
    font-weight: bold;
    border: none;
}
QPushButton:hover {
    background-color: #0369A1;
}
QPushButton:pressed {
    background-color: #075985;
}
QPushButton:disabled {
    background-color: #334155;
    color: #94A3B8;
}

/* حقول الإدخال */
QLineEdit {
    background-color: #0A131F;
    border: 1px solid #1E2E42;
    border-radius: 6px;
    padding: 6px;
    color: white;
}
QLineEdit:focus {
    border: 1px solid #38BDF8;
}

/* الجداول */
QTableWidget {
    background-color: #0A131F;
    border: 1px solid #1E2E42;
    border-radius: 6px;
    gridline-color: #1E2E42;
    selection-background-color: #0284C7;
    selection-color: white;
}
QHeaderView::section {
    background-color: #121E2E;
    color: #38BDF8;
    padding: 6px;
    border: none;
    border-bottom: 1px solid #1E2E42;
    font-weight: bold;
}
QTableView::item {
    padding: 4px;
    border-bottom: 1px solid #1E2E42;
}

/* شريط التقدم */
QProgressBar {
    background-color: #0A131F;
    border: 1px solid #1E2E42;
    border-radius: 4px;
    text-align: center;
    color: white;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #10B981;
    border-radius: 3px;
}

/* التبويبات (Tabs) */
QTabWidget::pane {
    border: 1px solid #1E2E42;
    background: #0A131F;
    border-radius: 6px;
}
QTabBar::tab {
    background: #121E2E;
    color: #94A3B8;
    padding: 8px 16px;
    border: 1px solid #1E2E42;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background: #0284C7;
    color: white;
    border-bottom-color: #0284C7;
}
QTabBar::tab:hover:!selected {
    background: #1E293B;
}

/* القوائم المنسدلة */
QComboBox {
    background-color: #0A131F;
    border: 1px solid #1E2E42;
    border-radius: 6px;
    padding: 4px 8px;
    color: white;
}
QComboBox::drop-down {
    border: none;
}
QComboBox QAbstractItemView {
    background-color: #121E2E;
    border: 1px solid #1E2E42;
    selection-background-color: #0284C7;
}

/* القوائم المنبثقة (Right Click Menu) */
QMenu {
    background-color: #121E2E;
    color: white;
    border: 1px solid #1E2E42;
    border-radius: 4px;
}
QMenu::item {
    padding: 6px 24px;
}
QMenu::item:selected {
    background-color: #0284C7;
}

/* رسائل التنبيه */
QMessageBox {
    background-color: #121E2E;
}
QMessageBox QLabel {
    color: white;
}
QMessageBox QPushButton {
    min-width: 80px;
}
"""
