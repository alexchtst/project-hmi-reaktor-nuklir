from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

class DigsilentWorker(QObject):
    finished = pyqtSignal()
    finishpayload = pyqtSignal(dict)
    message = pyqtSignal(str)

    def __init__(
        self,
        digsilent_path=None,
        proj_name=None,
        case_name=None,
        start_sim=None,
        stop_sim=None,
        sim_step=None,
        start_fault=None,
        stop_fault=None,
        fault_type=None,
    ):
        super().__init__()
        self.__digsilent_path = digsilent_path
        self.__proj_name = proj_name
        self.__case_name = case_name
        self.__start_sim = start_sim
        self.__stop_sim = stop_sim
        self.__sim_step = sim_step
        self.__start_fault = start_fault
        self.__stop_fault = stop_fault
        self.__fault_type = fault_type
        self._running = True

    @pyqtSlot()
    def work_connectsetup(self):
        print(f"Running connect and setup with {self.__proj_name} and {self.__digsilent_path}")
        try:
            dgpath = self.__digsilent_path
            prjname = self.__proj_name

            if dgpath == None or prjname == None:
                raise TypeError("invalid input")

            import subprocess
            with subprocess.Popen(
                [
                    "python", "worker_connectandsetup.py", # belom ada [TODO]: BUAT NANTI LEX
                    "--digsilent_path", dgpath,
                    "--project_name", prjname,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as prs:
                # print("Running digsilent worker line 54")
                for line in iter(prs.stdout.readline, ''):
                    if not line or self._running == False:
                        break
                    
                    if "FINISH" in line:
                        line_data = line.strip().split("|")
                        self.finishpayload.emit({
                            "status": line_data[1],
                            "msg": line_data[2],
                            "data": line_data[3].split(","),
                            "type": line_data[4]
                        })
                        break
                    
                    self.message.emit(line.strip())
                    
                prs.wait()
                # prs.kill()
        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            print(err_msg)
            self.message.emit(err_msg)
        
        finally:
            self.finished.emit()

    @pyqtSlot()
    def work_runloadflow(self):
        try:
            dgpath = self.__digsilent_path
            prjname = self.__proj_name
            casename = self.__case_name

            if dgpath == None or prjname == None or casename == None:
                raise TypeError("invalid input")
            
            import subprocess
            with subprocess.Popen(
                [
                    "python", "worker_runloadflow.py",
                    "--digsilent_path", dgpath,
                    "--proj_name", prjname,
                    "--case_name", casename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            ) as prs:

                for line in iter(prs.stdout.readline, ''):
                    if not line:
                        break

                    if "FINISH" in line:
                        line_data = line.strip().split("|")
                        self.finishpayload.emit({
                            "status": line_data[1],
                            "msg": line_data[2],
                            "path": line_data[3],
                            "type": line_data[4],
                        })
                        print({
                            "status": line_data[1],
                            "msg": line_data[2],
                            "path": line_data[3],
                            "type": line_data[4],
                        })
                        break
                    self.message.emit(line.strip())
                    
                prs.wait()
                # prs.kill()

        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            self.message.emit(err_msg)

        finally:
            self.finished.emit()

    @pyqtSlot()
    def work_workdynamic(self):
        try:
            dgpath = self.__digsilent_path
            prjname = self.__proj_name
            casename = self.__case_name
            start_sim = self.__start_sim
            stop_sim = self.__stop_sim
            sim_step = self.__sim_step
            start_fault = self.__start_fault
            stop_fault = self.__stop_fault
            fault_type = self.__fault_type

            if dgpath == None or prjname == None or casename == None:
                raise TypeError("invalid input")

            if (
                start_fault == None or 
                start_sim == None or 
                stop_sim == None or 
                stop_fault == None or 
                sim_step == None
                # fault_type == None
            ):
                raise TypeError("invalid input time")

            if (
                start_fault > stop_fault or
                stop_fault > stop_sim or
                start_sim > stop_sim or
                start_sim > start_fault
                # sim_step > abs(start_fault - stop_fault)
                # sim_step > abs(start_sim - stop_sim)
            ):
                raise TypeError("invalid input time")

            import subprocess
            with subprocess.Popen(
                [
                    "python", "worker_dynamic.py", # belom ada [TODO]: BUAT NANTI LEX
                    "--digsilent_path", dgpath,
                    "--project_name", prjname,
                    "--case_name", casename,
                    "--start_time", str(start_sim),
                    "--stop_time", str(stop_sim),
                    "--start_fault", str(start_fault),
                    "--clear_fault", str(stop_fault),
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                bufsize=1,
                text=True
                
            ) as prs :
                for line in iter(prs.stdout.readline, ''):
                    print(line.strip(), flush=True)
                    if not line:
                        break
                    
                    if "FINISH" in line:
                        line_data = line.strip().split("|")
                        print(line_data)
                        self.finishpayload.emit({
                            "status": line_data[1],
                            "msg": line_data[2],
                            "path": line_data[3],
                            "type": line_data[4],
                        })
                        break

                    self.message.emit(line.strip())
                    
                    print(line.strip(), flush=True)
                    
                prs.wait()
        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            print(err_msg)
            self.message.emit(err_msg)
            self.finishpayload.emit({
                "status": "ERROR",
                "msg": err_msg,
                "path": "...",
                "type": "DYNAMIC",
            })
            self.finished.emit()

        finally:
            self.finished.emit()

    def stop(self):
        self._running = False