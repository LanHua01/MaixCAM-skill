#!/usr/bin/env python3
"""统计主循环中的结构性帧成本，不估算毫秒数或 FPS。"""

from __future__ import annotations

import argparse
import ast
from collections import Counter
import json
from pathlib import Path
import sys


GROUPS = {
    "vision": {"find_blobs", "find_lines", "find_line_segments", "find_rects", "find_circles", "get_regression"},
    "inference": {"detect", "classify", "segment", "track"},
    "transform": {"resize", "crop", "warp_affine", "warp_perspective", "to_format"},
    "display": {"show"},
    "serial": {"read", "write", "readline"},
    "drawing": {"draw_rect", "draw_rectangle", "draw_line", "draw_circle", "draw_string"},
}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, metavar="PROJECT")
    parser.add_argument("--entry", default="main.py")
    parser.add_argument("--json", type=Path, dest="json_output", metavar="OUTPUT")
    return parser.parse_args()


def call_leaf(node: ast.Call) -> str:
    """返回函数调用的末级名称。"""
    if isinstance(node.func, ast.Attribute):
        return node.func.attr
    if isinstance(node.func, ast.Name):
        return node.func.id
    return "<dynamic>"


class LoopVisitor(ast.NodeVisitor):
    """收集 while/for 热循环中的调用与重复分配。"""

    def __init__(self) -> None:
        """初始化循环深度、调用计数和分配计数。"""
        self.depth = 0
        self.calls: Counter[str] = Counter()
        self.allocations = 0

    def visit_While(self, node: ast.While) -> None:  # noqa: N802
        """进入 while 循环并访问其内容。"""
        self._visit_loop(node)

    def visit_For(self, node: ast.For) -> None:  # noqa: N802
        """进入 for 循环并访问其内容。"""
        self._visit_loop(node)

    def _visit_loop(self, node: ast.While | ast.For) -> None:
        """统一处理循环深度。"""
        self.depth += 1
        self.generic_visit(node)
        self.depth -= 1

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        """记录热循环内函数调用。"""
        if self.depth:
            name = call_leaf(node)
            self.calls[name] += 1
            if name in {"list", "dict", "set", "bytearray"}:
                self.allocations += 1
        self.generic_visit(node)

    def visit_List(self, node: ast.List) -> None:  # noqa: N802
        """记录热循环内列表字面量分配。"""
        if self.depth:
            self.allocations += 1
        self.generic_visit(node)

    def visit_Dict(self, node: ast.Dict) -> None:  # noqa: N802
        """记录热循环内字典字面量分配。"""
        if self.depth:
            self.allocations += 1
        self.generic_visit(node)

    def visit_Set(self, node: ast.Set) -> None:  # noqa: N802
        """记录热循环内集合字面量分配。"""
        if self.depth:
            self.allocations += 1
        self.generic_visit(node)

    def visit_ListComp(self, node: ast.ListComp) -> None:  # noqa: N802
        """记录热循环内列表推导分配。"""
        if self.depth:
            self.allocations += 1
        self.generic_visit(node)

    def visit_DictComp(self, node: ast.DictComp) -> None:  # noqa: N802
        """记录热循环内字典推导分配。"""
        if self.depth:
            self.allocations += 1
        self.generic_visit(node)


def assess(calls: Counter[str], allocations: int) -> list[str]:
    """按调用组合给出结构性风险，不推断实际耗时。"""
    risks: list[str] = []
    expensive = GROUPS["vision"] | GROUPS["inference"] | GROUPS["transform"]
    repeated = sorted(name for name in expensive if calls[name] > 1)
    if repeated:
        risks.append("同一帧重复高成本调用：" + "、".join(repeated))
    if sum(calls[name] for name in GROUPS["inference"]) and sum(calls[name] for name in GROUPS["vision"]):
        risks.append("同一主循环同时执行模型推理和传统视觉，需验证是否都映射评分项")
    if sum(calls[name] for name in GROUPS["transform"]) > 1:
        risks.append("同一帧存在多次图像变换，检查是否可复用结果或降低输入尺寸")
    if allocations:
        risks.append("热循环内存在推导式分配，需观察长期内存稳定性")
    return risks


def build_report(entry: Path, root: Path) -> dict[str, object]:
    """解析入口文件并生成调用计数报告。"""
    tree = ast.parse(entry.read_text(encoding="utf-8-sig"), filename=entry.name)
    visitor = LoopVisitor()
    visitor.visit(tree)
    grouped = {
        group: sum(visitor.calls[name] for name in names)
        for group, names in GROUPS.items()
    }
    return {
        "entry": entry.relative_to(root).as_posix(),
        "loop_calls": dict(sorted(visitor.calls.items())),
        "group_totals": grouped,
        "loop_comprehension_allocations": visitor.allocations,
        "risks": assess(visitor.calls, visitor.allocations),
        "measurement_status": "待目标板实测",
    }


def emit(report: dict[str, object], output: Path | None) -> None:
    """输出报告，并仅按显式参数写文件。"""
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def main() -> int:
    """执行结构成本分析并返回统一退出码。"""
    args = parse_args()
    try:
        root = args.project.resolve(strict=True)
        entry = (root / args.entry).resolve(strict=True)
        entry.relative_to(root)
        report = build_report(entry, root)
        emit(report, args.json_output)
        return 1 if report["risks"] else 0
    except (OSError, ValueError, SyntaxError) as exc:
        print(f"输入或运行错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
