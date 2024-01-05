#! /bin/bash

mkdir -p /tmp/sweb
cd /tmp/sweb
cmake /SWEB/
make -j
make qemu -nographic -append 'console=ttyS0'