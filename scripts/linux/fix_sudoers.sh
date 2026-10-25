#!/bin/bash
echo "=== 修改前 ==="
sed -n '115,125p' /etc/sudoers
grep -n "includedir\|^wht" /etc/sudoers

# 把主 sudoers 里的 wht 规则直接改为 NOPASSWD
sed -i 's/^wht ALL=(ALL) ALL$/wht ALL=(ALL) NOPASSWD: ALL/' /etc/sudoers

echo "=== 修改后 ==="
grep -n "^wht" /etc/sudoers
visudo -c 2>&1 | tail -2
echo "=== 验证 ==="
su - wht -c 'sudo -n whoami && echo NOPASSWD_OK'
su - wht -c 'sudo -n ls -ld /root && echo ROOT_ACCESS_OK'
