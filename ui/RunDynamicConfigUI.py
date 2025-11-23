from PyQt5.QtWidgets import (
    QDialog, QPushButton, QLabel, 
    QHBoxLayout, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox,
    QWidget, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from ui.UIStyle import FINDPATH_BUTTON_STYLESHEET

class FaultConfigDialog(QDialog):
    """Dialog untuk konfigurasi fault pada komponen"""
    
    def __init__(self, component_name, parent=None):
        super().__init__(parent)
        self.component_name = component_name
        self.fault_config = {}
        
        self.setWindowTitle(f"Fault Configuration - {component_name}")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(400)
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Header
        header = QLabel(f"Configure Fault for: {self.component_name}")
        header.setStyleSheet("font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)
        
        # Form layout untuk konfigurasi
        form_layout = QFormLayout()
        
        # Start Fault Time
        self.start_fault_spin = QDoubleSpinBox()
        self.start_fault_spin.setRange(0, 1000)
        self.start_fault_spin.setValue(1.0)
        self.start_fault_spin.setSuffix(" s")
        self.start_fault_spin.setDecimals(3)
        form_layout.addRow("Start Fault Time:", self.start_fault_spin)
        
        # Clear Fault Time
        self.clear_fault_spin = QDoubleSpinBox()
        self.clear_fault_spin.setRange(0, 1000)
        self.clear_fault_spin.setValue(1.5)
        self.clear_fault_spin.setSuffix(" s")
        self.clear_fault_spin.setDecimals(3)
        form_layout.addRow("Clear Fault Time:", self.clear_fault_spin)
        
        # Fault Type
        self.fault_type_combo = QComboBox()
        self.fault_type_combo.addItems([
            "3-Phase",
            "Line-to-Ground (LG)",
            "Line-to-Line (LL)",
            "Line-to-Line-to-Ground (LLG)",
            "Double Line-to-Ground"
        ])
        form_layout.addRow("Fault Type:", self.fault_type_combo)
        
        # Fault Impedance
        self.fault_impedance_spin = QDoubleSpinBox()
        self.fault_impedance_spin.setRange(0, 100)
        self.fault_impedance_spin.setValue(0.0)
        self.fault_impedance_spin.setSuffix(" Ω")
        self.fault_impedance_spin.setDecimals(3)
        form_layout.addRow("Fault Impedance:", self.fault_impedance_spin)
        
        layout.addLayout(form_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton("Save")
        save_btn.setFixedWidth(100)
        save_btn.clicked.connect(self.save_config)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedWidth(100)
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def save_config(self):
        """Simpan konfigurasi fault"""
        start_time = self.start_fault_spin.value()
        clear_time = self.clear_fault_spin.value()
        
        if clear_time <= start_time:
            QMessageBox.warning(self, "Invalid Configuration", 
                              "Clear fault time must be greater than start fault time!")
            return
        
        self.fault_config = {
            'start_time': start_time,
            'clear_time': clear_time,
            'fault_type': self.fault_type_combo.currentText(),
            'impedance': self.fault_impedance_spin.value()
        }
        
        self.accept()
    
    def get_config(self):
        """Ambil konfigurasi fault"""
        return self.fault_config


class RunDynamicConfigUI(QDialog):
    datareading = pyqtSignal(str)
    simulation_started = pyqtSignal(dict)  # Signal untuk mulai simulasi
    
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Run Dynamic Simulation")
        self.setWindowIcon(QIcon(r"C:\Users\Alex\NgodingDulu\project-hmi-nuklir-new\asset\logo-ugm.jpg"))
        self.setFixedWidth(900)
        self.setFixedHeight(600)
        self.shc_data = {}
        self.fault_configs = {}  # Menyimpan konfigurasi fault untuk setiap komponen
        
        self.setWindowModality(Qt.ApplicationModal)
        
        self.data_folder = r"C:\Users\Alex\NgodingDulu\hmi-reactor-nuklir\data"
        
        self.setup_ui()
        
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Header
        header_label = QLabel("Dynamic Simulation Configuration")
        header_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header_label)
        
        # Simulation Settings Group
        sim_group = QGroupBox("Simulation Settings")
        sim_layout = QFormLayout()
        
        # Start Time
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(0, 1000)
        self.start_time_spin.setValue(0.0)
        self.start_time_spin.setSuffix(" s")
        self.start_time_spin.setDecimals(3)
        sim_layout.addRow("Start Time:", self.start_time_spin)
        
        # Stop Time
        self.stop_time_spin = QDoubleSpinBox()
        self.stop_time_spin.setRange(0, 1000)
        self.stop_time_spin.setValue(10.0)
        self.stop_time_spin.setSuffix(" s")
        self.stop_time_spin.setDecimals(3)
        sim_layout.addRow("Stop Time:", self.stop_time_spin)
        
        # Time Step
        self.time_step_spin = QDoubleSpinBox()
        self.time_step_spin.setRange(0.001, 1)
        self.time_step_spin.setValue(0.01)
        self.time_step_spin.setSuffix(" s")
        self.time_step_spin.setDecimals(4)
        sim_layout.addRow("Time Step:", self.time_step_spin)
        
        sim_group.setLayout(sim_layout)
        main_layout.addWidget(sim_group)
        
        # Components and Fault Events Group
        events_group = QGroupBox("Fault Events Configuration")
        events_layout = QVBoxLayout()
        
        # Table untuk komponen
        self.components_table = QTableWidget()
        self.components_table.setColumnCount(4)
        self.components_table.setHorizontalHeaderLabels([
            "Component Type", "Component Name", "Fault Configured", "Action"
        ])
        
        # Set column widths
        header = self.components_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        
        self.components_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.components_table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        # Populate dengan contoh data
        self.populate_components_table()
        
        events_layout.addWidget(self.components_table)
        events_group.setLayout(events_layout)
        main_layout.addWidget(events_group)
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        run_btn = QPushButton("Run Simulation")
        run_btn.clicked.connect(self.run_simulation)
        run_btn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        button_layout.addWidget(run_btn)
        close_btn = QPushButton("Close")
        close_btn.setStyleSheet(FINDPATH_BUTTON_STYLESHEET)
        close_btn.clicked.connect(self.reject)
        button_layout.addWidget(close_btn)
        main_layout.addLayout(button_layout)
        self.setLayout(main_layout)
    
    def populate_components_table(self):
        components = [
            ("Bus", "Bus 1"),
            ("Bus", "Bus 2"),
            ("Bus", "Bus 3"),
            ("Line", "Line 1-2"),
            ("Line", "Line 2-3"),
            ("Line", "Line 1-3"),
        ]
        
        self.components_table.setRowCount(len(components))
        
        for row, (comp_type, comp_name) in enumerate(components):
            type_item = QTableWidgetItem(comp_type)
            self.components_table.setItem(row, 0, type_item)
            
            name_item = QTableWidgetItem(comp_name)
            self.components_table.setItem(row, 1, name_item)
            
            status_item = QTableWidgetItem("No")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.components_table.setItem(row, 2, status_item)
            
            self.create_action_buttons(row)
    
    def configure_fault(self, row):
        """Buka dialog konfigurasi fault untuk komponen tertentu"""
        comp_type = self.components_table.item(row, 0).text()
        comp_name = self.components_table.item(row, 1).text()
        
        dialog = FaultConfigDialog(f"{comp_type}: {comp_name}", self)
        
        # Load existing config if available
        key = f"{comp_type}_{comp_name}"
        if key in self.fault_configs:
            config = self.fault_configs[key]
            dialog.start_fault_spin.setValue(config['start_time'])
            dialog.clear_fault_spin.setValue(config['clear_time'])
            dialog.fault_type_combo.setCurrentText(config['fault_type'])
            dialog.fault_impedance_spin.setValue(config['impedance'])
        
        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()
            self.fault_configs[key] = config
            
            # Update status dan buttons
            self.update_row_status(row, True)
    
    def create_action_buttons(self, row):
        """Buat tombol aksi untuk setiap baris"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)
        
        # Configure Button
        config_btn = QPushButton("Configure")
        config_btn.setFixedWidth(85)
        config_btn.clicked.connect(lambda checked, r=row: self.configure_fault(r))
        layout.addWidget(config_btn)
        
        # Remove Button
        remove_btn = QPushButton("Remove")
        remove_btn.setFixedWidth(75)
        remove_btn.clicked.connect(lambda checked, r=row: self.remove_fault_config(r))
        remove_btn.setEnabled(False)  # Disabled by default
        layout.addWidget(remove_btn)
        
        widget.setLayout(layout)
        self.components_table.setCellWidget(row, 3, widget)
    
    def update_row_status(self, row, configured):
        """Update status baris dan enable/disable tombol"""
        status_item = self.components_table.item(row, 2)
        
        if configured:
            status_item.setText("Yes")
            status_item.setForeground(Qt.darkGreen)
        else:
            status_item.setText("No")
            status_item.setForeground(Qt.black)
        
        # Update button states
        widget = self.components_table.cellWidget(row, 3)
        if widget:
            buttons = widget.findChildren(QPushButton)
            if len(buttons) >= 2:
                remove_btn = buttons[1]  # Remove button is second
                remove_btn.setEnabled(configured)
    
    def remove_fault_config(self, row):
        """Hapus konfigurasi fault dari komponen"""
        comp_type = self.components_table.item(row, 0).text()
        comp_name = self.components_table.item(row, 1).text()
        
        key = f"{comp_type}_{comp_name}"
        
        # Konfirmasi penghapusan
        reply = QMessageBox.question(
            self, 
            'Remove Fault Configuration',
            f'Are you sure you want to remove fault configuration from:\n{comp_type}: {comp_name}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # Hapus dari dictionary
            if key in self.fault_configs:
                del self.fault_configs[key]
            
            # Update status dan buttons
            self.update_row_status(row, False)
            
            QMessageBox.information(
                self,
                'Configuration Removed',
                f'Fault configuration removed from {comp_type}: {comp_name}'
            )
    
    def run_simulation(self):
        """Jalankan simulasi dengan konfigurasi yang telah dibuat"""
        start_time = self.start_time_spin.value()
        stop_time = self.stop_time_spin.value()
        time_step = self.time_step_spin.value()
        
        # Validasi
        if stop_time <= start_time:
            QMessageBox.warning(self, "Invalid Configuration",
                              "Stop time must be greater than start time!")
            return
        
        # Prepare simulation config
        sim_config = {
            'start_time': start_time,
            'stop_time': stop_time,
            'time_step': time_step,
            'fault_events': self.fault_configs
        }
        
        # Emit signal atau proses simulasi
        self.simulation_started.emit(sim_config)
        
        QMessageBox.information(self, "Simulation Started",
                               f"Dynamic simulation configured with {len(self.fault_configs)} fault event(s).")
        
        self.accept()
    
    def load_components_from_system(self, buses, lines):
        """Load komponen dari sistem power flow"""
        self.components_table.setRowCount(0)
        
        components = []
        
        # Add buses
        for bus_name in buses:
            components.append(("Bus", bus_name))
        
        # Add lines
        for line_name in lines:
            components.append(("Line", line_name))
        
        self.components_table.setRowCount(len(components))
        
        for row, (comp_type, comp_name) in enumerate(components):
            type_item = QTableWidgetItem(comp_type)
            self.components_table.setItem(row, 0, type_item)
            
            name_item = QTableWidgetItem(comp_name)
            self.components_table.setItem(row, 1, name_item)
            
            status_item = QTableWidgetItem("No")
            status_item.setTextAlignment(Qt.AlignCenter)
            self.components_table.setItem(row, 2, status_item)
            
            # Create action buttons
            self.create_action_buttons(row)