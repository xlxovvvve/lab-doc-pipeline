#!/bin/bash
# ============ 实验一：动态库创建与调用 ============
# 执行账户：wht
cd /root/wht || exit 1

echo "### STEP1: 创建实验目录 ###"
sudo mkdir -p /root/wht+OtherHeadFiles /root/wht+OtherLibs
sudo chown -R wht:wht /root/wht+OtherHeadFiles /root/wht+OtherLibs
ls -ld /root/wht+OtherHeadFiles /root/wht+OtherLibs
sudo ls -l /root/ | grep wht

echo "### STEP2: 编写头文件 MyLib.h ###"
cat > /root/wht+OtherHeadFiles/MyLib.h << 'EOF'
#ifndef _MYLIB_H_
#define _MYLIB_H_
int add(int, int);
#endif
EOF
cat /root/wht+OtherHeadFiles/MyLib.h

echo "### STEP3: 编写 add.c ###"
cat > /root/wht/add.c << 'EOF'
#include <stdio.h>
#include "MyLib.h"
int add(int a, int b)
{
    return a + b;
}
EOF
cat /root/wht/add.c

echo "### STEP4: 编译生成 libadd.so ###"
cd /root/wht
gcc -fPIC -shared -I../wht+OtherHeadFiles/ -o libadd.so add.c
ls -l libadd.so
file libadd.so

echo "### STEP5: 移动动态库到 OtherLibs ###"
mv libadd.so /root/wht+OtherLibs/
ls -l /root/wht+OtherLibs/

echo "### STEP6: 编写 Compute.c ###"
cat > /root/wht/Compute.c << 'EOF'
#include <stdio.h>
#include "MyLib.h"
int main(void)
{
    int a = 3, b = 4;
    printf("%d + %d = %d\n", a, b, add(a, b));
    return 0;
}
EOF
cat /root/wht/Compute.c

echo "### STEP7: 编译链接生成 Compute ###"
gcc Compute.c -o Compute -I../wht+OtherHeadFiles/ -L../wht+OtherLibs/ -ladd
ls -l Compute
file Compute

echo "### STEP8: 设置 LD_LIBRARY_PATH ###"
export LD_LIBRARY_PATH=/root/wht+OtherLibs/:$LD_LIBRARY_PATH
echo $LD_LIBRARY_PATH

echo "### STEP9: 运行 Compute ###"
./Compute

echo "### STEP10: ldd 验证动态链接 ###"
ldd Compute
