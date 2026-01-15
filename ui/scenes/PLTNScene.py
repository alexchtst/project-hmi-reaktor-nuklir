from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QComboBox, QLabel, QPushButton, QFileDialog
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.PLTNcardUI import PLTNCardUI
from ui.ConnectSetupProcessDialogUI import ConnectSetupProcessDialogUI
from ui.UIStyle import (
    PLTN_SYSTEM_TITLE_STYLESHEET, NAV_BUTTON_STYLESHEET, FINDPATH_BUTTON_STYLESHEET,
    CASES_COMBO_BOX_STYLESHEET
)

SYSTEM_PROVIDED = [
    "39 Bus New England System SMR",
    "Nine-bus System",
]

SYSTEM_PROVIDED_DADATA = {
    "39 Bus New England System SMR": {
        "title": "39 Bus New England System SMR",
        "desccontent": [
            "Simulasi Sistem PLTN"
        ],
        "pfd_path_file": ""
    },
    "Nine-bus System": {
        "title": "Nine-bus System SMR",
        "desccontent": [
            "(belum tersedia)"
            "Sedang Dalam Pengerjaan"
        ],
        "pfd_path_file": ""
    },
}

class PLTNOptionScreenScene(QWidget):
    nextscenario = pyqtSignal()
    pltnsystemsignal = pyqtSignal(str)
    digsilentpathsignal = pyqtSignal(str)
    
    casessignal = pyqtSignal(list)
    casseseventsignal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
                
        title = QLabel("PLTN System Option")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        
        default_key = SYSTEM_PROVIDED[0]
        data = SYSTEM_PROVIDED_DADATA[default_key]
        
        self.validation_status = {
            "39 Bus New England System SMR": False,
            "Nine-bus System": False
        }

        self.card_widget = PLTNCardUI(
            title=data["title"],
            desccontent=data["desccontent"],
            pfd_path_file=data["pfd_path_file"]
        )

        self.btn = QPushButton("Lanjut Scenario Option")
        self.btn.setStyleSheet(NAV_BUTTON_STYLESHEET)
        self.btn.setEnabled(False)
        self.btn.clicked.connect(self.on_send_pltn_system_change)

        pltn_system_layout = QHBoxLayout()
        pltn_system_layout.addStretch()
                
        self.pltn_system_combobox = QComboBox()
        self.pltn_system_combobox.addItems(SYSTEM_PROVIDED)
        self.pltn_system_combobox.setStyleSheet(CASES_COMBO_BOX_STYLESHEET)
        self.pltn_system_combobox.currentTextChanged.connect(self.on_pltn_system_change)
        
        pltn_system_layout.addWidget(self.pltn_system_combobox)
        self.current_pltn_system = str(self.pltn_system_combobox.currentText())
        
        self.current_digsilent_pf_pth = ""
        find_path_layout = QHBoxLayout()
        find_path_layout.addStretch()
        wraper_path_layout = QVBoxLayout()
        
        find_btn_layout = QHBoxLayout()
        find_btn_layout.addStretch()
        self.find_path_btn = QPushButton("Hubungkan Digsilent")
        self.find_path_btn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        find_btn_layout.addWidget(self.find_path_btn)
        self.find_path_btn.clicked.connect(self.select_digsilent_folder)
        
        selected_path_label = QHBoxLayout()
        selected_path_label.addStretch()
        self.selected_path_label = QLabel(self.current_digsilent_pf_pth)
        selected_path_label.addWidget(self.selected_path_label)
        
        wraper_path_layout.addLayout(find_btn_layout)
        wraper_path_layout.addLayout(selected_path_label)
        find_path_layout.addLayout(wraper_path_layout)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addLayout(pltn_system_layout)
        layout.addLayout(find_path_layout)
        layout.addStretch(1)
        layout.addWidget(self.card_widget)
        layout.addStretch(1)
        layout.addWidget(self.btn)
        self.setLayout(layout)
    
    def on_pltn_system_change(self, value):
        self.current_pltn_system = str(value)
        
        data = SYSTEM_PROVIDED_DADATA[value]
        
        self.btn.setEnabled(self.validation_status[value])
        
        self.card_widget.update_card(
            title=data["title"],
            desccontent=data["desccontent"],
            pfd_path_file=data["pfd_path_file"]
        )
        
    
    def select_digsilent_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Pilih Folder DigSilent Python version")

        if folder:
            self.current_digsilent_pf_pth = folder
            self.selected_path_label.setText(folder)
            self.on_verification_btn()
        else:
            self.selected_path_label.setText("")
    
    def on_send_pltn_system_change(self):
        self.pltnsystemsignal.emit(self.current_pltn_system)
        self.digsilentpathsignal.emit(self.current_digsilent_pf_pth)
        self.nextscenario.emit()
        
    def on_verification_btn(self):
        df_path = self.current_digsilent_pf_pth
        projname = self.current_pltn_system
        
        self.progress_dialog = ConnectSetupProcessDialogUI(
            titile="Memvalidasi Digsilent PowerFactory Path", 
            content="Mohon Tunggu Sebentar...",
            proj_name=projname,
            ds_pf_pathfle=df_path
        )
        self.progress_dialog.finsihedpayload.connect(self.on_finished_with_payload)
        self.progress_dialog.show()
    
    def on_finished_with_payload(self, value):
        self.validation_status[self.current_pltn_system] = True
        self.casessignal.emit(value["data"])
        self.casseseventsignal.emit(value["events"])
        self.btn.setEnabled(self.validation_status[self.current_pltn_system])
