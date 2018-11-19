# PowerControl plugin
# a plugin to control power outlet or lights using the Mosquitto protocol
# https://github.com/zefryuuko
# ------------------------------------------------------------------------

from datetime import datetime as dt
import json
import threading
from modules.consolelog import log
# import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import paho.mqtt.subscribe as subscribe


class Plugin:
    # function to open the configuration file
    def __openConfig(self):
        try:
            file = open("plugins/powercontrol/config.json", "r").read()
        except (FileNotFoundError):
            log("POWERCONTROL", 1, "Config file not found.")
            exit()
        else:
            log("POWERCONTROL", 0, "Loaded config.json")
            return json.loads(file)

    # plugin initialzation
    def __init__(self):
        self.__pluginIdentifier = "powerControl"
        self.__commands = ["on", "off", "toggle"]

        # loads the config.json and set each keys to a variable
        self.__configFile = self.__openConfig()
        self.__MQTT_ADDRESS = self.__configFile["MQTT_ADDRESS"]
        self.__MQTT_PORT = self.__configFile["MQTT_PORT"]
        self.__MQTT_KEEPALIVE = self.__configFile["MQTT_KEEPALIVE"]
        self.__MQTT_RESPONSE_TIMEOUT = self.__configFile[
            "MQTT_RESPONSE_TIMEOUT"]

        currentDT = dt.now().strftime("%Y/%m/%d %H:%M")
        log("POWERCONTROL", 0, "PowerControl initialized at {}"
            .format(currentDT))

        # temporary variable for thread returns
        self.__tempVerifyThread = []

    def commands(self):
        return self.__commands

    def getPluginID(self):
        return self.__pluginIdentifier

    def getPluginType(self):
        return self.__pluginType

    def backgroundTask(self):
        log("POWERCONTROL", 2, "No background task. Quitting thread...")

    def __simpleSubscribe(self, topic):
        msgRcv = subscribe.simple(topic, hostname=self.__MQTT_ADDRESS,
                                  port=self.__MQTT_PORT,
                                  keepalive=self.__MQTT_RESPONSE_TIMEOUT,
                                  msg_count=1)
        self.__tempVerifyThread.append(str(msgRcv.payload)[2:-1])

    def sendData(self, id, val, param):
        if val == "on":
            value = 1
        elif val == "off":
            value = 0
        elif val == "toggle":
            value = 2

        log("POWERCONTROL", 0, "Sending value '{}' in key '{}' to {}"
            .format(value, id, self.__MQTT_ADDRESS))
        try:
            self.__tempVerifyThread = [""]
            publish.single(id, value, hostname=self.__MQTT_ADDRESS,
                           port=self.__MQTT_PORT,
                           keepalive=self.__MQTT_KEEPALIVE)
        except Exception as e:
            log("POWERCONTROL", 1, "{}".format(e))
            return False
        else:
            log("POWERCONTROL", 0, "Successfully sent to MQTT broker.")
            log("POWERCONTROL", 0, "Waiting for verification...")
            try:
                verifyThread = threading.Thread(target=self.__simpleSubscribe,
                                                args=(id+"R",))
                verifyThread.start()
                verifyThread.join(timeout=self.__MQTT_RESPONSE_TIMEOUT)
                msgRcv = self.__tempVerifyThread.pop()
            except Exception as e:
                log("POWERCONTROL", 1, e)
                return False
            else:
                if msgRcv == "MSGRCV {} {}".format(id, value):
                    log("POWERCONTROL", 0,
                        "Successfully received verification request.")
                    return True
                else:
                    log("POWERCONTROL", 1, "Request timed out.")
                    return False
