#!/bin/sh

echo "Cleaning index..."
dd if=/dev/zero of=out/index bs=1 count=2406399

echo "Unmounting partitions"
umount mnt2
umount mnt

echo "Which process to kill?"
ps aux|grep ./usb
