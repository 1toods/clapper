## TestRunner

The idea is to write a test runner software for use with GitLab Runners and to test SWEB implementation.

## Tester Idea

The basic idea is to read the ``/userspace/tests/`` directory and put all the test files into ``common/include/kernel/user_progs.h``. After the tests run, remove all added tests from the file again to not mess with versioning.
To check if a test was successful read the output of the test.

## GitLab Runner

see how this may work.
