CUSTOM_GLOBAL_STYLESHEET = """
QWidget {
    font-family: 'Segoe UI';
    font-size: 12px;
    color: #222;
}
QGroupBox {
    background-color: #f8f9fa;
    border: 1px solid #ccc;
    border-radius: 2px;
    padding: 12px;
    font-weight: bold;
}
QPushButton {
    background-color: #0078d7;
    color: white;
    border-radius: 6px;
    padding: 6px 12px;
}
QPushButton:hover {
    background-color: #005a9e;
}
QListWidget {
    background: white;
    border: 1px solid #bbb;
    border-radius: 2px;
}
QLineEdit {
    background-color: white;
    border: 1px solid #aaa;
    border-radius: 6px;
    font-family: 'Segoe UI';
    padding: 2px;
}
QTextEdit {
    background-color: white;
    border: 1px solid #bbb;
    border-radius: 2px;
    font-family: 'Segoe UI';
}
"""

PROGRESS_BAR_STYLE_SHEET = """
#BlueProgressBar {
    border: 1px solid #2196F3;
    border-radius: 2px;
    background-color: #E0E0E0;
}
#BlueProgressBar::chunk {
    background-color: #2196F3;
    width: 10px; 
    margin: 0.5px;
}
"""

NAV_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #0078d7;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 40px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00416B;
}
QPushButton:pressed {
    background-color: #21618c;
}
"""

NAV_SKIP_BUTTON_STYLESHEET = """
QPushButton {
    background-color: transparent;
    color: white;
    border: 1px solid #0078d7;
    border-radius: 10px;
    padding: 12px 40px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #0078d7;
}
"""

ACTIVE_DOT_NAV_STYLESHEET = "color: #00416B; font-size: 24px;"
INAVTIVE_DOT_NAV_STYLESHEET ="color: #bdc3c7; font-size: 20px;"

STEP_WIDGET_STYLESHEET = """
QWidget {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 10px;
}
"""

STEP_LABEL_STYLESHEET ="""
QLabel {
    font-size: 16px;
    color: black;
    padding: 8px 15px;
    background-color: white;
    border-radius: 5px;
    border-left: 4px solid #3498db;
}
"""

STEP_TITLE_LABEL_STYLESHEET = """
QLabel {
    font-size: 32px;
    font-weight: bold;
    color: white;
    padding: 20px;
}
"""
STEP_SUBTITLE_LABEL_STYLESHEET = """
QLabel {
    font-size: 20px;
    color: white;
    padding: 10px 20px;
    line-height: 1.6;
}
"""

COVER_TITLE_STYLESHEET = """
QLabel {
    color: white;
    font-size: 60px;
    font-weight: bold;
    background: transparent;
    padding: 20px;
}
"""
COVER_SUBTITLE_STYLESHEET = """
QLabel {
    color: white;
    font-size: 20px;
    background: transparent;
    padding: 20px;
}
"""
COVER_CONTENT_STYLESHEET = """
QLabel {
    color: white;
    font-size: 20px;
    background: transparent;
    padding: 20px;
}
"""

PLTN_SYSTEM_TITLE_STYLESHEET = """
QLabel {
    color: black;
    font-size: 32px;
    font-weight: bold;
    background: transparent;
    padding: 20px;
}
"""

CARD_CONTAINER_STYLESHEET = """
    QWidget {
        background-color: #ffffff;
        border: 1px solid #dcdcdc;
        border-radius: 12px;
        padding: 16px 24px;   /* padding dalam card */
    }
"""

CARD_TITLE_STYLESHEET = """
    QLabel {
        font-size: 20px;
        font-weight: bold;
        color: #333333;
    }
"""

CARD_CONTENT_STYLESHEET = """
    QLabel {
        font-size: 18px;
        color: #555555;
        line-height: 1.4;
    }
"""

SCENARIO_NAV_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #0078d7;
    color: white;
    border: none;
    border-radius: 10px;
    padding: 12px 40px;
    font-size: 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #00416B;
}
QPushButton:pressed {
    background-color: #21618c;
}
"""

FINDPATH_BUTTON_STYLESHEET = """
QPushButton {
    background-color: #0078d7;
    padding: 16px 24px;   /* padding dalam card */
    color: white;
    border: none;
    border-radius: 5px;
    font-size: 12px;
}
QPushButton:hover {
    background-color: #00416B;
}
QPushButton:pressed {
    background-color: #21618c;
}
"""