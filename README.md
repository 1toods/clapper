## Clapper

The idea is to write a test runner software for use with GitLab Runners and to test SWEB implementation.

## Tester Idea

The basic idea is to read the ``/userspace/tests/`` directory and put all the test files into ``common/include/kernel/user_progs.h``. After the tests run, remove all added tests from the file again to not mess with versioning.
To check if a test was successful read the output of the test.

## GitLab Runner

The runner should trigger the SWEB build after changing `user_progs.h`. So the runner can catch a failed build in the pipeline.

## Prerequisites

First dependencies must be installed with `pip3 install -r requirements.txt`.

### Prepare SWEB

Before you can start the runner, you should add the following line to a file in your SWEB repository:
`timeout 0`
This has to go in the file `utils/images/menu.list`.

### Passing Example Test

```
#include "stdio.h"

int main()
{
  // do something
  // when everything went fine...
  print("SUCCESS\n");
  return 0;
}
```

When no `SUCCESS` is being printed, or the test runs in a timeout (7 seconds), the runner automatically assumes that the test failed.

## Usage

Run normal docker:

`python3 src/main.py -s [SWEB DIRECTORY] [additional flags].`

Flags to choose from:

| Flag | Description                                                                                                                                                                                     |
| ---- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| -c   | Just compile.                                                                                                                                                                                   |
| -r   | Run test. specify just name, e.g: test for test.c in userspace/tests.                                                                                                                           |
| -a   | Run all tests Serialized, except of `multi` and `shell`. Boots SWEB for every test.                                                                                                                                        |
| -l   | List all tests in userspace/tests.                                                                                                                                                              |
| -t   | Timeout in seconds. Defaults to 7. This is also the time after which a test is shut down to check the output log. This means that the `timeout` flag also specifyes the runtime of each test. |
 | -b   | Run all found tests, except of `multi` and `shell`. No Boot between tests. [This does not work right now]

### Working Examples

Just compile SWEB:

```
python3 src/main.py -s ~/sweb/ -c
```

Run one test:

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
