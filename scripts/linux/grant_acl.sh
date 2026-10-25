#!/bin/bash
# 让 wheel 组可进入 /root（实验目录在 /root 下，报告模板要求）
setfacl -m g:wheel:x /root 2>/dev/null || chmod 755 /root
echo "--- /root 权限 ---"
ls -ld /root
getfacl /root 2>/dev/null | head -8
echo "--- wht 进入 /root 测试 ---"
su - wht -c 'ls /root && echo ENTER_ROOT_OK'
su - wht -c 'ls -ld /root/wht /root/wht+OtherHeadFiles /root/wht+OtherLibs'
su - wht -c 'echo hi > /root/wht/t.txt && cat /root/wht/t.txt && rm -f /root/wht/t.txt && echo WRITE_OK'
