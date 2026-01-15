from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton
)
from ui.UIStyle import (
    NAV_BUTTON_STYLESHEET, CARD_CONTAINER_STYLESHEET, CARD_TITLE_STYLESHEET, CARD_CONTENT_STYLESHEET
)

class PLTNCardUI(QWidget):
    def __init__(self, title, desccontent, pfd_path_file):
        super().__init__()
        
        self.titlecontent = title
        self.desccontent = desccontent
        self.pfd_path_file = pfd_path_file
        
        card_widget = QWidget()
        card_widget.setStyleSheet(CARD_CONTAINER_STYLESHEET)
        card_widget.setFixedWidth(700)

        card_layout = QVBoxLayout()
        card_layout.setSpacing(8)

        self.card_title = QLabel(self.titlecontent)
        self.card_title.setStyleSheet(CARD_TITLE_STYLESHEET)

        card_download_pfd = QPushButton("Download pfd file")
        card_download_pfd.setStyleSheet(NAV_BUTTON_STYLESHEET)

        self.card_brief_content = QLabel("\n".join(self.desccontent))
        self.card_brief_content.setStyleSheet(CARD_CONTENT_STYLESHEET)
        self.card_brief_content.setWordWrap(True)

        card_layout.addWidget(self.card_title)
        # card_layout.addWidget(card_download_pfd)
        card_layout.addWidget(self.card_brief_content)
        card_widget.setLayout(card_layout)

        card_center_layout = QHBoxLayout()
        card_center_layout.addStretch()
        card_center_layout.addWidget(card_widget)
        card_center_layout.addStretch()

        self.setLayout(card_center_layout)
    
    def update_card(self, title, desccontent, pfd_path_file):
        self.card_title.setText(title)
        self.card_brief_content.setText("\n".join(desccontent))
        
        self.titlecontent = title
        self.desccontent = desccontent
        self.pfd_path_file = pfd_path_file
    