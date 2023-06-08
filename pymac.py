#!/usr/bin/env python3
import pyautogui
import sys
import logging
from myfuncs import logf
from threading import Thread
from time import sleep

logging.basicConfig(level=logging.DEBUG)

class Macro:
    quit = False
    start_delay = 0
    line_delay = 0

    curindex = None
    curline = None

    def __init__(self, pymfile: str = 'macros/hold-down.pym'):
        with open(pymfile, 'r') as f:
            self.lines = f.read().splitlines()
        self.curindex = 0

    @logf()
    def parse_line(self, pymline: str):
        print(pymline)
        self.curline = pymline

        pymline = pymline.strip().split()
        pymline[0] = pymline[0].upper()

        if pymline[0] == 'WAIT':
            sleep(float(pymline[1]))
        elif pymline[0] == 'HOLD':
            holdkey = pymline[1]
            holdfor = float(pymline[2])
            pyautogui.keyDown(holdkey)
            sleep(holdfor)
            pyautogui.keyUp(holdkey)

        self.curindex += 1

    @logf()
    def start_macro(self):
        sleep(self.start_delay)
        maxindex = len(self.lines) - 1

        while self.quit is not True and self.curindex <= maxindex:
            self.parse_line(self.lines[self.curindex])

def main():
    pmac = Macro()
    pmac.start_macro()

if __name__ == '__main__':
    main()