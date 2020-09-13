#!/bin/bash -e

dd if=/dev/zero of="disk.img" bs=100K count=1
mkfs.fat "disk.img"

mknod /dev/loop0 b 7 0
LO_DEVICE=$(losetup --find --show "./disk.img")
MOUNT_DIR="webdir"

mkdir "${MOUNT_DIR}"
mount "${LO_DEVICE}" "${MOUNT_DIR}"

cp "main.go" \
   "flag_file.txt" \
   "list.gohtml" \
   "show.gohtml" "${MOUNT_DIR}/"

./main
