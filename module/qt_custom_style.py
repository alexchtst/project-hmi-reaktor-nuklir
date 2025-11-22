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