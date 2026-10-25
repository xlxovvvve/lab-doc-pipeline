#!/bin/bash
set -e
mkdir -p /home/wht/.ssh
cp /root/.ssh/authorized_keys /home/wht/.ssh/authorized_keys
chown -R wht:wht /home/wht/.ssh
chmod 700 /home/wht/.ssh
chmod 600 /home/wht/.ssh/authorized_keys
echo 'wht ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wht-nopasswd
chmod 440 /etc/sudoers.d/wht-nopasswd
echo "--- visudo check ---"
visudo -c 2>&1 | tail -2
echo "--- perms ---"
ls -ld /home/wht/.ssh
ls -l /home/wht/.ssh/authorized_keys
