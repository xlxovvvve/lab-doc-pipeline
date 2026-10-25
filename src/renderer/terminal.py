"""终端截图渲染器 —— 把真实命令输出渲染成规范的终端风格图片。

风格：黑底 + 浅灰等宽字 + `[wht@localhost xxx]$` 提示符。
宽度按插入 Word 的目标物理宽度换算，长行自动缩排保证完整显示不被截断。

依赖：Pillow
"""
from __future__ import annotations

import os
import platform
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- 样式常量
BG = (0, 0, 0)
FG = (204, 204, 204)
PROMPT_FG = (238, 238, 238)
CMD_FG = (255, 255, 255)
NOTE_FG = (150, 150, 150)

FONT_SIZE = 19
LINE_H_FACTOR = 1.26
PAD_X = 12
PAD_Y = 10

# 目标物理宽度 355pt @ 96dpi ≈ 473px（Word 中按 355pt 插入）
TARGET_W_PX = 474

_KIND_ORDER = ("cmd", "out", "blank", "note")


def _font_candidates() -> list[str]:
    """按平台找等宽字体。"""
    if platform.system() == "Windows":
        return [
            r"C:\Windows\Fonts\consola.ttf",
            r"C:\Windows\Fonts\cour.ttf",
            r"C:\Windows\Fonts\lucon.ttf",
        ]
    return [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
    ]


def load_font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont:
    """加载等宽字体；找不到时回退到 Pillow 默认位图字体。"""
    for path in _font_candidates():
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except OSError:
                continue
    return ImageFont.load_default()


@dataclass
class RenderOptions:
    """渲染参数。"""

    font_size: int = FONT_SIZE
    pad_x: int = PAD_X
    pad_y: int = PAD_Y
    target_w_px: int = TARGET_W_PX


def _measure(draw: ImageDraw.ImageDraw, lines: Sequence[tuple[str, str]], font) -> int:
    if not lines:
        return 0
    return int(max(draw.textlength(t, font=font) for _, t in lines))


def render_lines(
    lines: Iterable[tuple[str, str]],
    out_path: str | Path,
    options: RenderOptions | None = None,
) -> Path:
    """渲染一组 (kind, text) 为 PNG 图片。

    kind: 'cmd' 命令行（带提示符）| 'out' 普通输出 | 'blank' 空行 | 'note' 灰色注释
    """
    opts = options or RenderOptions()
    lines = [(k, t) for k, t in lines if k in _KIND_ORDER]
    if not lines:
        lines = [("out", "")]

    font = load_font(opts.font_size)
    line_h = int(opts.font_size * LINE_H_FACTOR)

    probe = Image.new("RGB", (10, 10))
    d0 = ImageDraw.Draw(probe)
    content_w = _measure(d0, lines, font)
    img_w = int(content_w + opts.pad_x * 2)
    img_h = opts.pad_y * 2 + line_h * len(lines)

    img = Image.new("RGB", (img_w, img_h), BG)
    d = ImageDraw.Draw(img)

    y = opts.pad_y
    for kind, text in lines:
        if kind == "cmd":
            # 拆出提示符（前缀到第一个 $ 为止），单独着色
            if "$" in text:
                prompt, rest = text.split("$", 1)
                prompt += "$"
            else:
                prompt, rest = "", text
            if prompt:
                d.text((opts.pad_x, y), prompt, font=font, fill=PROMPT_FG)
                pw = d.textlength(prompt, font=font)
                d.text((opts.pad_x + pw, y), rest, font=font, fill=CMD_FG)
            else:
                d.text((opts.pad_x, y), rest, font=font, fill=CMD_FG)
        elif kind == "note":
            d.text((opts.pad_x, y), text, font=font, fill=NOTE_FG)
        elif kind == "blank":
            pass
        else:
            d.text((opts.pad_x, y), text, font=font, fill=FG)
        y += line_h

    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    img.save(p)
    return p


def parse_shell_output(text: str, prompt: str = "[wht@localhost ~]$") -> list[tuple[str, str]]:
    """把一段 shell 输出转成 (kind, text) 序列。

    规则：
    - 以 prompt 开头或包含 `$ ` 的行 → 判为命令
    - 空行 → blank
    - 以 # 开头的注释行 → note
    - 其余 → 普通输出
    """
    out: list[tuple[str, str]] = []
    for raw in text.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            out.append(("blank", ""))
            continue
        if stripped.startswith("#"):
            out.append(("note", stripped))
            continue
        if prompt in line or stripped.startswith("$ ") or stripped.endswith("$ "):
            out.append(("cmd", stripped))
            continue
        out.append(("out", line))
    return out


def render_shell_output(
    text: str,
    out_path: str | Path,
    prompt: str = "[wht@localhost ~]$",
    options: RenderOptions | None = None,
) -> Path:
    """便捷入口：一段 shell 输出 → 一张终端风格图片。"""
    return render_lines(parse_shell_output(text, prompt), out_path, options)
