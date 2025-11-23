def connectandsetup(digsilent_path, proj_name):
    import sys
    import os

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} tidak terdeteksi")

        print(f"[INFO]: Activating project...")
        sys.path.append(f"{os.path.abspath(digsilent_path)}")
        import powerfactory as pf

        app = pf.GetApplication()
        if app is None:
            raise RuntimeError(
                "Tidak dapat membuka digsilent, coba perhatikan digsilent path anda atau terminate applikasi digsilent anda terlebih dahulu.")

        app.ClearOutputWindow()
        app.ResetCalculation()

        project = app.ActivateProject(proj_name)
        print(f"[DONE]: Berhasil mengaktivasi project")

        if project == None:
            raise TypeError(
                f"Tidak dapat mengaktifkan project {proj_name}, download pfd file dan load di digsilent terlebih dahulu.")

        print(f"[INFO]: Activasi study cases project...")
        study_case_folder = app.GetProjectFolder("study")
        print(f"[INFO]: Melakukan pengecekan pada study case")
        all_study_cases = study_case_folder.GetContents('*.IntCase')

        events_cases = {}

        if not all_study_cases:
            print("[WARNING]: Tidak ada study case yang terdeteksi")
            raise Exception("Study Case gagal di load.")

        for case in all_study_cases:
            case_name = case.loc_name
            print(f"[INFO]: Mengecek study case: {case_name}")
            case.Activate()

            event_folder = app.GetFromStudyCase('IntEvt')

            if event_folder is None:
                print(
                    f"[WARNING]: Study case '{case_name}' tidak memiliki event folder")
                events_cases[case_name] = []
                continue

            all_events = event_folder.GetContents()
            if not all_events:
                print(
                    f"[WARNING]: Study case '{case_name}' tidak memiliki event yang di setup")
                events_cases[case_name] = []
                continue

            # Menyimpan informasi event
            event_list = []
            for event in all_events:
                event_info = {
                    'name': event.loc_name,
                    'class': event.GetClassName(),
                }

                # Tambahkan informasi spesifik berdasarkan tipe event
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

            events_cases[case_name] = event_list
            print(
                f"[INFO]: {len(all_events)} event ditemukan di study case '{case_name}'")

        print(f"[DONE]: Berhasil mengecek semua study case")
        cases = [obj.loc_name for obj in all_study_cases]

        print(
            f"[DONE]: Berhasil mengkoneksikan digsilent power factory api dengan applikasi")
        return True, "Berhasil mengkoneksikan digsilent power factory api dengan applikasi", cases, events_cases

    except Exception as e:
        print(f"[ERROR]: Terjadi Error :{str(e)}")
        return False, f"Terjadi Error :{str(e)}", [], {}

def setup_load_showeddata(
    data_dictionary,
    project_name=None,
    case_name=None,
    output_dir="../data"
):
    data_voltage = []
    data_bus_phase_voltage = []
    label_bus = []
    label_gen = []
    active_power = []
    reactive_power = []

    import json
    import os
    from datetime import datetime

    for buss in data_dictionary.get("buses", []):
        label_bus.append(buss.get("name", "Unknown"))
        data_voltage.append(buss.get("voltage_kv", 0.0))
        data_bus_phase_voltage.append(buss.get("angle_deg", 0.0))

    for gen in data_dictionary.get("generators", []):
        label_gen.append(gen.get("name", "Unknown"))
        active_power.append(gen.get("P", 0.0))
        reactive_power.append(gen.get("Q", 0.0))

    # Susun data hasilnya
    result_data = {
        "generatorlabel": label_gen,
        "busslabel": label_bus,
        "busvoltage": data_voltage,
        "busphasevoltage": data_bus_phase_voltage,
        "generatoractivepower": active_power,
        "generatorreactivepower": reactive_power,
    }

    # Pastikan folder output ada
    os.makedirs(output_dir, exist_ok=True)

    # Buat nama file dinamis berdasarkan waktu
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    if project_name is not None or case_name is not None:
        filename = f"loadflow-{project_name}-{case_name}-{timestamp}.json"
    else:
        filename = f"loadflow-{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Simpan ke JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)

    return filepath

def safe_getattr(obj, attr, default=0):
    try:
        val = obj.GetAttribute(attr)
        if val is None:
            return default
        return val
    except:
        return default

