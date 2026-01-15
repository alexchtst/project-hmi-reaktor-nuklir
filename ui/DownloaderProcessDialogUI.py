from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, 
    QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from ui.ProgressBarUI import ProgressLoaderBar
from asset.assetloader import LOGO

class DownloaderProcessDialogUI(QDialog):
    finished = pyqtSignal()
    messages = pyqtSignal(str)

    def __init__(
            self,
            title = "Unduh PFD File"
    ):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowIcon(QIcon(fr"{LOGO}"))
        self.setFixedWidth(480)
        self.setFixedHeight(120)

        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)