from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton,
    QTabWidget, QComboBox,
    QHBoxLayout,
)
from PyQt5.QtCore import Qt, pyqtSignal

from ui.CasescardUI import CaseCardUI
from ui.DynamicHistoryDialogUI import DynamicHistoryDialogUI
from ui.RunDynamicConfigUI import RunDynamicConfigUI
from ui.GraphicalUI import GraphicalVisualization
from ui.CasescardUI import CaseCardUI
from ui.UIStyle import (
    PLTN_SYSTEM_TITLE_STYLESHEET, FINDPATH_BUTTON_STYLESHEET,
    CASES_COMBO_BOX_STYLESHEET
)


class DynamicActifityScreenScene(QWidget):
    backcenario = pyqtSignal()
    backpltn = pyqtSignal()
    project_name_signal = pyqtSignal(str)
    ds_pf_path_signal = pyqtSignal(str)
    caseses_signal = pyqtSignal(list)
    casesesevent_signal = pyqtSignal(dict)
    resultisready = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.__isdata_ready = False
        self.data_tobe_showed = None
        self.__df_path = None
        self.__projectname = None
        self.__caseses = []
        self.__selected_case = None
        
        self.__eventcases = None

        self.tabs = QTabWidget()
        # tab running and general info
        self.tab_gen_info_widget, self.tab_gen_info_layout = self.create_table_tab(
            "Simulasi Dinamis")
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

        self.card_widget = CaseCardUI(
            title="No Cases",
        )
        self.cases_combo_box = QComboBox()
        self.cases_combo_box.addItems(self.__caseses)
        self.cases_combo_box.setStyleSheet(CASES_COMBO_BOX_STYLESHEET)
        self.cases_combo_box.currentTextChanged.connect(self.on_update_cases)

        self.run_loadflow_btn = QPushButton("Dynamic Simulation")
        self.run_loadflow_btn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        self.run_loadflow_btn.clicked.connect(
            self.clicked_dynamic_configuration)

        self.existing_loadflow_data = QPushButton("Existing Running Data")
        self.existing_loadflow_data.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        self.existing_loadflow_data.clicked.connect(
            self.clicked_history_handler)

        self.card_widget.card_layout.addWidget(self.cases_combo_box)
        self.card_widget.card_layout.addWidget(self.existing_loadflow_data)
        self.card_widget.card_layout.addWidget(self.run_loadflow_btn)

        self.tab_gen_info_layout.addWidget(self.card_widget)
        self.tab_gen_info_layout.addStretch(1)
        self.tab_gen_info_layout.addLayout(navigationlayout)

        # tab bus volate
        self.tab_active_pow_widget, self.tab_active_pow_layout = self.create_table_tab(
            "Active Power")
        # tab bus phasevolate
        self.tab_reactive_pow_widget, self.tab_reactive_pow_layout = self.create_table_tab(
            "Reactive Power")
        # tab generator active power
        self.tab_gen_freq_widget, self.tab_gen_freq_layout = self.create_table_tab(
            "Generator Frequency")
        # tab generator reactive power
        self.tab_bus_freq_widget, self.tab_bus_freq_layout = self.create_table_tab(
            "Bus Frequency")

        self.tabs.addTab(self.tab_gen_info_widget, "Simulasi")
        self.tabs.addTab(self.tab_active_pow_widget, "Active Power")
        self.tabs.addTab(self.tab_reactive_pow_widget, "Reactive Power")
        self.tabs.addTab(self.tab_gen_freq_widget, "Generator Frequency")
        self.tabs.addTab(self.tab_bus_freq_widget, "Bus Frequency")

        self.project_name_signal.connect(self.on_listen_projname)
        self.ds_pf_path_signal.connect(self.on_listen_df_path)
        self.caseses_signal.connect(self.on_listen_casses)
        self.casesesevent_signal.connect(self.on_listen_cassesevent)

        self.deactivate_result_tabs()
        self.resultisready.connect(self.on_israady_change)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    def create_table_tab(self, title_text):
        tab = QWidget()
        layout = QVBoxLayout()
        title = QLabel(title_text)
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        layout.addWidget(title)
        tab.setLayout(layout)
        layout.addStretch(1)
        return tab, layout

    def clear_layout(self, layout):
        if layout is None:
            return

        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                sub_layout = item.layout()
                if sub_layout is not None:
                    self.clearLayout(sub_layout)

    def set_visualization(self):
        viz_tab_active_pow = GraphicalVisualization()
        viz_tab_active_pow.load_from_csv_multi_included(
            self.data_tobe_showed, x_col="Time_s", include_patterns=["m_Q_"]
        )
        viz_tab_active_pow.plot_multiline(
            x_label="time (s)", y_label="Active Power", legend=True
        )
        self.clear_layout(self.tab_active_pow_layout)
        title = QLabel("Active Power")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        self.tab_active_pow_layout.addWidget(title)
        self.tab_active_pow_widget.setLayout(self.tab_active_pow_layout)
        self.tab_active_pow_layout.addWidget(viz_tab_active_pow)
        self.tab_active_pow_layout.addStretch(1)
        
        viz_tab_reactive_pow = GraphicalVisualization()
        viz_tab_reactive_pow.load_from_csv_multi_included(
            self.data_tobe_showed, x_col="Time_s", include_patterns=["m_P_"]
        )
        viz_tab_reactive_pow.plot_multiline(
            x_label="time (s)", y_label="Reactive Power", legend=True
        )
        self.clear_layout(self.tab_reactive_pow_layout)
        title = QLabel("Reactive Power")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        self.tab_reactive_pow_layout.addWidget(title)
        self.tab_reactive_pow_widget.setLayout(self.tab_reactive_pow_layout)
        self.tab_reactive_pow_layout.addWidget(viz_tab_reactive_pow)
        self.tab_reactive_pow_layout.addStretch(1)

        viz_tab_gen_freq = GraphicalVisualization()
        viz_tab_gen_freq.load_from_csv_multi_included(
            self.data_tobe_showed, x_col="Time_s", include_patterns=["n_fehz"]
        )
        viz_tab_gen_freq.plot_multiline(
            x_label="time (s)", y_label="Generator Frequency", legend=True
        )
        self.clear_layout(self.tab_gen_freq_layout)
        title = QLabel("Generator Frequency")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        self.tab_gen_freq_layout.addWidget(title)
        self.tab_gen_freq_widget.setLayout(self.tab_gen_freq_layout)
        self.tab_gen_freq_layout.addWidget(viz_tab_gen_freq)
        self.tab_gen_freq_layout.addStretch(1)

        viz_tab_bus_freq = GraphicalVisualization()
        viz_tab_bus_freq.load_from_csv_multi_included(
            self.data_tobe_showed, x_col="Time_s", include_patterns=["m_fehz"]
        )
        viz_tab_bus_freq.plot_multiline(
            x_label="time (s)", y_label="Bus Frequency", legend=True
        )
        self.clear_layout(self.tab_bus_freq_layout)
        title = QLabel("Bus Frequency")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet(PLTN_SYSTEM_TITLE_STYLESHEET)
        self.tab_bus_freq_layout.addWidget(title)
        self.tab_bus_freq_widget.setLayout(self.tab_bus_freq_layout)
        self.tab_bus_freq_layout.addWidget(viz_tab_bus_freq)
        self.tab_bus_freq_layout.addStretch(1)


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
        self.cases_combo_box.clear()
        self.cases_combo_box.addItems(self.__caseses)
    
    def on_listen_cassesevent(self, value):
        self.__eventcases = value

    def on_update_cases(self, value):
        self.__selected_case = value
        self.card_widget.update_card(value)

    def on_data_received(self, value):
        if value is not None:
            self.data_tobe_showed = value
            self.__isdata_ready = True
        else:
            self.__isdata_ready = False

        self.resultisready.emit()

    def clicked_history_handler(self):
        self.loadhistory = DynamicHistoryDialogUI()
        self.loadhistory.datareading.connect(self.on_data_received)
        self.loadhistory.show()

    def clicked_dynamic_configuration(self):
        self.dynamiconfig = RunDynamicConfigUI(
            ds_pf_pathfile=self.__df_path,
            proj_name=self.__projectname,
            case_name=self.__selected_case,
            event_cases=self.__eventcases
        )
        self.dynamiconfig.show()

    def on_israady_change(self):
        if (self.__isdata_ready):
            self.set_visualization()
            self.activate_result_tabs()
        else:
            self.deactivate_result_tabs()
