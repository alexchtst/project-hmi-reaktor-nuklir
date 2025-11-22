from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTabWidget,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.UIStyle import (
    PLTN_SYSTEM_TITLE_STYLESHEET, FINDPATH_BUTTON_STYLESHEET
)

class DynamicActifityScreenScene(QWidget):
    backcenario = pyqtSignal()
    backpltn = pyqtSignal()
    project_name_signal = pyqtSignal(str)
    ds_pf_path_signal = pyqtSignal(str)
    caseses_signal = pyqtSignal(list)
    resultisready = pyqtSignal()
    resultisready = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()
        self.__isdata_ready = False
        self.__df_path = None
        self.__projectname = None
        self.__caseses = None
        
        self.tabs = QTabWidget()
        # tab running and general info
        self.tab_gen_info = self.create_table_tab("Simulasi Dinamis")
        # tab bus volate
        self.tab_active_pow = self.create_table_tab("Active Power")
        # tab bus phasevolate
        self.tab_reactive_pow = self.create_table_tab("Reactive Power")
        # tab generator active power
        self.tab_gen_freq = self.create_table_tab("Generator Frequency")
        # tab generator reactive power
        self.tab_bus_freq = self.create_table_tab("Bus Frequency")
        
        self.tabs.addTab(self.tab_gen_info, "Simulasi")
        self.tabs.addTab(self.tab_active_pow, "Active Power")
        self.tabs.addTab(self.tab_reactive_pow, "Reactive Power")
        self.tabs.addTab(self.tab_gen_freq, "Generator Frequency")
        self.tabs.addTab(self.tab_bus_freq, "Bus Frequency")
        
        self.project_name_signal.connect(self.on_listen_projname)
        self.ds_pf_path_signal.connect(self.on_listen_df_path)
        self.caseses_signal.connect(self.on_listen_casses)

        self.deactivate_result_tabs()
        
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

    def create_table_tab(self, title_text): 
        tab = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        
        backtoscenariolayout = QHBoxLayout()
        backtoscenariolayout.addStretch()
        backtoscenario = QPushButton("Kembali ke Scenario")
        backtoscenario.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        backtoscenario.clicked.connect(self.backcenario.emit)
        backtoscenariolayout.addWidget(backtoscenario)
        
        backtopltnlayout = QHBoxLayout()
        backtopltnlayout.addStretch()
        backtopltn = QPushButton("Kembali ke PLTN System")
        backtopltn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        backtopltn.clicked.connect(self.backpltn.emit)
        backtopltnlayout.addWidget(backtopltn)

        layout.addWidget(title)
        layout.addStretch(1)
        layout.addLayout(backtopltnlayout)
        layout.addLayout(backtoscenariolayout)
        layout.addStretch(2)

        label = QLabel(title_text)
        layout.addWidget(label)

        tab.setLayout(layout)
        return tab

    def deactivate_result_tabs(self):
        self.tabs.setTabEnabled(1, False)
        self.tabs.setTabEnabled(2, False)
        self.tabs.setTabEnabled(3, False)
        self.tabs.setTabEnabled(4, False)
    
    def activate_result_tabs(self):
        self.tabs.setTabEnabled(1, True)
        self.tabs.setTabEnabled(2, True)
        self.tabs.setTabEnabled(3, True)
        self.tabs.setTabEnabled(4, True)
    
    def on_listen_df_path(self, value):
        self.__df_path = value

    def on_listen_projname(self, value):
        self.__projectname = value
    
    def on_listen_casses(self, value):
        self.__caseses = value

"""
"Active Power": P
"Reactive Power (Q)": Q
"Generator Frequency (Hz)": m:fehz
"Bus Frequency (Hz)": n:fehz
"""