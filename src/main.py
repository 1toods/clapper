#! /bin/python3

import os
import time
import argparse


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
        nargs='?',
        help='Specify test to run. If this argument is given, only the specifyed tests will run.'
    )

    arguments = parser.parse_args()

    print(arguments)

if __name__ == '__main__':
    main()