#!/usr/bin/env python3
import argparse
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
    """This class represents a Macro, essentially a script that consists of a series of commands.

    The Macro class reads the commands from a file and then executes each command in sequence. The
    commands can be a variety of actions such as 'WAIT', 'HOLD', 'PRESS', and 'RESTART'. It also
    supports loops that repeat a sequence of commands.

    Attributes:
        start_delay (float): A delay (in seconds) before the macro starts.
        line_delay (float): A delay (in seconds) between each line/command.
        curindex (int): The current line/command index.
        curline (str): The current line/command.
        lines (List[str]): All lines/commands of the macro.
        maxlines (int): The total number of lines/commands.
        maxindex (int): The maximum index value (maxlines - 1).

    Returns:
        Macro: The Macro object with the commands loaded.
    """
    curindex = None
    curline = None

    def __init__(self,
        pymfile: str = 'm/test.pym',
        start_delay: float = 1.0,
        line_delay: float = 0.0
    ):
        with open(pymfile, 'r', encoding='utf8') as f:
            self.lines = f.read().splitlines()
            self.maxlines = len(self.lines)
            self.maxindex = self.maxlines - 1

        self.start_delay = start_delay
        self.line_delay = line_delay

    def __repr__(self):
        return f'Macro<lineno={self.curindex} line={self.curline}>'

    @logf()
    def exec_cmd(self, spline: list):
        """ Executes the post split/striped line

        Args:
            spline (list): list representing line from the pymacro file
        """
        cmd = str(spline[0])
        if cmd == 'WAIT':
            WAIT(float(spline[1]))
        elif cmd == 'HOLD':
            HOLD(str(spline[1]), float(spline[2]))
        elif cmd == 'PRESS':
            PRESS(str(spline[1]))
        elif cmd == 'RESTART':
            self.restart_macro()

    @logf()
    def exec_line(self, exline):
        """Executes a single line/command. Handles loop commands.

        Args:
            exline (str): The line/command to execute.
        """
        exline = str(exline)
        self.curline = exline

        if exline.startswith(' '):
            logging.debug(f'skipping in-loop line: {exline}')
            return

        logging.info(exline)

        spline = exline.strip().split()
        cmd = str(spline[0]).upper()

        # the one simple exception for our pymacro language, LOOPS!
        if cmd.startswith('LOOP'):
            loopfor = int(spline[1])
            loop, loopindex = [], self.curindex

            while loopindex < self.maxindex:
                loopindex = loopindex + 1
                loopline = str(self.lines[loopindex])
                if loopline.startswith(' '):
                    loop.append(loopline.strip().split())
                else:
                    break

            # execute every line idented after LOOP
            # only supports depth=1 currently as that's all i needed
            for i in range(loopfor):
                for l in loop:
                    self.exec_cmd(l)
        else:
            self.exec_cmd(spline)

    @logf()
    def start_macro(self):
        """ Starts iterating through and executing the lines in the macro file """
        self.curindex = 0
        sleep(self.start_delay)
        while self.curindex <= self.maxindex:
            self.exec_line(self.lines[self.curindex])
            self.curindex += 1
            sleep(self.line_delay)

    @logf()
    def restart_macro(self):
        """ resets macro file execution by setting the line execution index to 0 """
        self.curindex = 0


def main():
    """ this program is intended to be used by running this file directly """
    parser = argparse.ArgumentParser(description='Execute macros from a file.')

    parser.add_argument(
        'pymfile', type=str, nargs='?', default='m/test.pym',
        help='Path to the macro file'
    )
    parser.add_argument(
        '-s', '--start-delay', type=float, default=1.0,
        help='Delay (in seconds) before the macro starts'
    )
    parser.add_argument(
        '-l', '--line-delay', type=float, default=0.0,
        help='Delay (in seconds) between each line/command'
    )

    args = parser.parse_args()

    pmac = Macro(pymfile=args.pymfile, start_delay=args.start_delay, line_delay=args.line_delay)
    pmac.start_macro()


if __name__ == '__main__':
    main()
