from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, 
    QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QThread
from ui.ProgressBarUI import ProgressLoaderBar
from module.digsilentpf_worker import DigsilentWorker

class LoadflowProcessDialogUI(QDialog):
    finished = pyqtSignal()
    messages = pyqtSignal(str)
    
    def __init__(
        self, 
        ds_pf_pathfle: str,
        proj_name: str,
        case_name: str
    ):
        super().__init__()
        
        self.setWindowTitle("Running Load Flow")
        self.setWindowIcon(QIcon(r"C:\Users\Alex\NgodingDulu\project-hmi-nuklir-new\asset\logo-ugm.jpg"))
        self.setFixedWidth(480)
        self.setFixedHeight(120)
        
        self.ds_pf_pathfle = ds_pf_pathfle
        self.proj_name = proj_name
        self.case_name = case_name
        
        self.wrapper_layout = QVBoxLayout()
        self.content_label = QLabel("Sedang Menjalankan Simulasi Loadflow")
        
        self.progress_info_layout = QVBoxLayout()
        
        self.loginfo = QLabel("Memulai....")
        self.progress_info_layout.addWidget(self.loginfo)
        
        self.progress_bar = ProgressLoaderBar(minimum=0, maximum=0, objectName="BlueProgressBar", textVisible=False)
        self.progress_info_layout.addWidget(self.progress_bar)
        
        self.cancel_button = QPushButton("Batalkan")
        self.progress_info_layout.addWidget(self.cancel_button)
        self.cancel_button.clicked.connect(self.cancel_operation)
        
        self.wrapper_layout.addWidget(self.content_label)
        self.wrapper_layout.addLayout(self.progress_info_layout)

        self.setLayout(self.wrapper_layout)
        self.start_task()
    
    def cancel_operation(self):
        self.stop_task()
        self.close()
    
    def start_task(self):
        self.worker_thread = QThread()
        self.worker = DigsilentWorker(
            digsilent_path=self.ds_pf_pathfle,
            proj_name=self.proj_name,
            case_name=self.case_name
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.work_runloadflow)
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
        self.loginfo.setText(value)