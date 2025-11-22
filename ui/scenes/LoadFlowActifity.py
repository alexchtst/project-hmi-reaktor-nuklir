from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QTabWidget,
    QPushButton, QListWidget, QTableWidgetItem, QMessageBox, QTableWidget,
    QComboBox
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.CasescardUI import CaseCardUI
from ui.LoadflowProcessDialogUI import LoadflowProcessDialogUI

from ui.UIStyle import (
    PLTN_SYSTEM_TITLE_STYLESHEET, FINDPATH_BUTTON_STYLESHEET
)

class LoadflowActifityScreenScene(QWidget):
    backcenario = pyqtSignal()
    backpltn = pyqtSignal()
    project_name_signal = pyqtSignal(str)
    ds_pf_path_signal = pyqtSignal(str)
    caseses_signal = pyqtSignal(list)
    resultisready = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        self.layout = QVBoxLayout()
        
        self.__isdata_ready = False
        self.__df_path = None
        self.__projectname = None
        self.__caseses = []
        self.__selected_case = None
        
        self.project_name_signal.connect(self.on_listen_projname)
        self.ds_pf_path_signal.connect(self.on_listen_df_path)
        self.caseses_signal.connect(self.on_listen_casses)
        
        self.tabs = QTabWidget()
        
        # tab running and general info
        self.tab_gen_info_widget, self.tab_gen_info_layout = self.create_tab("Simulasi Loadflow")
        
        self.card_widget = CaseCardUI(
            title="No Cases",
        )
        
        self.cases_combo_box = QComboBox()
        self.cases_combo_box.addItems(self.__caseses)
        self.cases_combo_box.currentTextChanged.connect(self.on_update_cases)
        
        self.run_loadflow_btn = QPushButton("Run Load Flow")
        self.run_loadflow_btn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        self.run_loadflow_btn.clicked.connect(self.clicked_run_loadflow_handler)
        
        self.card_widget.card_layout.addWidget(self.cases_combo_box)
        self.card_widget.card_layout.addWidget(self.run_loadflow_btn)
        
        navigationlayout = QHBoxLayout()
        
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
        
        navigationlayout.addStretch(1)
        navigationlayout.addLayout(backtopltnlayout)
        navigationlayout.addLayout(backtoscenariolayout)
        
        self.tab_gen_info_layout.addWidget(self.card_widget)
        self.tab_gen_info_layout.addStretch(1)
        self.tab_gen_info_layout.addLayout(navigationlayout)
        
        # tab bus volate
        self.tab_bus_volatage_widget, self.tab_bus_volatage_layout = self.create_tab("Bus Voltage")
        # tab bus phasevolate
        self.tab_bus_phasevolatage_widget, self.tab_bus_phasevolatage_layout = self.create_tab("Bus Phasevoltage")
        # tab generator active power
        self.tab_gen_activepow_widget, self.tab_gen_activepow_layout = self.create_tab("Generator Active Power")
        # tab generator reactive power
        self.tab_gen_reactivepow_widget, self.tab_gen_reactivepow_layout = self.create_tab("Generator Reactive Power")
        
        self.tabs.addTab(self.tab_gen_info_widget, "Simulasi")
        self.tabs.addTab(self.tab_bus_volatage_widget, "Bus Voltage")
        self.tabs.addTab(self.tab_bus_phasevolatage_widget, "Bus Phasevoltage")
        self.tabs.addTab(self.tab_gen_activepow_widget, "Generator Active Power")
        self.tabs.addTab(self.tab_gen_reactivepow_widget, "Generator Reactive Power")

        self.deactivate_result_tabs()
        
        self.layout.addWidget(self.tabs)

        self.setLayout(self.layout)

    def create_tab(self, title_text):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        layout.addWidget(title)
        tab.setLayout(layout)
        layout.addStretch(1)
        return tab, layout

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
        print("="*10, value)
        self.__projectname = value
    
    def on_listen_casses(self, value):
        self.__caseses = value
        self.cases_combo_box.clear()
        self.cases_combo_box.addItems(self.__caseses)
    
    def on_update_cases(self, value):
        self.__selected_case = value
        self.card_widget.update_card(value)
    
    def clicked_run_loadflow_handler(self):
        df_path = self.__df_path
        projname = self.__projectname
        case = self.__selected_case
        
        print(df_path, projname, case)
        
        self.progress_dialog = LoadflowProcessDialogUI(
            ds_pf_pathfle=df_path,
            proj_name=projname,
            case_name=case
        )
        self.progress_dialog.show()