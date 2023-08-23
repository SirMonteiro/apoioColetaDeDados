#!/bin/sudo sh
modprobe ftdi_sio
echo 12ec 2015 > /sys/bus/usb-serial/drivers/ftdi_sio/new_id