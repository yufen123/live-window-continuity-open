#!/usr/bin/env python3
"""Build a deterministic local review ZIP. Never uploads or publishes."""
import hashlib
import json
from pathlib import Path
import zipfile

root = Path(__file__).resolve().parents[1]
manifest = json.loads((root / "plugin.json").read_text())
paths = [root / "plugin.json", root / "LICENSE"]
for directory in ("skills",):
    for path in (root / directory).rglob("*"):
        if path.is_symlink():
            raise SystemExit("Refusing symlink in package")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc":
            paths.append(path)
out = root / "build"
out.mkdir(exist_ok=True)
target = out / (manifest["name"] + "-v" + manifest["version"] + "-review.zip")
with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in sorted(paths):
        entry = zipfile.ZipInfo(path.relative_to(root).as_posix(), (2026, 1, 1, 0, 0, 0))
        entry.compress_type = zipfile.ZIP_DEFLATED
        entry.create_system = 3
        entry.external_attr = 0o100644 << 16
        archive.writestr(entry, path.read_bytes())
with zipfile.ZipFile(target) as archive:
    assert archive.testzip() is None
print(target.name)
print("SHA256", hashlib.sha256(target.read_bytes()).hexdigest())
