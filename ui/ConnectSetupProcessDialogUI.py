from PyQt5.QtWidgets import (
    QDialog, QPushButton, QVBoxLayout, 
    QLabel
)
from PyQt5.QtGui import QIcon
from PyQt5 import sip
from PyQt5.QtCore import pyqtSignal, QThread
from PyQt5.QtCore import Qt
from ui.ProgressBarUI import ProgressLoaderBar
from module.digsilentpf_worker import DigsilentWorker
from asset.assetloader import LOGO


class ConnectSetupProcessDialogUI(QDialog):
    finished = pyqtSignal()
    messages = pyqtSignal(str)
    finsihedpayload = pyqtSignal(dict)
    
    def __init__(
        self, 
        titile: str, 
        content: str,
        ds_pf_pathfle: str,
        proj_name: str
    ):
        super().__init__()
        
        self.setWindowTitle(titile)
        self.setWindowIcon(QIcon(fr"{LOGO}"))
        self.setFixedWidth(480)
        self.setFixedHeight(120)
        
        self.setWindowModality(Qt.ApplicationModal)
        self.setWindowFlag(Qt.WindowCloseButtonHint, False)
        
        self.ds_pf_pathfle = ds_pf_pathfle
        self.proj_name = proj_name
        
        # Tambahkan flag untuk tracking status
        self.is_cancelled = False
        self.worker = None
        self.worker_thread = None
        
        self.wrapper_layout = QVBoxLayout()
        self.content_label = QLabel(content)
        
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
        
        self.finished.connect(self.on_finished_progress)
        self.messages.connect(self.on_messages_from_progress)
        self.finsihedpayload.connect(self.on_finished_success)
        
        self.start_task()
    
    def on_finished_progress(self):
        pass
    
    def on_messages_from_progress(self, value):
        pass
    
    def on_finished_success(self, value):
        pass
    
    def cancel_operation(self):
        if not self.is_cancelled:
            self.is_cancelled = True
            self.stop_task()
            self.close()
    
    def start_task(self):
        self.worker_thread = QThread()
        self.worker = DigsilentWorker(
            digsilent_path=self.ds_pf_pathfle,
            proj_name=self.proj_name
        )
        self.worker.moveToThread(self.worker_thread)

        self.worker_thread.started.connect(self.worker.work_connectsetup)
        self.worker.message.connect(self.update_progress_log)
        self.worker.finished.connect(self.on_finished_event)
        self.worker.finishpayload.connect(self.on_finished_success_event)
        
        # Ubah urutan cleanup - thread dulu baru worker
        self.worker.finished.connect(self.worker_thread.quit)
        self.worker_thread.finished.connect(self.cleanup_worker)

        self.worker_thread.start()
    
    def stop_task(self):
        """Stop task dengan aman"""
        if self.worker and not sip.isdeleted(self.worker):
            try:
                self.loginfo.setText("Proses dihentikan oleh user...")
                self.worker.stop()
            except RuntimeError as e:
                print(f"Worker sudah dihapus: {e}")
        
        # Tunggu thread selesai dengan timeout
        if self.worker_thread and self.worker_thread.isRunning():
            self.worker_thread.quit()
            if not self.worker_thread.wait(3000):  # Timeout 3 detik
                print("Thread tidak berhenti, forcing termination...")
                self.worker_thread.terminate()
                self.worker_thread.wait()
    
    def cleanup_worker(self):
        """Cleanup worker dan thread setelah selesai"""
        if self.worker:
            self.worker.deleteLater()
            self.worker = None
        
        if self.worker_thread:
            self.worker_thread.deleteLater()
            self.worker_thread = None
    
    def on_finished_event(self):
        if not self.is_cancelled:
            self.finished.emit()
            self.progress_bar.hide()
            self.cancel_button.setText("Tutup")
    
    def on_finished_success_event(self, value):
        if not self.is_cancelled:
            self.finsihedpayload.emit(value)
    
    def update_progress_log(self, value):
        self.loginfo.setText(value)
    
    def closeEvent(self, event):
        """Override closeEvent untuk cleanup yang benar"""
        if not self.is_cancelled:
            self.is_cancelled = True
            self.stop_task()
        event.accept()