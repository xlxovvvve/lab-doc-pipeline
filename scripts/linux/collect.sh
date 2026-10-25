#!/bin/bash
# 采集实验一/二的真实终端输出（带 wht 提示符），供报告截图渲染
cd /root/wht || exit 1

run() {
  echo "###CMD### $1"
  eval "$1" 2>&1
  echo "###END###"
}

{
echo "@@@SHOT1@@@"
run "sudo mkdir -p /root/wht+OtherHeadFiles /root/wht+OtherLibs && sudo chown -R wht:wht /root/wht+OtherHeadFiles /root/wht+OtherLibs && ls -ld /root/wht+OtherHeadFiles /root/wht+OtherLibs"

echo "@@@SHOT2@@@"
run "cat /root/wht+OtherHeadFiles/MyLib.h"

echo "@@@SHOT3@@@"
run "cat /root/wht/add.c"

echo "@@@SHOT4@@@"
run "cd /root/wht && gcc -fPIC -shared -I../wht+OtherHeadFiles/ -o libadd.so add.c && ls -l libadd.so && file libadd.so"

echo "@@@SHOT5@@@"
run "mv /root/wht/libadd.so /root/wht+OtherLibs/ && ls -l /root/wht+OtherLibs/"

echo "@@@SHOT6@@@"
run "cat /root/wht/Compute.c"

echo "@@@SHOT7@@@"
run "cd /root/wht && gcc Compute.c -o Compute -I../wht+OtherHeadFiles/ -L../wht+OtherLibs/ -ladd && ls -l Compute && file Compute"

echo "@@@SHOT8@@@"
run "export LD_LIBRARY_PATH=/root/wht+OtherLibs/:\$LD_LIBRARY_PATH && echo \$LD_LIBRARY_PATH"

echo "@@@SHOT9@@@"
run "cd /root/wht && ./Compute"

echo "@@@SHOT10@@@"
run "cd /root/wht && ldd Compute"

echo "@@@SHOT11@@@"
run "cat /root/wht/Del_str.h /root/wht/Print_str.h"

echo "@@@SHOT12@@@"
run "cat /root/wht/mystr.c"

echo "@@@SHOT13@@@"
run "cat /root/wht/Del_str.c"

echo "@@@SHOT14@@@"
run "cat /root/wht/Print_str.c"

echo "@@@SHOT15@@@"
run "cat /root/wht/Makefile"

echo "@@@SHOT16@@@"
run "cd /root/wht && make"

echo "@@@SHOT17@@@"
run "cd /root/wht && ls -l Str && echo e | ./Str"

echo "@@@SHOT18@@@"
run "cd /root/wht && make clean && ls -l /root/wht/"
} > /tmp/exp_out.txt 2>&1

echo "采集完成，字节数："
wc -c /tmp/exp_out.txt
