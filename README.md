
## Clapper

The idea is to write a test runner software for use with GitLab Runners and to test SWEB implementation.

## Tester Idea

The basic idea is to read the ``/userspace/tests/`` directory and put all the test files into ``common/include/kernel/user_progs.h``. After the tests run, remove all added tests from the file again to not mess with versioning.
To check if a test was successful read the output of the test.

## GitLab Runner

The runner should trigger the SWEB build after changing `user:progs.h`. So the runner can catch a failed build in the pipeline.

### Other

Build this as a docker image and put the sweb folder as input directory.

## Usage

Run without docker:

`python3 src/main.py -s [SWEB DIRECTORY] [additional flags].`

Flags to choose from:

| Flag | Description                                                          |
| ---- | -------------------------------------------------------------------- |
| -c   | just compile                                                         |
| -r   | run test. specify just name, e.g: test for test.c in userspace/tests |
| -a   | run all found tests.                                                 |
| -l   | list all tests in userspace/tests                                    |



Just compile SWEB: \

```
python3 src/main.py -s ~/sweb/ -c
```



Run one test: \

```
python3 src/main.py -s ~/sweb/ -r hello-world
```


Not Needed:
Build the container with `docker build -t sweb_tester .`.
Start container. Make sure to point your SWEB directory to `/SWEB/` inside the container.
Make sure to mount a RAM disk to `/tmp` inside the container to save SSD writes.

Run with:

```
docker run --rm -v ~/sweb/:/SWEB/ -v /tmp/:/tmp/ sweb_tester:latest
```

Maybe add an exclude function for not running a test...
