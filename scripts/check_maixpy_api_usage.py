#!/usr/bin/env python3
"""扫描明显混入的 OpenMV、K210 或桌面专属 API。"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import sys


ERROR_IMPORTS = {
    "sensor": "OpenMV sensor API",
    "pyb": "OpenMV pyb API",
    "KPU": "K210 KPU API",
    "Maix": "K210 Maix API",
    "fpioa_manager": "K210 FPIOA API",
}
ERROR_CALLS = {
    "sensor.reset": "OpenMV sensor API",
    "sensor.snapshot": "OpenMV sensor API",
    "sensor.set_pixformat": "OpenMV sensor API",
    "pyb.UART": "OpenMV pyb API",
    "lcd.init": "K210 lcd API",
    "lcd.display": "K210 lcd API",
    "lcd.clear": "K210 lcd API",
}
REVIEW_IMPORTS = {
    "cv2": "cv2 需确认目标 MaixPy 版本与具体调用",
    "numpy": "NumPy 需确认板端支持与内存预算",
}
REVIEW_CALLS = {
    "cv2.imshow": "桌面窗口 API 不能直接用于板端 UI",
    "cv2.waitKey": "桌面窗口 API 不能直接用于板端 UI",
    "cv2.VideoCapture": "桌面采集 API 不能直接用于板端相机",
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, metavar="PROJECT")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--json", type=Path, dest="json_output", metavar="OUTPUT")
    return parser.parse_args()


def dotted_name(node: ast.AST) -> str:
    """返回导入或调用节点的点分名称。"""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def finding(level: str, path: Path, root: Path, line: int, message: str) -> dict[str, object]:
    """构造不含绝对路径的发现记录。"""
    return {
        "level": level,
        "file": path.relative_to(root).as_posix(),
        "line": line,
        "message": message,
    }


def imported_modules(node: ast.Import | ast.ImportFrom) -> list[str]:
    """提取 import 节点的顶级模块名称。"""
    if isinstance(node, ast.Import):
        return [alias.name.split(".")[0] for alias in node.names]
    return [(node.module or "").split(".")[0]]


def scan_file(path: Path, root: Path) -> list[dict[str, object]]:
    """按 Python 语法树扫描真实导入和调用，忽略注释与字符串。"""
    tree = ast.parse(path.read_text(encoding="utf-8-sig"), filename=path.name)
    results: list[dict[str, object]] = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            for module in imported_modules(node):
                if module in ERROR_IMPORTS:
                    results.append(finding("risk", path, root, node.lineno, ERROR_IMPORTS[module]))
                if module in REVIEW_IMPORTS:
                    results.append(finding("review", path, root, node.lineno, REVIEW_IMPORTS[module]))
        elif isinstance(node, ast.Call):
            name = dotted_name(node.func)
            if name in ERROR_CALLS or name.startswith("kpu."):
                message = ERROR_CALLS.get(name, "K210 KPU API")
                results.append(finding("risk", path, root, node.lineno, message))
            if name in REVIEW_CALLS:
                results.append(finding("review", path, root, node.lineno, REVIEW_CALLS[name]))
    return results


def build_report(root: Path, strict: bool) -> dict[str, object]:
    """生成 API 边界检查报告。"""
    findings = [
        finding
        for path in sorted(root.rglob("*.py"))
        for finding in scan_file(path, root)
    ]
    risks = [item for item in findings if item["level"] == "risk"]
    reviews = [item for item in findings if item["level"] == "review"]
    return {
        "status": "risk" if risks or (strict and reviews) else "pass",
        "strict": strict,
        "findings": findings,
        "note": "正向 API 仍须按目标 MaixPy 官方文档与板端版本复核。",
    }


def emit(report: dict[str, object], output: Path | None) -> None:
    """输出报告，并仅按显式参数写文件。"""
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def main() -> int:
    """执行检查并返回统一退出码。"""
    args = parse_args()
    try:
        root = args.project.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("PROJECT 必须是目录")
        report = build_report(root, args.strict)
        emit(report, args.json_output)
        return 1 if report["status"] == "risk" else 0
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"输入或运行错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
