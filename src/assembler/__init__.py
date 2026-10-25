"""assembler —— 文档装配（锚点定位与插入编排）。"""
from .anchors import (
    AnchorError,
    AnchorHit,
    AnchorRegistry,
    assert_unique_anchors,
    build_registry_from_spec,
    find_anchor,
    locate_all,
)

__all__ = [
    "AnchorError",
    "AnchorHit",
    "AnchorRegistry",
    "assert_unique_anchors",
    "build_registry_from_spec",
    "find_anchor",
    "locate_all",
]
