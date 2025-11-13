from PyQt5.QtWidgets import (
    QMainWindow, QWidget, 
    QVBoxLayout, QHBoxLayout, QGroupBox, QComboBox, QLabel, 
    QTableWidget, QTableWidgetItem, QTableWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd


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
