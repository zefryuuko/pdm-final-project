# Program Design Methods Final Project:
# Google Assistant Voice Control
# --------------------------------------
# Program by
# Zefanya Gedalya B.L.T - 2201796970
# Student of Computer Science
# Binus University International
# --------------------------------------
# File Description (main.py)
# This file contains the main program. This file is what's responsible
# for handling webhook requests.

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

timeAppStart = time.time()      # Gets the time that the app started
log("MAIN", 0, "Initalizing Flask and Flask-Assistant...")
app = Flask(__name__)
assist = Assistant(app, route='/')

# Load the JSON files
jsonConfigFile = JSON("config.json")
jsonDeviceList = JSON("devices.json")

# Load plugins
ploader = PluginLoader("plugins")
plugins = ploader.getPlugins()
pluginNames = ploader.getPluginList()

# Run background tasks for each plugin
log("MAIN", 0, "Running plugin background tasks...")
bgh = BackgroundHandler(plugins)
bgh.run()

# Disables or enables the flask command line output depending on what the user
# had already set on config.json file.
if jsonConfigFile.json()["flaskLogging"] == 0:
    log("MAIN", 2,
        "flaskLogging is set to 0. Will not show flask command line output.")
    flasklogger = logging.getLogger('werkzeug')
    flasklogger.setLevel(logging.ERROR)
elif jsonConfigFile.json()["flaskLogging"] == 1:
    log("MAIN", 2,
        "flaskLogging is set to 0. Will show flask command line output.")

timeAppEnd = time.time()        # Gets the time that the app finished loading.
log("MAIN", 0, "DONE in {}s".format(round((timeAppEnd - timeAppStart), 3)))


# A function that handles data sending to a certain plugin that returns
# a boolean value
def sendData(plugin, id, value, param):
    for i in range(len(pluginNames)):
        if pluginNames[i].lower() == plugin.lower():
            if plugins[i].sendData(id, value, param):
                return True
    return False

# A function that handles data sending to a certain plugin that returns
# a string


def sendDataStr(plugin, id, value, param):
    for i in range(len(pluginNames)):
        if pluginNames[i].lower() == plugin.lower():
            return plugins[i].sendData(id, value, param)
    return False


# A function to log the HTTP request activities
def httpLogging(ip, path, method, time):
    log("MAIN", 0, "{} {} \"{}\" at {}".format(ip, method, path, time))


dflowErrMsg = "Something went wrong. Please check the console and try again."


# ----- HTTP REQUEST HANDLING ----- #
# This part of the code is mainly used for debugging purposes. Some of it is
# used to communicate between programs via the internet

# Shows the message when user opened "/" in the web browser, indicating that
# the program is running successfully
@app.route("/")
def httpRoot():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return "If you see this message, the program is running."


# Shows the devices.json file when user opened "/devices.json"
@app.route("/devices.json")
def httpDevicesJson():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return jsonDeviceList.toString()


# Shows the config.json file when user opened "/config.json"
@app.route("/config.json")
def httpConfigJson():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return jsonConfigFile.toString()


# Shows the list of running threads when the user opened "/threads"
@app.route("/threads")
def httpThreadsList():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return str(bgh.getRunningThreads())


# This function is simillar to @app.route("/devices.json"), but it
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


# Sends command based on the device ID specified on the json file, and check
# if the plugin has the command or not. This can be used for debugging, or
# for another program to commmunicate with each other
@app.route("/devices/<deviceID>/<command>/<param>")
def sendCommand(deviceID, command, param):
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)

    # check if the deviceID is on the devices.json file
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
# This part of the code handles the input from Google Assistant.

# Actions to do if "toggleOnOff" intent is triggered by voice or text
# via Google Assistant
@assist.action('toggleOnOff', mapping={'bool': 'boolean', 'obj': 'any'})
def dflowToggle(bool, obj):
    log("MAIN", 0, "Received \"toggleOnOff\" intent from Dialogflow.")
    keys = jsonDeviceList.json().keys()
    for i in keys:
        # Check if the device name that the user wanted to send command to\
        # exists in the devices.json
        if jsonDeviceList.json()[i]["name"].lower() == obj.lower():
            # If the data is sent successfully
            if sendData(jsonDeviceList.json()[i]["type"], i, bool, ""):
                log("toggleOnOff", 0, "Command sent successfully")
                speech = "Ok. the {} is {}".format(obj, bool)
                return ask(speech)
            else:
                log("toggleOnOff", 2, "Command not sent.")
                return ask(dflowErrMsg)
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
                # If the command ran successfully
                if responseJSON["return"] == "1":
                    log("appOpen", 0, "Action ran successfully.")
                    return ask("Ok.")
                else:
                    # This part handles the error message that will be told to
                    # the user when it encountered errors.
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
    # Shows the response from the plugin, to further investigate the error if
    # an error happened
    log("appOpen", 2, "Response: {}".format(response))
    log("appOpen", 2, "Action failed to run.")
    return ask("I can't do that action for some reason. Check \
    the console for more information.")
