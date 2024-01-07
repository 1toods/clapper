#! /bin/python3

import os
import time
import argparse

from CompileUtils import CompileUtils
from SwebExceptions import *

utils = CompileUtils()

def getAllTests() -> [ ]:
    tests = [ ]
    testFiles = os.listdir("/SWEB/userspace/tests/")
    # filter out unwanted files
    for file in testFiles:
        if file.endswith('.c'):
            fileName = file[:-2]
            if fileName == "shell":
                continue
            tests.append(f'{fileName}.sweb')
    return tests

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

    testsToRun = [ ]

    # check input arguments
    arguments = parser.parse_args()
    if arguments.list_tests:
        allTests = getAllTests()
        for test in allTests:
            print(test)
        return 0
    
    if arguments.run_all:
        utils.addTest(getAllTests())
        raise NotImplementedError("This functionallity is not implemented yet!")
    
    if arguments.run_test:
        allFoundTests = getAllTests()
        specifyedTests = [ ]
        for test in arguments.run_test:
            specifyedTests.append(f'{test}.sweb')

        if set(allFoundTests) != set(specifyedTests):
            raise TestNotFoundException("Your specifyed test was not found!")
        
        raise NotImplementedError("This functionallity is not implemented yet!")

    # configure sweb first!
    # search for available and/or specifyed tests and put them into user_progs.h

    utils.compileSWEB()

    # after that configure qemu to use text only and somehow connect its output
    # to be read

if __name__ == '__main__':
    main()