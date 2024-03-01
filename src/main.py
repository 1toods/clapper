#! /bin/python3

import os
import sys
import time
import argparse
import traceback

from CompileUtils import CompileUtils
from SwebExceptions import *

workingDir = ""

def init():
    if not os.path.exists("/tmp/clapper/"):
            os.makedirs("/tmp/clapper/")

    if not os.path.exists("/tmp/clapper/logs"):
        os.makedirs("/tmp/clapper/logs/")

def getAllTests() -> [ ]:
    tests = [ ]
    testFiles = os.listdir(f'{workingDir}userspace/tests/')
    # filter out unwanted files
    for file in testFiles:
        if file.endswith('.c'):
            fileName = file[:-2]
            if fileName == "shell":
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
    
    # this should be the default setting
    parser.add_argument(
        '-a',
        '--run-all',
        action='store_true',
        help='Runs all available tests in sequence.'
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

    # check input arguments
    arguments = parser.parse_args()

    if arguments.sweb_dir:
        global workingDir
        workingDir = arguments.sweb_dir[0]
    else:
        workingDir = "/SWEB/"

    changeToWorkingDir()
    utils = CompileUtils(workingDir)

    if arguments.list_tests:
        allTests = getAllTests()
        for test in allTests:
            print(test)
        return 0

    if arguments.run_all:
        print("Not implemented!")
        return

    testsToRun = [ ]
    if arguments.run_test:
        allFoundTests = getAllTests()
        #specifyedTests = [ ]

        # save all tests in a list
        for test in arguments.run_test:
            testsToRun.append(f'{test}.sweb')

        # double check if given tests actually exist
        for test in testsToRun:
            if not (test in allFoundTests):
                raise TestNotFoundException(f'Your specifyed test "{test}" was not found!')

    # here comes the advanced stuff
    if not arguments.run_all and not arguments.run_test:
        utils.saveUserProgs()

    # if we just need to compile, return here
    if arguments.just_compile:
        utils.compileSWEB()
        return 0

    # just in case
    utils.compileSWEB()

    # run all tests on its own
    utils.saveUserProgs()
    for test in testsToRun:
        utils.addTest(test)
        utils.runTest(test)
        utils.restoreUserProc()

if __name__ == '__main__':
    init()
    main()