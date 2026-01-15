from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout
from PyQt5.QtCore import pyqtSignal, Qt

from ui.UIStyle import (
    PLTN_SYSTEM_TITLE_STYLESHEET, 
    SCENARIO_NAV_BUTTON_STYLESHEET, 
    CARD_CONTENT_STYLESHEET
)

class ScenarioScreenScene(QWidget):
    backtopltn = pyqtSignal()
    toloadflow = pyqtSignal()
    todynamic = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        
        self.proj_name = None
        self.digsilent_path = None

        title = QLabel("Pilih Salah Satu Simulasi")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)

        loadflowdynamiclayout = QHBoxLayout()
        loadflowdynamiclayout.addStretch()

        loadflowvlayout = QVBoxLayout()

        self.nextloadflowactifity = QPushButton("Loadflow")
        self.nextloadflowactifity.setStyleSheet(SCENARIO_NAV_BUTTON_STYLESHEET)
        self.nextloadflowactifity.setMinimumSize(250, 150)

        loadflowdescription = QLabel(
            "Proses Load Flow digunakan untuk menghitung aliran daya, tegangan bus, "
            "arus saluran, serta rugi-rugi pada sistem tenaga. Analisis ini membantu "
            "memastikan sistem beroperasi dalam kondisi stabil dan sesuai batas operasi."
        )

        loadflowdescription.setStyleSheet(CARD_CONTENT_STYLESHEET)
        loadflowdescription.setWordWrap(True)
        loadflowdescription.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loadflowvlayout.addWidget(self.nextloadflowactifity)
        loadflowvlayout.addWidget(loadflowdescription)
        loadflowvlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dynamicvlayout = QVBoxLayout()

        self.nextdynamicctifity = QPushButton("Dynamic")
        self.nextdynamicctifity.setMinimumSize(250, 150)
        self.nextdynamicctifity.setStyleSheet(SCENARIO_NAV_BUTTON_STYLESHEET)

        dynamicdescription = QLabel(
            "Dynamic Simulation digunakan untuk menganalisis respon transien sistem tenaga "
            "terhadap gangguan, seperti hubung singkat atau perubahan beban. Proses ini "
            "memungkinkan evaluasi kestabilan dan performa dinamis sistem."
        )

        dynamicdescription.setStyleSheet(CARD_CONTENT_STYLESHEET)
        dynamicdescription.setWordWrap(True)
        dynamicdescription.setAlignment(Qt.AlignmentFlag.AlignCenter)

        dynamicvlayout.addWidget(self.nextdynamicctifity)
        dynamicvlayout.addWidget(dynamicdescription)
        
        dynamicvlayout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        loadflowdynamiclayout.addLayout(loadflowvlayout)
        loadflowdynamiclayout.addSpacing(50)  # jarak antar card
        loadflowdynamiclayout.addLayout(dynamicvlayout)
        loadflowdynamiclayout.addStretch()

        backtooption = QPushButton("Back to PLTN System Option")
        backtooption.setStyleSheet(SCENARIO_NAV_BUTTON_STYLESHEET)
        backtooption.setFixedHeight(50)

        backtooption.clicked.connect(self.backtopltn.emit)
        self.nextloadflowactifity.clicked.connect(self.toloadflow.emit)
        self.nextdynamicctifity.clicked.connect(self.todynamic.emit)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addLayout(loadflowdynamiclayout)
        layout.addStretch(1)
        layout.addWidget(backtooption)

        self.setLayout(layout)