from datetime import datetime as dt
from modules.consolelog import log
import json
import time
import urllib.request


class Plugin:
    def __openConfig(self):
        try:
            file = open("plugins/windowscontrol/config.json", "r").read()
        except (FileNotFoundError):
            log("WINDOWSCONTROL", 1, "Config file not found.")
            exit()
        except Exception as e:
            log("WINDOWSCONTROL", 1, "Error: {}".format(e))
        else:
            log("WINDOWSCONTROL", 0, "Loaded config.json")
            return json.loads(file)

    def __init__(self):
        self.__pluginIdentifier = "windowsControl"
        self.__commands = ["run", "kill", "check", "setaddr"]

        self.__configFile = self.__openConfig()
        self.__isDynamicAddress = self.__configFile["isDynamicAddress"]
        self.__desktopAddress = self.__configFile["desktopAddress"]
        self.__pingInterval = self.__configFile["pingInterval"]

        currentDT = dt.now().strftime("%Y/%m/%d %H:%M")
        log("WINDOWSCONTROL", 0, "WindowsControl initialized at {}"
            .format(currentDT))

    def commands(self):
        return self.__commands

    def getPluginID(self):
        return self.__pluginIdentifier

    def getPluginType(self):
        return self.__pluginType

    def backgroundTask(self):
        if self.__isDynamicAddress == 1:
            isAddrFound = False
            self.__desktopAddress = ""
            log("WINDOWSCONTROL", 2, "Desktop IP address is set to Dynamic.")
            log("WINDOWSCONTROL", 2, "Waiting for address...")
            while not isAddrFound:
                if self.__desktopAddress != "":
                    log("WINDOWSCONTROL", 0,
                        "Address received. Running background task.")
                    isAddrFound = True

            url = "http://{}/{}".format(self.__desktopAddress, "ping")
            while True:
                url = url.replace(" ", "%20")
                log("WINDOWSCONTROL", 0, "Requesting ON status...")
                try:
                    response = urllib.request.urlopen(url).read()[2:-1]
                except Exception as e:
                    log("WINDOWSCONTROL", 1, "ERROR: {}".format(e))
                else:
                    log("WINDOWSCONTROL", 0, "Windows Client is connected.")
                    self.__desktopAddress = response
                    time.sleep(self.__pingInterval*60)

    def sendData(self, id, value, param):
        if value == "run" or value == "kill":
            url = "http://{addr}/{cmd}/{app}".format(addr=self.__desktopAddress,
                                                     cmd=value, app=param)
            url = url.replace(" ", "%20")
            log("WINDOWSCONTROL", 0, "Requesting response from {}".format(url))
            response = json.loads(str(urllib.request.urlopen(url).read())[2:-1])
            return json.dumps(response)
        elif value == "setaddr":
            self.__desktopAddress = param
            log("WINDOWSCONTROL", 0, "Received machine IP Address: {}"
                .format(param))
