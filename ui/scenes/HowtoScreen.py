from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, 
    QLabel, QPushButton, QStackedWidget
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap

from ui.HowToUseSlideUI import HowToUseSlide
from ui.UIStyle import (
    NAV_BUTTON_STYLESHEET, NAV_SKIP_BUTTON_STYLESHEET,
    ACTIVE_DOT_NAV_STYLESHEET, INAVTIVE_DOT_NAV_STYLESHEET
)

slides_data = [
    {
        "title": "Selamat Datang di Simulator PLTN",
        "description": "Aplikasi ini membantu Anda mensimulasikan integrasi PLTN dengan sistem kelistrikan. Mari kita pelajari cara menggunakannya.",
        "content": [],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"
    },
    {
        "title": "Fitur dan Service",
        "description": "Terdapat beberapa fitur dalam aplikasi ini, yaitu analisis loadflow simmulation, analisis dynamic simulation, analisis shortcircuit simulation",
        "content": [
            "Pilih Sistem PLTN",
            "Pilih Skenario yang ingin diamati",
            "Sesuaikan Simulasi dan Amati Grafik hasil analisis simulasi",
        ],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"

    },
    {
        "title": "Pilih Tipe PLTN System",
        "description": "Langkah pertama, pilih tipe PLTN yang ingin Anda simulasikan. Tersedia berbagai jenis reaktor dengan karakteristik berbeda.",
        "content": [],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"
    },
    {
        "title": "Pilih Skenario Simulasi",
        "description": "Pilih skenario yang ingin disimulasikan: Load Flow untuk analisis aliran daya atau Dynamic Simulation untuk analisis stabilitas sistem.",
        "content": [],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"
    },
    {
        "title": "Jalankan Simulasi",
        "description": "Atur parameter yang diperlukan, kemudian jalankan simulasi. Hasil akan ditampilkan dalam bentuk grafik dan tabel.",
        "content": [],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"
    },
    {
        "title": "Siap Memulai!",
        "description": "Anda siap untuk memulai simulasi. Klik tombol 'Mulai' untuk melanjutkan ke aplikasi.",
        "content": [],
        "image": r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\app.v2\notes-and-lofi\Alex_UIUX.jpg"
    }
]

class HowToScreenScene(QWidget):
    nextpltn = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.current_slide = 0
        self.indicators = []
        self.setup_background()
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        
        skip_btn = QPushButton("Skip Tutorial")
        skip_btn.setStyleSheet(NAV_SKIP_BUTTON_STYLESHEET)
        skip_btn.clicked.connect(self.skip_tutorial)
        header_layout.addWidget(skip_btn)
        
        main_layout.addLayout(header_layout)
        
        self.slides_stack = QStackedWidget()
        self.slides_stack.setStyleSheet("background-color: transparent;")
        main_layout.addWidget(self.slides_stack)
        
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(20)
        
        self.prev_btn = QPushButton("Sebelumnya")
        self.prev_btn.setStyleSheet(NAV_BUTTON_STYLESHEET)
        self.prev_btn.clicked.connect(self.previous_slide)
        self.prev_btn.setEnabled(False)
        nav_layout.addWidget(self.prev_btn)
        
        self.indicator_layout = QHBoxLayout()
        self.indicator_layout.setSpacing(10)
        nav_layout.addLayout(self.indicator_layout)
        
        self.next_btn = QPushButton("Selanjutnya")
        self.next_btn.setStyleSheet(NAV_BUTTON_STYLESHEET)
        self.next_btn.clicked.connect(self.next_slide)
        nav_layout.addWidget(self.next_btn)
        
        main_layout.addLayout(nav_layout)
        
        self.setLayout(main_layout)
        
        self.create_slides()
        self.update_indicators()
    
    def setup_background(self):
        """Setup background image"""
        self.background_label = QLabel(self)
        pixmap = QPixmap(r"C:\Users\Alex\NgodingDulu\hmi-reactor-nuklir\asset\Backgroundv2.jpg")
        
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)
        self.background_label.setAlignment(Qt.AlignCenter)
    
    def resizeEvent(self, event):
        """Update ukuran background saat window di-resize"""
        super().resizeEvent(event)
        self.background_label.setGeometry(0, 0, self.width(), self.height())
        self.background_label.lower()
    
    def create_slides(self):
        
        for slide_data in slides_data:
            slide = HowToUseSlide(
                title=slide_data["title"],
                description=slide_data["description"],
                content=slide_data.get("content", []),
                image_path=slide_data["image"]
            )
            self.slides_stack.addWidget(slide)
        
        for i in range(len(slides_data)):
            dot = QLabel("●")
            dot.setAlignment(Qt.AlignCenter)
            dot.setFixedSize(20, 20)
            self.indicators.append(dot)
            self.indicator_layout.addWidget(dot)
    
    def update_indicators(self):
        """Update indicator dots"""
        for i, dot in enumerate(self.indicators):
            if i == self.current_slide:
                dot.setStyleSheet(ACTIVE_DOT_NAV_STYLESHEET)
            else:
                dot.setStyleSheet(INAVTIVE_DOT_NAV_STYLESHEET)
    
    def next_slide(self):
        """Pindah ke slide berikutnya"""
        if self.current_slide < self.slides_stack.count() - 1:
            self.current_slide += 1
            self.slides_stack.setCurrentIndex(self.current_slide)
            self.update_navigation()
        else:
            self.nextpltn.emit()
    
    def previous_slide(self):
        """Pindah ke slide sebelumnya"""
        if self.current_slide > 0:
            self.current_slide -= 1
            self.slides_stack.setCurrentIndex(self.current_slide)
            self.update_navigation()
    
    def skip_tutorial(self):
        """Skip tutorial dan langsung lanjut"""
        self.nextpltn.emit()
    
    def update_navigation(self):
        """Update state tombol navigasi"""
        # Update tombol Previous
        self.prev_btn.setEnabled(self.current_slide > 0)
        
        # Update tombol Next/Finish
        if self.current_slide == self.slides_stack.count() - 1:
            self.next_btn.setText("Mulai")
        else:
            self.next_btn.setText("Selanjutnya")
        
        # Update indicators
        self.update_indicators()