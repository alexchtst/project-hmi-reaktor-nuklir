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
CASES_COMBO_BOX_STYLESHEET = """
QComboBox {
    background-color: white;
    color: #333333;
    border: 1px solid #dcdcdc;
    border-radius: 5px;
    padding: 8px 15px;
    font-size: 16px;
    min-height: 20px;
}
QComboBox:hover {
    border: 1px solid #0078d7;
    background-color: #f8f9fa;
}
QComboBox:focus {
    border: 2px solid #0078d7;
    background-color: white;
}
QComboBox::drop-down {
    border: none;
    width: 30px;
}
QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 6px solid #555555;
    margin-right: 8px;
}
QComboBox::down-arrow:hover {
    border-top-color: #0078d7;
}
QComboBox QAbstractItemView {
    background-color: white;
    border: 1px solid #dcdcdc;
    border-radius: 5px;
    selection-background-color: #0078d7;
    selection-color: white;
    outline: none;
    padding: 4px;
}
QComboBox QAbstractItemView::item {
    padding: 8px 15px;
    border-radius: 3px;
    min-height: 20px;
}
QComboBox QAbstractItemView::item:hover {
    background-color: #f8f9fa;
    color: #0078d7;
}
QComboBox QAbstractItemView::item:selected {
    background-color: #0078d7;
    color: white;
}
"""