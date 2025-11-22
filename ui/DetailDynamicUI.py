from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QTableWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QTabWidget,
    QPushButton, QListWidget,
    QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtCore import pyqtSignal, QObject, QThread
import pandas as pd

from module.qt_custom_style import *
from module.config_manager import *
from module.digsilent_pf import *

from ui.ProgressBarUI import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class Worker(QObject):
    finished = pyqtSignal()
    result = pyqtSignal(object)
    message = pyqtSignal(str)

    def __init__(self, file_path):
        super().__init__()
        self.__fp = file_path

    def run(self):
        try:
            data_frame = pd.read_csv(self.__fp)
            msg = f"Success load all the data"
            self.message.emit(msg)
            self.result.emit(data_frame)
        except Exception as e:
            msg = f"Error happened: {str(e)}"
            self.message.emit(msg)
        finally:
            self.finished.emit()

class PopulateWorker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(str)
    table_data_ready = pyqtSignal(object)  # row_count, col_count, headers, data_dict
    plot_data_ready = pyqtSignal(str, object)  # kind, sanitized_df
    
    def __init__(self, data_frame):
        super().__init__()
        self.data_frame = data_frame
        
    def run(self):
        try:
            self.progress.emit("Preparing table data...")
            table_data = self.prepare_table_data()
            self.table_data_ready.emit(table_data)
            
            kinds = [
                "Active Power",
                "Reactive Power (Q)",
                "Generator Frequency (Hz)",
                "Bus Frequency (Hz)"
            ]
            
            for kind in kinds:
                self.progress.emit(f"Preparing plot for {kind}...")
                sanitized_df = self.sanitized_data_frame(kind)
                self.plot_data_ready.emit(kind, sanitized_df)
            
            self.progress.emit("All data prepared successfully!")
            
        except Exception as e:
            self.progress.emit(f"Error: {str(e)}")
        finally:
            self.finished.emit()
    
    def prepare_table_data(self):
        df = self.data_frame
        
        data_dict = {}
        for i in range(df.shape[0]):
            row_data = []
            for j in range(df.shape[1]):
                row_data.append(str(df.iat[i, j]))
            data_dict[i] = row_data
        
        return {
            'row_count': df.shape[0],
            'col_count': df.shape[1],
            'headers': df.columns.tolist(),
            'data': data_dict
        }
    
    def sanitized_data_frame(self, kind):
        patterns = {
            "Active Power": "_m_P_bus1",
            "Reactive Power (Q)": "_m_Q_bus1",
            "Generator Frequency (Hz)": "_n_fehz_bus1",
            "Bus Frequency (Hz)": "_m_fehz",
        }

        if kind not in patterns:
            raise ValueError(f"Unknown kind '{kind}'")

        pattern = patterns[kind]
        selected_columns = ["Time_s"]

        for col in self.data_frame.columns:
            if pattern in col:
                selected_columns.append(col)

        return self.data_frame[selected_columns].copy()

