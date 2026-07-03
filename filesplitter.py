#!/usr/bin/env python3
"""
filesplit.py — split a big file into chunks and join them back, 100% lossless.

Usage:
    python filesplit.py split <file> [--size 50M]      # split into chunks
    python filesplit.py join <file.part000> [-o out]   # rebuild original

Chunks are named <file>.part000, <file>.part001, ...
Lossless: everything is read/written in binary mode, byte for byte.
A SHA-256 checksum is saved on split and verified on join.
"""

import argparse
import hashlib
import re
import sys
from pathlib import Path

CHUNK_READ = 1024 * 1024  # 1 MiB read buffer


def parse_size(s: str) -> int:
    """Parse sizes like 500K, 50M, 1G, or plain bytes."""
    m = re.fullmatch(r"(\d+)([KMG]?)", s.strip().upper())
    if not m:
        sys.exit(f"Invalid size: {s!r} (use e.g. 500K, 50M, 1G)")
    num, unit = int(m.group(1)), m.group(2)
    mult = {"": 1, "K": 1024, "M": 1024**2, "G": 1024**3}[unit]
    return num * mult


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while chunk := f.read(CHUNK_READ):
            h.update(chunk)
    return h.hexdigest()


def split(file: Path, chunk_size: int) -> None:
    if not file.is_file():
        sys.exit(f"Not a file: {file}")

    total = file.stat().st_size
    print(f"Splitting {file} ({total} bytes) into {chunk_size}-byte chunks...")

    checksum = hashlib.sha256()
    part_idx = 0
    with file.open("rb") as src:
        while True:
            part_path = file.with_name(f"{file.name}.part{part_idx:03d}")
            written = 0
            with part_path.open("wb") as dst:
                while written < chunk_size:
                    data = src.read(min(CHUNK_READ, chunk_size - written))
                    if not data:
                        break
                    checksum.update(data)
                    dst.write(data)
                    written += len(data)
            if written == 0:
                part_path.unlink()  # remove empty trailing part
                break
            print(f"  wrote {part_path.name} ({written} bytes)")
            part_idx += 1
            if written < chunk_size:
                break

    # save checksum so join can verify
    sha_file = file.with_name(f"{file.name}.sha256")
    sha_file.write_text(checksum.hexdigest() + "\n")
    print(f"Done: {part_idx} parts + {sha_file.name} (checksum for verification)")


def join(first_part: Path, output: Path | None) -> None:
    m = re.fullmatch(r"(.+)\.part\d{3}", first_part.name)
    if not m:
        sys.exit(f"Expected a file named like something.part000, got: {first_part.name}")
    base = m.group(1)
    folder = first_part.parent

    parts = sorted(folder.glob(f"{base}.part[0-9][0-9][0-9]"))
    if not parts:
        sys.exit(f"No parts found for {base}")

    # sanity check: parts must be consecutive 000, 001, 002...
    for i, p in enumerate(parts):
        expected = f"{base}.part{i:03d}"
        if p.name != expected:
            sys.exit(f"Missing part: {expected} (found {p.name} instead)")

    out = output or folder / base
    if out.resolve() in (p.resolve() for p in parts):
        sys.exit("Output would overwrite a part file, choose another name with -o")

    print(f"Joining {len(parts)} parts -> {out}")
    checksum = hashlib.sha256()
    with out.open("wb") as dst:
        for p in parts:
            with p.open("rb") as src:
                while chunk := src.read(CHUNK_READ):
                    checksum.update(chunk)
                    dst.write(chunk)

    # verify against saved checksum if present
    sha_file = folder / f"{base}.sha256"
    if sha_file.exists():
        expected = sha_file.read_text().strip()
        actual = checksum.hexdigest()
        if actual == expected:
            print("Checksum OK — file is byte-identical to the original ✅")
        else:
            sys.exit(f"CHECKSUM MISMATCH!\n  expected {expected}\n  got      {actual}")
    else:
        print(f"(no {sha_file.name} found, skipped verification)")
    print(f"Done: {out} ({out.stat().st_size} bytes)")


def main() -> None:
    ap = argparse.ArgumentParser(description="Lossless file splitter/joiner")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("split", help="split a file into chunks")
    sp.add_argument("file", type=Path)
    sp.add_argument("--size", default="50M", help="chunk size, e.g. 500K, 50M, 1G (default 50M)")

    jp = sub.add_parser("join", help="rebuild the original from chunks")
    jp.add_argument("first_part", type=Path, help="the .part000 file")
    jp.add_argument("-o", "--output", type=Path, default=None, help="output filename")

    args = ap.parse_args()
    if args.cmd == "split":
        split(args.file, parse_size(args.size))
    else:
        join(args.first_part, args.output)


if __name__ == "__main__":
    main()