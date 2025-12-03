from PyQt5.QtWidgets import (
    QDialog, QPushButton, QLabel,
    QHBoxLayout, QVBoxLayout, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox,
    QWidget, QFormLayout, QComboBox, QDoubleSpinBox,
    QMessageBox, QCheckBox
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from ui.UIStyle import FINDPATH_BUTTON_STYLESHEET
from ui.DynamicProcessDialogUI import DynamicProcessDialogUI
from asset.assetloader import LOGO


class EventConfigDialog(QDialog):
    """Dialog untuk konfigurasi event (fault atau switch)"""

    def __init__(self, event_data, parent=None):
        super().__init__(parent)
        self.event_data = event_data
        self.event_config = {}

        event_name = event_data.get('name', 'Event')
        self.setWindowTitle(f"Event Configuration - {event_name}")
        self.setWindowModality(Qt.ApplicationModal)
        self.setFixedWidth(450)

        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()

        # Header
        header = QLabel(
            f"Configure Event: {self.event_data.get('name', 'N/A')}")
        header.setStyleSheet(
            "font-size: 14px; font-weight: bold; padding: 10px;")
        layout.addWidget(header)

        # Event Info
        info_group = QGroupBox("Event Information")
        info_layout = QFormLayout()

        type_label = QLabel(self.event_data.get('class', 'N/A'))
        info_layout.addRow("Event Type:", type_label)

        target_label = QLabel(self.event_data.get('target', 'N/A'))
        info_layout.addRow("Target Object:", target_label)

        original_time_label = QLabel(f"{self.event_data.get('time', 'N/A')} s")
        info_layout.addRow("Original Time:", original_time_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Configuration
        config_group = QGroupBox("Event Configuration")
        config_layout = QFormLayout()

        # In Service checkbox
        self.in_service_check = QCheckBox()
        self.in_service_check.setChecked(True)
        config_layout.addRow("In Service:", self.in_service_check)

        # Event Type/Class specific configuration
        event_class = self.event_data.get('class', '')

        if 'Shc' in event_class:  # Short Circuit Event
            # Start Fault Time
            self.start_fault_spin = QDoubleSpinBox()
            self.start_fault_spin.setRange(0, 1000)
            self.start_fault_spin.setValue(self.event_data.get('time', 1.0))
            self.start_fault_spin.setSuffix(" s")
            self.start_fault_spin.setDecimals(3)
            config_layout.addRow("Start Fault Time:", self.start_fault_spin)

            # Clear Fault Time
            self.clear_fault_spin = QDoubleSpinBox()
            self.clear_fault_spin.setRange(0, 1000)
            fault_time = self.event_data.get('time', 1.0)
            self.clear_fault_spin.setValue(fault_time + 0.5)
            self.clear_fault_spin.setSuffix(" s")
            self.clear_fault_spin.setDecimals(3)
            config_layout.addRow("Clear Fault Time:", self.clear_fault_spin)

            # Fault Type
            self.fault_type_combo = QComboBox()
            self.fault_type_combo.addItems([
                "3-Phase Short Circuit",
                "2-Phase Short Circuit",
                "2-Phase-Ground Short Circuit",
                "1-Phase-Ground Short Circuit",
                "Clear Fault"
            ])
            config_layout.addRow("Fault Type:", self.fault_type_combo)

        elif 'Switch' in event_class:  # Switch Event
            # Event Time
            self.event_time_spin = QDoubleSpinBox()
            self.event_time_spin.setRange(0, 1000)
            self.event_time_spin.setValue(self.event_data.get('time', 0.0))
            self.event_time_spin.setSuffix(" s")
            self.event_time_spin.setDecimals(3)
            config_layout.addRow("Event Time:", self.event_time_spin)

            # Switch State
            self.switch_state_combo = QComboBox()
            self.switch_state_combo.addItems([
                "Open (0)",
                "Close (1)"
            ])
            switch_state = self.event_data.get('switch_state', 0)
            self.switch_state_combo.setCurrentIndex(switch_state)
            config_layout.addRow("Switch State:", self.switch_state_combo)
        else:
            # Generic event - just time
            self.event_time_spin = QDoubleSpinBox()
            self.event_time_spin.setRange(0, 1000)
            self.event_time_spin.setValue(self.event_data.get('time', 0.0))
            self.event_time_spin.setSuffix(" s")
            self.event_time_spin.setDecimals(3)
            config_layout.addRow("Event Time:", self.event_time_spin)

        config_group.setLayout(config_layout)
        layout.addWidget(config_group)

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
        """Simpan konfigurasi event"""
        event_class = self.event_data.get('class', '')

        self.event_config = {
            'name': self.event_data.get('name'),
            'class': event_class,
            'target': self.event_data.get('target'),
            'in_service': self.in_service_check.isChecked()
        }

        if 'Shc' in event_class:  # Short Circuit
            start_time = self.start_fault_spin.value()
            clear_time = self.clear_fault_spin.value()

            if clear_time <= start_time:
                QMessageBox.warning(self, "Invalid Configuration",
                                    "Clear fault time must be greater than start fault time!")
                return

            self.event_config.update({
                'start_fault': start_time,
                'clear_fault': clear_time,
                'fault_type': self.fault_type_combo.currentIndex()
            })

        elif 'Switch' in event_class:  # Switch Event
            self.event_config.update({
                'time': self.event_time_spin.value(),
                'switch_state': self.switch_state_combo.currentIndex()
            })
        else:
            self.event_config.update({
                'time': self.event_time_spin.value()
            })

        self.accept()

    def get_config(self):
        """Ambil konfigurasi event"""
        return self.event_config


class RunDynamicConfigUI(QDialog):
    datareading = pyqtSignal(str)
    simulation_started = pyqtSignal(dict)  # Signal untuk mulai simulasi

    def __init__(self, ds_pf_pathfile=None, proj_name=None, case_name=None, event_cases=None):
        super().__init__()

        # Store properties
        self.__df_path = ds_pf_pathfile
        self.__proj_name = proj_name
        self.__case_name = case_name
        self.__event_cases = event_cases if event_cases else {}

        self.setWindowTitle("Run Dynamic Simulation")
        self.setWindowIcon(QIcon(fr"{LOGO}"))
        self.setFixedWidth(1000)
        self.setFixedHeight(680)

        self.dynamic_config = {}  # Menyimpan konfigurasi untuk setiap event

        self.setWindowModality(Qt.ApplicationModal)

        self.data_folder = r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\project-hmi-reaktor-nuklir\data"

        self.setup_ui()

    def setup_ui(self):
        main_layout = QVBoxLayout()

        # Header
        header_label = QLabel("Dynamic Simulation Configuration")
        header_label.setStyleSheet(
            "font-size: 16px; font-weight: bold; padding: 10px;")
        main_layout.addWidget(header_label)

        # Project Info Group
        info_group = QGroupBox("Project Information")
        info_layout = QFormLayout()

        proj_label = QLabel(self.__proj_name if self.__proj_name else "N/A")
        proj_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        info_layout.addRow("Project Name:", proj_label)

        case_label = QLabel(self.__case_name if self.__case_name else "N/A")
        case_label.setStyleSheet("color: #2c3e50; font-weight: bold;")
        info_layout.addRow("Study Case:", case_label)

        self.start_calc_time = QDoubleSpinBox()
        self.start_calc_time.setRange(-1000000, 10000)
        self.start_calc_time.setValue(-100.0)
        self.start_calc_time.setSuffix(" ms")
        self.start_calc_time.setDecimals(3)
        info_layout.addRow("Start Calculation Time:", self.start_calc_time)

        # Show event count for selected case
        event_count = 0
        if self.__case_name and self.__case_name in self.__event_cases:
            event_count = len(self.__event_cases[self.__case_name])

        event_count_label = QLabel(str(event_count))
        event_count_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        info_layout.addRow("Existing Events:", event_count_label)

        info_group.setLayout(info_layout)
        main_layout.addWidget(info_group)

        # Simulation Settings Group
        sim_group = QGroupBox("Simulation Settings")
        sim_layout = QFormLayout()

        # Start Time
        self.start_time_spin = QDoubleSpinBox()
        self.start_time_spin.setRange(-1000, 1000)
        self.start_time_spin.setValue(0.0)
        self.start_time_spin.setSuffix(" s")
        self.start_time_spin.setDecimals(3)
        sim_layout.addRow("Start Time:", self.start_time_spin)

        # Stop Time
        self.stop_time_spin = QDoubleSpinBox()
        self.stop_time_spin.setRange(-100, 1000)
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

        # Events Configuration from PowerFactory
        if self.__case_name and self.__case_name in self.__event_cases:
            existing_events = self.__event_cases[self.__case_name]
            if existing_events:
                events_pf_group = QGroupBox(
                    f"Events Configuration ({len(existing_events)})")
                events_pf_layout = QVBoxLayout()

                # Table untuk existing events dengan konfigurasi
                self.events_table = QTableWidget()
                self.events_table.setColumnCount(6)
                self.events_table.setHorizontalHeaderLabels([
                    "Event Name", "Event Type", "Target", "In Service", "Configured", "Action"
                ])

                header = self.events_table.horizontalHeader()
                header.setSectionResizeMode(0, QHeaderView.Stretch)
                header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(2, QHeaderView.Stretch)
                header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
                header.setSectionResizeMode(5, QHeaderView.ResizeToContents)

                self.events_table.setEditTriggers(QTableWidget.NoEditTriggers)

                # Populate events dengan action buttons
                self.populate_events_table(existing_events)

                events_pf_layout.addWidget(self.events_table)
                events_pf_group.setLayout(events_pf_layout)
                main_layout.addWidget(events_pf_group)

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

    def populate_events_table(self, events):
        """Populate table dengan events dan action buttons"""
        self.events_table.setRowCount(len(events))

        for row, event in enumerate(events):
            # Event Name
            name_item = QTableWidgetItem(event.get('name', 'N/A'))
            self.events_table.setItem(row, 0, name_item)

            # Event Type/Class
            class_name = event.get('class', 'N/A')
            # Simplify class name (remove 'Evt' prefix if exists)
            if class_name.startswith('Evt'):
                class_name = class_name[3:]
            type_item = QTableWidgetItem(class_name)
            self.events_table.setItem(row, 1, type_item)

            # Target
            target = event.get('target', 'N/A')
            target_item = QTableWidgetItem(target)
            self.events_table.setItem(row, 2, target_item)

            # In Service - Checkbox
            in_service_widget = QWidget()
            in_service_layout = QHBoxLayout(in_service_widget)
            in_service_layout.setContentsMargins(0, 0, 0, 0)
            in_service_layout.setAlignment(Qt.AlignCenter)

            in_service_check = QCheckBox()
            in_service_check.setChecked(True)  # Default in service
            in_service_check.stateChanged.connect(
                lambda state, r=row: self.on_in_service_changed(r, state)
            )
            in_service_layout.addWidget(in_service_check)
            in_service_widget.setLayout(in_service_layout)
            self.events_table.setCellWidget(row, 3, in_service_widget)

            # Configured Status
            status_item = QTableWidgetItem("Default")
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setForeground(Qt.darkYellow)
            self.events_table.setItem(row, 4, status_item)

            # Action buttons
            self.create_action_buttons(row, event)

            # Initialize config with default values
            event_key = f"{event.get('name')}_{event.get('target', 'unknown')}"
            self.dynamic_config[event_key] = {
                'event_data': event,
                'in_service': True,
                'configured': False,
                'config': {}
            }

    def create_action_buttons(self, row, event_data):
        """Buat tombol aksi untuk setiap event"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(4)

        # Configure Button
        config_btn = QPushButton("Configure")
        config_btn.setFixedWidth(85)
        config_btn.clicked.connect(
            lambda checked, r=row, e=event_data: self.configure_event(r, e))
        layout.addWidget(config_btn)

        # Reset Button
        reset_btn = QPushButton("Reset")
        reset_btn.setFixedWidth(75)
        reset_btn.clicked.connect(
            lambda checked, r=row, e=event_data: self.reset_event_config(r, e))
        reset_btn.setEnabled(False)  # Disabled by default
        layout.addWidget(reset_btn)

        widget.setLayout(layout)
        self.events_table.setCellWidget(row, 5, widget)

    def on_in_service_changed(self, row, state):
        """Handle perubahan checkbox in service"""
        event_name = self.events_table.item(row, 0).text()
        target = self.events_table.item(row, 2).text()
        event_key = f"{event_name}_{target}"

        is_checked = (state == Qt.Checked)

        if event_key in self.dynamic_config:
            self.dynamic_config[event_key]['in_service'] = is_checked

    def configure_event(self, row, event_data):
        """Buka dialog konfigurasi untuk event"""
        dialog = EventConfigDialog(event_data, self)

        event_key = f"{event_data.get('name')}_{event_data.get('target', 'unknown')}"

        # Load existing config if available
        if event_key in self.dynamic_config and self.dynamic_config[event_key]['configured']:
            # TODO: Load previous config ke dialog
            pass

        if dialog.exec_() == QDialog.Accepted:
            config = dialog.get_config()

            # Save configuration
            if event_key in self.dynamic_config:
                self.dynamic_config[event_key]['config'] = config
                self.dynamic_config[event_key]['configured'] = True
                self.dynamic_config[event_key]['in_service'] = config.get(
                    'in_service', True)

            # Update UI
            self.update_event_status(row, True)

            # Update in_service checkbox
            in_service_widget = self.events_table.cellWidget(row, 3)
            if in_service_widget:
                checkbox = in_service_widget.findChild(QCheckBox)
                if checkbox:
                    checkbox.setChecked(config.get('in_service', True))

    def reset_event_config(self, row, event_data):
        """Reset konfigurasi event ke default"""
        reply = QMessageBox.question(
            self,
            'Reset Configuration',
            f'Are you sure you want to reset configuration for:\n{event_data.get("name")}?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            event_key = f"{event_data.get('name')}_{event_data.get('target', 'unknown')}"

            if event_key in self.dynamic_config:
                self.dynamic_config[event_key]['config'] = {}
                self.dynamic_config[event_key]['configured'] = False

            # Update UI
            self.update_event_status(row, False)

            QMessageBox.information(
                self,
                'Configuration Reset',
                f'Configuration reset to default for {event_data.get("name")}'
            )

    def update_event_status(self, row, configured):
        """Update status event di table"""
        status_item = self.events_table.item(row, 4)

        if configured:
            status_item.setText("Custom")
            status_item.setForeground(Qt.darkGreen)
        else:
            status_item.setText("Default")
            status_item.setForeground(Qt.darkYellow)

        # Update button states
        widget = self.events_table.cellWidget(row, 5)
        if widget:
            buttons = widget.findChildren(QPushButton)
            if len(buttons) >= 2:
                reset_btn = buttons[1]  # Reset button is second
                reset_btn.setEnabled(configured)

    def run_simulation(self):
        """Jalankan simulasi dengan konfigurasi yang telah dibuat"""
        start_time = self.start_time_spin.value()
        stop_time = self.stop_time_spin.value()
        time_step = self.time_step_spin.value()
        start_calc = self.start_calc_time.value()

        # Validasi
        if stop_time <= start_time:
            QMessageBox.warning(self, "Invalid Configuration", "Stop time must be greater than start time!")
            return

        # Prepare simulation config
        sim_config = {
            'digsilent_path': self.__df_path,
            'proj_name': self.__proj_name,
            'case_name': self.__case_name,
            'start_time_calc': start_calc,
            'start_time_simulation': start_time,
            'stop_time_simulation': stop_time,
            'step_size': time_step,
            'events_config': self.dynamic_config
        }
        # print(sim_config)
        self.processdialog = DynamicProcessDialogUI(
            ds_pf_pathfle=self.__df_path,
            proj_name=self.__proj_name,
            case_name=self.__case_name,
            events_config=sim_config,
        )
        self.processdialog.show()
        self.accept()
