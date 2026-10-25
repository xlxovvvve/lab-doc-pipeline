"""文本锚点定位 —— 解决 Word 自动化插入时的段号漂移问题。

问题
----
用 Word COM 往文档里插内容时，每插入一次，后面所有段落的编号都会变。
按固定行号/段号定位，插入几次之后就必然串位。

解法
----
不记录段号，而是记录一段**在文档中唯一出现的锚点文本**。
运行时全文查找这段文本，拿到它当前的真实位置，再在它之后插入。

两个必须遵守的约束
------------------
1. **锚点必须唯一** —— 出现多次会导致定位歧义，必须直接报错而不是猜
2. **锚点必须取在内容块的最后一行** —— 否则插入的内容会把代码块从中间切断
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


class AnchorError(RuntimeError):
    """锚点定位失败。"""


@dataclass
class AnchorHit:
    """一次锚点查找的结果。"""

    anchor: str
    index: int          # 锚点在文档中的起始位置
    length: int
    occurrences: int    # 命中次数（必须为 1）

    @property
    def end(self) -> int:
        return self.index + self.length


@dataclass
class AnchorRegistry:
    """锚点表：维护 锚点文本 -> 说明 的映射。

    anchors 里的每一项描述"在哪个锚点之后插入什么"。
    """

    items: list[dict] = field(default_factory=list)

    def add(
        self,
        key: str,
        anchor_text: str,
        description: str = "",
        payload: dict | None = None,
    ) -> None:
        self.items.append(
            {
                "key": key,
                "anchor_text": anchor_text,
                "description": description,
                "payload": payload or {},
            }
        )

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self):
        return iter(self.items)


def find_anchor(
    document_text: str,
    anchor_text: str,
    *,
    strict: bool = True,
) -> AnchorHit:
    """在文档全文中查找锚点。

    strict=True 时，命中 0 次或多次都抛 AnchorError（默认，更安全）。
    strict=False 时，命中多次取第一次（不推荐）。
    """
    if not anchor_text:
        raise AnchorError("锚点文本为空")

    count = document_text.count(anchor_text)
    if count == 0:
        raise AnchorError(f"锚点未找到：{anchor_text[:60]!r}")
    if count > 1:
        msg = f"锚点不唯一（命中 {count} 次）：{anchor_text[:60]!r}"
        if strict:
            raise AnchorError(msg)
        return AnchorHit(anchor_text, document_text.find(anchor_text), len(anchor_text), count)

    idx = document_text.find(anchor_text)
    return AnchorHit(anchor_text, idx, len(anchor_text), count)


def locate_all(
    document_text: str,
    registry: AnchorRegistry,
    *,
    strict: bool = True,
) -> list[tuple[dict, AnchorHit]]:
    """为注册表里的每一项定位锚点。

    返回 [(item, hit), ...]。任何一项失败都会抛 AnchorError，
    这样可以保证"要么全对，要么全不做"，避免半途插入导致文档损坏。
    """
    results: list[tuple[dict, AnchorHit]] = []
    errors: list[str] = []

    for item in registry:
        try:
            hit = find_anchor(document_text, item["anchor_text"], strict=strict)
            results.append((item, hit))
        except AnchorError as e:
            errors.append(f"[{item['key']}] {e}")

    if errors:
        raise AnchorError("锚点定位失败，未执行任何插入：\n  " + "\n  ".join(errors))
    return results


def assert_unique_anchors(registry: AnchorRegistry, document_text: str) -> None:
    """预检：确认所有锚点在文档中都恰好出现一次。

    在批量插入之前调用，可以提前发现配置错误。
    """
    problems: list[str] = []
    seen: dict[str, str] = {}

    for item in registry:
        a = item["anchor_text"]
        n = document_text.count(a)
        if n == 0:
            problems.append(f"[{item['key']}] 锚点不存在：{a[:50]!r}")
        elif n > 1:
            problems.append(f"[{item['key']}] 锚点命中 {n} 次：{a[:50]!r}")
        if a in seen:
            problems.append(
                f"[{item['key']}] 锚点与 [{seen[a]}] 重复：{a[:50]!r}"
            )
        seen[a] = item["key"]

    if problems:
        raise AnchorError("锚点预检未通过：\n  " + "\n  ".join(problems))


def build_registry_from_spec(spec: Iterable[dict]) -> AnchorRegistry:
    """从字典列表构造注册表。"""
    reg = AnchorRegistry()
    for s in spec:
        reg.add(
            key=s["key"],
            anchor_text=s["anchor_text"],
            description=s.get("description", ""),
            payload=s.get("payload", {}),
        )
    return reg
