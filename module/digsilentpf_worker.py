from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot
from utils import resource_path, get_subprocess_startup_info
import sys
import subprocess

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
        events_config=None
    ):
        super().__init__()
        self.__digsilent_path = digsilent_path
        self.__proj_name = proj_name
        self.__case_name = case_name
        self.__start_sim = start_sim
        self.__stop_sim = stop_sim
        self.__sim_step = sim_step
        self.__events_config = events_config
        self._running = True
        self._current_process = None  # Tambahan: simpan referensi ke proses

    @pyqtSlot()
    def work_connectsetup(self):
        try:
            dgpath = self.__digsilent_path
            prjname = self.__proj_name

            if dgpath == None or prjname == None:
                raise TypeError("invalid input")

            self._current_process = subprocess.Popen(
                [
                    "python", resource_path("worker_connectandsetup.py"),
                    "--digsilent_path", dgpath,
                    "--project_name", prjname,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=get_subprocess_startup_info(),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0  
            )
            
            for line in iter(self._current_process.stdout.readline, ''):                    
                if not line or self._running == False:
                    break
                
                if "FINISH" in line:
                    line_data = line.strip().split("|")
                    
                    import base64
                    import json
                    events_data = {}
                    try:
                        if len(line_data) > 5 and line_data[5]:
                            events_json = base64.b64decode(line_data[5]).decode('utf-8')
                            events_data = json.loads(events_json)
                            
                    except Exception as e:
                        print(f"[WARNING]: Gagal decode events data: {str(e)}")
                    
                    self.finishpayload.emit({
                        "status": line_data[1],
                        "type": line_data[2],
                        "msg": line_data[3],
                        "data": line_data[4].split(",") if line_data[4] else [],
                        "events": events_data,
                    })
                    break
                
                if "TERMINATE" in line:
                    line_data = line.strip().split("|")
                    self.finishpayload.emit({
                        "status": line_data[1],
                        "type": line_data[2],
                        "msg": line_data[3],
                        "data": [],
                        "events": {},
                    })
                    break
                
                self.message.emit(line.strip())
                
            self._current_process.wait()
            
        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            print(err_msg)
            self.message.emit(err_msg)
        
        finally:
            self._cleanup_process()
            self.finished.emit()
    
    
    @pyqtSlot()
    def work_runloadflow(self):
        try:
            dgpath = self.__digsilent_path
            prjname = self.__proj_name
            casename = self.__case_name

            if dgpath == None or prjname == None or casename == None:
                raise TypeError("invalid input")
            
            self._current_process = subprocess.Popen(
                [
                    "python", resource_path("worker_runloadflow.py"),
                    "--digsilent_path", dgpath,
                    "--proj_name", prjname,
                    "--case_name", casename,
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=get_subprocess_startup_info(),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0  
            )

            for line in iter(self._current_process.stdout.readline, ''):
                if not line or self._running == False:
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
                
            self._current_process.wait()

        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            self.message.emit(err_msg)

        finally:
            self._cleanup_process()
            self.finished.emit()

    @pyqtSlot()
    def work_workdynamic(self):
        """Run dynamic simulation menggunakan subprocess"""
        try:
            sim_config = self.__events_config
            digsilent_path = sim_config.get('digsilent_path')
            proj_name = sim_config.get('proj_name')
            case_name = sim_config.get('case_name')
            start_time = sim_config.get('start_time_simulation')
            start_calc = sim_config.get('start_time_calc', None)
            stop_time = sim_config.get('stop_time_simulation')
            step_size = sim_config.get('step_size')
            events_config = sim_config.get('events_config', {})
            
            import json
            import base64
            
            # Clean events_config
            clean_events_config = {}
            for key, value in events_config.items():
                clean_events_config[key] = {
                    'event_data': {
                        'name': value['event_data'].get('name'),
                        'class': value['event_data'].get('class'),
                        'target': value['event_data'].get('target'),
                        'time': value['event_data'].get('time')
                    },
                    'in_service': value.get('in_service', True),
                    'configured': value.get('configured', False),
                    'config': value.get('config', {})
                }
            
            events_json = json.dumps(clean_events_config, ensure_ascii=False)
            events_encoded = base64.b64encode(events_json.encode('utf-8')).decode('utf-8')
            
            self._current_process = subprocess.Popen(
                [
                    "python", resource_path("worker_dynamic.py"),
                    "--digsilent_path", digsilent_path,
                    "--project_name", proj_name,
                    "--case_name", case_name,
                    "--start_time", str(start_time),
                    "--stop_time", str(stop_time),
                    "--step_size", str(step_size),
                    "--start_calc", str(start_calc),
                    "--events_config", events_encoded,
                    "--output_dir", "../data"
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,
                startupinfo=get_subprocess_startup_info(),
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0  
            )
            
            for line in iter(self._current_process.stdout.readline, ''):
                print(line.strip(), flush=True)
                
                if not line or self._running == False:
                    break
                
                if "FINISH" in line:
                    line_data = line.strip().split("|")
                    self.finishpayload.emit({
                        "status": line_data[1],
                        "type": line_data[2],
                        "msg": line_data[3],
                        "data": line_data[4] if len(line_data) > 4 else "",
                    })
                    break
                
                if "TERMINATE" in line:
                    line_data = line.strip().split("|")
                    self.finishpayload.emit({
                        "status": line_data[1],
                        "type": line_data[2],
                        "msg": line_data[3],
                        "data": "",
                    })
                    break
                
                self.message.emit(line.strip())
                
            self._current_process.wait()
            
        except Exception as e:
            err_msg = f"Error happened: {str(e)}"
            print(err_msg)
            self.message.emit(err_msg)
        
        finally:
            self._cleanup_process()
            self.finished.emit()

    def _cleanup_process(self):
        """Helper method untuk membersihkan proses"""
        if self._current_process:
            try:
                # Terminate proses dengan cara yang lebih agresif
                self._current_process.terminate()
                try:
                    self._current_process.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    # Jika terminate gagal, gunakan kill
                    self._current_process.kill()
                    self._current_process.wait()
            except Exception as e:
                print(f"Error cleaning up process: {str(e)}")
            finally:
                self._current_process = None

    def stop(self):
        """Stop worker dan kill proses DIgSILENT"""
        self._running = False
        self.message.emit("Stopping DIgSILENT process...")
        self._cleanup_process()