def running_loadflow(
    digsilent_path,
    proj_name,
    case_name,
    output_dir="../data"
):
    import sys
    import os

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} does not exist")

        print(f"[INFO]: loadflow Activating project...")
        sys.path.append(rf"{digsilent_path}")
        import powerfactory as pf

        app = pf.GetApplication()

        if app is None:
            raise TypeError(f"Error: app is not initialized")
        app.ClearOutputWindow()

        project = app.ActivateProject(proj_name)
        print(f"[DONE]: Success activating project")

        if project is None:
            raise TypeError(f"Error: Project '{proj_name}' not found")

        print(f"[INFO]: Activating study cases project...")
        study_case_folder = app.GetProjectFolder("study")
        print(f"[INFO]: Validating all study cases project...")
        all_study_cases = study_case_folder.GetContents()

        if study_case_folder is None:
            raise ValueError(
                "[INFO]: Study case folder not found. Project mungkin tidak punya folder 'study'.")

        study_case = None
        for obj in all_study_cases:
            if obj.loc_name.strip() == case_name.strip():
                study_case = obj
                break

        if study_case is None:
            raise ValueError(
                f"[INFO]: Study case '{case_name}' not found in project '{proj_name}'")

        study_case.Activate()
        print(f"[DONE]: Success getting all study cases project")

        print(f"[INFO]: Running loadflow...")
        ldf = app.GetFromStudyCase("ComLdf")
        if ldf is None:
            raise TypeError(
                "Load flow command (ComLdf) not found in study case")

        ierr = ldf.Execute()
        if ierr != 0:
            raise RuntimeError(f"Load flow failed with error code {ierr}")
        print(f"[INFO]: Success running loadflow")

        insert_to = {
            "project": proj_name,
            "study_case": case_name,
            "buses": [],
            "generators": [],
            "lines": [],
            "loads": [],
            "transformers": [],
        }

        print(f"[INFO]: Collecting bus loadflow data...")
        buses = app.GetCalcRelevantObjects("*.ElmTerm")
        for bus in buses:
            insert_to["buses"].append({
                "name": bus.loc_name,
                "voltage_pu": bus.GetAttribute("m:u"),
                "voltage_kv": bus.GetAttribute("m:Ul"),
                "angle_deg": bus.GetAttribute("m:phiu"),
            })

        print(f"[INFO]: Collecting generator loadflow data...")
        gens = app.GetCalcRelevantObjects("*.ElmSym")
        for gen in gens:
            insert_to["generators"].append({
                "name": gen.loc_name,
                "P": safe_getattr(gen, "m:P:bus1"),
                "Q": safe_getattr(gen, "m:Q:bus1"),
                "I": safe_getattr(gen, "m:I:bus1"),
                "COSPHI": safe_getattr(gen, "m:cosphi:bus1"),
                "S": safe_getattr(gen, "m:S:bus1"),
                "I1": safe_getattr(gen, "m:i1:bus1"),
                "PHII1": safe_getattr(gen, "m:phii1:bus1"),
            })

        print(f"[INFO]: Collecting line loadflow data...")
        lines = app.GetCalcRelevantObjects("*.ElmLne")
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
        loads = app.GetCalcRelevantObjects("*.ElmLod")
        for load in loads:
            insert_to["loads"].append({
                "name": load.loc_name,
                "P_MW": load.GetAttribute("m:P:bus1"),
                "Q_Mvar": load.GetAttribute("m:Q:bus1"),
                "I_kA": load.GetAttribute("m:I:bus1"),
            })

        print(f"[INFO]: Collecting transformers loadflow data...")
        trafos = app.GetCalcRelevantObjects("*.ElmTr2")
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
        return True, "Success running loadflow and collect all the data", setup_load_showeddata(
            project_name=proj_name,
            case_name=case_name,
            data_dictionary=insert_to,
            output_dir=output_dir,
        )

    except Exception as e:
        return False, f"[DONE]: Error happened: {str(e)}", ""

# "ElmSym": ["s:xspeed", "m:P:bus1", "m:Q:bus1", "m:u:bus1", "m:fe"],
# "ElmTerm": ["m:u", "m:phiu", "m:fehz"],
# "ElmLne": ["m:P:bus1", "m:P:bus2", "m:Q:bus1", "m:Q:bus2", "m:I:bus1"],
# "ElmTr2": ["m:P:bushv", "m:P:buslv", "c:loading"],

