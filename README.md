# **PROJECT PLTN HILIRISET NUKLIR** HMI-REAKTOR NUKLIR `[DIGSILENT POWER FACTORY INTEGRATION]`


## Digsilent Power Factory Library 
[in progress]

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