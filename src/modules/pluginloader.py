# Program Design Methods Final Project:
# Google Assistant Voice Control
# --------------------------------------
# Program by
# Zefanya Gedalya B.L.T - 2201796970
# Student of Computer Science
# Binus University International
# --------------------------------------
# File Description (pluginloader.py)
# Plugin loader
# A class designed to dynamically load plugins (.py file) using importlib.

import importlib
import os
from modules.consolelog import log


class PluginLoader:
    # Gets the list of python files in the directory.
    def __getPlugins(self, pluginDir):
        for (dirpath, dirnames, filenames) in os.walk(pluginDir):
            x = []
            x.extend(filenames)
            x = x[::-1]
            xa = []
            for i in range(0, len(x)):
                if ".py" in x[i]:
                    x[i] = x[i].replace(".py", "")
                    xa.append(x[i])
            return xa

    # A method to construct the plugin and put the plugins in a list
    def __loadPlugin(self, pluginDir, pluginNameList):
        plugins = []
        for i in range(len(pluginNameList)):
            log("MAIN", 0, "Loading plugin {}".format(pluginNameList[i]))
            pluginFile = str(pluginDir) + "." + str(pluginNameList[i])
            currentPlugin = importlib.import_module(pluginFile, ".")
            plugins.append(currentPlugin.Plugin())
        return plugins

    def __init__(self, pluginDir):
        self.__pluginNameList = self.__getPlugins(pluginDir)
        self.__pluginList = self.__loadPlugin(pluginDir, self.__pluginNameList)

    def getPlugins(self):
        return self.__pluginList

    def getPluginList(self):
        return self.__pluginNameList
