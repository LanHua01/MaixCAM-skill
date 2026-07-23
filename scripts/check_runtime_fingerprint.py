#!/usr/bin/env python3
"""生成工程指纹，并与用户提供的板端证据进行离线比较。"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import sys


SKIP_PARTS = {".git", "__pycache__", ".pytest_cache"}


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project", type=Path, metavar="PROJECT")
    parser.add_argument("--board-evidence", type=Path, metavar="FILE")
    parser.add_argument("--json", type=Path, dest="json_output", metavar="OUTPUT")
    return parser.parse_args()


def file_hash(path: Path) -> str:
    """计算文件 SHA-256。"""
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(65536), b""):
            digest.update(block)
    return digest.hexdigest()


def fingerprint(root: Path) -> dict[str, str]:
    """生成全部工程文件的相对路径哈希表。"""
    result: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not path.is_file() or any(part in SKIP_PARTS for part in path.parts):
            continue
        result[path.relative_to(root).as_posix()] = file_hash(path)
    return result


def project_relative(path: Path | None, root: Path) -> str | None:
    """路径位于工程内时返回相对路径，否则返回空。"""
    if path is None:
        return None


def normalize_evidence_path(value: object) -> str:
    """规范板端证据路径并拒绝绝对路径或目录穿越。"""
    text = str(value).replace("\\", "/")
    path = PurePosixPath(text)
    if not text or path.is_absolute() or ".." in path.parts or ":" in path.parts[0]:
        raise ValueError(f"板端证据必须使用项目相对路径：{value}")
    return path.as_posix()
    try:
        return path.resolve().relative_to(root).as_posix()
    except ValueError:
        return None


def read_evidence(path: Path) -> dict[str, str]:
    """读取 JSON 或“哈希 路径”格式的板端证据。"""
    text = path.read_text(encoding="utf-8-sig")
    try:
        data = json.loads(text)
        files = data.get("files", data)
        if not isinstance(files, dict):
            raise ValueError("证据中的 files 必须是对象")
        return {normalize_evidence_path(key): str(value) for key, value in files.items()}
    except json.JSONDecodeError:
        pairs = [line.strip().split(maxsplit=1) for line in text.splitlines() if line.strip()]
        if not pairs or any(len(pair) != 2 for pair in pairs):
            raise ValueError("板端证据不是有效 JSON 或哈希清单")
        return {normalize_evidence_path(pair[1]): pair[0] for pair in pairs}


def compare(source: dict[str, str], board: dict[str, str]) -> dict[str, list[str]]:
    """比较源码指纹与板端证据。"""
    shared = source.keys() & board.keys()
    return {
        "matched": sorted(path for path in shared if source[path] == board[path]),
        "mismatched": sorted(path for path in shared if source[path] != board[path]),
        "missing_on_board": sorted(source.keys() - board.keys()),
        "board_only": sorted(board.keys() - source.keys()),
    }


def emit(report: dict[str, object], output: Path | None) -> None:
    """输出报告，并仅按显式参数写文件。"""
    payload = json.dumps(report, ensure_ascii=False, indent=2)
    if output:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload + "\n", encoding="utf-8")
    print(payload)


def main() -> int:
    """生成与比较指纹；该工具不会自动访问设备。"""
    args = parse_args()
    try:
        root = args.project.resolve(strict=True)
        if not root.is_dir():
            raise ValueError("PROJECT 必须是目录")
        files = fingerprint(root)
        for artifact in (args.json_output, args.board_evidence):
            relative_artifact = project_relative(artifact, root)
            if relative_artifact:
                files.pop(relative_artifact, None)
        report: dict[str, object] = {"files": files, "board_status": "待提供板端证据"}
        risky = False
        if args.board_evidence:
            board = read_evidence(args.board_evidence.resolve(strict=True))
            comparison = compare(files, board)
            report.update({"board_status": "已离线比较", "comparison": comparison})
            risky = bool(
                comparison["mismatched"]
                or comparison["missing_on_board"]
                or comparison["board_only"]
            )
        emit(report, args.json_output)
        return 1 if risky else 0
    except (OSError, ValueError) as exc:
        print(f"输入或运行错误：{exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
