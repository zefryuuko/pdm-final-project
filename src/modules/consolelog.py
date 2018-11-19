# Program Design Methods Final Project:
# Google Assistant Voice Control
# --------------------------------------
# Program by
# Zefanya Gedalya B.L.T - 2201796970
# Student of Computer Science
# Binus University International
# --------------------------------------
# File Description (consolelog.py)
# A module to print out command line output with colors based on the message
# type

from colorama import init, Fore, Style
init()


def log(moduleName, type, string):
    # Coloring for types of console logging
    if type == 0:
        t = "{}INFO{}".format(Fore.BLUE, Style.RESET_ALL)
    elif type == 1:
        t = "{} ERR{}".format(Fore.RED, Style.RESET_ALL)
    elif type == 2:
        t = "{}WARN{}".format(Fore.LIGHTYELLOW_EX, Style.RESET_ALL)

    n = "{}{}{}".format(Fore.LIGHTCYAN_EX, moduleName, Style.RESET_ALL)
    print("{} [{}] {}".format(t, n, string))
