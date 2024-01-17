#! /bin/python3

import os
import time
import argparse

from CompileUtils import CompileUtils
from SwebExceptions import *

workingDir = ""

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
        utils.addTest(getAllTests())

    if arguments.run_test:
        allFoundTests = getAllTests()
        specifyedTests = [ ]

        for test in arguments.run_test:
            specifyedTests.append(f'{test}.sweb')

        for test in specifyedTests:
            if not (test in allFoundTests):
                raise TestNotFoundException(f'Your specifyed test "{test}" was not found!')

        utils.addTest(specifyedTests)

    # here comes the advanced stuff
    if not arguments.run_all and not arguments.run_test:
        utils.saveUserProgs()

    utils.compileSWEB()

    # if we just need to compile, return here
    if arguments.just_compile:
        return 0

    utils.runTests()

    # the last thing before exiting
    utils.restoreUserProc()

if __name__ == '__main__':
    main()