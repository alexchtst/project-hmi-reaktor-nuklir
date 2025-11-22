from random import randint
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QProgressBar

from ui.UIStyle import PROGRESS_BAR_STYLE_SHEET

class ProgressLoaderBar(QProgressBar):
    def __init__(self, *args, **kwargs):
        super(ProgressLoaderBar, self).__init__(*args, **kwargs)
        self.setValue(0)
        
        self.setStyleSheet(PROGRESS_BAR_STYLE_SHEET)

        if self.minimum() != self.maximum():
            self.timer = QTimer(self, timeout=self.onTimeout)
            self.timer.start(randint(1, 3) * 1000)

    def onTimeout(self):
        if self.value() >= 100:
            self.timer.stop()
            self.timer.deleteLater()
            del self.timer
            return
        self.setValue(self.value() + 1)