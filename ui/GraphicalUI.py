from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import pandas as pd
import os


class GraphicalVisualization(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(10, 6))
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
        self.ax.plot(self.x, self.y)
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.fig.tight_layout()
        self.draw()

    def add_line(self, y_values, label=None):
        self.lines_data.append({'y': y_values, 'label': label})

    def plot_multiline(self, x_label="", y_label="", legend=True):
        self.ax.clear()
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.tick_params(axis="x", rotation=90)

        if legend:
            self.ax.legend()

        self.fig.tight_layout()
        self.draw()

    def load_from_csv_multi(self, csv_path, x_col=None, y_cols=None):
        """
        Load data dari CSV untuk multiline chart

        Args:
            csv_path: Path ke file CSV
            x_col: Nama kolom untuk x-axis (default: kolom pertama)
            y_cols: List nama kolom untuk y-axis/multiple lines (default: semua kolom kecuali x_col)

        Example:
            graph.load_from_csv_multi('data.csv', x_col='Month', y_cols=['Sales', 'Target', 'Profit'])
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV tidak ditemukan: {csv_path}")

        df = pd.read_csv(csv_path)

        # Set x column
        if x_col is None:
            x_col = df.columns[0]

        # Set y columns
        if y_cols is None:
            # Ambil semua kolom kecuali kolom x
            y_cols = [col for col in df.columns if col != x_col]

        # Load data
        self.x = df[x_col].tolist()
        self.lines_data = []

        # Tambahkan setiap line ke lines_data
        for col in y_cols:
            self.lines_data.append({
                'y': df[col].tolist(),
                'label': col
            })

        print(f"Loaded {len(self.lines_data)} lines from CSV:")
        for line in self.lines_data:
            print(f"  - {line['label']}: {line['y']}")

    def plot_multiline(self, x_label="", y_label="", legend=True):
        self.ax.clear()
        
        # Plot setiap line
        if hasattr(self, 'lines_data') and self.lines_data:
            for line_data in self.lines_data:
                self.ax.plot(self.x, line_data['y'], label=line_data['label'])
        
        self.ax.set_xlabel(x_label)
        self.ax.set_ylabel(y_label)
        self.ax.tick_params(axis="x", rotation=90)
        
        if legend:
            # Legend di bawah plot dengan multiple columns
            self.ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), 
                        ncol=10, fontsize=7, frameon=False)
        
        self.fig.tight_layout(rect=[0.1, 0.1, 1, 1])
        self.draw()
    
    def load_from_csv_multi_included(self, csv_path, x_col=None, include_patterns=None):
        """
        Load data dari CSV untuk multiline chart dengan filter pattern

        Args:
            csv_path: Path ke file CSV
            x_col: Nama kolom untuk x-axis (default: kolom pertama)
            include_patterns: List pattern yang ingin diinclude (contoh: ['m_fehz', 'n_fehz', 'm_P_', 'm_Q_'])
                            Jika None, akan ambil semua kolom kecuali x_col

        Example:
            graph.load_from_csv_multi('data.csv', x_col='Time_s', include_patterns=['m_fehz', 'n_fehz'])
        """
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"CSV tidak ditemukan: {csv_path}")

        df = pd.read_csv(csv_path)

        if x_col is None:
            x_col = df.columns[0]

        if include_patterns is None:
            y_cols = [col for col in df.columns if col != x_col]
        else:
            y_cols = []
            for col in df.columns:
                if col != x_col:
                    # Check apakah kolom mengandung salah satu pattern
                    if any(pattern in col for pattern in include_patterns):
                        y_cols.append(col)

        self.x = df[x_col].tolist()
        self.lines_data = []

        for col in y_cols:
            self.lines_data.append({
                'y': df[col].tolist(),
                'label': col
            })
