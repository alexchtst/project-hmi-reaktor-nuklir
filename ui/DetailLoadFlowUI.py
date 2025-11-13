from PyQt5.QtWidgets import (
    QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGroupBox,
)
from PyQt5.QtCore import Qt, pyqtSignal, QObject, QThread

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd

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
