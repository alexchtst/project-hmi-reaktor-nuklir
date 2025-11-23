from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel
)
from ui.UIStyle import (
    CARD_CONTAINER_STYLESHEET, CARD_TITLE_STYLESHEET
)

class CaseCardUI(QWidget):

    def __init__(self, title):
        super().__init__()
        
        self.titlecontent = title
        
        self.card_widget = QWidget()
        self.card_widget.setStyleSheet(CARD_CONTAINER_STYLESHEET)
        self.card_widget.setFixedWidth(700)

        self.card_layout = QVBoxLayout()
        self.card_layout.setSpacing(8)

        self.card_title = QLabel(self.titlecontent)
        self.card_title.setStyleSheet(CARD_TITLE_STYLESHEET)

        self.card_layout.addWidget(self.card_title)
        self.card_widget.setLayout(self.card_layout)

        card_center_layout = QHBoxLayout()
        card_center_layout.addWidget(self.card_widget)

        self.setLayout(card_center_layout)
    
    def update_card(self, title):
        self.card_title.setText(title)
        
        self.titlecontent = title
    