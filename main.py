from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QCheckBox,
    QVBoxLayout, QHBoxLayout, QGroupBox, QLabel,
    QPushButton, QListWidget, QLineEdit, QTextEdit, QComboBox,
    QTableWidget, QTableWidgetItem, QSpinBox, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread
import sys
import os
import pandas as pd

from module.qt_custom_style import *
from module.config_manager import *
from module.digsilent_pf import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class DetailLoadflowWindow(QMainWindow):
    def __init__(self, history_name, data, parent=None):
        super().__init__(parent)

        self.setWindowTitle(f"Detail - {history_name}")
        self.setGeometry(150, 100, 1000, 600)
        self.setMinimumSize(1000, 600)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = QGroupBox("Visualization")
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        fig = Figure(figsize=(12, 8))
        self.canvas = FigureCanvas(fig)
        left_layout.addWidget(self.canvas)
        self.ax1 = fig.add_subplot(2, 2, 1)
        self.ax2 = fig.add_subplot(2, 2, 2)
        self.ax3 = fig.add_subplot(2, 2, 3)
        self.ax4 = fig.add_subplot(2, 2, 4)
        fig.tight_layout(pad=8)

        self.plot_data(data)

        main_layout.addWidget(left_panel)

    def plot_data(self, data):
        bar_color = "#005a9e"
        rotation_angle = 90

        self.ax1.clear()
        self.ax1.bar(data["busslabel"], data["busvoltage"], color=bar_color)
        self.ax1.set_title("Bus Voltage (kA.)", fontsize=10)
        self.ax1.set_xlabel("Bus Name")
        self.ax1.set_ylabel("Voltage (p.u.)")
        self.ax1.tick_params(axis='x', rotation=rotation_angle)

        self.ax2.clear()
        self.ax2.bar(data["busslabel"],
                     data["busphasevoltage"], color=bar_color)
        self.ax2.set_title("Bus Phase Voltage (°)", fontsize=10)
        self.ax2.set_xlabel("Bus Name")
        self.ax2.set_ylabel("Angle (°)")
        self.ax2.tick_params(axis='x', rotation=rotation_angle)

        self.ax3.clear()
        self.ax3.bar(data["generatorlabel"],
                     data["generatoractivepower"], color=bar_color)
        self.ax3.set_title("Generator Active Power (MW)", fontsize=10)
        self.ax3.set_xlabel("Generator Name")
        self.ax3.set_ylabel("P (MW)")
        self.ax3.tick_params(axis='x', rotation=rotation_angle)

        self.ax4.clear()
        self.ax4.bar(data["generatorlabel"],
                     data["generatorreactivepower"], color=bar_color)
        self.ax4.set_title("Generator Reactive Power (MVAr)", fontsize=10)
        self.ax4.set_xlabel("Generator Name")
        self.ax4.set_ylabel("Q (MVAr)")
        self.ax4.tick_params(axis='x', rotation=rotation_angle)

        self.canvas.draw()


