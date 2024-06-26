#! /bin/python3

import os
import sys
import time
import argparse
import traceback
from sys import exit
from signal import signal, SIGINT

from CompileUtils import CompileUtils
from SwebExceptions import *
from colorama import Fore, Back, Style

# in seconds
RUNNER_DEFAULT_TIMEOUT = 7
workingDir = ""
excludeTests = [ "shell", "mult", "clock_test", "fail_test" ]

compileUtils = None

def init():
    signal(SIGINT, keyboardInterruptHandler)

    if not os.path.exists("/tmp/clapper/"):
            os.makedirs("/tmp/clapper/")

    if not os.path.exists("/tmp/clapper/logs"):
        os.makedirs("/tmp/clapper/logs/")

# handle SIGINT and restore user progs
def keyboardInterruptHandler(signal, frame):
    global compileUtils
    compileUtils.restoreUserProc()
    sys.stdout.write("\n-> You killed the runner!\n")
    sys.stdout.flush()
    exit(0)

def getAllTests(noExclude=False) -> [ ]:
    tests = [ ]
    testFiles = os.listdir(f'{workingDir}userspace/tests/')
    # filter out unwanted files
    for file in testFiles:
        if file.endswith('.c'):
            fileName = file[:-2]
            if not noExclude:
                if fileName in excludeTests:
                    continue
            tests.append(f'{fileName}.sweb')
    return tests

def changeToWorkingDir() -> None:
    global workingDir
    if not os.path.exists(workingDir):
        os.makedirs(workingDir)
    os.chdir(workingDir)

def main():
    parser = argparse.ArgumentParser(
        prog='SWEB Tester',
        description='Testrunner for SWEB'
    )
    
    parser.add_argument(
        '-l',
        '--list-tests',
        action='store_true',
        help='Shows a list of available tests to run.'
    )

    parser.add_argument(
        '-r',
        '--run-test',
        nargs='+',
        help='Specify test to run. If this argument is given, only the specifyed test(s) will run. Just enter the name without file extention.'
    )

    parser.add_argument(
        '-c',
        '--just_compile',
        action='store_true',
        help='Just compiles SWEB. Nothing more.'
    )

    parser.add_argument(
        '-s',
        '--sweb-dir',
        nargs='+',
        help='Set specific SWEB directory. Do not use with docker.'
    )

    parser.add_argument(
        '-t',
        '--timeout',
        nargs='+',
        help='Specifyes timeout after which a test automatically fails if no SUCCESS flag has been found in the output log.'
    )

    parser.add_argument(
        '-a',
        '--serialized',
        action='store_true',
        help='Runs all tests serialized, but boots SWEB for every test.'
    )

    # check and parse input arguments
    arguments = parser.parse_args()

    runnerTimeout = RUNNER_DEFAULT_TIMEOUT
    if arguments.timeout:
        runnerTimeout = int(arguments.timeout[0])

    if arguments.sweb_dir:
        global workingDir
        workingDir = arguments.sweb_dir[0] + '/'
    else:
        workingDir = "/SWEB/"

    changeToWorkingDir()
    utils = CompileUtils(workingDir, runnerTimeout)

    global compileUtils
    compileUtils = utils

    if arguments.list_tests:
        allTests = getAllTests()
        for test in allTests:
            print(test)
        return

    # -r
    if arguments.run_test:
        testsFail = False
        allFoundTests = getAllTests(noExclude=True)
        testsToRun = [ ]

        sys.stdout.write("Compile SWEB...")
        sys.stdout.flush()
        utils.compileSWEB()
        print(Fore.GREEN + "PASS!" + '\033[39m')

        # save all tests in a list
        for test in arguments.run_test:
            # filter out shell and multi
            testsToRun.append(f'{test}.sweb')

        # double check if given tests actually exist
        utils.saveUserProgs()
        for test in testsToRun:
            if not (test in allFoundTests):
                raise TestNotFoundException(f'Your specifyed test "{test}" was not found!')
            if not utils.runTest(test, printLogOnFail=True):
                testsFail = True
            utils.restoreUserProc()
        sys.exit(1)

    # if we just need to compile, return here
    if arguments.just_compile:
        sys.stdout.write("Compile SWEB...")
        sys.stdout.flush()
        utils.compileSWEB()
        print(Fore.GREEN + "PASS!" + '\033[39m')
        return

    # seriaziled mode -a
    if arguments.serialized:
        # first try to compile, just once for user to see
        sys.stdout.write("Compile SWEB...")
        sys.stdout.flush()
        utils.compileSWEB()
        print(Fore.GREEN + "PASS!" + '\033[39m')

        testsFail = False
        testsToRun = getAllTests()
        utils.saveUserProgs()
        for test in testsToRun:
            # need to compile for every test for user_progs changes to apply
            utils.compileSWEB()
            if not utils.runTest(test, False):
                testsFail = True
            utils.restoreUserProc()
        
        # so gitlab ci detects an error
        if testsFail:
            sys.exit(1)

if __name__ == '__main__':
    init()
    main()