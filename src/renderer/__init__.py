"""renderer —— 终端截图渲染。"""
from .terminal import RenderOptions, load_font, parse_shell_output, render_lines, render_shell_output

__all__ = [
    "RenderOptions",
    "load_font",
    "parse_shell_output",
    "render_lines",
    "render_shell_output",
]
