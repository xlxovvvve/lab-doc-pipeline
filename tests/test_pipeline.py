"""锚点定位与一致性校验的测试。

核心要验证的场景：
1. 锚点能正确找到
2. 锚点不唯一时**必须报错**（而不是猜第一个）
3. 锚点不存在时必须报错
4. 一致性校验能发现数量不符、图注错位、图片缺失
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from assembler import AnchorError, AnchorRegistry, assert_unique_anchors, find_anchor, locate_all
from validator import verify_alignment

DOC = """1、动态库创建与调用
本实验需要建立两个目录来存放头文件和动态库。
命令如下：gcc -fPIC -shared -o libadd.so add.c
编译成功，生成 libadd.so。
编写头文件：MyLib.h
查看生成的可执行程序 Compute。
清理：make clean
"""


def test_find_anchor_ok():
    hit = find_anchor(DOC, "编写头文件：MyLib.h")
    assert hit.occurrences == 1
    assert hit.index > 0
    assert DOC[hit.index : hit.end] == "编写头文件：MyLib.h"
    print("[PASS] 锚点正确定位")


def test_anchor_not_found():
    try:
        find_anchor(DOC, "这段文字不存在于文档中")
    except AnchorError as e:
        assert "未找到" in str(e)
        print("[PASS] 锚点不存在时报错")
        return
    raise AssertionError("应当抛出 AnchorError")


def test_anchor_not_unique():
    doc = DOC + "\n再次提到：编写头文件：MyLib.h\n"
    try:
        find_anchor(doc, "编写头文件：MyLib.h")
    except AnchorError as e:
        assert "不唯一" in str(e)
        print("[PASS] 锚点不唯一时报错（而非猜测）")
        return
    raise AssertionError("应当抛出 AnchorError")


def test_registry_locate_all():
    reg = AnchorRegistry()
    reg.add("a1", "编写头文件：MyLib.h", "第一步")
    reg.add("a2", "清理：make clean", "第二步")
    results = locate_all(DOC, reg)
    assert len(results) == 2
    print("[PASS] 注册表批量定位")


def test_registry_all_or_nothing():
    reg = AnchorRegistry()
    reg.add("good", "编写头文件：MyLib.h")
    reg.add("bad", "根本不存在的内容")
    try:
        locate_all(DOC, reg)
    except AnchorError as e:
        assert "未执行任何插入" in str(e)
        print("[PASS] 任一锚点失败则整体中止（不半途插入）")
        return
    raise AssertionError("应当抛出 AnchorError")


def test_precheck_duplicates():
    reg = AnchorRegistry()
    reg.add("a", "编写头文件：MyLib.h")
    reg.add("b", "编写头文件：MyLib.h")
    try:
        assert_unique_anchors(reg, DOC)
    except AnchorError as e:
        assert "重复" in str(e)
        print("[PASS] 预检发现重复锚点")
        return
    raise AssertionError("应当抛出 AnchorError")


# ------------------------------------------------------------ 一致性校验
GOOD = [
    {
        "command": "gcc -fPIC -shared -o libadd.so add.c",
        "meaning": "编译生成动态库" * 3,
        "result": "生成 libadd.so，7880 字节。",
        "caption": "图 1-1　步骤 1　编译动态库",
        "image": "shot01.png",
    },
    {
        "command": "./Compute",
        "meaning": "运行可执行程序查看结果" * 3,
        "result": "输出 3 + 4 = 7。",
        "caption": "图 1-2　步骤 2　运行程序",
        "image": "shot02.png",
    },
]


def test_alignment_ok(tmp_dir: Path):
    """用一个独立子目录，避免与图片缺失用例互相干扰。"""
    d = tmp_dir / "ok"
    d.mkdir()
    for e in GOOD:
        (d / e["image"]).write_bytes(b"x")
    rep = verify_alignment(GOOD, image_root=d)
    assert rep.ok, rep.mismatches
    print("[PASS] 一致条目校验通过")


def test_alignment_count_mismatch():
    bad = [dict(GOOD[0]), dict(GOOD[1])]
    bad[1]["meaning"] = ""
    rep = verify_alignment(bad, require_image=False)
    assert not rep.ok
    assert any(m.kind == "COUNT_MISMATCH" for m in rep.mismatches)
    print("[PASS] 发现含义缺失导致数量不符")


def test_alignment_caption_order():
    bad = [dict(GOOD[0]), dict(GOOD[1])]
    bad[1]["caption"] = "图 1-1　步骤 2　运行程序"
    rep = verify_alignment(bad, require_image=False)
    assert not rep.ok
    assert any(m.kind == "CAPTION_ORDER" for m in rep.mismatches)
    print("[PASS] 发现图注编号与位置错位")


def test_alignment_image_missing(tmp_dir: Path):
    """独立空目录 —— 这里的图片一定不存在。"""
    d = tmp_dir / "missing"
    d.mkdir()
    rep = verify_alignment(GOOD, image_root=d)
    assert not rep.ok
    assert any(m.kind == "IMAGE_NOT_FOUND" for m in rep.mismatches)
    print("[PASS] 发现图片文件缺失")


def main() -> int:
    import tempfile

    print("=" * 66)
    print("lab-doc-pipeline 测试")
    print("=" * 66)
    tests = [
        test_find_anchor_ok,
        test_anchor_not_found,
        test_anchor_not_unique,
        test_registry_locate_all,
        test_registry_all_or_nothing,
        test_precheck_duplicates,
    ]
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        tests += [
            lambda: test_alignment_ok(tmp),
            test_alignment_count_mismatch,
            test_alignment_caption_order,
            lambda: test_alignment_image_missing(tmp),
        ]
        failed = 0
        for t in tests:
            try:
                t()
            except AssertionError as e:
                failed += 1
                print(f"[FAIL] {t.__name__ if hasattr(t,'__name__') else t}: {e}")
    print("=" * 66)
    print("全部通过" if failed == 0 else f"{failed} 个用例失败")
    print("=" * 66)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
