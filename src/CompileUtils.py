'''
    Compile Utils
    provide helper functions for compiling sweb + check the compiler output
'''

import os
import io
import sys
import time
import shlex
import subprocess
import pexpect

from SwebExceptions import *

class CompileUtils():

    COMPILE_TIMEOUT = 180
    RUN_TIMEOUT = 3*60

    oldUserProgsDir = "/tmp/clapper/old_user_progs.h"
    stdOut = "/tmp/clapper/stdout"
    stdErr = "/tmp/clapper/stderr"
    stdIn = "/tmp/clapper/stdin"
    logsDirectory = "/tmp/clapper/logs/"

    QEMU_COMMAND = ["qemu-system-x86_64", "-m", "8M", "-cpu", "qemu64", "-drive", "file=SWEB.qcow2,index=0,media=disk", "-monitor", "none", "-nographic" ]# -serial stdio"]

    oldUserProgs = None
    testsToRun = [ ]

    def __init__(self, workingDir):
        self.workingDir = workingDir
        open(self.oldUserProgsDir, 'w+').close()

    def getOldUserProgs(self) -> [ ]:
        userProgsText = ""

        if self.oldUserProgs is None:
            self.oldUserProgs = open(self.oldUserProgsDir, 'r+')
            userProgsText = self.oldUserProgs.read()
            userProgsFile.close()

        return userProgsText

    def saveUserProgs(self):
        if self.oldUserProgs is None:
            self.oldUserProgs = open(self.oldUserProgsDir, 'w+')

        userProgs = open(f'{self.workingDir}common/include/kernel/user_progs.h', 'r+')
        self.oldUserProgs.write(userProgs.read())

        self.oldUserProgs.close()
        userProgs.close()

    def compileSWEB(self) -> None:
        subprocess.run(["mkdir", "-p", "/tmp/sweb/"], stdout=subprocess.DEVNULL)
        os.chdir("/tmp/sweb/")

        f_stdout = open(self.stdOut, 'wt')
        f_stderr = open(self.stdErr, 'wt')

        sys.stdout.write("Configure SWEB...")
        sys.stdout.flush()

        ret = subprocess.run(["cmake", self.workingDir],
                            stderr=subprocess.DEVNULL,
                            universal_newlines=True,
                            shell=False,
                            timeout=self.COMPILE_TIMEOUT)

        sys.stdout.write("finished.\n")
        sys.stdout.flush()

        sys.stdout.write("Build SWEB...")
        sys.stdout.flush()

        ret = subprocess.run(["make", "-j"],
                            stdout=f_stdout,
                            stderr=f_stderr,
                            universal_newlines=True,
                            shell=True,
                            timeout=self.COMPILE_TIMEOUT)

        # this might have to be redone. this stops the compilation after first error.
        # if there is always the reason for the error printed, this is fine
        if ret.returncode != 0:
            f_stdout.close()
            f_stderr.close()

            f_stderr = open(self.stdErr, 'rt')
            errorText = f_stderr.read()
            f_stderr.close()
            raise NotCompileException(f'n\During compilation an error occoured!\n{errorText}')

        sys.stdout.write("finished.\n")
        sys.stdout.flush()

        f_stdout.close()
        f_stderr.close()

    def addTest(self, testsToRun) -> None:
        # TODO: change position to insert before shell!

        self.testsToRun = testsToRun

        self.saveUserProgs()

        # find location where to insert new tests
        self.oldUserProgs = open(self.oldUserProgsDir, 'r+')
        oldUserProgsText = self.oldUserProgs.read()
        self.oldUserProgs.close()

        #insertPos = oldUserProgsText.find('shell.sweb')
        insertPos = oldUserProgsText.find('automated testing')
        #insertPos = insertPos + 12
        insertPos = insertPos + 17

        if insertPos == -1:
            raise ValueError("user_progs.h needs to contain shell.sweb as reference!")

        # build insert string
        insertString = ""
        for test in testsToRun:
            insertString += f'\n                            "/usr/{test}",'
        insertString += '\n'

        # insert string
        prefixString = oldUserProgsText[:insertPos]
        appendString = oldUserProgsText[insertPos+1:]
        newUserProgs = prefixString + insertString + appendString

        userProgs = open(f'{self.workingDir}common/include/kernel/user_progs.h', 'w+')
        userProgs.write(newUserProgs)
        userProgs.close()

    def restoreUserProc(self) -> None:
        oldUserProgsText = ""
        self.oldUserProgs = open(self.oldUserProgsDir, 'r+') # cant find file!

        oldUserProgsText = self.oldUserProgs.read()
        self.oldUserProgs.close()

        userProgs = open(f'{self.workingDir}common/include/kernel/user_progs.h', 'w+')
        userProgs.write(oldUserProgsText)
        userProgs.close()

    def runTestsSeperated(self) -> None:
        print("Starting Tests:")

        # run tests seperated. restart qemu for every one.
        for testName in self.testsToRun:
            os.chdir("/tmp/sweb/")
            logFileName = f'{self.logsDirectory}{testName}.log'

            sys.stdout.write(f'{testName}...')
            sys.stdout.flush()

            # this does work and the shell output is being put into the logfile
            child = subprocess.Popen(
                self.QEMU_COMMAND + [ f'-debugcon', f'file:{logFileName}' ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                universal_newlines=True)

            # close io files if qemu had an error
            if child.returncode != 0:                
                print(f'Error during runtime [{child.returncode}]!\nStdERR: {child.stderr.read()}')
                child.terminate()
                continue

            # TODO: capture and analyze output

            child.wait()
        print("finished")