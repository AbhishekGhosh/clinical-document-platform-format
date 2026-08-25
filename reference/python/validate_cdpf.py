#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys

from cdpf import CDPFError, validate_package


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate a CDPF Draft 0.1 .cdp package")
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        result = validate_package(args.package)
    except CDPFError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("VALID CDPF Draft 0.1 package")
    print(f"  package_id:  {result.manifest['package_id']}")
    print(f"  document_id: {result.document['document_id']}")
    print(f"  blocks:      {len(result.document.get('blocks', []))}")
    print(f"  members:     {len(result.member_names)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
