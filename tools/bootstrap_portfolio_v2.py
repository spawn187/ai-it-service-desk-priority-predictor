"""One-time branch bootstrap for the reviewed portfolio upgrade."""

from __future__ import annotations

import base64
import io
import lzma
import shutil
import tarfile
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    parts_dir = root / "tools" / "payload_parts"
    encoded = "".join(
        path.read_text(encoding="ascii") for path in sorted(parts_dir.glob("part_*.txt"))
    )
    archive = lzma.decompress(base64.b64decode(encoded))
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for member in tar.getmembers():
            if not member.isfile():
                continue
            target = (root / member.name).resolve()
            if root.resolve() not in target.parents:
                raise ValueError(f"Unsafe archive path: {member.name}")
            target.parent.mkdir(parents=True, exist_ok=True)
            source = tar.extractfile(member)
            if source is None:
                raise ValueError(f"Missing archive content: {member.name}")
            target.write_bytes(source.read())

    shutil.rmtree(parts_dir)
    for relative in (
        "tools/bootstrap_portfolio_v2.py",
        ".github/workflows/bootstrap-portfolio-v2.yml",
    ):
        candidate = root / relative
        if candidate.exists():
            candidate.unlink()


if __name__ == "__main__":
    main()
