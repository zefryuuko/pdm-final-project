# -------------------------------------- #
#     Google Assistant Home Control      #
#   using Dialogflow and HTTP Request    #
# -------------------------------------- #
#            Final Project By            #
#      Zefanya Gedalya - 2201796970      #
# -------------------------------------- #

import time
import logging
import json
from datetime import datetime as dt
from flask import Flask, request
from flask_assistant import Assistant, ask
from modules.consolelog import log
from modules.jsonhandler import JsonHandler as JSON
from modules.pluginloader import PluginLoader
from modules.backgroundhandler import BackgroundHandler


# ----- MAIN INITIALIZATION ----- #
timeAppStart = time.time()
log("MAIN", 0, "Initalizing Flask and Flask-Assistant...")
app = Flask(__name__)
assist = Assistant(app, route='/')

jsonConfigFile = JSON("config.json")
jsonDeviceList = JSON("devices.json")

ploader = PluginLoader("plugins")
plugins = ploader.getPlugins()
pluginNames = ploader.getPluginList()

log("MAIN", 0, "Running plugin background tasks...")
bgh = BackgroundHandler(plugins)
bgh.run()

if jsonConfigFile.json()["flaskLogging"] == 0:
    log("MAIN", 2,
        "flaskLogging is set to 0. Will not show flask command line output.")
    flasklogger = logging.getLogger('werkzeug')
    flasklogger.setLevel(logging.ERROR)
elif jsonConfigFile.json()["flaskLogging"] == 1:
    log("MAIN", 2,
        "flaskLogging is set to 0. Will show flask command line output.")

timeAppEnd = time.time()
log("MAIN", 0, "DONE in {}s".format(round((timeAppEnd - timeAppStart), 3)))


def sendData(plugin, id, value, param):
    for i in range(len(pluginNames)):
        if pluginNames[i].lower() == plugin.lower():
            if plugins[i].sendData(id, value, param):
                return True
    return False


def sendDataStr(plugin, id, value, param):
    for i in range(len(pluginNames)):
        if pluginNames[i].lower() == plugin.lower():
            return plugins[i].sendData(id, value, param)
    return False


def httpLogging(ip, path, method, time):
    log("MAIN", 0, "{} {} \"{}\" at {}".format(ip, method, path, time))


dflowErrMsg = "Something went wrong. Please check the console and try again."


# ----- HTTP REQUEST HANDLING ----- #


@app.route("/")
def httpRoot():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return "If you see this message, the program is running."


@app.route("/devices.json")
def httpDevicesJson():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return jsonDeviceList.toString()


@app.route("/config.json")
def httpConfigJson():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return jsonConfigFile.toString()


@app.route("/threads")
def httpThreadsList():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return str(bgh.getRunningThreads())


# returns only specific JSON key requested (<deviceID>) when called
@app.route("/devices/<deviceID>")
def httpDeviceJson(deviceID):
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    try:
        keyValue = str(jsonDeviceList.value(deviceID))
    except (KeyError):
        return '{"ERROR": "KeyError"}'
    else:
        return keyValue


# send command based on the device ID specified on the json file, and check
# if the plugin has the command or not.
@app.route("/devices/<deviceID>/<command>/<param>")
def sendCommand(deviceID, command, param):
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    # check if the deviceID is on the config.json file
    if deviceID in jsonDeviceList.json():
        pluginType = jsonDeviceList.json()[deviceID]["type"]
        pluginID = pluginNames.index(pluginType)

        # if the command requested is on the commands list on each plugin
        if command in plugins[pluginID].commands():
            cmdList = plugins[pluginID].commands()
            # check if the command is registered in the plugin's command list
            for i in range(0, len(cmdList)):
                if command == cmdList[i]:
                    if not plugins[pluginID].sendData(deviceID, command,
                                                      param):
                        return '{"return": "SendDataFalse"}'
        else:
            # fallback code
            return '{"return": "UnknownCommandError"}'

        return '{"return": "success"}'

    else:
        # if the key (deviceID) is not found
        return '{"return": "KeyError"}'


#  ----- DIALOGFLOW INTENT HANDLING ----- #

# Actions to do if "toggleOnOff" intent is triggered by voice or text
# via Google Assistant
@assist.action('toggleOnOff', mapping={'bool': 'boolean', 'obj': 'any'})
def dflowToggle(bool, obj):
    log("MAIN", 0, "Received \"toggleOnOff\" intent from Dialogflow.")
    keys = jsonDeviceList.json().keys()
    for i in keys:
        if jsonDeviceList.json()[i]["name"].lower() == obj.lower():
            if sendData(jsonDeviceList.json()[i]["type"], i, bool, ""):
                log("toggleOnOff", 0, "Command sent successfully")
                speech = "Ok. the {} is {}".format(obj, bool)
                return ask(speech)
            else:
                log("toggleOnOff", 2, "Command not sent.")
                return ask(dflowErrMsg)
        # else:
        #     return ask("Sorry, I don't see any device called " + obj)
    log("toggleOnOff", 2, "Command not sent (UnknownDevice:{})".format(obj))
    return ask("Sorry, I don't know a device called {}".format(obj))


# Actions to do if "appOpen" intent is triggered by voice or text
# via Google Assistant
@assist.action('appOpen', mapping={'app': 'appName', 'action': 'action',
                                   'device': 'deviceName'})
def dflowOpenApp(app, action, device):
    log("MAIN", 0, "Received \"appOpen\" intent from Dialogflow.")
    keys = jsonDeviceList.json().keys()
    for i in keys:
        if jsonDeviceList.json()[i]["name"].lower() == device.lower():
            response = sendDataStr(jsonDeviceList.json()[i]["type"], i, action,
                                   app)
            try:
                responseJSON = json.loads(response)
            except Exception as e:
                log("appOpen", 1, "Failed to parse response: {}".format(e))
                return ask(dflowErrMsg)
            else:
                log("appOpen", 0, "Successfully parsed response.")
                if responseJSON["return"] == "1":
                    log("appOpen", 0, "Action ran successfully.")
                    return ask("Ok.")
                else:
                    if responseJSON["msg"] == "ProcAlreadyRunning":
                        log("appOpen", 2, "Only one instance of {} is allowed"
                            .format(app))
                        return ask("I can't run multiple instances of {}."
                                   .format(app))
                    elif responseJSON["msg"] == "ProgNotFound":
                        log("appOpen", 2, "Unknown Program: {}".format(app))
                        return ask("I don't know a program called {}."
                                   .format(app))
                    elif responseJSON["msg"] == "InvalidAllowMultipleVal":
                        return ask("There's something wrong with your \
                        configuration file. Check the file and restart the\
                        Windows client, then try again.")
    log("appOpen", 2, "Response: {}".format(response))
    log("appOpen", 2, "Action failed to run.")
    return ask("I can't do that action for some reason. Check \
    the console for more information.")