class DetailDynamicWindow(QMainWindow):
    data_frame_ready_signal = pyqtSignal()
    on_selected_ready_signal = pyqtSignal(list)
    
    def __init__(self, fp, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Dynamic Simulation Detail")
        self.setGeometry(150, 100, 1200, 600)
        self.setMinimumSize(1200, 600)
        
        self.result_fp = fp

        self.data_frame = None
        self.plot_windows = []

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        self.setStyleSheet(CUSTOM_GLOBAL_STYLESHEET)

        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        self.general_tab = self.create_table_tab(name="Data")
        self.active_power_tab = self.create_tab(name="Active Power (P)")
        self.reactive_power_tab = self.create_tab(name="Reactive Power (Q)")
        self.generator_frequency_tab = self.create_tab(name="Generator Frequency (Hz)")
        self.bus_frequency_tab = self.create_tab(name="Bus Frequency (Hz)")

        self.initui()

        status_layout = QHBoxLayout()
        self.status_label = QLabel("Loading data...")
        status_layout.addWidget(self.status_label)
        
        self.progress_bar = ProgressBar(self, minimum=0, maximum=0, objectName="BlueProgressBar", textVisible=False)
        status_layout.addWidget(self.progress_bar, 1)
        
        main_layout.addLayout(status_layout)

        self.setup_worker()

    def initui(self):
        self.tabs.addTab(self.general_tab, "Data")
        self.tabs.addTab(self.active_power_tab, "Active Power")
        self.tabs.addTab(self.reactive_power_tab, "Reactive Power")
        self.tabs.addTab(self.generator_frequency_tab, "Generator Frequency")
        self.tabs.addTab(self.bus_frequency_tab, "Bus Frequency")

        self.tabs.setEnabled(False)

    def setup_worker(self):
        self.thread = QThread()
        self.worker = Worker(file_path=self.result_fp)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.run)
        self.worker.message.connect(self.on_message)
        self.worker.result.connect(self.on_result)
        self.worker.finished.connect(self.on_finished)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.start()

    def on_finished(self):
        pass

    def on_result(self, df):
        self.data_frame = df
        print(f"Data loaded: {df.shape[0]} rows x {df.shape[1]} columns")
        
        self.start_populate_worker()

    def start_populate_worker(self):
        self.status_label.setText("Processing data...")
        
        self.populate_thread = QThread()
        self.populate_worker = PopulateWorker(self.data_frame)
        self.populate_worker.moveToThread(self.populate_thread)
        
        self.populate_thread.started.connect(self.populate_worker.run)
        self.populate_worker.progress.connect(self.on_populate_progress)
        self.populate_worker.table_data_ready.connect(self.on_table_data_ready)
        self.populate_worker.plot_data_ready.connect(self.on_plot_data_ready)
        self.populate_worker.finished.connect(self.on_populate_finished)
        self.populate_worker.finished.connect(self.populate_thread.quit)
        self.populate_worker.finished.connect(self.populate_worker.deleteLater)
        self.populate_thread.finished.connect(self.populate_thread.deleteLater)
        
        self.populate_thread.start()
    
    def on_populate_progress(self, msg: str):
        self.status_label.setText(msg)
        print(msg)
    
    def on_table_data_ready(self, table_data):
        table = self.general_tab.findChild(QTableWidget)
        
        table.setRowCount(table_data['row_count'])
        table.setColumnCount(table_data['col_count'])
        table.setHorizontalHeaderLabels(table_data['headers'])
        
        for i, row_data in table_data['data'].items():
            for j, value in enumerate(row_data):
                table.setItem(i, j, QTableWidgetItem(value))
        
        print(f"Table populated: {table_data['row_count']} rows")
        
        self.populate_column_list()
    
    def on_plot_data_ready(self, kind: str, sanitized_df):
        tab_map = {
            "Active Power": self.active_power_tab,
            "Reactive Power (Q)": self.reactive_power_tab,
            "Generator Frequency (Hz)": self.generator_frequency_tab,
            "Bus Frequency (Hz)": self.bus_frequency_tab
        }
        
        if kind in tab_map:
            self.update_plot(tab_map[kind], kind, sanitized_df)
            print(f"Plot updated: {kind}")
    
    def on_populate_finished(self):
        self.tabs.setEnabled(True)
        self.progress_bar.setValue(100)
        self.progress_bar.hide()
        self.status_label.setText("Ready")
        
        # Enable buttons
        self.show_plot_btn.setEnabled(True)
        self.refresh_btn.setEnabled(True)
        
        print("All data populated successfully!")
        self.data_frame_ready_signal.emit()

    def on_message(self, msg: str):
        self.message = msg
        self.status_label.setText(msg)
        print(self.message)

    def create_table_tab(self, name):
        general_showing_data_widget = QWidget()
        layout = QVBoxLayout()
        general_showing_data_widget.setLayout(layout)

        table_panel = QGroupBox(f"Data Table {name}")
        table_layout = QHBoxLayout()
        table_panel.setLayout(table_layout)

        table = QTableWidget()
        table_layout.addWidget(table)

        selector_panel = QGroupBox("Show Data")
        selector_layout = QVBoxLayout()
        selector_panel.setLayout(selector_layout)

        select_label = QLabel("Select columns to plot (Shift + Click for multiple):")
        selector_layout.addWidget(select_label)
        
        self.column_list = QListWidget()
        self.column_list.setSelectionMode(QListWidget.MultiSelection)
        selector_layout.addWidget(self.column_list)

        button_layout = QHBoxLayout()
        self.show_plot_btn = QPushButton("Show Plot in New Window")
        self.show_plot_btn.clicked.connect(self.show_selected_columns_plot)
        self.show_plot_btn.setEnabled(False)
        button_layout.addWidget(self.show_plot_btn)
        
        self.refresh_btn = QPushButton("Refresh Selection")
        self.refresh_btn.clicked.connect(self.refresh_column_selection)
        self.refresh_btn.setEnabled(False)
        button_layout.addWidget(self.refresh_btn)
        
        selector_layout.addLayout(button_layout)

        layout.addWidget(table_panel, 4)
        layout.addWidget(selector_panel, 1)
        return general_showing_data_widget

    def populate_column_list(self):
        if self.data_frame is None:
            return
        
        self.column_list.clear()
        for col in self.data_frame.columns:
            if col != "Time_s":
                self.column_list.addItem(col)

    def refresh_column_selection(self):
        self.column_list.clearSelection()

    def show_selected_columns_plot(self):
        selected_items = self.column_list.selectedItems()
        
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Please select at least one column to plot.")
            return
        
        selected_columns = [item.text() for item in selected_items]
        
        plot_window = QMainWindow(self)
        plot_window.setWindowTitle(f"Custom Plot - {', '.join(selected_columns[:3])}{'...' if len(selected_columns) > 3 else ''}")
        plot_window.setGeometry(200, 150, 1000, 600)
        
        central_widget = QWidget()
        plot_window.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        info_label = QLabel(f"Plotting {len(selected_columns)} column(s): {', '.join(selected_columns)}")
        info_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(info_label)
        
        fig = Figure(figsize=(10, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        
        time_col = self.data_frame["Time_s"]
        
        for col in selected_columns:
            if col in self.data_frame.columns:
                ax.plot(time_col, self.data_frame[col], label=col, linewidth=1.5, marker='o', markersize=2)
        
        ax.set_xlabel("Time (s)", fontsize=11)
        ax.set_ylabel("Value", fontsize=11)
        ax.set_title("Selected Columns vs Time", fontsize=13, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        layout.addWidget(canvas)
        
        from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
        toolbar = NavigationToolbar2QT(canvas, plot_window)
        layout.addWidget(toolbar)
        
        plot_window.show()
        
        self.plot_windows.append(plot_window)

    def create_tab(self, name):
        visualization_widget = QWidget()
        visualization_layout = QHBoxLayout()
        visualization_widget.setLayout(visualization_layout)

        right_panel = QGroupBox(f"Visualization {name}")
        right_layout = QVBoxLayout()
        right_panel.setLayout(right_layout)

        fig = Figure(figsize=(8, 6))
        canvas = FigureCanvas(fig)
        ax = fig.add_subplot(111)
        right_layout.addWidget(canvas)

        visualization_layout.addWidget(right_panel, 6)

        return visualization_widget

    def update_plot(self, tab_widget, kind, sanitized_df):
        time = sanitized_df["Time_s"]

        canvas = tab_widget.findChild(FigureCanvas)
        ax = canvas.figure.axes[0]

        ax.clear()

        for col in sanitized_df.columns:
            if col != "Time_s":
                ax.plot(time, sanitized_df[col], label=col, linewidth=1.5)

        ax.set_title(kind, fontsize=12, fontweight='bold')
        ax.set_xlabel("Time (s)", fontsize=10)
        ax.set_ylabel(kind, fontsize=10)
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)

        canvas.draw()

    def sanitized_data_frame(self, kind):
        patterns = {
            "Active Power": "_m_P_bus1",
            "Reactive Power (Q)": "_m_Q_bus1",
            "Generator Frequency (Hz)": "_n_fehz_bus1",
            "Bus Frequency (Hz)": "_m_fehz",
        }

        if kind not in patterns:
            raise ValueError(f"Unknown kind '{kind}'")

        pattern = patterns[kind]
        selected_columns = ["Time_s"]

        for col in self.data_frame.columns:
            if pattern in col:
                selected_columns.append(col)

        return self.data_frame[selected_columns].copy()

    def closeEvent(self, event):
        for window in self.plot_windows:
            window.close()
        event.accept()