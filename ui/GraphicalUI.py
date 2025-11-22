from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import os

class GraphicalVisualization(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(5, 4))
        self.ax = self.fig.add_subplot(111)

        super().__init__(self.fig)
        self.setParent(parent)

    def load_from_array(self, x_labels, y_values):
        self.x = x_labels
        self.y = y_values

    def load_from_dict(self, data_dict):
        self.x = list(data_dict.keys())
        self.y = list(data_dict.values())

    def load_from_csv(self, csv_path, x_col=None, y_col=None):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV tidak ditemukan: {csv_path}")

        df = pd.read_csv(csv_path)

        if x_col is None:
            x_col = df.columns[0]
        if y_col is None:
            y_col = df.columns[1]

        self.x = df[x_col].tolist()
        self.y = df[y_col].tolist()

    def plot_bar(self, x_label="", y_label=""):
        self.ax.clear()
        self.ax.bar(self.x, self.y)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.tick_params(axis="x", rotation=90)
        self.fig.tight_layout()
        self.draw()

    def plot_line(self, x_label="", y_label=""):
        self.ax.clear()
        self.ax.plot(self.x, self.y, marker="o")
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.fig.tight_layout()
        self.draw()
