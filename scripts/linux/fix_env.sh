#!/bin/bash
# 修复：root 目录属主、sshd 可读 authorized_keys、创建 /root/wht、给 wht 免密 sudo
chown root:root /root
chmod 750 /root

# sshd 以 StrictModes 运行时，/root 及 authorized_keys 属主必须正确
chown -R root:root /root/.ssh
chmod 700 /root/.ssh
chmod 600 /root/.ssh/authorized_keys

# 建立实验主目录
mkdir -p /root/wht
chown wht:wht /root/wht
chmod 755 /root/wht

# 实验目录
mkdir -p /root/wht+OtherHeadFiles /root/wht+OtherLibs
chown -R wht:wht /root/wht+OtherHeadFiles /root/wht+OtherLibs

# 免密 sudo（覆盖之前的规则）
echo 'wht ALL=(ALL) NOPASSWD: ALL' > /etc/sudoers.d/wht-nopasswd
chmod 440 /etc/sudoers.d/wht-nopasswd
visudo -c 2>&1 | tail -2

echo "--- 校验 ---"
ls -ld /root /root/.ssh /root/.ssh/authorized_keys /root/wht /root/wht+OtherHeadFiles /root/wht+OtherLibs
echo "--- wht sudo 免密测试 ---"
su - wht -c 'sudo -n whoami && echo NOPASSWD_OK'
echo "--- wht 读写测试 ---"
su - wht -c 'echo hello > /root/wht/t.txt && cat /root/wht/t.txt && rm /root/wht/t.txt && echo WRITE_OK'
echo "--- sshd 状态 ---"
systemctl restart sshd
systemctl is-active sshd
