#!/usr/bin/env python3
from __future__ import annotations
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
FIXED_ZIP_DT = (2026, 8, 26, 0, 0, 0)

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def write_json(path: Path, obj: dict) -> None:
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")

def build(name: str, package_id: str, created_at: str) -> Path:
    d = EXAMPLES / name
    doc_path = d / "document.json"
    doc = doc_path.read_bytes()
    attachments = []
    attach_dir = d / "attachments"
    if attach_dir.exists():
        fixed_ids = {
            "lab-summary.txt": "7fd3fb50-b264-4e54-89ac-3cc8f3219c77",
        }
        for path in sorted(p for p in attach_dir.rglob("*") if p.is_file()):
            rel = path.relative_to(d).as_posix()
            raw = path.read_bytes()
            attachments.append({
                "attachment_id": fixed_ids.get(path.name) or "00000000-0000-4000-8000-000000000001",
                "path": rel,
                "media_type": "text/plain" if path.suffix == ".txt" else "application/octet-stream",
                "sha256": sha256(raw),
                "size_bytes": len(raw),
                "title": path.stem.replace("-", " ").title(),
            })
    manifest = {
        "cdpf_version": "0.1",
        "package_id": package_id,
        "created_at": created_at,
        "generator": {"name": "CDPF example builder", "version": "0.1"},
        "document": {"path": "document.json", "media_type": "application/json", "sha256": sha256(doc), "size_bytes": len(doc)},
        "attachments": attachments,
    }
    write_json(d / "manifest.json", manifest)
    out = EXAMPLES / f"{name}.cdp"
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in sorted(p for p in d.rglob("*") if p.is_file()):
            rel = path.relative_to(d).as_posix()
            info = zipfile.ZipInfo(rel, FIXED_ZIP_DT)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            zf.writestr(info, path.read_bytes())
    print(out.relative_to(ROOT))
    return out

def main() -> None:
    build("minimal", "0f699417-c4e0-46bb-8129-cb0aca6ea24f", "2026-08-26T09:00:00+05:30")
    build("outpatient-note", "647f95ac-6d22-47d2-81e2-b19932b917cc", "2026-08-26T10:15:00+05:30")

if __name__ == "__main__":
    main()
