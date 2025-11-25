class DigsilentPowerFactory:
    def __init__(
        self,
        digsilent_path,
        proj_name = None,
        case_name = None,
    ):
        import sys
        import os
        import powerfactory as pf
        
        self.dgs_pf = digsilent_path
        self.proj_name = proj_name
        self.case_name = case_name
        
        self.__ready_to_run__ = False
        
        self.pf_app = None
        self.project_app = None
        
        if not os.path.exists(self.dgs_pf):
            print(f"{digsilent_path} tidak terdeteksi")
        
        sys.path.append(f"{os.path.abspath(digsilent_path)}")
        self.pf_app = pf.GetApplication()
        
        if self.pf_app is None:
            self.__ready_to_run__ = True
            print(f"Gagal mengaktifasi power factory digsilent")

        self.pf_app.ClearOutputWindow()
        self.pf_app.ResetCalculation()
        print("berhasil Menginisiasi power factory digsilent")
    
    def detect_study_cases(self):
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            study_case_folder = self.pf_app.GetProjectFolder("study")
            all_study_cases = study_case_folder.GetContents('*.IntCase')
            cases = [obj.loc_name for obj in all_study_cases]
            return True, f"[SUCCESS]: Berhasil mengambil semua case dalam project {self.proj_name}", cases
        
        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", []
    
    def detect_project_names(self):
        pass
    
    def detect_all_event_in_cases(self):
        pass
    
    def detect_event_in_case(self, case_specific_name):
        pass
    
    def connect_digsilent_pf_project(self, connect_to_project = None):
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            proj_target = self.proj_name
            if connect_to_project is not None:
                proj_target = connect_to_project
            
            if self.proj_name is None  and connect_to_project is None:
                raise Exception("Tidak ada project yang ingin dikoneksikan")
            
            temp_ = self.pf_app.ActivateProject(proj_target)
            if temp_ is None:
                print("[FAILED] setting project kembali ke sebelumnya")
                raise TypeError(f"Tidak dapat mengaktifkan project {proj_target}. Pastikan.pfd file terload di digsilent power factory dan memiliki nama yang sama.")
            
            self.project_app = temp_
            return True, "[SUCCESS]: Berhasil aktifasi dan mengganti project"
            
        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}"
    
    def safe_getattr(self, obj, attr, default=0):
        try:
            val = obj.GetAttribute(attr)
            if val is None:
                return default
            return val
        except:
            return default
    
    def running_loadflow(self, case_specific_name):
        pass
    
    def running_loadflow(
        self,
        case_specific_name,
        start_time_simulation=0,
        stop_time_simulation=100,
        step_size=0.01,
        events_config=None,
        properties_data_name={
            "ElmSym": ["m:P:bus1", "m:Q:bus1", "n:fehz:bus1"],
            "ElmTerm": ["m:fehz"],
            "ElmLne": [],
            "ElmTr2": [],
        },
    ):
        pass
    
    