def run_dynamic_simulation(
    digsilent_path,
    proj_name,
    case_name="Study Case",
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
    output_dir="../data"
):
    import sys
    import os
    import csv

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} is not exist")

        print(f"[INFO]: Activating project...")
        sys.path.append(rf"{digsilent_path}")
        import powerfactory as pf

        app = pf.GetApplication()
        if app is None:
            raise RuntimeError("Cannot get PowerFactory application.")

        app.ClearOutputWindow()
        app.ResetCalculation()
        print(f"[DONE]: Success activating project")

        project = app.ActivateProject(proj_name)
        if project is None:
            raise RuntimeError(f"Cannot activate project '{proj_name}'")

        print(f"[INFO]: Activating study case...")
        study_case = app.GetActiveStudyCase()
        if study_case is None:
            study_cases = app.GetProjectFolder(
                'study').GetContents('*.IntCase')
            for case in study_cases:
                if case.loc_name == case_name:
                    case.Activate()
                    study_case = case
                    break

            if study_case is None:
                raise RuntimeError(
                    f"Cannot find or activate study case '{case_name}'")
        print(f"[DONE]: Success activating study case")

        print(f"[INFO]: Setting up initial condition...")
        comInc = app.GetFromStudyCase("ComInc")
        comSim = app.GetFromStudyCase("ComSim")

        if comInc is None or comSim is None:
            raise RuntimeError(
                "Cannot get simulation commands (ComInc or ComSim)")

        comInc.iopt_sim = "rms"
        comInc.iopt_show = 0
        comInc.iopt_adapt = 0
        comInc.dtgrd = 30 # Integration time step
        comInc.dtout = step_size
        
        comInc.start = start_time_simulation
        comSim.tstop = stop_time_simulation

        comInc.Execute()
        elmRes = comInc.p_resvar
        print(f"[DONE]: Success running initial condition")

        if elmRes is None:
            raise RuntimeError("Cannot get result variable object")

        # Configure events berdasarkan events_config dari UI
        print(f"[INFO]: Configuring events...")
        event_folder = app.GetFromStudyCase('IntEvt')

        if event_folder is None:
            print("[WARNING]: No event folder found, creating one...")
            event_folder = app.GetFromStudyCase(
                '.').CreateObject('IntEvt', 'Simulation Events')

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
                    print(
                        f"[WARNING]: Event '{event_name}' not found in PowerFactory, skipping...")
                    continue

                # Set in service status
                if hasattr(pf_event, 'outserv'):
                    pf_event.outserv = 0 if in_service else 1
                elif hasattr(pf_event, 'i_outserv'):
                    pf_event.i_outserv = 0 if in_service else 1

                if not in_service:
                    events_disabled += 1
                    print(
                        f"[INFO]: Event '{event_name}' set to OUT OF SERVICE")
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
                                clear_event = event_folder.CreateObject(
                                    'EvtShc', clear_event_name)
                                clear_event.p_target = pf_event.p_target

                            clear_event.time = config['clear_fault']
                            clear_event.i_shc = 4  # Clear fault
                            clear_event.outserv = 0
                            print(
                                f"[INFO]: Clear fault event created/updated at {config['clear_fault']}s")

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

                        print(
                            f"[INFO]: Configured event '{event_name}': time={config.get('time')}s")

                    events_configured += 1
                else:
                    print(
                        f"[INFO]: Event '{event_name}' using default configuration")

        print(f"[DONE]: Events configuration complete. "
              f"Configured: {events_configured}, Disabled: {events_disabled}")

        # Add variables to result object
        print(f"[INFO]: Adding monitoring variables...")
        total_vars = 0
        for element_type, variables in properties_data_name.items():
            elements = app.GetCalcRelevantObjects(element_type)

            for elem in elements:
                for var in variables:
                    try:
                        elmRes.AddVariable(elem, var)
                        total_vars += 1
                    except Exception as e:
                        pass

        print(f"[INFO]: Added {total_vars} monitoring variables")

        # Execute initial condition again after event configuration
        app.EchoOff()
        comInc.Execute()
        app.EchoOn()

        print(f"[INFO]: Running dynamic simulation...")
        result = comSim.Execute()

        if result != 0:
            raise RuntimeError(f"Simulation failed with error code: {result}")

        elmRes.Load()

        nCols = elmRes.GetNumberOfColumns()
        nRows = elmRes.GetNumberOfRows()
        print(f"[DONE]: Success running dynamic simulation")
        print(f"[INFO]: Results - Columns: {nCols}, Rows: {nRows}")

        from datetime import datetime
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        print(f"[INFO]: Collecting simulation data...")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        datapath_result = os.path.join(
            output_dir, f"dynamic_sim_{case_name}_{timestamp}.csv")

        with open(datapath_result, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            # Header
            header = ["Time_s"]
            for col in range(nCols):
                varName = elmRes.GetVariable(col)
                objName = elmRes.GetObject(col)
                header.append(
                    f"{objName.loc_name}_{varName.replace(':', '_')}")
            writer.writerow(header)

            # Filter data berdasarkan start_time dan stop_time
            rows_written = 0
            for row in range(nRows):
                time_val = elmRes.GetValue(row, -1)[1]

                # FILTER: Hanya ambil data dalam range waktu yang ditentukan
                if start_time_simulation <= time_val <= stop_time_simulation:
                    dataRow = [time_val]

                    for col in range(nCols):
                        value = elmRes.GetValue(row, col)[1]
                        dataRow.append(value)

                    writer.writerow(dataRow)
                    rows_written += 1

        print(f"[DONE]: Success collecting simulation data")
        print(f"[INFO]: Data saved to: {datapath_result}")
        print(f"[INFO]: Total rows written: {rows_written}")

        elmRes.Release()

        return True, f"Success to run dynamic simulation. Rows written: {rows_written}", datapath_result

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_message = f"Dynamic simulation error: {str(e)}\n\nDetails:\n{error_details}"
        print(error_message)
        return False, error_message, "-"
