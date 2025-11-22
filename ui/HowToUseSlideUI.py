from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from ui.UIStyle import STEP_TITLE_LABEL_STYLESHEET, STEP_SUBTITLE_LABEL_STYLESHEET, STEP_LABEL_STYLESHEET, STEP_WIDGET_STYLESHEET

class HowToUseSlide(QWidget):
    """Widget untuk satu slide tutorial"""
    def __init__(self, title, description, content=None, image_path=None):
        super().__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(STEP_TITLE_LABEL_STYLESHEET)
        title_label.setWordWrap(True)
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setStyleSheet(STEP_SUBTITLE_LABEL_STYLESHEET)
        desc_label.setWordWrap(True)
        desc_label.setMaximumWidth(900)
        layout.addWidget(desc_label)
        
        content_widget = QWidget()
        content_layout = QHBoxLayout()
        content_layout.setSpacing(30)
        content_widget.setLayout(content_layout)
        
        # Image (jika ada)
        if image_path:
            image_label = QLabel()
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(500, 400, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                image_label.setPixmap(scaled_pixmap)
                image_label.setAlignment(Qt.AlignCenter)
                content_layout.addWidget(image_label)
        
        # Step Content (jika ada)
        if content and len(content) > 0:
            steps_widget = QWidget()
            steps_layout = QVBoxLayout()
            steps_layout.setSpacing(15)
            steps_layout.setContentsMargins(20, 20, 20, 20)
            
            # Style untuk container steps
            steps_widget.setStyleSheet(STEP_WIDGET_STYLESHEET)
            
            for i, step in enumerate(content, 1):
                step_label = QLabel(f"{i}. {step}")
                step_label.setStyleSheet(STEP_LABEL_STYLESHEET)
                step_label.setWordWrap(True)
                steps_layout.addWidget(step_label)
            
            steps_widget.setLayout(steps_layout)
            steps_widget.setMaximumWidth(600)
            content_layout.addWidget(steps_widget)
        
        if image_path or (content and len(content) > 0):
            layout.addWidget(content_widget)
        
        layout.addStretch()
        self.setLayout(layout)