#!/usr/bin/env python3
import argparse
import pyautogui
import sys
import logging
import re
import os
from typing import List
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


@logf()
def read_macrofile(pymfile: str = 'macros/test.pym') -> list:
    """ this is its own func to allow easy logging with logf, returns macrofile lines as list """
    with open(pymfile, 'r+', encoding='utf8') as f:
        return f.read().splitlines()


@logf()
def write_macrofile(mlines: List[str], pymfile: str = 'macros/test.pym') -> list:
    """ this is its own func to allow easy logging with logf, writes list of lines to macrofile """
    mfstr = ''
    with open(pymfile, 'w', encoding='utf8') as f:
        mfstr = '\n'.join([l for l in mlines])
        logging.debug(f'writing macrofile: \n{mfstr}')
        f.write(mfstr)


@logf(level='info')
def format_macrolines(mlines: List[str]) -> List[str]:
    """ formats every line in a provided list according to expected pymfile format """
    formlines = []
    for l in mlines:
        fl = l

        inloop = False
        if l.startswith(' ') or l.startswith('\t'):
            inloop = True
            fl = l.replace('\t', '  ')

        fl = fl.strip().split()
        fl[0] = str(fl[0]).upper()
        fl = ' '.join(fl)

        if inloop:
            fl = '  ' + fl

        formlines.append(fl)
    return formlines


@logf(level='info')
def format_macrofile(pymfile: str = 'macros/test.pym') -> List[str]:
    """ replaces any lower case commands in macrofiles with upper and converts ident to 2 spaces """
    lines = read_macrofile()
    lines = format_macrolines(lines)
    write_macrofile(lines)


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
        pymfile: str = 'macros/test.pym',
        start_delay: float = 1.0,
        line_delay: float = 0.0
    ):
        self.lines = format_macrolines(read_macrofile(pymfile))
        write_macrofile(self.lines, pymfile)

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
        self.curindex = -1 # is incremented after to 0


@logf(level='info')
def select_pymfile(macdir: str = 'macros/') -> str:
    """ allows the users to select the macrofile using keyboard option rather than filename """
    pymfiles = [x for x in os.listdir(macdir)]

    choicestr = '\nSelect Macro File to execute: \n\n'

    for i in range(len(pymfiles)):
        choicestr += f'[{i + 1}] {pymfiles[i]}\n'

    print(choicestr)
    uc = input(f'Select Macrofile: ')
    return macdir + pymfiles[int(uc) - 1]


def main():
    """ this program is intended to be used by running this file directly """
    parser = argparse.ArgumentParser(description='Execute macros from a file.')

    parser.add_argument(
        'pymfile', type=str, nargs='?', default='',
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
    if args.pymfile == '':
        pymfile = select_pymfile()
    else:
        pymfile = args.pymfile

    pmac = Macro(pymfile=pymfile, start_delay=args.start_delay, line_delay=args.line_delay)
    pmac.start_macro()


if __name__ == '__main__':
    main()
