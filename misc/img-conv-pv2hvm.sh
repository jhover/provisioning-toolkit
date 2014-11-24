#!/bin/bash

##=====================##
## Alexandr S. Zaytsev ##
## BNL, RACF (C) 2014 =##
## alezayt@bnl.gov ====##
##=====================##

dev_in=xvdm
dev_out=xvdo

umount /mnt 2> /dev/null

# --------------------------------------------------------

[ ! -z "$1" ] && dev_in=$1
[ ! -z "$2" ] && dev_out=$2

fdisk -l /dev/${dev_in} >& /dev/null
if [ $? != 0 ]; then
    echo -e "### Error: source device /dev/${dev_in} is not attached! Exiting..."
    exit 127
fi

fdisk -l /dev/${dev_out} >& /dev/null
if [ $? != 0 ]; then
    echo -e "### Error: destination device /dev/${dev_out} is not attached! Exiting..."
    exit 127
fi

# --------------------------------------------------------

echo -e "### Re-partitioning destination device (/dev/${dev_out})..."

parted /dev/${dev_out} --script 'rm 1'
parted /dev/${dev_out} --script 'mklabel msdos mkpart primary 1M -1s print quit'
partprobe /dev/${dev_out}
udevadm settle

echo "--- done"

# --------------------------------------------------------

echo -e "### Optimizing the file system on the source device (/dev/${dev_in})...\n"

e2fsck -f /dev/${dev_in}

echo

resize_msg=`resize2fs -M /dev/${dev_in} 2>&1`

echo -e "${resize_msg}"

src_fs_size=`echo -e "${resize_msg}"|grep 'blocks long'|sed 's/[^0-9]*//g'`

echo -e "\n--- done [FS-size:${src_fs_size}]"

# --------------------------------------------------------

echo -e "### Copying the source device (/dev/${dev_in}) to a partition on destination device (/dev/${dev_out})..."

dd if=/dev/${dev_in} of=/dev/${dev_out}1 bs=4K count=${src_fs_size}

echo "--- done"

# --------------------------------------------------------

echo -e "### Optimizing the file system on a partition of the destination device (/dev/${dev_out})..."

resize2fs /dev/${dev_out}1

echo "--- done"

# --------------------------------------------------------

echo -e "### Adjusting the OS configuration on the destination device (/dev/${dev_out})..."

mount /dev/${dev_out}1 /mnt

cp -a /dev/${dev_out} /dev/${dev_out}1 /mnt/dev/
rm -f /mnt/boot/grub/*stage*
cp /mnt/usr/*/grub/*/*stage* /mnt/boot/grub/
rm -f /mnt/boot/grub/device.map

cat <<EOF | chroot /mnt grub --batch
device (hd0) /dev/${dev_out}
root (hd0,0)
setup (hd0)
EOF

rm -f /mnt/dev/${dev_out} /mnt/dev/${dev_out}1

cp -f /mnt/boot/grub/menu.lst /mnt/boot/grub/menu.lst.cp
cat /mnt/boot/grub/menu.lst.cp|sed 's/(hd0)/(hd0,0)/;s/root=LABEL=\//root=LABEL=\/ console=ttyS0 xen_pv_hvm=enable/' > /mnt/boot/grub/menu.lst
rm -f /mnt/boot/grub/menu.lst.cp

echo -e "\n--- done"

# --------------------------------------------------------

echo -e "### Labling and unmounting destination device (/dev/${dev_out})..."

e2label /dev/${dev_out}1 /
sync
umount /mnt

echo "--- done"

# --------------------------------------------------------

echo "### Done."

exit 0
