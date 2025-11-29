# **PROJECT PLTN HILIRISET NUKLIR** HMI-REAKTOR NUKLIR `[DIGSILENT POWER FACTORY INTEGRATION]`


## Digsilent Power Factory Library 
Create Ready to Use Library to connect `digsilent powerfactory` software untill now **`nov 2025`**. This library is use for connection, check the project, check the study case, running loadflow, and running dynamic simulation with costumizeable event such as `switch-event` or `short-circuit-event`. The documentation is provided in `library/example.ipynb`.

This library will soon published in `pypi` as the open library python that can be access with this such as class
```python
from digsilent_pf_lib import DigsilentPowerFactoryLibrary

dspf = DigsilentPowerFactoryLibrary(
    digsilent_path=r"C:\Program Files\DIgSILENT\PowerFactory 2024\Python\3.10",
    proj_name='39 Bus New England System',
    case_name="1. Power Flow"
)

# SUCCESS RETURN

status_conn_project, message_conn_project = dspf.connect_digsilent_pf_project(connect_to_project='39 Bus New England System')

print("status connection project :", status_conn_project)
print("message connection project :", message_conn_project)
```

## Digsilent Power Factory GUI `[Graphical User Interface]`
Create PyQt GUI to make a simple overview as HMI (Human Machine Intareface) in PLTN .pfd file that created with `Naufal Anwar`. This HMI is used to do automatication of pfd file in PLTN Project.

## Subprocess Template Communication

[flag] [status] [type] [message] [data] ... [additional-info]

- `[flag]` = FINISH | TERMINATE

- `[status]` = SUCCESS | ERROR

- `[type]` = DYANMIC | CONNECTANDSETUP | LOADFLOW | ..etc

- `[message]` = defined as str from the code flow

- `[data]` = data return **(be cautious of this, you `[as the developer]` have to parse string into the python readable and digestable data such as dictionary, list or event the tuple)**

**`REASON`** : digsilent power factory wont to be placed in non-main thread while your pyqt have to be placed in the main thread. That's why `[ach]` design this as the communication to separate pyqt thread and digsilent power factory thread into subprocess while the communication is being rule with `STDOUT` between them.

**`NOTES`**: use the template as it has to be used for.