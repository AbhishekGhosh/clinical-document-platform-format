from __future__ import annotations
from pathlib import Path
import json
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "reference" / "python"))
from cdpf import CDPFError, validate_json, validate_known_core_blocks, validate_package

class ReferenceValidatorTests(unittest.TestCase):
    def test_minimal_example_valid(self):
        r = validate_package(ROOT / "examples" / "minimal.cdp", ROOT)
        self.assertEqual(r.document["cdpf_version"], "0.1")
        self.assertEqual(len(r.document["blocks"]), 1)

    def test_outpatient_example_valid(self):
        r = validate_package(ROOT / "examples" / "outpatient-note.cdp", ROOT)
        self.assertEqual(len(r.manifest["attachments"]), 1)
        self.assertGreaterEqual(len(r.document["blocks"]), 5)

    def test_path_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "bad.cdp"
            with zipfile.ZipFile(p, "w") as zf:
                zf.writestr("manifest.json", "{}")
                zf.writestr("../escape.txt", "x")
            with self.assertRaisesRegex(CDPFError, "Unsafe package member path"):
                validate_package(p, ROOT)

    def test_unknown_block_type_is_preserved_and_valid(self):
        src = validate_package(ROOT / "examples" / "minimal.cdp", ROOT)
        self.assertEqual(src.document["blocks"][0]["block_type"], "cdpf.core.chief_complaints")
        # Structural schema intentionally permits namespaced block types it does not know.
        doc_schema = json.loads((ROOT / "schema" / "document.schema.json").read_text(encoding="utf-8"))
        self.assertTrue(doc_schema["properties"]["blocks"]["items"]["properties"]["block_type"]["minLength"] == 1)


    def test_known_block_profile_schemas_validate_example_data(self):
        outpatient = validate_package(ROOT / "examples" / "outpatient-note.cdp", ROOT).document
        schema_dir = ROOT / "schema"
        by_type = {b["block_type"]: b["data"] for b in outpatient["blocks"]}
        validate_json(
            by_type["cdpf.core.examination.general"],
            schema_dir / "blocks" / "examination.schema.json",
            schema_dir,
        )
        validate_json(
            by_type["cdpf.core.medications"],
            schema_dir / "blocks" / "medications.schema.json",
            schema_dir,
        )
        validate_json(
            by_type["cdpf.core.chief_complaints"],
            schema_dir / "blocks" / "narrative.schema.json",
            schema_dir,
        )


    def test_known_core_block_bad_payload_rejected(self):
        document = {
            "blocks": [
                {
                    "block_id": "f7eadbb8-675f-4e9a-b7f5-1166734983bd",
                    "block_type": "cdpf.core.medications",
                    "data": {"items": [{"medication": {}}]},
                }
            ]
        }
        with self.assertRaisesRegex(CDPFError, "Invalid data for block"):
            validate_known_core_blocks(document, ROOT / "schema")

    def test_directory_entries_are_allowed(self):
        source = ROOT / "examples" / "outpatient-note.cdp"
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "with-dir-entry.cdp"
            with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(out, "w") as zout:
                zout.writestr("attachments/", b"")
                for info in zin.infolist():
                    zout.writestr(info.filename, zin.read(info.filename))
            r = validate_package(out, ROOT)
            self.assertEqual(r.document["cdpf_version"], "0.1")

    def test_tampered_document_hash_rejected(self):
        source = ROOT / "examples" / "minimal.cdp"
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "tampered.cdp"
            with zipfile.ZipFile(source, "r") as zin, zipfile.ZipFile(out, "w") as zout:
                for info in zin.infolist():
                    data = zin.read(info.filename)
                    if info.filename == "document.json":
                        data += b" "
                    zout.writestr(info.filename, data)
            with self.assertRaisesRegex(CDPFError, "byte size|SHA-256"):
                validate_package(out, ROOT)

if __name__ == "__main__":
    unittest.main()
