#!/usr/bin/env python3
"""Modular, reusable integrity gate -- run this after editing ANY tracked YAML/JSON file, not just
STANDING_DIRECTIVE.yaml. Mechanically catches the two real mistakes made in this session:
(1) a header comment block silently stripped by a raw yaml.safe_dump
(2) a top-level key silently lost during an edit
Usage: python3 file_edit_guard.py <before_path> <after_path>
Exits non-zero and prints FAIL if either check fails -- meant to be the LAST step of every file edit,
never skipped, per STANDING_DIRECTIVE.yaml rule_4_self_review_pass.
"""
import sys, yaml, json

def load_structured(path):
    if path.endswith(".json"):
        return json.load(open(path))
    return yaml.safe_load(open(path))

def header_lines(path):
    lines = open(path).read().split("\n")
    out = []
    for line in lines:
        if line.strip().startswith("#") or line.strip() == "":
            out.append(line)
        else:
            break
    return out

def main():
    before_path, after_path = sys.argv[1], sys.argv[2]
    failures = []

    before_header = header_lines(before_path)
    after_header = header_lines(after_path)
    real_before_header = [l for l in before_header if l.strip().startswith("#")]
    real_after_header = [l for l in after_header if l.strip().startswith("#")]
    if real_before_header and not real_after_header:
        failures.append(f"HEADER_COMMENT_LOST: before had {len(real_before_header)} comment lines, after has 0")
    elif real_before_header and real_before_header != real_after_header:
        failures.append(f"HEADER_COMMENT_CHANGED: before={real_before_header[:2]}... after={real_after_header[:2]}...")

    try:
        before_doc = load_structured(before_path)
        after_doc = load_structured(after_path)
    except Exception as e:
        print(f"FAIL: could not parse one of the files as valid YAML/JSON: {e}")
        sys.exit(1)

    if isinstance(before_doc, dict) and isinstance(after_doc, dict):
        lost_keys = set(before_doc.keys()) - set(after_doc.keys())
        if lost_keys:
            failures.append(f"TOP_LEVEL_KEYS_LOST: {sorted(lost_keys)}")
    else:
        failures.append("NOT_A_DICT_AT_TOP_LEVEL -- cannot check key preservation")

    if failures:
        print("FAIL:")
        for f in failures:
            print(" -", f)
        sys.exit(1)
    else:
        print(f"PASS: header preserved (or was never present), all top-level keys preserved. "
              f"before_keys={len(before_doc) if isinstance(before_doc, dict) else 'n/a'} "
              f"after_keys={len(after_doc) if isinstance(after_doc, dict) else 'n/a'}")
        sys.exit(0)

if __name__ == "__main__":
    main()
