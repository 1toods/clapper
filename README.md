[![pipeline status](https://gitlab.tugraz.at/fatcookie/sweb_tester/badges/main/pipeline.svg)](https://gitlab.tugraz.at/fatcookie/sweb_tester/-/commits/main) 
[![coverage report](https://gitlab.tugraz.at/fatcookie/sweb_tester/badges/main/coverage.svg)](https://gitlab.tugraz.at/fatcookie/sweb_tester/-/commits/main) 

## TestRunner

The idea is to write a test runner software for use with GitLab Runners and to test SWEB implementation.

## Tester Idea

The basic idea is to read the ``/userspace/tests/`` directory and put all the test files into ``common/include/kernel/user_progs.h``. After the tests run, remove all added tests from the file again to not mess with versioning.
To check if a test was successful read the output of the test.

## GitLab Runner

The runner should trigger the SWEB build after changing `user:progs.h`. So the runner can catch a failed build in the pipeline.


### Other

Build this as a docker image and put the sweb folder as input directory.

## Usage
Build the container with `docker build -t sweb_tester .`.
Start container. Make sure to point your SWEB directory to `/SWEB/` inside the container.
Make sure to mount a RAM disk to `/tmp` inside the container to save SSD writes.

Run with:
```
docker run --rm -v ~/sweb/:/SWEB/ -v /tmp/:/tmp/ sweb_tester:latest
```