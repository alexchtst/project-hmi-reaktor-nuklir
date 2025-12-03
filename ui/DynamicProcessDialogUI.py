from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, 
    QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QThread, Qt
from ui.ProgressBarUI import ProgressLoaderBar
from module.digsilentpf_worker import DigsilentWorker
from asset.assetloader import LOGO


class DynamicProcessDialogUI(QDialog):
    finished = pyqtSignal()
    messages = pyqtSignal(str)
    
    def __init__(
        self, 
        ds_pf_pathfle: str,
        proj_name: str,
        case_name: str,
        start_sim=None,
        stop_sim=None,
        time_step = None,
        events_config=None
    ):
        super().__init__()
        
        self.setWindowTitle("Dynamic Run")
        self.setWindowIcon(QIcon(fr"{LOGO}"))
        self.setFixedWidth(480)
        self.setFixedHeight(120)
        
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.__digsilent_path = ds_pf_pathfle
        self.__proj_name = proj_name
        self.__case_name = case_name
        self.__start_sim = start_sim
        self.__stop_sim = stop_sim
        self.__time_step = time_step
        self.__events_config = events_config 
        
        self.wrapper_layout = QVBoxLayout()
        self.content_label = QLabel("Running Dynamic Simulation")
        
        self.progress_info_layout = QVBoxLayout()
        
        self.loginfo = QLabel("Memulai....")
        self.progress_info_layout.addWidget(self.loginfo)
        
        self.progress_bar = ProgressLoaderBar(minimum=0, maximum=0, objectName="BlueProgressBar", textVisible=False)
        self.progress_info_layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Cancle")
        self.progress_info_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_operation)
        
        self.wrapper_layout.addWidget(self.content_label)
        self.wrapper_layout.addLayout(self.progress_info_layout)

        self.setLayout(self.wrapper_layout)
        
        self.finished.connect(self.on_finished_progress)
        self.messages.connect(self.on_messages_from_progress)
        
        self.start_task()
    
    def on_finished_progress(self):
        pass
    
    def on_messages_from_progress(self, value):
        if value:
            self.loginfo.setText(value)
            
    def cancel_operation(self):
        self.stop_task()
        self.close()
    
    def start_task(self):
        self.worker_thread = QThread()
        self.worker = DigsilentWorker(
            digsilent_path=self.__digsilent_path,
            proj_name=self.__proj_name,
            case_name=self.__case_name,
            events_config=self.__events_config
        )
        self.worker.moveToThread(self.worker_thread)
        self.worker_thread.started.connect(self.worker.work_workdynamic)
        self.worker.message.connect(self.update_progress_log)
        self.worker.finished.connect(self.on_finished_event)
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker_thread.finished.connect(self.worker_thread.deleteLater)

        self.worker_thread.start()
    
    def stop_task(self):
        if self.worker:
            self.loginfo.setText("Proses dihentikan oleh user...")
            self.worker.stop()
    
    def on_finished_event(self):
        self.finished.emit()
        self.progress_bar.hide()
    
    def update_progress_log(self, value):
        print(value)
        self.loginfo.setText(value)