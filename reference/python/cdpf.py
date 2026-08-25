"""Small CDPF Draft 0.1 reference reader/validator.

Apache-2.0. This is intentionally conservative and is not a certified security product.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath
import hashlib
import json
import stat
import zipfile

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

CDPF_VERSION = "0.1"
MAX_MEMBERS = 1000
MAX_TOTAL_UNCOMPRESSED_BYTES = 100 * 1024 * 1024

class CDPFError(ValueError):
    pass

@dataclass(frozen=True)
class ValidatedPackage:
    manifest: dict
    document: dict
    member_names: tuple[str, ...]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_member_name(name: str) -> bool:
    if not name or "\\" in name or name.startswith("/"):
        return False
    p = PurePosixPath(name)
    if p.is_absolute() or any(part in ("", ".", "..") for part in p.parts):
        return False
    return True


def _is_symlink(info: zipfile.ZipInfo) -> bool:
    mode = (info.external_attr >> 16) & 0xFFFF
    return stat.S_ISLNK(mode)


def _load_json(data: bytes, label: str) -> dict:
    try:
        value = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CDPFError(f"{label} is not valid UTF-8 JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise CDPFError(f"{label} must contain a JSON object")
    return value


def _schema_registry(schema_dir: Path) -> Registry:
    registry = Registry()
    for path in schema_dir.rglob("*.schema.json"):
        obj = json.loads(path.read_text(encoding="utf-8"))
        resource = Resource.from_contents(obj)
        registry = registry.with_resource(obj["$id"], resource)
        # Also register relative file URI used by local $refs.
        registry = registry.with_resource(path.resolve().as_uri(), resource)
    return registry


def validate_json(value: dict, schema_path: Path, schema_dir: Path) -> None:
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    # Rewrite simple relative refs into file URIs by using the schema's retrieval URI.
    registry = _schema_registry(schema_dir)
    resource = Resource.from_contents(schema)
    registry = registry.with_resource(schema_path.resolve().as_uri(), resource)
    validator = Draft202012Validator(
        schema,
        registry=registry,
        format_checker=FormatChecker(),
    )
    errors = sorted(validator.iter_errors(value), key=lambda e: list(e.absolute_path))
    if errors:
        msgs = []
        for e in errors[:10]:
            where = "/".join(str(x) for x in e.absolute_path) or "<root>"
            msgs.append(f"{where}: {e.message}")
        raise CDPFError("JSON Schema validation failed: " + "; ".join(msgs))


CORE_NARRATIVE_BLOCKS = {
    "cdpf.core.chief_complaints",
    "cdpf.core.history",
    "cdpf.core.investigations",
    "cdpf.core.diagnosis",
    "cdpf.core.advice",
}


def validate_known_core_blocks(document: dict, schema_dir: Path) -> None:
    """Validate payloads for core block profiles standardized in Draft 0.1.

    Unknown/custom blocks remain structurally valid and are intentionally not rejected.
    """
    for index, block in enumerate(document.get("blocks", [])):
        block_type = block.get("block_type", "")
        schema_path = None
        if block_type in CORE_NARRATIVE_BLOCKS:
            schema_path = schema_dir / "blocks" / "narrative.schema.json"
        elif block_type.startswith("cdpf.core.examination."):
            schema_path = schema_dir / "blocks" / "examination.schema.json"
        elif block_type == "cdpf.core.medications":
            schema_path = schema_dir / "blocks" / "medications.schema.json"
        if schema_path is None:
            continue
        try:
            validate_json(block.get("data"), schema_path, schema_dir)
        except CDPFError as exc:
            raise CDPFError(f"Invalid data for block {index} ({block_type}): {exc}") from exc


def validate_package(path: str | Path, repo_root: str | Path | None = None) -> ValidatedPackage:
    package_path = Path(path)
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[2]
    repo_root = Path(repo_root)
    schema_dir = repo_root / "schema"

    try:
        zf = zipfile.ZipFile(package_path, "r")
    except zipfile.BadZipFile as exc:
        raise CDPFError("Not a valid ZIP/CDPF package") from exc

    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_MEMBERS:
            raise CDPFError(f"Package has too many members ({len(infos)} > {MAX_MEMBERS})")
        total_size = sum(i.file_size for i in infos)
        if total_size > MAX_TOTAL_UNCOMPRESSED_BYTES:
            raise CDPFError("Package exceeds reference validator uncompressed-size limit")

        names = []
        seen = set()
        for info in infos:
            if info.flag_bits & 0x1:
                raise CDPFError(f"Encrypted member is unsupported: {info.filename}")
            if not _safe_member_name(info.filename):
                raise CDPFError(f"Unsafe package member path: {info.filename!r}")
            if _is_symlink(info):
                raise CDPFError(f"Symbolic link is forbidden: {info.filename}")
            if info.filename in seen:
                raise CDPFError(f"Duplicate package member: {info.filename}")
            seen.add(info.filename)
            if info.is_dir():
                continue
            names.append(info.filename)

        if "manifest.json" not in seen:
            raise CDPFError("manifest.json is missing")
        manifest = _load_json(zf.read("manifest.json"), "manifest.json")
        validate_json(manifest, schema_dir / "manifest.schema.json", schema_dir)

        doc_meta = manifest["document"]
        doc_path = doc_meta["path"]
        if not _safe_member_name(doc_path) or doc_path not in seen:
            raise CDPFError("Declared clinical document path is missing or unsafe")
        doc_bytes = zf.read(doc_path)
        if len(doc_bytes) != doc_meta["size_bytes"]:
            raise CDPFError("Clinical document byte size does not match manifest")
        if _sha256(doc_bytes) != doc_meta["sha256"]:
            raise CDPFError("Clinical document SHA-256 does not match manifest")
        document = _load_json(doc_bytes, doc_path)
        validate_json(document, schema_dir / "document.schema.json", schema_dir)
        validate_known_core_blocks(document, schema_dir)
        if document.get("cdpf_version") != manifest.get("cdpf_version"):
            raise CDPFError("Manifest and document cdpf_version differ")

        attachment_ids = set()
        declared_payloads = {"manifest.json", doc_path}
        for att in manifest.get("attachments", []):
            att_id = att["attachment_id"]
            if att_id in attachment_ids:
                raise CDPFError(f"Duplicate attachment_id: {att_id}")
            attachment_ids.add(att_id)
            apath = att["path"]
            if not _safe_member_name(apath) or apath not in seen:
                raise CDPFError(f"Attachment is missing or unsafe: {apath!r}")
            if apath in declared_payloads:
                raise CDPFError(f"Package path declared more than once: {apath}")
            raw = zf.read(apath)
            if len(raw) != att["size_bytes"]:
                raise CDPFError(f"Attachment byte size mismatch: {apath}")
            if _sha256(raw) != att["sha256"]:
                raise CDPFError(f"Attachment SHA-256 mismatch: {apath}")
            declared_payloads.add(apath)

        unlisted = set(names) - declared_payloads
        if unlisted:
            raise CDPFError("Unlisted package payload(s): " + ", ".join(sorted(unlisted)))

        # Validate references used by the current core examples/profiles. Unknown blocks remain valid.
        def walk(obj):
            if isinstance(obj, dict):
                if set(obj) >= {"attachment_id"} and isinstance(obj.get("attachment_id"), str):
                    yield obj["attachment_id"]
                for v in obj.values():
                    yield from walk(v)
            elif isinstance(obj, list):
                for v in obj:
                    yield from walk(v)
        for ref in walk(document.get("blocks", [])):
            if ref not in attachment_ids:
                raise CDPFError(f"Document references undeclared attachment_id: {ref}")

        block_ids = [b["block_id"] for b in document.get("blocks", [])]
        if len(block_ids) != len(set(block_ids)):
            raise CDPFError("Duplicate block_id in document")

        return ValidatedPackage(manifest, document, tuple(names))
