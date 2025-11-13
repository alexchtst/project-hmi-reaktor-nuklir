def connectandsetup(digsilent_path, proj_name):
    import sys
    import os

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} is not exist")

        sys.path.append(f"{os.path.abspath(digsilent_path)}")
        import powerfactory as pf

        app = pf.GetApplication()
        app.ClearOutputWindow()

        project = app.ActivateProject(proj_name)

        if project == None:
            raise TypeError(f"Error: project is none")

        study_case_folder = app.GetProjectFolder("study")
        all_study_cases = study_case_folder.GetContents()

        cases = [obj.loc_name for obj in all_study_cases]

        return True, "Success to connect with the digsilent python path api", cases
    except Exception as e:
        return False, f"Error happened :{str(e)}", ""


def setup_load_showeddata(data_dictionary, output_dir="../data"):
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
    filename = f"loadflow-{timestamp}.json"
    filepath = os.path.join(output_dir, filename)

    # Simpan ke JSON
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result_data, f, indent=4, ensure_ascii=False)


    return filepath



def running_loadflow(
    digsilent_path,
    proj_name,
    case_name,
    output_dir = "../data"
):
    import sys
    import os

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} does not exist")

        sys.path.append(rf"{digsilent_path}")
        import powerfactory as pf

        app = pf.GetApplication()
        
        if app is None:
            raise TypeError(f"Error: app is not initialized")
        app.ClearOutputWindow()

        project = app.ActivateProject(proj_name)
        if project is None:
            raise TypeError(f"Error: Project '{proj_name}' not found")

        study_case_folder = app.GetProjectFolder("study")
        all_study_cases = study_case_folder.GetContents()
        # print
        for obj in all_study_cases:
            
            pass

        study_case = None
        for obj in all_study_cases:
            if obj.loc_name.strip() == case_name.strip():
                study_case = obj
                break

        if study_case is None:
            raise ValueError(
                f"Study case '{case_name}' not found in project '{proj_name}'")

        study_case.Activate()
        

        ldf = app.GetFromStudyCase("ComLdf")
        if ldf is None:
            raise TypeError(
                "Load flow command (ComLdf) not found in study case")

        
        ierr = ldf.Execute()
        if ierr != 0:
            raise RuntimeError(f"Load flow failed with error code {ierr}")

        

        insert_to = {
            "project": proj_name,
            "study_case": case_name,
            "buses": [],
            "generators": [],
            "lines": [],
            "loads": [],
            "transformers": [],
        }

        
        buses = app.GetCalcRelevantObjects("*.ElmTerm")
        for bus in buses:
            insert_to["buses"].append({
                "name": bus.loc_name,
                "voltage_pu": bus.GetAttribute("m:u"),
                "voltage_kv": bus.GetAttribute("m:Ul"),
                "angle_deg": bus.GetAttribute("m:phiu"),
            })

        
        gens = app.GetCalcRelevantObjects("*.ElmSym")
        for gen in gens:
            insert_to["generators"].append({
                "name": gen.loc_name,
                "P": gen.GetAttribute("m:P:bus1"),
                "Q": gen.GetAttribute("m:Q:bus1"),
                "I": gen.GetAttribute("m:I:bus1"),
                "COSPHI": gen.GetAttribute("m:cosphi:bus1"),
                "S": gen.GetAttribute("m:S:bus1"),
                "I1": gen.GetAttribute("m:i1:bus1"),
                "PHII1": gen.GetAttribute("m:phii1:bus1"),
            })

        
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

        
        loads = app.GetCalcRelevantObjects("*.ElmLod")
        for load in loads:
            insert_to["loads"].append({
                "name": load.loc_name,
                "P_MW": load.GetAttribute("m:P:bus1"),
                "Q_Mvar": load.GetAttribute("m:Q:bus1"),
                "I_kA": load.GetAttribute("m:I:bus1"),
            })

        
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

        return True, setup_load_showeddata(insert_to, output_dir)

    except Exception as e:
        return False, f"Error happened: {str(e)}"

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
    start_fault=None,  # None = no fault
    clear_fault=None,
    fault_element_name=None,
    fault_element_type="ElmLne",
    fault_type=0,  # 0=3-phase short circuit
    step_size=0.01,
    properties_data_name={
        "ElmSym": ["m:P:bus1", "m:Q:bus1", "n:fehz:bus1"],
        "ElmTerm": ["m:fehz"],
        "ElmLne": [],
        "ElmTr2": [],
    },
    output_dir = "../data"
):
    import sys
    import os
    import csv

    try:
        if not os.path.exists(digsilent_path):
            raise OSError(f"{digsilent_path} is not exist")

        sys.path.append(rf"{digsilent_path}")
        import powerfactory as pf

        app = pf.GetApplication()
        if app is None:
            raise RuntimeError("Cannot get PowerFactory application.")

        app.ClearOutputWindow()
        app.ResetCalculation()

        project = app.ActivateProject(proj_name)
        if project is None:
            raise RuntimeError(f"Cannot activate project '{proj_name}'")

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

        comInc = app.GetFromStudyCase("ComInc")
        comSim = app.GetFromStudyCase("ComSim")

        if comInc is None or comSim is None:
            raise RuntimeError(
                "Cannot get simulation commands (ComInc or ComSim)")

        comInc.iopt_sim = "rms"      # RMS simulation
        comInc.iopt_show = 0         # No graphical output during simulation
        comInc.iopt_adapt = 0        # Fixed step size
        comInc.dtgrd = step_size     # Step size
        comInc.start = start_time_simulation  # Start time

        comSim.tstop = stop_time_simulation   # Stop time

        

        comInc.Execute()
        elmRes = comInc.p_resvar

        if elmRes is None:
            raise RuntimeError("Cannot get result variable object")

        faultFolder = app.GetFromStudyCase("Simulation Events/Fault.IntEvt")
        if faultFolder is not None:
            cont = faultFolder.GetContents()
            for obj in cont:
                obj.Delete()
            

        fault_configured = False
        if start_fault is not None and fault_element_name is not None:
            

            fault_element = None
            elements = app.GetCalcRelevantObjects(fault_element_type)
            for elem in elements:
                if fault_element_name in elem.loc_name:
                    fault_element = elem
                    break

            if fault_element is None:
                pass
            else:
                if fault_element_type == "ElmLne":
                    if hasattr(fault_element, 'ishclne'):
                        if fault_element.ishclne == 0:
                            fault_element.ishclne = 1

                event_fault = faultFolder.CreateObject(
                    "EvtShc", f"Fault_{fault_element.loc_name}")
                event_fault.p_target = fault_element
                event_fault.time = start_fault
                event_fault.i_shc = fault_type

                if clear_fault is not None:
                    event_clear = faultFolder.CreateObject(
                        "EvtShc", f"Clear_{fault_element.loc_name}")
                    event_clear.p_target = fault_element
                    event_clear.time = clear_fault
                    event_clear.i_shc = 4

                fault_configured = True
        else:
            pass

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


        app.EchoOff()
        comInc.Execute()
        app.EchoOn()

        result = comSim.Execute()

        if result != 0:
            raise RuntimeError(f"Simulation failed with error code: {result}")


        elmRes.Load()

        nCols = elmRes.GetNumberOfColumns()
        nRows = elmRes.GetNumberOfRows()


        from datetime import datetime
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        sim_type = "with_fault" if fault_configured else "no_fault"
        datapath_result = os.path.join(
            output_dir, f"dynamic_result_{sim_type}_{timestamp}.csv")

        with open(datapath_result, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)

            header = ["Time_s"]
            for col in range(nCols):
                varName = elmRes.GetVariable(col)
                objName = elmRes.GetObject(col)
                header.append(
                    f"{objName.loc_name}_{varName.replace(':', '_')}")
            writer.writerow(header)

            for row in range(nRows):
                time_val = elmRes.GetValue(row, -1)[1]
                dataRow = [time_val]

                for col in range(nCols):
                    value = elmRes.GetValue(row, col)[1]
                    dataRow.append(value)

                writer.writerow(dataRow)

        elmRes.Release()


        return True, "Success to run dynamic simulation", datapath_result

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        error_message = f"Error happened: {str(e)}\n\nDetails:\n{error_details}"
        return False, error_message, "-"
