import subprocess
import psutil
import os
import threading
import json


def __openProc(exec):
    try:
        subprocess.call(exec)
    except Exception:
        return False
    else:
        return True


def __isRunning(exec):
    if exec in (p.name() for p in psutil.process_iter()):
        return True
    else:
        return False
    return


def open(list, name):
    applist = json.loads(list)
    programs = applist["programs"]
    for program in programs:
        currentProgExec = program["exec"]
        currentProgName = program["name"]
        currentProgName = [name.lower() for name in currentProgName]
        currentProgMult = program["allowMultiple"]
        if name.lower() in currentProgName:
            if currentProgMult == 1:
                t = threading.Thread(target=__openProc,
                                     args=(currentProgExec, ))
                t.start()
                msg = '"name":"{}","return":"1","msg":"done"'.format(name)
                return '{' + msg + '}'
            elif currentProgMult == 0:
                progLoc = currentProgExec.split("\\")
                progExec = progLoc[len(progLoc)-1]
                if progExec not in (p.name() for p in psutil.process_iter()):
                    t = threading.Thread(target=__openProc,
                                         args=(currentProgExec, ))
                    t.start()
                    msg = '"name":"{}","return":"1","msg":"done"'.format(name)
                    return '{' + msg + '}'
                else:
                    msg = '"name":"{}","return":"0",\
                    "msg":"ProcAlreadyRunning"'.format(name)
                    return '{' + msg + '}'
            else:
                msg = '"name":"{}","return":"0","msg":\
                "InvalidAllowMultipleVal"'
                return '{' + msg + '}'
    msg = '"name":"{}","return":"0","msg":"ProgNotFound"'.format(name)
    return '{' + msg + '}'


def close(list, name):
    applist = json.loads(list)
    programs = applist["programs"]
    for program in programs:
        currentProgExec = program["exec"]
        currentProgName = program["name"]
        currentProgName = [name.lower() for name in currentProgName]
        if name.lower() in currentProgName:
            progLoc = currentProgExec.split("\\")
            progExec = progLoc[len(progLoc)-1]
            if __isRunning(progExec):
                os.system("taskkill /im {}".format(progExec))
                msg = '"name":"{}","return":"1","msg":"done"'.format(name)
                return '{' + msg + '}'
            else:
                msg = '"name":"{}","return":"0","msg":"ProcNotRunning"'
                return '{' + msg + '}'
    msg = '"name":"{}","return":"0","msg":"ProgNotFound"'
    return '{' + msg + '}'
