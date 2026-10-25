#!/bin/bash
# ============ 实验二：make 与 makefile 配合 ============
# 执行账户：wht
cd /root/wht || exit 1

echo "### STEP1: 编写主函数 mystr.c ###"
cat > /root/wht/Del_str.h << 'EOF'
#ifndef _DEL_STR_H_
#define _DEL_STR_H_
void Del_str(char str[], char ch);
#endif
EOF
cat > /root/wht/Print_str.h << 'EOF'
#ifndef _PRINT_STR_H_
#define _PRINT_STR_H_
void Print_str(char str[]);
#endif
EOF
cat /root/wht/Del_str.h
cat /root/wht/Print_str.h

cat > /root/wht/mystr.c << 'EOF'
#include <stdio.h>
#include <string.h>
#include "Del_str.h"
#include "Print_str.h"

int main(void)
{
    char str[] = "Hello Linux, welcome to C Programming!";
    char ch;

    printf("Original string: %s\n", str);
    printf("Please input the character to delete: ");
    scanf("%c", &ch);

    Del_str(str, ch);
    Print_str(str);

    return 0;
}
EOF
cat /root/wht/mystr.c

echo "### STEP2: 编写删除函数 Del_str.c ###"
cat > /root/wht/Del_str.c << 'EOF'
#include <string.h>

void Del_str(char str[], char ch)
{
    int i, j = 0;
    for (i = 0; str[i] != '\0'; i++) {
        if (str[i] != ch) {
            str[j++] = str[i];
        }
    }
    str[j] = '\0';
}
EOF
cat /root/wht/Del_str.c

echo "### STEP3: 编写输出函数 Print_str.c ###"
cat > /root/wht/Print_str.c << 'EOF'
#include <stdio.h>

void Print_str(char str[])
{
    printf("String after deletion: %s\n", str);
}
EOF
cat /root/wht/Print_str.c

echo "### STEP4: 编写 makefile ###"
cat > /root/wht/Makefile << 'EOF'
CC = gcc
CFLAGS = -Wall
TARGET = Str
OBJS = mystr.o Del_str.o Print_str.o

all: $(TARGET)

$(TARGET): $(OBJS)
	$(CC) $(CFLAGS) -o $@ $(OBJS)

mystr.o: mystr.c Del_str.h Print_str.h
	$(CC) $(CFLAGS) -c mystr.c

Del_str.o: Del_str.c
	$(CC) $(CFLAGS) -c Del_str.c

Print_str.o: Print_str.c
	$(CC) $(CFLAGS) -c Print_str.c

clean:
	rm -f $(OBJS) $(TARGET)

.PHONY: all clean
EOF
cat /root/wht/Makefile

echo "### STEP5: 一键构建 make ###"
cd /root/wht
make

echo "### STEP6: 运行可执行程序 Str ###"
ls -l Str
echo "e" | ./Str

echo "### STEP7: 清理 make clean ###"
make clean
ls -l /root/wht/
