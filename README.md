[![Build and Publish](https://github.com/1toods/clapper/actions/workflows/publish-image.yml/badge.svg)](https://github.com/1toods/clapper/actions/workflows/publish-image.yml)
## Clapper

This runner changes the `user_progs.h` file by adding a test and then compiling and starting SWEB with quemu. When the Test runs for the specifyed timeout, quemu gets stopped and the logfile gets checked. Unfortunally qemu does not write live to a logfile, so we need to wait for a timeout and can not check when a test has finished.

This script can be executed locally via python, in a docker container and is supposed to be used in a gitlab runner.

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

If some of your testcases take longer to run, then you can add them to the file src/set_biggertimeout.txt. These testcases will have a timeout of 17 seconds. The testcases which are not in the file will have the default timeout 7.


### Working Examples

Just compile SWEB:

```
python3 src/main.py -s ~/sweb/ -c
```

Run one test:

```
python3 src/main.py -s ~/sweb/ -r hello-world
```

Run all found tests with a custom timeout of 15 seconds:
```
python3 src/main.py -s ~/sweb/ -a -t 15
```

## Docker
Build the container with `docker build -t sweb_tester .`.
Start container. Make sure to point your SWEB directory to `/SWEB/` inside the container.
Make sure to mount a RAM disk to `/tmp` inside the container to save SSD writes.

Run with:

```
docker run --rm -v ~/path/to/sweb/repo/:/SWEB/ -v /tmp/:/tmp/ clapper:latest [ ARGUMENTS LIST ]
```

> Note that the `-s` argument is already passed to the runner via the Dockerfile, you just have to mount the right directory to the container.