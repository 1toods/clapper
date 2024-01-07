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

    compileCommands = [ "mkdir -p /tmp/sweb",
                        "cd /tmp/sweb/",
                        "cmake /SWEB/",
                        "make -j"]

    oldUserProgs = ""

    def compileSWEB(self) -> None:
        subprocess.run(["mkdir", "-p", "/tmp/sweb/"], stdout=subprocess.DEVNULL)
        os.chdir("/tmp/sweb/")

        # ToDo: change this to in-memory files!
        # this raises a io.UnsupportedOperation: fileno exception
        #f_stdout = io.StringIO()
        #f_stderr = io.StringIO()

        f_stdout = open("/stdout", 'wt')
        f_stderr = open("/stderr", 'wt')

        ret = subprocess.run(["cmake", "/SWEB/"],
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

            f_stderr = open("/stderr", 'rt')
            errorText = f_stderr.read()
            f_stderr.close()
            
            raise NotCompileException(f'During compilation an error occoured!\n{errorText}')

        else:
            print("SWEB compiled successfully!")
            f_stdout.close()
            f_stderr.close()

    def addTest(self, testsToRun) -> None:
        userProgs = open("/SWEB/common/kernel/user_progs.h", 'r+')
        oldUserProgs = userProgs.read()

        # find location where to insert new tests
        insertPos = userProgs.find('"/usr/shell.web",')
        if insertPos == -1:
            raise ValueError("user_progs.h needs to contain shell.sweb as reference!")

        # insert tests
        for test in testsToRun:
            pass