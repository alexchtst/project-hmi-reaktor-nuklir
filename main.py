import sys
from PyQt5.QtWidgets import QApplication, QStackedWidget
from PyQt5.QtGui import QIcon

from ui.scenes.CoverScene import CoverScreenScene
from ui.scenes.HowtoScreen import HowToScreenScene
from ui.scenes.PLTNScene import PLTNOptionScreenScene
from ui.scenes.ScenarioScene import ScenarioScreenScene
from ui.scenes.LoadFlowActifity import LoadflowActifityScreenScene
from ui.scenes.DynamicSimulation import DynamicActifityScreenScene

class MainApp(QStackedWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HMI Reaktor Nuklir")
        self.setWindowIcon(QIcon(r"C:\Users\MSI\code-base\project-hmi-reaktor-nuklir\project-hmi-reaktor-nuklir\asset\logo-ugm.jpg"))
        
        # variables and options
        self.pltnssytemprojetcname = None
        self.digsilent_path = None
        
        self.cases = []
        self.eventcases = {}

        # Buat scene scene
        self.splash = CoverScreenScene()
        self.howto = HowToScreenScene()
        self.pltn = PLTNOptionScreenScene()
        self.scenario = ScenarioScreenScene()
        self.loadflow = LoadflowActifityScreenScene()
        self.dynamic = DynamicActifityScreenScene()

        self.addWidget(self.splash) # 0
        self.addWidget(self.howto) # 1
        self.addWidget(self.pltn) # 2
        self.addWidget(self.scenario) # 3
        self.addWidget(self.loadflow) # 4
        self.addWidget(self.dynamic) # 5

        self.splash.finished.connect(self.show_howto)
        self.howto.nextpltn.connect(self.show_pltn)
        self.pltn.nextscenario.connect(self.show_scenario)
        
        self.scenario.backtopltn.connect(self.show_pltn)
        self.scenario.toloadflow.connect(self.show_loadflowactifity)
        self.scenario.todynamic.connect(self.show_dynamicctifity)
        
        self.dynamic.backcenario.connect(self.show_scenario)
        self.dynamic.backpltn.connect(self.show_pltn)
        
        self.loadflow.backcenario.connect(self.show_scenario)
        self.loadflow.backpltn.connect(self.show_pltn)
        
        self.pltn.pltnsystemsignal.connect(self.on_listen_pltn_system)
        self.pltn.digsilentpathsignal.connect(self.on_listen_digsilent_path)
        self.pltn.casessignal.connect(self.on_pltn_connect_signal)
        self.pltn.casseseventsignal.connect(self.on_pltn_connect_caseseventsignal)

        self.setMinimumSize(1020, 680)
        self.setCurrentIndex(0)
    
    def on_pltn_connect_signal(self, value):
        self.cases = value
        
    def on_pltn_connect_caseseventsignal(self, value):
        self.eventcases = value
    
    def on_listen_pltn_system(self, value):
        self.pltnssytemprojetcname = value
    
    def on_listen_digsilent_path(self, value):
        self.digsilent_path = value

    def show_howto(self):
        self.setCurrentIndex(1)

    def show_pltn(self):
        self.setCurrentIndex(2)
        
    def show_scenario(self):
        self.setCurrentIndex(3)
        self.scenario.digsilent_path = self.digsilent_path
        self.scenario.proj_name = self.pltnssytemprojetcname
    
    def show_loadflowactifity(self):
        self.setCurrentIndex(4)
        
        self.loadflow.ds_pf_path_signal.emit(self.digsilent_path)
        self.loadflow.project_name_signal.emit(self.pltnssytemprojetcname)
        self.loadflow.caseses_signal.emit(self.cases)
    
    def show_dynamicctifity(self):
        self.setCurrentIndex(5)
        
        self.dynamic.ds_pf_path_signal.emit(self.digsilent_path)
        self.dynamic.project_name_signal.emit(self.pltnssytemprojetcname)
        self.dynamic.caseses_signal.emit(self.cases)
        self.dynamic.casesesevent_signal.emit(self.eventcases)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainApp()
    win.show()
    sys.exit(app.exec_())
