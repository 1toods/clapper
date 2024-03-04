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
    RUN_TIMEOUT = 0

    oldUserProgsDir = "/tmp/clapper/old_user_progs.h"
    currentUserProgsDir = "/common/include/kernel/user_progs.h"
    stdOut = "/tmp/clapper/stdout"
    stdErr = "/tmp/clapper/stderr"
    stdIn = "/tmp/clapper/stdin"
    logsDirectory = "/tmp/clapper/logs/"

    QEMU_COMMAND = ["qemu-system-x86_64", "-m", "8M", "-cpu", "qemu64", "-drive", "file=SWEB.qcow2,index=0,media=disk", "-monitor", "none", "-nographic" ]# -serial stdio"]

    oldUserProgs = None
    testsToRun = [ ]

    def __init__(self, workingDir: str, timeout: int):
        self.workingDir = workingDir
        self.RUN_TIMEOUT = timeout
        open(self.oldUserProgsDir, 'w+').close()

    def getOldUserProgs(self) -> [ ]:
        userProgsText = ""

        if self.oldUserProgs is None:
            self.oldUserProgs = open(self.oldUserProgsDir, 'r+')
            userProgsText = self.oldUserProgs.read()
            userProgsFile.close()
        return userProgsText

    def saveUserProgs(self):
        self.oldUserProgs = open(self.oldUserProgsDir, 'w')

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
            raise NotCompileException(f'\nDuring compilation an error occoured!\n{errorText}')

        sys.stdout.write("finished.\n")
        sys.stdout.flush()

        f_stdout.close()
        f_stderr.close()

    def addTest(self, testToRun) -> None:
        # find location where to insert new tests
        userProgs = open(self.workingDir + self.currentUserProgsDir, 'r+')
        userProgsText = userProgs.read()
        userProgs.close()

        insertPos = userProgsText.find('automated testing')
        insertPos = insertPos + 17

        if insertPos == -1:
            raise ValueError("user_progs.h has to contain teh original comment on line 5 as reference!")

        # build insert string
        insertString = f'\n                            "/usr/{testToRun}",\n'

        # insert string
        prefixString = userProgsText[:insertPos]
        appendString = userProgsText[insertPos+1:]
        newUserProgs = prefixString + insertString + appendString

        # write string
        userProgs = open(f'{self.workingDir}common/include/kernel/user_progs.h', 'w+')
        userProgs.write(newUserProgs)
        userProgs.close()

    def restoreUserProc(self) -> None:
        oldUserProgsText = ""
        self.oldUserProgs = open(self.oldUserProgsDir, 'r+')

        oldUserProgsText = self.oldUserProgs.read()
        self.oldUserProgs.close()

        userProgs = open(f'{self.workingDir}common/include/kernel/user_progs.h', 'w+')
        userProgs.write(oldUserProgsText)
        userProgs.close()

    def _parseTestLogfile(self, logFileName: str) -> int:
        with open(logFileName, 'r') as logFile:
            for line in logFile:
                if "SUCCESS" in line:
                    print("PASS!")
                    return
            print("FAIL!")
    
    def _runQemu(self,logFileName: str, timeout: int) -> None:
        # TODO: configure so that gitlab runner sees the stdio output
        child = subprocess.Popen(
            self.QEMU_COMMAND + [ f'-debugcon', f'file:{logFileName}' ],
            stdout=subprocess.PIPE, # otherwise no userspace test output is in logfile!
            stderr=subprocess.PIPE,
            universal_newlines=True)

        # wait runtimeout and then kill the child
        time.sleep(self.RUN_TIMEOUT)
        child.terminate()

    def runTest(self, testName) -> None:
        os.chdir("/tmp/sweb/")
        logFileName = f'{self.logsDirectory}{testName}.log'

        sys.stdout.write(f'{testName}...')
        sys.stdout.flush()

        # run tests and parse output
        self._runQemu(logFileName, self.RUN_TIMEOUT)        
        self._parseTestLogfile(logFileName)

    def runMultipleTests(self, testsToRun: []) -> None:
        numTests = len(testsToRun)
        os.chdir("/tmp/sweb/")

        logFileName = f'{numTests}_tests.log'

        collectiveTimeout = self.RUN_TIMEOUT * numTests
        print(f'Waiting for tests to finish. This may take {collectiveTimeout} seconds.')
        
        # now start qemu
        self._runQemu(logFileName, collectiveTimeout)
        
        # and then parse logfile for every test
        passedTestsCounter = 0
        with open(logFileName, 'r') as logFile:
            for line in logFile:
                if "SUCCESS" in line:
                    passedTestsCounter += 1
        print(f'-> {passedTestsCounter} SUCCESFUL tests from {numTests} tests!')