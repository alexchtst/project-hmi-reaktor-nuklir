class DigsilentPowerFactoryLibrary:
    def __init__(
        self,
        digsilent_path,
        proj_name = None,
        case_name = None,
    ):
        import sys
        import os
        
        self.dgs_pf = digsilent_path # as astring
        self.proj_name = proj_name # as string
        self.case_name = case_name # as string
        
        self.__ready_to_run__ = False
        
        self.pf_app = None # as pf app
        self.project_app = None # as project app
        self.cases_app = None # as lists app case name

        self.all_projetcs_name = []
        self.all_cases = []
        
        if not os.path.exists(self.dgs_pf):
            print(f"{digsilent_path} tidak terdeteksi")
        
        sys.path.append(f"{os.path.abspath(digsilent_path)}")
        import powerfactory as pf
        self.pf_app = pf.GetApplication()
        
        if self.pf_app is None:
            print(f"Gagal mengaktifasi power factory digsilent")
        else:
            self.__ready_to_run__ = True
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()
            print("berhasil Menginisiasi power factory digsilent")
    
    def detect_study_cases(self):
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            if self.pf_app is None or self.project_app is None:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory / project app belum diaktifasi")
            
            study_case_folder = self.pf_app.GetProjectFolder("study")
            all_study_cases = study_case_folder.GetContents('*.IntCase')
            self.cases_app = all_study_cases
            cases = [obj.loc_name for obj in all_study_cases]
            return True, f"[SUCCESS]: Berhasil mengambil semua case dalam project {self.proj_name}", cases
        
        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", []
    
    def detect_project_names(self):
        try:
            if self.__ready_to_run__ == False:
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
            if self.pf_app is None:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory")
            
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()

            user = self.pf_app.GetCurrentUser()

            projects = user.GetContents('*.Intprj', 0)
            self.all_projetcs_name = [proj.loc_name for proj in projects]

            return True, f"[SUCCESS]: Berhasil mengambil semua case dalam project {self.proj_name}", self.all_projetcs_name
        except Exception as e:
            print(e)
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", []
    
    def detect_event_in_case(self, case_specific_name = None):
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            if self.pf_app is None or self.project_app is None:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory / project app belum diaktifasi")
            
            choosen_case = self.case_name
            if case_specific_name is not None:
                choosen_case = case_specific_name
            
            all_study_case_app = None
            if self.cases_app is not None or len(self.cases_app) != 0:
                all_study_case_app = self.cases_app
            else:
                all_study_case_app = self.pf_app.GetProjectFolder("study")
            
            if all_study_case_app is None:
                raise Exception("Study Case gagal di load.")
            
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()

            for case in all_study_case_app:
                case_name = case.loc_name.strip()

                if case_name == choosen_case.strip():
                    case.Activate()
                    break
            event_folder = self.pf_app.GetFromStudyCase('IntEvt')
            all_events = event_folder.GetContents()
            
            event_list = []
            for event in all_events:
                event_info = {
                    'name': event.loc_name,
                    'class': event.GetClassName(),
                }

                try:
                    if hasattr(event, 'p_target') and event.p_target:
                        event_info['target'] = event.p_target.loc_name
                    if hasattr(event, 'time'):
                        event_info['time'] = event.time
                    if hasattr(event, 'i_switch'):
                        # 0=open, 1=close
                        event_info['switch_state'] = event.i_switch
                except:
                    pass

                event_list.append(event_info)
            print(f"[INFO]: {len(all_events)} event ditemukan di study case '{case_name}'"), event_list

        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", []
    
    def connect_digsilent_pf_project(self, connect_to_project = None):
        try:
            if self.__ready_to_run__ == False:
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
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
            self.__ready_to_run__ = True
            if self.proj_name is None and connect_to_project is not None:
                self.proj_name = connect_to_project
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
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            if self.pf_app is None or self.project_app is None:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory / project app belum diaktifasi")
            
            choosen_case = self.case_name
            if case_specific_name is not None:
                choosen_case = case_specific_name
            
            all_study_case_app = None
            if self.cases_app is not None or len(self.cases_app) != 0:
                all_study_case_app = self.cases_app
            else:
                all_study_case_app = self.pf_app.GetProjectFolder("study")
            
            if all_study_case_app is None:
                raise Exception("Study Case gagal di load.")
            
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()

            for case in all_study_case_app:
                case_name = case.loc_name.strip()

                if case_name == choosen_case.strip():
                    case.Activate()
                    break
            ldf = self.pf_app.GetFromStudyCase("ComLdf")

            if ldf is None:
                raise TypeError("Load flow command (ComLdf) not found in study case")

            ierr = ldf.Execute()
            if ierr != 0:
                raise RuntimeError(f"Load flow failed with error code {ierr}")

            insert_to = {
                "project": self.proj_name,
                "study_case": self.case_name,
                "buses": [],
                "generators": [],
                "lines": [],
                "loads": [],
                "transformers": [],
            }

            print(f"[INFO]: Collecting bus loadflow data...")
            buses = self.pf_app.GetCalcRelevantObjects("*.ElmTerm")
            for bus in buses:
                insert_to["buses"].append({
                    "name": bus.loc_name,
                    "voltage_pu": bus.GetAttribute("m:u"),
                    "voltage_kv": bus.GetAttribute("m:Ul"),
                    "angle_deg": bus.GetAttribute("m:phiu"),
                })
            
            print(f"[INFO]: Collecting generator loadflow data...")
            gens = self.pf_app.GetCalcRelevantObjects("*.ElmSym")
            for gen in gens:
                insert_to["generators"].append({
                    "name": gen.loc_name,
                    "P": self.safe_getattr(gen, "m:P:bus1"),
                    "Q": self.safe_getattr(gen, "m:Q:bus1"),
                    "I": self.safe_getattr(gen, "m:I:bus1"),
                    "COSPHI": self.safe_getattr(gen, "m:cosphi:bus1"),
                    "S": self.safe_getattr(gen, "m:S:bus1"),
                    "I1": self.safe_getattr(gen, "m:i1:bus1"),
                    "PHII1": self.safe_getattr(gen, "m:phii1:bus1"),
                })
            
            print(f"[INFO]: Collecting line loadflow data...")
            lines = self.pf_app.GetCalcRelevantObjects("*.ElmLne")
            for line in lines:
                insert_to["lines"].append({
                    "name": line.loc_name,
                    "loading_percent": line.GetAttribute("c:loading"),
                    "P_from_MW": line.GetAttribute("m:P:bus1"),
                    "P_to_MW": line.GetAttribute("m:P:bus2"),
                    "Q_from_Mvar": line.GetAttribute("m:Q:bus1"),
                    "Q_to_Mvar": line.GetAttribute("m:Q:bus2"),
                    "I_from_kA": line.GetAttribute("m:I:bus1"),
                    "I_to_kA": line.GetAttribute("m:I:bus2"),
                })
            
            print(f"[INFO]: Collecting loads loadflow data...")
            loads = self.pf_app.GetCalcRelevantObjects("*.ElmLod")
            for load in loads:
                insert_to["loads"].append({
                    "name": load.loc_name,
                    "P_MW": load.GetAttribute("m:P:bus1"),
                    "Q_Mvar": load.GetAttribute("m:Q:bus1"),
                    "I_kA": load.GetAttribute("m:I:bus1"),
                })
            
            print(f"[INFO]: Collecting transformers loadflow data...")
            trafos = self.pf_app.GetCalcRelevantObjects("*.ElmTr2")
            for trafo in trafos:
                insert_to["transformers"].append({
                    "name": trafo.loc_name,
                    "loading_percent": trafo.GetAttribute("c:loading"),
                    "P_HV_MW": trafo.GetAttribute("m:P:bushv"),
                    "P_LV_MW": trafo.GetAttribute("m:P:buslv"),
                    "Q_HV_Mvar": trafo.GetAttribute("m:Q:bushv"),
                    "Q_LV_Mvar": trafo.GetAttribute("m:Q:buslv"),
                    "I_HV_kA": trafo.GetAttribute("m:I:bushv"),
                    "I_LV_kA": trafo.GetAttribute("m:I:buslv"),
                })
            
            print(f"[DONE]: Collecting all loadflow data...")
            return True, "Success running loadflow and collect all the data", insert_to

        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", {}
    
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
        try:
            if self.__ready_to_run__ == False:
                raise "[NOT READY] Tidak dapat aktivasi project"
            
            if self.pf_app is None:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory")
            
        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", {}
    
    