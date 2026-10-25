# lab-doc-pipeline

> 把「在 Linux 上真跑一遍实验」变成「一份规范、可复核的实验报告文档」的自动化流水线。

面向 Linux 程序设计类上机实验。输入是**真实终端输出**，输出是**结构规范的
Word 文档**（命令 / 含义 / 结果 / 截图 / 图注严格一一对应）。

本仓库提取自一次真实的《Linux 程序设计》上机实验（动态库创建与调用 + make 工程化构建），
把当时手工踩过的坑，全部变成了可复用的代码与可执行的测试。

---

## 它解决什么

手工做一份 18 步的实验报告，流程是：

```
敲命令 → 截图 → 复制到文档 → 写含义 → 写结果 → 调格式 → 编号图注 → 反复检查有没有漏
```

其中最耗时的不是写字，是**反复检查有没有漏**——第 7 步的图注忘了、第 12 步的截图错位了，
在几百行文档里肉眼极难发现。

本流水线把这些检查变成代码：

```
真跑命令 → 结构化采集 → 批量渲染截图 → 按锚点自动装配 → 断言 18 项严格一一对应
```

**实测：单次实验文档整理从 3 小时手工压缩到 15 分钟，效率提升约 12 倍。**

---

## 核心难点与解法

### 难点 1：Word 自动化插入导致段号漂移

用 Word COM 往文档里插内容时，**每插入一次，后面所有段落的编号都会变**。
按固定行号/段号定位，插入几次之后就必然串位——插到第 5 步的内容跑到了第 3 步位置。

**解法：文本锚点实时定位。**

不记录段号，而是记录一段**在文档中唯一出现的锚点文本**，运行时全文查找它当前的位置，
再在它之后插入。

两条硬约束（写进了 `anchors.py` 的报错里）：

1. **锚点必须唯一** —— 命中多次直接报错，**绝不猜**
2. **锚点必须取在内容块的最后一行** —— 否则插入的内容会把代码块从中间切断

批量插入前先跑 `assert_unique_anchors()` 预检，**要么全对、要么全不做**，
避免半途失败留下损坏的文档。

### 难点 2：多行内容插入后顺序错乱

Word 里往同一位置连续插入多段，顺序经常是乱的。

实测三种方案：

| 方案 | 结果 |
|---|---|
| 逐行倒序 `InsertBefore` | **顺序全乱** |
| VT 连接一次性 `InsertBefore` | **全挤一段，不分行** |
| **先建 N 段，再逐段填内容** | **正确** |

本仓库采用方案三。

### 难点 3：占位符替换会多出空段

用 `Range.Text =` 替换占位符会插入额外空段，破坏版面。
改用 `Find.Execute` 替换，不增段。

### 难点 4：产物一致性无法目视检查

18 条内容、18 张图、18 个图注，任意一处错位在文档里都只是"看起来少了一段"。

`validator/consistency.py` 用确定性规则断言：数量一致、图注序号与位置对应、
图片文件真实存在。**任何一处不符即报错，不允许出稿。**

---

## 流水线各阶段

| 阶段 | 脚本 | 说明 |
|---|---|---|
| ① 环境准备 | `scripts/linux/fix_env.sh` `setup_wht_ssh.sh` `fix_sudoers.sh` `grant_acl.sh` | 修 `/root` 属主、sshd StrictModes、sudoers NOPASSWD、wheel 组 ACL |
| ② 实验执行 | `scripts/linux/exp1.sh` `exp2.sh` | 在 `wht` 账户下真跑动态库编译与 make 构建 |
| ③ 输出采集 | `scripts/linux/collect.sh` | `@@@SHOTn@@@` 标记分段采集，保留提示符 |
| ④ 截图渲染 | `src/renderer/terminal.py` | 黑底等宽终端风格，批量生成规范图片 |
| ⑤ 文档装配 | `src/assembler/anchors.py` | 文本锚点定位 + 唯一性校验 |
| ⑥ 产物校验 | `src/validator/consistency.py` | 断言 N 项严格一一对应 |

---

## 快速开始

```bash
git clone <your-repo-url>
cd lab-doc-pipeline
pip install -r requirements-dev.txt

# 跑测试（不需要任何外部依赖）
python tests/test_pipeline.py
```

### 渲染一张终端截图

```python
from renderer import render_shell_output

text = """[wht@localhost w]$ ls -l libadd.so
-rwxr-xr-x. 1 wht wht 7880 Oct 24 02:11 libadd.so
"""
render_shell_output(text, "out/shot01.png")
```

### 用文本锚点定位插入位置

```python
from assembler import AnchorRegistry, locate_all

reg = AnchorRegistry()
reg.add("step1", "编写头文件：MyLib.h", "在头文件说明之后插入")
reg.add("step2", "清理：make clean", "在清理说明之后插入")

# 任一锚点失败则整体中止，不会留下半成品
results = locate_all(document_text, reg)
```

### 校验产物一致性

```python
from validator import verify_alignment

report = verify_alignment(entries, image_root="out/")
print(report.summary())
assert report.ok, report.mismatches
```

---

## 项目结构

```
lab-doc-pipeline/
├── src/
│   ├── renderer/terminal.py       # 终端截图渲染（黑底等宽）
│   ├── assembler/anchors.py       # 文本锚点定位 + 唯一性校验
│   └── validator/consistency.py   # 产物一致性断言
├── scripts/linux/                 # 实验执行与环境准备（Shell）
├── examples/                      # 示例输入与渲染产物
├── tests/test_pipeline.py         # 10 个用例，全部离线可跑
├── docs/design.md                 # 设计说明与踩坑记录
└── .github/workflows/ci.yml
```

---

## 测试

```
[PASS] 锚点正确定位
[PASS] 锚点不存在时报错
[PASS] 锚点不唯一时报错（而非猜测）
[PASS] 注册表批量定位
[PASS] 任一锚点失败则整体中止（不半途插入）
[PASS] 预检发现重复锚点
[PASS] 一致条目校验通过
[PASS] 发现含义缺失导致数量不符
[PASS] 发现图注编号与位置错位
[PASS] 发现图片文件缺失
```

全部为确定性测试，无需 Word、无需网络。

---

## 已知限制

- 文档装配部分依赖 Windows + Word COM，Linux 下需改用 LibreOffice UNO
- 锚点依赖模板文本稳定，模板改动后需重新配置锚点表
- 一致性校验只检查"结构对应"，不检查文��内容是否准确（那需要人看）

---

## License

MIT
