# Program Design Methods Final Project:
# Google Assistant Voice Control
# --------------------------------------
# Program by
# Zefanya Gedalya B.L.T - 2201796970
# Student of Computer Science
# Binus University International
# --------------------------------------
# File Description (backgroundhandler.py)
# Background Handler
# A class that handles background tasks for each plugin.

import threading
from modules.consolelog import log


class BackgroundHandler:
    # Initialize the object with a list that contains plugins.
    def __init__(self, plugins):
        log("BGHANDLER", 0, "Loaded {} plugins.".format(len(plugins)))
        self.__plugins = plugins

    # Runs all the plugins on the plugins list.
    def run(self):
        for plugin in self.__plugins:
            pName = plugin.getPluginID()
            log("BGHANDLER", 0, "Running {} background task...".format(pName))
            t = threading.Thread(target=plugin.backgroundTask,
                                 name=pName)
            t.start()

    # Gets the list of running threads
    def getRunningThreads(self):
        return threading.enumerate()
