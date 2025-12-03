from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtGui import QPixmap

from ui.UIStyle import COVER_TITLE_STYLESHEET, COVER_SUBTITLE_STYLESHEET
from asset.assetloader import BACKGROUNDV1

SUBTITLE = """
Simulasi Human Machine Interface. 
PLTN (Pembangkit Listrik Tenaga Nuklir). 
"""

class CoverScreenScene(QWidget):
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        # Layout utama
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Label untuk background image
        self.background_label = QLabel(self)
        
        # [TODO] benerin ini lex
        pixmap = QPixmap(fr"{BACKGROUNDV1}")
        
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setAlignment(Qt.AlignCenter)
        
        # Title label
        self.title_label = QLabel("Simulasi Integrasi PLTN")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet(COVER_TITLE_STYLESHEET)
        self.title_label.setWordWrap(True)
        
        # Subtitle label
        self.subtitle_label = QLabel(SUBTITLE)
        self.subtitle_label.setAlignment(Qt.AlignCenter)
        self.subtitle_label.setStyleSheet(COVER_SUBTITLE_STYLESHEET)
        self.subtitle_label.setWordWrap(True)
        
        # Tambahkan background ke layout
        layout.addWidget(self.background_label)
        
        # Set parent untuk title dan subtitle agar overlay di atas background
        self.title_label.setParent(self)
        self.subtitle_label.setParent(self)
        
        self.setLayout(layout)
        
        self.setWindowOpacity(0)
        
        # Animasi fade in
        self.fade_in_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_in_animation.setDuration(1000)
        self.fade_in_animation.setStartValue(0)
        self.fade_in_animation.setEndValue(1)
        self.fade_in_animation.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Animasi fade out
        self.fade_out_animation = QPropertyAnimation(self, b"windowOpacity")
        self.fade_out_animation.setDuration(1000)
        self.fade_out_animation.setStartValue(1)
        self.fade_out_animation.setEndValue(0)
        self.fade_out_animation.setEasingCurve(QEasingCurve.InOutQuad)
        self.fade_out_animation.finished.connect(self.load_complete)
        
        # Mulai fade in saat widget ditampilkan
        QTimer.singleShot(100, self.start_fade_in)
        
        # Mulai fade out setelah 3 detik
        QTimer.singleShot(3000, self.start_fade_out)
    
    def start_fade_in(self):
        self.fade_in_animation.start()
    
    def start_fade_out(self):
        self.fade_out_animation.start()
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        center_y = self.height() // 2
        title_height = 120
        self.title_label.setGeometry(0, center_y - 150, self.width(), title_height)
        subtitle_height = 200
        self.subtitle_label.setGeometry(0, center_y - 20, self.width(), subtitle_height)
    
    def load_complete(self):
        self.finished.emit()