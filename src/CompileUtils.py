'''
    Compile Utils
    provide helper functions for compiling sweb + check the compiler output
'''

import os
import io
import subprocess

from SwebExceptions import *

class CompileUtils():

    COMPILE_TIMEOUT = 180
    RUN_TIMEOUT = 3*60

    oldUserProgsDir = "/tmp/old_user_progs.h"

    compileCommands = [ "mkdir -p /tmp/sweb",
                        "cd /tmp/sweb/",
                        "cmake /SWEB/",
                        "make -j"]

    #qemu-system-x86_64
    #QEMU_COMMAND = "qemu-system-x86_64 -m 8M -cpu qemu64 -drive file=SWEB.qcow2,index=0,media=disk -monitor none -nographics -debugcon"
    QEMU_COMMAND = ["qemu-system-x86_64", "-m", "8M", "-cpu", "qemu64", "-drive", "file=SWEB.qcow2,index=0,media=disk", "-monitor", "none", "-debugcon", "/dev/stdout"]

    oldUserProgs = None

    def __init__(self, workingDir):
        self.workingDir = workingDir

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

        '''
        compiling does fail when switching from hand<->testrunner. the repository
        needs then a fresh pull for whatever reason...
        '''

        f_stdout = open("/tmp/stdout", 'wt')
        f_stderr = open("/tmp/stderr", 'wt')

        ret = subprocess.run(["cmake", self.workingDir],
                            stderr=subprocess.DEVNULL,
                            universal_newlines=True,
                            shell=False,
                            timeout=self.COMPILE_TIMEOUT)

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

            f_stderr = open("/tmp/stderr", 'rt')
            errorText = f_stderr.read()
            f_stderr.close()
            raise NotCompileException(f'During compilation an error occoured!\n{errorText}')
            return

        print("SWEB compiled successfully!")
        f_stdout.close()
        f_stderr.close()

    def addTest(self, testsToRun) -> None:
        # TODO: change position to insert before shell!

        self.saveUserProgs()

        # find location where to insert new tests
        self.oldUserProgs = open(self.oldUserProgsDir, 'r+')
        oldUserProgsText = self.oldUserProgs.read()
        self.oldUserProgs.close()

        insertPos = oldUserProgsText.find('shell.sweb')
        insertPos = insertPos + 12

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

    def runTests(self) -> None:
        print("Starting Tests...")

        # ret = subprocess.Popen(["qemu-system-x86_64", "-m", "8M", "-cpu", "qemu64", "-drive", "file=SWEB.qcow2,index=0,media=disk", "-monitor", "none", "-nographics", "-debugcon"],
        #                         universal_newlines=True,
        #                         capture_output=True,
        #                         timeout=self.COMPILE_TIMEOUT)
        #output = subprocess.check_output("make -j", timeout=self.COMPILE_TIMEOUT)

        #os.chdir("/tmp/sweb/")
        ret = subprocess.Popen(self.QEMU_COMMAND, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = ret.communicate()

        print(stdout)
        print(stderr)

        #print(f'compiler returned with code {ret.returncode}')

        # find out how to conect to qemu...
        if ret.returncode != 0:
            # some error happened. catch that
            self.restoreUserProc()
            raise QemuRuntimeError(f'An error occoured during Qemu runtime! [Error: {ret.returncode}\n{stdout}]')

        #output = ret.check_output("")

        #output = subprocess.check_output((CATCH_COMMAND), stdin=ret.stdout)
        #ret.wait()

        raise NotImplementedError("This functionallity is not implemented yet!")