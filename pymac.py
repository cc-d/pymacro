#!/usr/bin/env python3
import pyautogui
import sys
import logging
import re
from myfuncs import logf
from threading import Thread
from time import sleep

logging.basicConfig(level=logging.DEBUG)

class MacroActions:
    @staticmethod
    def WAIT(secs: float):
        """
        Pause the execution for a given number of seconds.

        Args:
            secs (float): The number of seconds to wait.
        """
        sleep(float(secs))

    @staticmethod
    def HOLD(key: str, secs: float):
        """
        Hold a specified key for a given number of seconds.

        Args:
            key (str): The key to hold.
            secs (float): The number of seconds to hold the key.
        """
        secs = float(secs)
        pyautogui.keyDown(key)
        sleep(secs)
        pyautogui.keyUp(key)

    @staticmethod
    def PRESS(key: str):
        """
        Press a specified key.

        Args:
            key (str): The key to press.
        """
        pyautogui.press(key)


class Macro:
    quit = False
    start_delay = 2
    line_delay = 0

    curindex = None
    curline = None
    ma = MacroActions

    def __init__(self, pymfile: str = 'macros/hold-down.pym'):
        with open(pymfile, 'r') as f:
            self.lines = f.read().splitlines()
        self.curindex = 0

    @logf()
    def exec_line(self, exline=None):
        if exline is None:
            exline = self.curline

        spline = self.curline.split()
        cmd = spline[0]

        if cmd == 'WAIT':
            return self.ma.WAIT(float(spline[1]))
        elif cmd == 'HOLD':
            return self.ma.HOLD(str(spline[1]), float(spline[2]))
        elif cmd == 'PRESS':
            return self.ma.PRESS(str(spline[0]))
        elif cmd == 'RESTART':
            return self.restart_macro()

    @logf()
    def parse_line(self, pymline: str):
        print(pymline)
        self.curline = pymline
        self.exec_line()
        self.curindex += 1

    @logf()
    def start_macro(self):
        sleep(self.start_delay)
        maxindex = len(self.lines) - 1

        while self.quit is not True and self.curindex <= maxindex:
            self.parse_line(self.lines[self.curindex])

    @logf()
    def restart_macro(self):
        self.curindex = 0
        self.curline = None

def main():
    pymfile = 'macros/test.pym'
    if len(sys.argv) > 1:
        pymfile = str(sys.argv[1])

    pmac = Macro(pymfile)
    pmac.start_macro()

if __name__ == '__main__':
    main()