class DetailDynamicWindow(QMainWindow):
    def __init__(self, history_name="Loadflow", csv_path=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Detail - {history_name}")
        self.setGeometry(150, 100, 1200, 700)
        self.setMinimumSize(1200, 700)

        # Dataframe kosong (akan diisi dari CSV)
        self.data = pd.DataFrame()

        # Central widget dan layout utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        # ======================
        # PANEL KIRI: TABLE DATA
        # ======================
        left_panel = QGroupBox("Data Table")
        left_layout = QVBoxLayout()
        left_panel.setLayout(left_layout)

        # Table view
        self.table = QTableWidget()
        left_layout.addWidget(self.table)

        # ======================
        right_panel = QGroupBox("Visualization")
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        dropdown_layout = QHBoxLayout()
        dropdown_layout.addWidget(QLabel("Y Axis:"))
        self.y_selector = QComboBox()
        self.y_selector.currentTextChanged.connect(self.update_plot)
        dropdown_layout.addWidget(self.y_selector)
        right_layout.addLayout(dropdown_layout)

        self.fig = Figure(figsize=(8, 6))
        self.canvas = FigureCanvas(self.fig)
        self.ax = self.fig.add_subplot(111)
        right_layout.addWidget(self.canvas)

        main_layout.addWidget(left_panel, 4)
        main_layout.addWidget(right_panel, 6)

        if csv_path:
            self.load_csv(csv_path)
        else:
            pass

    def load_csv(self, path):
        try:
            df = pd.read_csv(path)
            self.on_csv_loaded(df)
        except Exception as e:
            self.on_csv_error(e)

    def on_csv_loaded(self, df):
        self.data = df

        if "Time_s" in self.data.columns:
            try:
                self.data["Time_s"] = self.data["Time_s"].astype(float)
            except Exception:
                pass

        self.update_table()
        self.y_selector.clear()
        if "Time_s" in self.data.columns:
            y_candidates = [c for c in self.data.columns if c != "Time_s"]
            self.y_selector.addItems(y_candidates)
        else:
            self.y_selector.addItems(self.data.columns)

        self.update_plot()

    def on_csv_error(self, err):
        print(f"❌ Error reading CSV: {err}")

    def update_table(self):
        df = self.data
        self.table.clear()
        self.table.setRowCount(len(df))
        self.table.setColumnCount(len(df.columns))
        self.table.setHorizontalHeaderLabels(df.columns)

        for i in range(len(df)):
            for j in range(len(df.columns)):
                item = QTableWidgetItem(str(df.iat[i, j]))
                self.table.setItem(i, j, item)

        self.table.resizeColumnsToContents()

    def update_plot(self):
        if self.data.empty:
            return

        if "Time_s" not in self.data.columns:
            self.ax.clear()
            self.ax.text(0.5, 0.5, "'Time_s' column not found!",
                         ha='center', va='center')
            self.canvas.draw()
            return

        y_col = self.y_selector.currentText()
        if not y_col:
            return

        try:
            x = self.data["Time_s"]
            y = self.data[y_col]
            self.ax.clear()
            self.ax.plot(x, y, color="#005a9e", linewidth=2)
            self.ax.set_title(f"{y_col} vs Time _s")
            self.ax.set_xlabel("Time (s)")
            self.ax.set_ylabel(y_col)
            self.ax.grid(True)
            self.canvas.draw()
        except Exception as e:
            print(f"Error plotting: {e}")


class NewConfigWindow(QMainWindow):
    """Window untuk membuat konfigurasi baru"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("New Configuration")
        self.setGeometry(200, 150, 500, 200)
        self.setMinimumSize(500, 200)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # DigSILENT Path
        layout.addWidget(QLabel("DigSILENT Path:"))
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText(
            "Select DigSILENT installation path...")
        path_layout.addWidget(self.path_input)

        browse_path_btn = QPushButton("Browse...")
        browse_path_btn.clicked.connect(self.browse_digsilent_path)
        path_layout.addWidget(browse_path_btn)
        layout.addLayout(path_layout)

        # Project Name
        layout.addWidget(QLabel("Project Name:"))
        self.project_input = QLineEdit()
        self.project_input.setPlaceholderText("Enter project name...")
        layout.addWidget(self.project_input)

        # Buttons
        btn_layout = QHBoxLayout()
        save_btn = QPushButton("Save Config")
        save_btn.clicked.connect(self.save_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(save_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def browse_digsilent_path(self):
        from PyQt5.QtWidgets import QFileDialog
        path = QFileDialog.getExistingDirectory(self, "Select DigSILENT Path")
        if path:
            self.path_input.setText(path)

    def save_config(self):
        digsilent_path = self.path_input.text()
        project_name = self.project_input.text()

        if not digsilent_path or not project_name:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Warning", "Please fill all fields!")
            return

        # Emit data ke parent window
        if self.parent():
            self.parent().set_config(digsilent_path, project_name)

        self.close()


class LoadConfigWindow(QMainWindow):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Load Existing Configuration")
        self.setGeometry(200, 150, 400, 300)
        self.setMinimumSize(400, 300)

        self.config = loadSanitizeSavedConfig(
            os.path.join(os.getcwd(), "config"))

        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        layout.addWidget(QLabel("Select Configuration:"))

        # List of existing configs
        self.config_list = QListWidget()
        self.config_list.addItems(self.config.keys())
        self.config_list.itemDoubleClicked.connect(self.load_selected_config)
        layout.addWidget(self.config_list)

        # Buttons
        btn_layout = QHBoxLayout()
        load_btn = QPushButton("Load")
        load_btn.clicked.connect(self.load_selected_config)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.close)

        btn_layout.addStretch()
        btn_layout.addWidget(load_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

    def load_selected_config(self):
        current_item = self.config_list.currentItem()
        try:
            if current_item:
                config_name = current_item.text()

                # Simulasi load config
                digsilent_path = loadConfig(self.config[config_name])[
                    "digsilentpath"]
                project_name = loadConfig(self.config[config_name])[
                    "projectname"]

                # Emit data ke parent window
                if self.parent():
                    self.parent().set_config(digsilent_path, project_name)

                self.close()
        except Exception as e:
            pass


class MainWindow(QMainWindow):
    ready_state_changed = pyqtSignal(bool)

    def __init__(self):
        super().__init__()

        self.loadflow_data = None
        self.ready_to_run = False
        self.dynamic_loadflow_res_file = None
        self.all_study_cases = []
        self.log_texts = []
        self.is_validated = False  # Track validation status

        self.setWindowTitle("HMI REAKTOR NUKLIR")
        self.setGeometry(100, 60, 1100, 640)
        self.setMinimumSize(1100, 640)
        self.setStyleSheet(CUSTOM_GLOBAL_STYLESHEET)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QHBoxLayout()
        self.left_layout = QVBoxLayout()
        self.center_layout = QVBoxLayout()
        self.right_layout = QVBoxLayout()

        self.central_widget.setLayout(self.main_layout)

        self.left_panel = QGroupBox("Running History")
        self.left_panel.setLayout(self.left_layout)

        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.on_history_item_clicked)
        self.left_layout.addWidget(self.history_list)

        # ========== CENTER PANEL ==========

        # Config Control Group
        self.config_group = QGroupBox("Config Control")
        self.config_layout = QVBoxLayout()
        self.config_group.setLayout(self.config_layout)

        # Sim time
        self.config_layout.addWidget(QLabel("Sim time [start, end]"))
        self.start_sim_spin = QSpinBox()
        self.start_sim_spin.setRange(0, 10000)
        self.start_sim_spin.setValue(0)
        self.start_sim_spin.valueChanged.connect(self.update_summary)

        self.stop_sim_spin = QSpinBox()
        self.stop_sim_spin.setRange(1, 10000)
        self.stop_sim_spin.setValue(100)
        self.stop_sim_spin.valueChanged.connect(self.update_summary)

        self.config_layout.addWidget(QLabel("Start Simulation (s):"))
        self.config_layout.addWidget(self.start_sim_spin)
        self.config_layout.addWidget(QLabel("Stop Simulation (s):"))
        self.config_layout.addWidget(self.stop_sim_spin)

        # Fault toggle
        self.toggle_usefault = QCheckBox("Using Fault Scenario")
        self.toggle_usefault.stateChanged.connect(self.on_toggle_fault_changed)
        self.config_layout.addWidget(self.toggle_usefault)

        # Fault time
        self.config_layout.addWidget(QLabel("Fault time [start, end]"))
        self.start_fault_spin = QSpinBox()
        self.start_fault_spin.setRange(0, 10000)
        self.start_fault_spin.setValue(0)
        self.start_fault_spin.valueChanged.connect(self.update_summary)

        self.stop_fault_spin = QSpinBox()
        self.stop_fault_spin.setRange(0, 10000)
        self.stop_fault_spin.setValue(1)
        self.stop_fault_spin.valueChanged.connect(self.update_summary)

        self.config_layout.addWidget(QLabel("Start Fault (s):"))
        self.config_layout.addWidget(self.start_fault_spin)
        self.config_layout.addWidget(QLabel("Stop Fault (s):"))
        self.config_layout.addWidget(self.stop_fault_spin)

        # Summary label
        self.summary_label = QLabel("")
        self.summary_label.setStyleSheet("font-weight: bold; color: #0078D7;")
        self.config_layout.addWidget(self.summary_label)

        # Start Simulation Button
        self.start_sim_btn = QPushButton("Start Simulation")
        self.start_sim_btn.clicked.connect(self.on_run_button)
        self.config_layout.addWidget(self.start_sim_btn)

        self.center_layout.addWidget(self.config_group, 3)

        # --- Log History Group ---
        self.log_group = QGroupBox("Log History")
        self.log_layout = QVBoxLayout()
        self.log_group.setLayout(self.log_layout)

        self.log_text = QTextEdit()
        self.log_text.setPlaceholderText("Simulation logs will appear here...")
        self.log_text.setReadOnly(True)
        self.log_layout.addWidget(self.log_text)

        self.center_layout.addWidget(self.log_group, 3)

        # --- Search Box ---
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Search log query...")
        self.center_layout.addWidget(self.search_box, 1)

        # ========== RIGHT PANEL ==========

        # --- Scenario Options Group ---
        self.skenario_group = QGroupBox("Scenario Options")
        self.skenario_layout = QVBoxLayout()
        self.skenario_group.setLayout(self.skenario_layout)

        self.scenario_combobox = QComboBox()
        self.scenario_combobox.addItems(["Load Flow", "Dynamic Simulation"])
        self.scenario_combobox.currentTextChanged.connect(
            self.on_scenario_changed)
        self.cases_combobox = QComboBox()

        self.skenario_layout.addWidget(QLabel("Set Your Scenario Simulation"))
        self.skenario_layout.addWidget(self.scenario_combobox)
        self.skenario_layout.addWidget(QLabel("Set Your Cases from Project"))
        self.skenario_layout.addWidget(self.cases_combobox)

        self.right_layout.addWidget(self.skenario_group)

        # --- Connect And Load Config Group (MOVED TO TOP) ---
        self.display_group = QGroupBox("Connect And Load Config")
        self.display_layout = QVBoxLayout()
        self.display_group.setLayout(self.display_layout)

        # New Config Button
        self.new_config_btn = QPushButton("New Config")
        self.new_config_btn.clicked.connect(self.on_new_config_clicked)
        self.display_layout.addWidget(self.new_config_btn)

        # Exist Load Config Button
        self.load_config_btn = QPushButton("Exist Load Config")
        self.load_config_btn.clicked.connect(self.on_load_config_clicked)
        self.display_layout.addWidget(self.load_config_btn)

        # Config Info Display
        self.display_layout.addWidget(QLabel("DigSILENT Path:"))
        self.digsilent_path_label = QLabel("-")
        self.digsilent_path_label.setStyleSheet(
            "padding-left: 10px; color: #666;")
        self.display_layout.addWidget(self.digsilent_path_label)

        self.display_layout.addWidget(QLabel("Project Name:"))
        self.project_name_label = QLabel("-")
        self.project_name_label.setStyleSheet(
            "padding-left: 10px; color: #666;")
        self.display_layout.addWidget(self.project_name_label)

        # Validate Button
        self.validate_btn = QPushButton("Validate")
        self.validate_btn.clicked.connect(self.on_validate_clicked)
        self.display_layout.addWidget(self.validate_btn)

        self.right_layout.addWidget(self.display_group)

        # ========== ASSEMBLE MAIN LAYOUT ==========
        self.main_layout.addWidget(self.left_panel)
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.right_layout)

        # ========== INITIALIZE STATE ==========
        self.detail_windows = []
        self.initialize_ui_state()

        self.ready_state_changed.connect(self.on_ready_state_changed)

    def initialize_ui_state(self):
        """Initialize UI state - disable everything until validation"""
        # Disable scenario selection until validated
        self.scenario_combobox.setEnabled(False)
        self.cases_combobox.setEnabled(False)

        # Disable all simulation fields
        self.disable_simulation_fields()

        # Update summary
        self.update_summary()

    def disable_simulation_fields(self):
        """Nonaktifkan semua input simulasi dan fault"""
        self.start_sim_spin.setEnabled(False)
        self.stop_sim_spin.setEnabled(False)
        self.toggle_usefault.setEnabled(False)
        self.start_fault_spin.setEnabled(False)
        self.stop_fault_spin.setEnabled(False)
        self.start_sim_btn.setEnabled(False)

    def enable_simulation_fields(self):
        """Aktifkan input simulasi dan toggle fault (fault time masih disabled)"""
        self.start_sim_spin.setEnabled(True)
        self.stop_sim_spin.setEnabled(True)
        self.toggle_usefault.setEnabled(True)
        # Fault time tetap disabled sampai checkbox dicentang
        self.start_fault_spin.setEnabled(False)
        self.stop_fault_spin.setEnabled(False)
        self.start_sim_btn.setEnabled(True)

    def validate_inputs(self):
        """Validasi input sesuai rule #4"""
        start_sim = self.start_sim_spin.value()
        stop_sim = self.stop_sim_spin.value()
        start_fault = self.start_fault_spin.value()
        stop_fault = self.stop_fault_spin.value()

        if start_sim >= stop_sim:
            QMessageBox.warning(
                self, "Invalid Input", "Start Simulation must be less than Stop Simulation.")
            return False

        if self.toggle_usefault.isChecked():
            if not (start_sim < start_fault < stop_sim):
                QMessageBox.warning(
                    self, "Invalid Input", "Start Fault must be between Start and Stop Simulation.")
                return False
            if stop_fault >= stop_sim:
                QMessageBox.warning(
                    self, "Invalid Input", "Stop Fault must be less than Stop Simulation.")
                return False
        return True

    def on_toggle_fault_changed(self, state):
        is_checked = self.toggle_usefault.isChecked()
        self.start_fault_spin.setEnabled(is_checked)
        self.stop_fault_spin.setEnabled(is_checked)
        self.update_summary()

    def update_summary(self):
        scenario = self.scenario_combobox.currentText()

        if scenario == "Load Flow":
            self.summary_label.setText(f"Scenario: {scenario}")
        else:  # Dynamic Simulation
            start_sim = self.start_sim_spin.value()
            stop_sim = self.stop_sim_spin.value()
            summary = f"Scenario: {scenario} | Duration: {stop_sim - start_sim}s"

            if self.toggle_usefault.isChecked():
                start_fault = self.start_fault_spin.value()
                stop_fault = self.stop_fault_spin.value()
                fault_dur = stop_fault - start_fault
                summary += f" | Fault: {start_fault}-{stop_fault}s ({fault_dur}s)"

            self.summary_label.setText(summary)

    def on_ready_state_changed(self):
        self.start_sim_btn.setEnabled(self.ready_to_run)
        self.toggle_usefault.setEnabled(self.ready_to_run)

    def refresh_result(self):
        data_path = "./data"
        
        os.path.abspath(data_path)

        hist_list = os.listdir(data_path)
        print(hist_list)

        self.history_list.clear()

        self.history_list.addItems(hist_list)
    
    def append_log(self, message: str):
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")

    def on_history_item_clicked(self, item):
        history_name = os.path.join(os.getcwd(), "data", item.text())
        import json
        if ".json" in history_name:
            print(history_name)
            with open(history_name, "r") as file:
                data_dict = json.load(file)
            detail_window = DetailLoadflowWindow("Load Flow Simulation", data_dict, self)
            detail_window.show()
            self.detail_windows.append(detail_window)
        else:
            detail_window = DetailDynamicWindow("Dynamic Simulation", history_name, self)
            detail_window.show()
            self.detail_windows.append(detail_window)

    def on_scenario_changed(self, text):
        """Handler ketika scenario berubah - atur enable/disable fields"""
        if not self.is_validated:
            return  # Jangan lakukan apa-apa jika belum validated

        if text == "Load Flow":
            # Load Flow: semua field simulasi disabled
            self.disable_simulation_fields()
            # Enable tombol run saja
            self.start_sim_btn.setEnabled(True)
        elif text == "Dynamic Simulation":
            # Dynamic Simulation: semua field aktif
            self.enable_simulation_fields()

        self.update_summary()

    def on_new_config_clicked(self):
        """Handler untuk tombol New Config"""
        new_config_window = NewConfigWindow(self)
        new_config_window.show()

    def on_load_config_clicked(self):
        """Handler untuk tombol Exist Load Config"""
        load_config_window = LoadConfigWindow(self)
        load_config_window.show()

    def set_config(self, digsilent_path, project_name):
        """Method untuk menerima config dari child windows"""
        self.digsilent_path_label.setText(digsilent_path)
        self.project_name_label.setText(project_name)

        if hasattr(self, 'log_text'):
            self.append_log(f"[INFO] Config loaded:")
            self.append_log(f"[INFO] DigSILENT Path: {digsilent_path}")
            self.append_log(f"[INFO] Project Name: {project_name}")

    def on_validate_clicked(self):
        digsilent_path = self.digsilent_path_label.text()
        project_name = self.project_name_label.text()
        import subprocess

        if digsilent_path == "-" or project_name == "-":
            QMessageBox.warning(
                self, "Warning", "Please load or create a config first!"
            )
            return

        self.append_log("[INFO] Starting validation of DIgSILENT PowerFactory configuration...")

        try:
            process = subprocess.Popen(
                [
                    "python",
                    "worker_connectandsetup.py",
                    "--digsilent_path", digsilent_path,
                    "--project_name", project_name
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()
            
            print("=== STDOUT ===")
            print(stdout)
            print("=== STDERR ===")
            print(stderr)

            if stderr.strip():
                self.append_log(f"[ERROR] {stderr.strip()}")
                QMessageBox.critical(self, "Error", stderr.strip())
                self.is_validated = False
                return

            parts = stdout.strip().split("|")
            if len(parts) >= 3 and parts[0] == "SUCCESS":
                message = parts[1]
                study_cases = parts[2].split(",") if parts[2] else []

                self.on_validate_success(message)
                self.all_study_cases = study_cases
                self.cases_combobox.clear()
                self.cases_combobox.addItems(study_cases)

                self.is_validated = True
                self.scenario_combobox.setEnabled(True)
                self.cases_combobox.setEnabled(True)
                self.on_scenario_changed(self.scenario_combobox.currentText())

            elif len(parts) >= 2 and parts[0] == "ERROR":
                message = parts[1]
                self.on_validate_error(message)
                self.is_validated = False
            else:
                self.append_log(f"[ERROR] Unexpected worker response: {stdout}")
                QMessageBox.critical(self, "Error", f"Unexpected output:\n{stdout}")
                self.is_validated = False

        except Exception as e:
            self.append_log(f"[EXCEPTION] {str(e)}")
            QMessageBox.critical(self, "Exception", str(e))
            self.is_validated = False

    def on_validate_success(self, message: str):
        """Dipanggil kalau validasi PowerFactory berhasil"""
        self.append_log(f"[INFO] Validation completed: {message}")
        self.refresh_result()
        QMessageBox.information(
            self, "Success", "Configuration validated successfully! You can now select scenario and case."
        )

    def on_validate_error(self, message: str):
        """Dipanggil kalau validasi gagal"""
        self.append_log(f"[ERROR] Validation failed: {message}")
        QMessageBox.critical(self, "Error", f"Validation failed:\n{message}")

    def on_run_button(self):
        if self.scenario_combobox.currentText() == "Dynamic Simulation":
            if not self.validate_inputs():
                return

        import subprocess

        if (self.scenario_combobox.currentText() == "Load Flow"):
            digsilent_path = self.digsilent_path_label.text()
            project_name = self.project_name_label.text()
            case_name = self.cases_combobox.currentText()

            print("Starting PowerFactory loadflow process...")

            process = subprocess.Popen(
                [
                    "python.exe",
                    "worker_runloadflow.py",
                    "--digsilent_path", digsilent_path,
                    "--proj_name", project_name,
                    "--case_name", case_name,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            print("=== STDOUT ===")
            print(stdout)
            print("=== STDERR ===")
            print(stderr)

            lines = [line.strip()
                     for line in stdout.splitlines() if line.strip()]
            status = False
            data = ""

            if len(lines) >= 2:
                if lines[0] == "SUCCESS":
                    status = True
                    data = lines[1]
                elif lines[0] == "FAILED":
                    status = False
                    data = lines[1]

            if status:
                self.log_text.append("[SUCCESS] Success running loadflow")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.information(
                    self, "Success", f"Success running loadflow\n\n{data}")
                self.loadflow_data = data
                self.refresh_result()
            else:
                self.log_text.append(
                    f"[ERROR] Failed running loadflow: {data}")
                from PyQt5.QtWidgets import QMessageBox
                QMessageBox.critical(
                    self, "Error", f"Error running loadflow:\n\n{data}")

        elif self.scenario_combobox.currentText() == "Dynamic Simulation":
            start_sim = self.start_sim_spin.value()
            stop_sim = self.stop_sim_spin.value()
            isusing_fault = self.toggle_usefault.isChecked()
            start_fault = self.start_fault_spin.value()
            stop_fault = self.stop_fault_spin.value()

            digsilent_path = self.digsilent_path_label.text()
            project_name = self.project_name_label.text()

            args = [
                "python",
                "worker_dynamic.py",
                "--digsilent_path", digsilent_path,
                "--project_name", project_name,
                "--start_time", str(start_sim),
                "--stop_time", str(stop_sim)
            ]
            
            if isusing_fault:
                args += [
                    "--start_fault", str(start_fault),
                    "--clear_fault", str(stop_fault)
                ]

            from PyQt5.QtWidgets import QMessageBox
            import subprocess

            process = subprocess.Popen(
                args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            stdout, stderr = process.communicate()

            if process.returncode != 0 or stderr:
                self.log_text.append(f"[ERROR] {stderr.strip()}")
                QMessageBox.critical(self, "Error", stderr.strip())
            else:
                self.log_text.append(stdout.strip())
                self.refresh_result()
                QMessageBox.information(self, "Success", stdout.strip())

        else:
            print(self.scenario_combobox.currentText())
        print("Finished....")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    sys.exit(1)
