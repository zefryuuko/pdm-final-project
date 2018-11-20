# bridge-windows-client
# A program to run commands sent by the bridge.
# github.com/zefryuuko
# ----------------------------------------------

import logging
import platform
import urllib.request
from flask import Flask, request
from datetime import datetime as dt
from modules.consolelog import log
import modules.appactions as actions
from modules.jsonhandler import JsonHandler as JSON
import json

# ----- INITIAL SETUP ----- #
log("MAIN", 0, "Initalizing Flask...")
app = Flask(__name__)
appStartTime = dt.now()

configJSON = JSON("config.json")
programList = open("programlist.json", 'r').read()

# Disable Flask logging other than errors.
flasklogger = logging.getLogger('werkzeug')
flasklogger.setLevel(logging.ERROR)


def httpLogging(ip, path, method, time):
    log("MAIN", 0, "{} {} \"{}\" at {}".format(ip, method, path, time))


# Get ngrok address from ngrok API
isGettingNgrokAdddr = True
log("MAIN", 0, "Getting ngrok address")
while isGettingNgrokAdddr:
    localNgrok = "http://localhost:4040/api/tunnels"
    try:
        response = str(urllib.request.urlopen(localNgrok).read())[2:-3]
    except Exception as e:
        log("MAIN", 1, e)
    else:
        responseJSON = json.loads(response)
        extNgrok = responseJSON["tunnels"][0]["public_url"]
        extNgrok = extNgrok.replace("http://", "")
        isGettingNgrokAdddr = False

# Send the address to the main program
log("MAIN", 0, "Sending ngrok address")
while True:
    addr = configJSON.json()["bridgeAddress"]
    deviceID = configJSON.json()["deviceID"]
    url = "{}/devices/{}/setaddr/{}".format(addr, deviceID, extNgrok)
    try:
        response = urllib.request.urlopen(url).read()[2:-1]
    except Exception as e:
        log("MAIN", 1, e)
    else:
        log("MAIN", 0, "Sent address to server successfully")
        break
    break
# ----- HTTP ROUTE ----- #


@app.route("/")
def routeRoot():
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)

    currentOS = platform.platform()
    content = "<h3>Bridge Windows Client</h3>" \
              "<p>{osname}</p>" \
              "<p>Process started at {startup}</p>"
    return content.format(osname=currentOS, startup=appStartTime)


@app.route("/run/<name>")
def routeOpen(name):
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return actions.open(programList, name)


@app.route("/kill/<name>")
def routeKill(name):
    time = dt.now().strftime("%Y/%m/%d %H:%M")
    httpLogging(request.remote_addr, request.path, request.method, time)
    return actions.close(programList, name)


@app.route("/ping")
def routePing():
    return "True"
