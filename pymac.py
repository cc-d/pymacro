#!/usr/bin/env python3
import pyautogui
import sys
import logging
import re
from myfuncs import logf
from threading import Thread
from time import sleep

logging.basicConfig(level=logging.INFO)


def WAIT(secs: float):
    """
    Pause the execution for a given number of seconds.

    Args:
        secs (float): The number of seconds to wait.
    """
    sleep(float(secs))


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
    ident = '  '

    curindex = None
    curline = None

    loopiter = None
    loopindex = None
    loopfor = None

    def __init__(self, pymfile: str = 'macros/hold-down.pym'):
        with open(pymfile, 'r') as f:
            self.lines = f.read().splitlines()
            self.maxlines = len(self.lines)
            self.maxindex = self.maxlines - 1
            self.curindex = 0

    def __repr__(self):
        return f'Macro<lineno={self.curindex} line={self.curline} ' + \
            f'loopfor={self.loopfor} loopiter={self.loopiter} loopindex={self.loopindex}>'

    @logf()
    def exec_line(self, exline=None):
        self.curline = exline
        print(f'{exline}')

        spline = self.curline.strip().split()
        cmd = str(spline[0]).upper()

        if cmd == 'WAIT':
            return WAIT(float(spline[1]))
        elif cmd == 'HOLD':
            return HOLD(str(spline[1]), float(spline[2]))
        elif cmd == 'PRESS':
            return PRESS(str(spline[0]))
        elif cmd == 'RESTART':
            return self.restart_macro()

    @logf()
    def start_macro(self):
        self.curindex = 0
        while self.curindex <= self.maxindex:
            self.exec_line(self.lines[self.curindex])
            self.curindex += 1

    @logf()
    def restart_macro(self):
        self.curindex = 0


def main():
    pymfile = 'macros/test.pym'
    if len(sys.argv) > 1:
        pymfile = str(sys.argv[1])

    pmac = Macro(pymfile)
    pmac.start_macro()

if __name__ == '__main__':
    main()