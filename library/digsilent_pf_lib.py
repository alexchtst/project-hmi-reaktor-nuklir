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
        
        else:
            sys.path.append(f"{os.path.abspath(digsilent_path)}")
            import powerfactory as pf
            self.pf_app = pf.GetApplication()
            
            if self.proj_name is not None:
                self.project_app = self.pf_app.ActivateProject(self.proj_name)
                if self.project_app is None or self.project_app != 0:
                    print("Project is not activated")
        
        if self.pf_app is None:
            print(f"Gagal mengaktivasi power factory digsilent")
        else:
            self.__ready_to_run__ = True
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()
            print("berhasil Menginisiasi power factory digsilent")
    
    def detect_study_cases(self):
        try:
            if self.__ready_to_run__ == False:
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
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
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
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
                all_study_case_app = self.pf_app.GetProjectFolder("study").GetContents('*.IntCase')
            
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
            
            if event_folder is None:
                return True, f"[SUCCESS]: Tidak ada event di study case '{choosen_case}'", []
            
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
            
            print(f"[INFO]: {len(all_events)} event ditemukan di study case '{choosen_case}'")
            return True, f"[SUCCESS]: Berhasil mengambil event dari case {choosen_case}", event_list

        except Exception as e:
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}", []
    
    def connect_digsilent_pf_project(self, connect_to_project = None):
        try:
            if self.__ready_to_run__ == False:
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
            proj_target = self.proj_name
            if connect_to_project is not None:
                proj_target = connect_to_project
            
            if self.proj_name is None and connect_to_project is None:
                raise Exception("Tidak ada project yang ingin dikoneksikan")
            
            temp_ = self.pf_app.ActivateProject(proj_target)
            if temp_ is None or temp_ != 0:
                print("[FAILED] setting project kembali ke sebelumnya")
                raise TypeError(f"Tidak dapat mengaktifkan project {proj_target}. Pastikan .pfd file terload di digsilent power factory dan memiliki nama yang sama.")
            
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
    
    def running_loadflow(self, case_specific_name=None):
        try:
            if self.__ready_to_run__ == False:
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
            if self.pf_app is None or self.project_app is None or self.project_app != 0:
                 self.__ready_to_run__ = False
                 raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory / project app belum diaktifasi")
            
            choosen_case = self.case_name
            if case_specific_name is not None:
                choosen_case = case_specific_name
            
            all_study_case_app = None
            if self.cases_app is not None and len(self.cases_app) != 0:
                all_study_case_app = self.cases_app
            else:
                study_folder = self.pf_app.GetProjectFolder("study")
                all_study_case_app = study_folder.GetContents('*.IntCase')
            
            if all_study_case_app is None or len(all_study_case_app) == 0:
                raise Exception("Study Case gagal di load.")
            
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()

            case_found = False
            for case in all_study_case_app:
                case_name = case.loc_name.strip()

                if case_name == choosen_case.strip():
                    case.Activate()
                    case_found = True
                    break
            
            if not case_found:
                raise ValueError(f"Study case '{choosen_case}' tidak ditemukan")
            
            print(f"[INFO]: Running loadflow...")
            ldf = self.pf_app.GetFromStudyCase("ComLdf")

            if ldf is None:
                raise TypeError("Load flow command (ComLdf) not found in study case")

            ierr = ldf.Execute()
            if ierr != 0:
                raise RuntimeError(f"Load flow failed with error code {ierr}")
            
            print(f"[INFO]: Success running loadflow")

            insert_to = {
                "project": self.proj_name,
                "study_case": choosen_case,
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
            import traceback
            error_details = traceback.format_exc()
            return False, f"[TERMINATE]: Terjadi Error => {str(e)}\n{error_details}", {}
    
    def running_dynamic(
        self,
        case_specific_name=None,
        start_calc=-10000,  # as the start initial condition (start calcultion ds pf) in ms
        start_time_simulation=0,  # as the start capture / record data
        stop_time_simulation=100,  # as the stop capture / record data
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
                raise Exception("[NOT READY] Tidak dapat aktivasi project")
            
            if self.pf_app is None or self.project_app is None:
                self.__ready_to_run__ = False
                raise RuntimeError("Tidak dapat membuka applikasi / mengakses power factory / project app belum diaktifasi")
             
            choosen_case = self.case_name
            if case_specific_name is not None:
                choosen_case = case_specific_name
            
            all_study_case_app = None
            if self.cases_app is not None and len(self.cases_app) != 0:
                all_study_case_app = self.cases_app
            else:
                study_folder = self.pf_app.GetProjectFolder("study")
                all_study_case_app = study_folder.GetContents('*.IntCase')
            
            if all_study_case_app is None or len(all_study_case_app) == 0:
                raise Exception("Study Case gagal di load.")
            
            self.pf_app.ClearOutputWindow()
            self.pf_app.ResetCalculation()

            case_found = False
            for case in all_study_case_app:
                case_name = case.loc_name.strip()

                if case_name == choosen_case.strip():
                    case.Activate()
                    case_found = True
                    break
            
            if not case_found:
                raise ValueError(f"Study case '{choosen_case}' tidak ditemukan")
            
            print(f"[INFO]: Setting up initial condition...")
            comInc = self.pf_app.GetFromStudyCase("ComInc")
            comSim = self.pf_app.GetFromStudyCase("ComSim")

            if comInc is None or comSim is None:
                raise RuntimeError("Cannot get simulation commands (ComInc or ComSim)")

            comInc.iopt_sim = "rms"
            comInc.iopt_show = 0
            comInc.iopt_adapt = 0
            comInc.dtgrd = 30  # Integration time step
            comInc.dtout = step_size
            
            if start_calc is not None:
                comInc.tstart = start_calc
            
            comInc.start = start_time_simulation
            comSim.tstop = stop_time_simulation

            comInc.Execute()
            elmRes = comInc.p_resvar
            print(f"[DONE]: Success running initial condition")

            if elmRes is None:
                raise RuntimeError("Cannot get result variable object")

            # Configure events berdasarkan events_config dari UI
            print(f"[INFO]: Configuring events...")
            event_folder = self.pf_app.GetFromStudyCase('IntEvt')

            if event_folder is None:
                print("[WARNING]: No event folder found, creating one...")
                event_folder = self.pf_app.GetFromStudyCase('.').CreateObject('IntEvt', 'Simulation Events')

            # Get all existing events in PowerFactory
            all_pf_events = event_folder.GetContents()

            events_configured = 0
            events_disabled = 0

            if events_config:
                for event_key, event_cfg in events_config.items():
                    event_data = event_cfg.get('event_data', {})
                    in_service = event_cfg.get('in_service', True)
                    configured = event_cfg.get('configured', False)
                    config = event_cfg.get('config', {})

                    event_name = event_data.get('name')
                    target_name = event_data.get('target')
                    event_class = event_data.get('class', '')

                    # Find corresponding PowerFactory event object
                    pf_event = None
                    for evt in all_pf_events:
                        if evt.loc_name == event_name:
                            pf_event = evt
                            break

                    if pf_event is None:
                        print(f"[WARNING]: Event '{event_name}' not found in PowerFactory, skipping...")
                        continue

                    # Set in service status
                    if hasattr(pf_event, 'outserv'):
                        pf_event.outserv = 0 if in_service else 1
                    elif hasattr(pf_event, 'i_outserv'):
                        pf_event.i_outserv = 0 if in_service else 1

                    if not in_service:
                        events_disabled += 1
                        print(f"[INFO]: Event '{event_name}' set to OUT OF SERVICE")
                        continue

                    # Apply custom configuration if exists
                    if configured and config:
                        if 'Shc' in event_class:  # Short Circuit Event
                            # Update fault timing
                            if 'start_fault' in config:
                                pf_event.time = config['start_fault']

                            if 'fault_type' in config and hasattr(pf_event, 'i_shc'):
                                pf_event.i_shc = config['fault_type']

                            print(f"[INFO]: Configured fault event '{event_name}': "
                                  f"start={config.get('start_fault')}s, "
                                  f"clear={config.get('clear_fault')}s, "
                                  f"type={config.get('fault_type')}")

                            # Create clear fault event if specified
                            if 'clear_fault' in config:
                                clear_event_name = f"Clear_{event_name}"
                                # Check if clear event already exists
                                clear_event = None
                                for evt in all_pf_events:
                                    if evt.loc_name == clear_event_name:
                                        clear_event = evt
                                        break

                                if clear_event is None:
                                    # Create new clear event
                                    clear_event = event_folder.CreateObject('EvtShc', clear_event_name)
                                    clear_event.p_target = pf_event.p_target

                                clear_event.time = config['clear_fault']
                                clear_event.i_shc = 4  # Clear fault
                                clear_event.outserv = 0
                                print(f"[INFO]: Clear fault event created/updated at {config['clear_fault']}s")

                        elif 'Switch' in event_class:  # Switch Event
                            if 'time' in config:
                                pf_event.time = config['time']

                            if 'switch_state' in config and hasattr(pf_event, 'i_switch'):
                                pf_event.i_switch = config['switch_state']

                            print(f"[INFO]: Configured switch event '{event_name}': "
                                  f"time={config.get('time')}s, "
                                  f"state={config.get('switch_state')}")

                        else:  # Generic event
                            if 'time' in config:
                                pf_event.time = config['time']

                            print(f"[INFO]: Configured event '{event_name}': time={config.get('time')}s")

                        events_configured += 1
                    else:
                        print(f"[INFO]: Event '{event_name}' using default configuration")

            print(f"[DONE]: Events configuration complete. "
                  f"Configured: {events_configured}, Disabled: {events_disabled}")

            # Add variables to result object
            print(f"[INFO]: Adding monitoring variables...")
            total_vars = 0
            for element_type, variables in properties_data_name.items():
                elements = self.pf_app.GetCalcRelevantObjects(element_type)

                for elem in elements:
                    for var in variables:
                        try:
                            elmRes.AddVariable(elem, var)
                            total_vars += 1
                        except Exception as e:
                            pass

            print(f"[INFO]: Added {total_vars} monitoring variables")

            # Execute initial condition again after event configuration
            self.pf_app.EchoOff()
            comInc.Execute()
            self.pf_app.EchoOn()

            print(f"[INFO]: Running dynamic simulation...")
            result = comSim.Execute()

            if result != 0:
                raise RuntimeError(f"Simulation failed with error code: {result}")

            elmRes.Load()

            nCols = elmRes.GetNumberOfColumns()
            nRows = elmRes.GetNumberOfRows()
            print(f"[DONE]: Success running dynamic simulation")
            print(f"[INFO]: Results - Columns: {nCols}, Rows: {nRows}")

            print(f"[INFO]: Collecting simulation data...")
            
            # Prepare header
            header = ["Time_s"]
            for col in range(nCols):
                varName = elmRes.GetVariable(col)
                objName = elmRes.GetObject(col)
                header.append(f"{objName.loc_name}_{varName.replace(':', '_')}")
            
            # Collect data rows
            data_rows = []
            rows_collected = 0
            
            for row in range(nRows):
                time_val = elmRes.GetValue(row, -1)[1]

                # FILTER: Hanya ambil data dalam range waktu yang ditentukan
                if start_time_simulation <= time_val <= stop_time_simulation:
                    dataRow = [time_val]

                    for col in range(nCols):
                        value = elmRes.GetValue(row, col)[1]
                        dataRow.append(value)

                    data_rows.append(dataRow)
                    rows_collected += 1

            print(f"[DONE]: Success collecting simulation data")
            print(f"[INFO]: Total rows collected: {rows_collected}")

            elmRes.Release()

            # Return hasil sebagai dictionary
            result_data = {
                "project": self.proj_name,
                "study_case": choosen_case,
                "header": header,
                "data": data_rows,
                "rows": rows_collected,
                "columns": nCols,
                "start_time": start_time_simulation,
                "stop_time": stop_time_simulation,
                "step_size": step_size
            }

            return True, f"Success to run dynamic simulation. Rows collected: {rows_collected}", result_data

        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            error_message = f"Dynamic simulation error: {str(e)}\n\nDetails:\n{error_details}"
            print(error_message)
            return False, error_message, {}