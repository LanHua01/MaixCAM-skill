#!/usr/bin/env python3
"""静态提取 MaixVision/MaixPy 工程的结构与关键调用。"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys


RESOURCE_SUFFIXES = {".mud", ".cvimodel", ".jpg", ".jpeg", ".png", ".bin", ".json"}
COMPONENT_MARKERS = {
    "Camera": ("camera.Camera",),
    "Display": ("display.Display",),
    "UART": ("uart.UART",),
    "Model": ("nn.YOLO", "nn.NN", ".mud", ".cvimodel"),
}
VISION_NAMES = {
    "find_blobs", "find_lines", "find_line_segments", "find_rects", "find_circles",
    "find_qrcodes", "find_apriltags", "get_regression", "detect", "segment", "track",
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, metavar="PROJECT")
    parser.add_argument("--json", type=Path, dest="json_output", metavar="OUTPUT")
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    """返回使用正斜杠的项目相对路径。"""
    return path.resolve().relative_to(root.resolve()).as_posix()


def call_name(node: ast.Call) -> str:
    """提取函数调用的可读名称。"""
    parts: list[str] = []
    target: ast.AST = node.func
    while isinstance(target, ast.Attribute):
        parts.append(target.attr)
        target = target.value
    if isinstance(target, ast.Name):
        parts.append(target.id)
    return ".".join(reversed(parts))


def inspect_python(path: Path) -> dict[str, object]:
    """解析单个 Python 文件的导入、调用和主循环。"""
    text = path.read_text(encoding="utf-8-sig")
    tree = ast.parse(text, filename=path.name)
    imports: set[str] = set()
    calls: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add(node.module or "")
        elif isinstance(node, ast.Call):
            calls.add(call_name(node))
    return {
        "imports": sorted(item for item in imports if item),
        "calls": sorted(item for item in calls if item),
        "while_loops": sum(isinstance(node, ast.While) for node in ast.walk(tree)),
        "text": text,
    }


def find_entry(root: Path, python_files: list[Path]) -> str | None:
    """按 MaixVision 常见约定寻找工程入口。"""
    main = root / "main.py"
    if main.is_file():
        return "main.py"
    return relative(python_files[0], root) if python_files else None


def build_report(root: Path) -> dict[str, object]:
    """构建不含绝对路径的工程静态报告。"""
    python_files = sorted(root.rglob("*.py"))
    analyses = {relative(path, root): inspect_python(path) for path in python_files}
    all_text = "\n".join(str(item["text"]) for item in analyses.values())
    all_calls = {call for item in analyses.values() for call in item["calls"]}
    resources = sorted(
        relative(path, root)
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in RESOURCE_SUFFIXES
    )
    components = [
        name for name, markers in COMPONENT_MARKERS.items()
        if any(marker in all_text for marker in markers)
    ]
    return {
        "entry": find_entry(root, python_files),
        "python_files": sorted(analyses),
        "imports": {name: item["imports"] for name, item in analyses.items()},
        "components": components,
        "vision_calls": sorted({call.split(".")[-1] for call in all_calls} & VISION_NAMES),
        "resources": resources,
        "main_loop_files": [name for name, item in analyses.items() if item["while_loops"]],
    }


def emit(report: dict[str, object], output: Path | None) -> None:
    """向终端输出报告，并仅在显式指定时写 JSON 文件。"""
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def main() -> int:
    """执行工程检查并返回统一退出码。"""
    args = parse_args()
    try:
        root = args.project.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("PROJECT 必须是目录")
        emit(build_report(root), args.json_output)
        return 0
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"输入或运行错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
