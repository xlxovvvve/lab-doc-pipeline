"""产物一致性校验 —— 确保「命令 / 含义 / 结果 / 图注 / 图片」严格一一对应。

这是整条流水线的最后一道关卡，也是最容易出问题的地方：
插入过程中任何一步失败，都会导致某一项缺失或错位，
而这类问题在最终文档里**肉眼很难发现**（页面上看起来只是"少了一段"）。

校验维度
--------
- 数量一致：每一类的条目数必须相同
- 配对一致：第 i 条的图注文字必须出现在第 i 个位置附近
- 完整性：不允许有空含义、空结果、空图注
- 图片存在：每一项声明的截图文件必须真实存在
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Mismatch:
    """一处不一致。"""

    kind: str
    message: str
    index: int = -1

    def __str__(self) -> str:
        loc = f"#{self.index + 1}" if self.index >= 0 else "-"
        return f"[{loc}] {self.kind}: {self.message}"


@dataclass
class ConsistencyReport:
    """一致性校验报告。"""

    expected: int = 0
    counts: dict[str, int] = field(default_factory=dict)
    mismatches: list[Mismatch] = field(default_factory=list)

    def add(self, kind: str, message: str, index: int = -1) -> None:
        self.mismatches.append(Mismatch(kind, message, index))

    @property
    def ok(self) -> bool:
        return not self.mismatches

    def summary(self) -> str:
        parts = " ".join(f"{k}={v}" for k, v in sorted(self.counts.items()))
        return f"期望 {self.expected} 条 | {parts} | 不一致 {len(self.mismatches)} 处"

    def to_dict(self) -> dict[str, Any]:
        return {
            "ok": self.ok,
            "expected": self.expected,
            "counts": self.counts,
            "mismatches": [
                {"kind": m.kind, "message": m.message, "index": m.index}
                for m in self.mismatches
            ],
        }


def verify_alignment(
    entries: list[dict[str, Any]],
    *,
    keys: tuple[str, ...] = ("command", "meaning", "result", "caption"),
    image_key: str = "image",
    image_root: str | Path | None = None,
    require_image: bool = True,
) -> ConsistencyReport:
    """校验一组条目的内部一致性。

    entries: [{"command":..., "meaning":..., "result":..., "caption":..., "image": "path"}]
    """
    rep = ConsistencyReport(expected=len(entries))

    # --- 1. 数量一致 ---
    for k in keys:
        n = sum(1 for e in entries if e.get(k))
        rep.counts[k] = n
        if n != len(entries):
            rep.add(
                "COUNT_MISMATCH",
                f"{k} 数量 {n} != 条目数 {len(entries)}",
            )

    # --- 2. 图注编号必须连续且与序号对应 ---
    # 图注形如「图 1-1」「图 2-3」：前半段是实验编号，后半段才是条目序号。
    # 只校验后半段与条目位置是否对应。
    for i, e in enumerate(entries):
        cap = (e.get("caption") or "").strip()
        if not cap:
            continue
        m = re.search(r"图\s*\d+\s*[-–—]\s*(\d+)", cap)
        if m:
            seq = int(m.group(1))
            if seq != i + 1:
                rep.add(
                    "CAPTION_ORDER",
                    f"图注序号 {seq} 与位置 {i + 1} 不一致",
                    i,
                )
        else:
            m2 = re.search(r"图\s*(\d+)\s*$", cap)
            if m2 and int(m2.group(1)) != i + 1:
                rep.add(
                    "CAPTION_ORDER",
                    f"图注编号 {m2.group(1)} 与位置 {i + 1} 不一致",
                    i,
                )

    # --- 3. 每条的图注必须能唯一定位 ---
    captions = [(e.get("caption") or "").strip() for e in entries]
    for i, c in enumerate(captions):
        if c and captions.count(c) > 1:
            rep.add("CAPTION_DUP", f"图注重复：{c[:40]!r}", i)

    # --- 4. 图片文件必须存在 ---
    if require_image:
        root = Path(image_root) if image_root else None
        for i, e in enumerate(entries):
            img = e.get(image_key)
            if not img:
                rep.add("IMAGE_MISSING", "条目未声明图片", i)
                continue
            p = Path(img)
            if not p.is_absolute() and root is not None:
                p = root / p
            if not p.exists():
                rep.add("IMAGE_NOT_FOUND", f"图片文件不存在：{p.name}", i)

    return rep


def verify_document_structure(
    doc_text: str,
    expected_images: int,
    *,
    expected_captions: list[str] | None = None,
) -> ConsistencyReport:
    """校验最终文档的文本结构（配合图片计数一起用）。"""
    rep = ConsistencyReport(expected=expected_images)

    if expected_captions:
        for i, cap in enumerate(expected_captions):
            cap = (cap or "").strip()
            if not cap:
                rep.add("CAPTION_EMPTY", "图注为空", i)
                continue
            if cap not in doc_text:
                rep.add("CAPTION_ABSENT", f"文档中找不到图注：{cap[:40]!r}", i)

    return rep
