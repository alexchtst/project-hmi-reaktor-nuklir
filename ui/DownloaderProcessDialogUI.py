from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, 
    QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from ui.ProgressBarUI import ProgressLoaderBar

class DownloaderProcessDialogUI(QDialog):
    finished = pyqtSignal()
    messages = pyqtSignal(str)

    def __init__(
            self,
            title = "Unduh PFD File"
    ):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\project-hmi-reaktor-nuklir\asset\logo-ugm.jpg"))
        self.setFixedWidth(480)
        self.setFixedHeight(120)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)