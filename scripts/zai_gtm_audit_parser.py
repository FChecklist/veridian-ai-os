#!/usr/bin/env python3
"""
zai_gtm_audit_parser.py

Parses the 8 real Z.AI black-box GTM certification source files under
/opt/veridian/ai-os/memory/zai-gtm-findings/ and enumerates every
"point" per the atomic-unit definition given in dispatch
UMR-20260806-102500-ab50 (child of UMR-20260806-101802-a350):

  The atomic unit is:
    - every individually-labeled finding: BLOCKER-NNN, CB-NN, HP-NN, MP-NN,
      OBS-NNN, wherever they appear in the 8 source files, AND
    - every individually-verdicted sub-check inside each of the 25 tests
      that carries its own FAIL/WARN/PARTIAL verdict AND its own
      recommendation.

  NOT points: the 8 parts themselves, the 25 tests themselves (those are
  containers), and sub-checks whose own verdict is a clean PASS with no
  associated recommendation.

This script is deliberately re-runnable: re-run it any time the source
files or the merged file change, and it will regenerate the manifest from
scratch (no manual editing of the manifest is expected).

Output: a JSON manifest (list of point objects) + a run summary printed
to stdout (total count, breakdown by severity, breakdown by part).

This script does ONLY inventory / enumeration. It does not create UMRs,
does not touch gtm_certification_categories, and does not perform any
closure work.
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field, asdict
from typing import Optional

SRC_DIR = "/opt/veridian/ai-os/memory/zai-gtm-findings"
DEFAULT_OUT = "/opt/veridian/ai-os/memory/ZAI_BLACKBOX_AUDIT_POINTS_MANIFEST.json"

PARTS = [
    ("Part1_Smoke_E2E_Auth_Testing_Report.txt", 1),
    ("Part2_UIUX_CrossBrowser_Responsive_Testing_Report.txt", 2),
    ("Part3_Accessibility_Performance_WebVitals_Testing_Report.txt", 3),
    ("Part4_PWA_Offline_Storage_Testing_Report.txt", 4),
    ("Part5_API_Security_Testing_Report.txt", 5),
    ("Part6_RBAC_AI_Governance_Testing_Report.txt", 6),
    ("Part7_Backend_System_Testing_Report.txt", 7),
    ("Part8_Regression_Final_Certification_Report.txt", 8),
]

# Verdict keywords that qualify a sub-check as an actionable "point" per the
# literal atomic-unit definition (FAIL / WARN / PARTIAL). Verdicts outside
# this set (PASS, UNTESTABLE, UNVERIFIABLE, BLOCKED, N/A, NOT TESTED,
# CONFIRMS) are captured for transparency but are NOT counted as points,
# since the dispatch's definition names only FAIL/WARN/PARTIAL explicitly.
POINT_VERDICT_KEYWORDS = ("FAIL", "WARN", "PARTIAL")

TEST_HEADER_RE = re.compile(r"^TEST #(\d+)\s*[—-]\s*(.+?)\s*$")
OVERALL_VERDICT_RE = re.compile(
    r"^(?:Overall VERDICT for Test #\d+|VERDICT)\s*:\s*(.+?)\s*$", re.IGNORECASE
)
# Sub-check header, two known styles:
#   "  3a. Page loads without errors"                (verdict elsewhere in block)
#   "  1a. App starts                 : PASS  (...)"  (inline, Part 1 tests 1-2 style)
SUBCHECK_RE = re.compile(r"^\s{2,6}(\d+[a-z])\.\s+(.*)$")
INLINE_VERDICT_RE = re.compile(
    r"^(.*?)\s*:\s*(PASS|FAIL|WARN|PARTIAL(?: PASS)?|BLOCKED|N/A|UNTESTABLE|"
    r"UNVERIFIABLE|NOT TESTED|CONFIRMS)\b(.*)$",
    re.IGNORECASE,
)
VERDICT_LINE_RE = re.compile(r"^\s*(?:VERDICT|Verdict)\s*:\s*(.+)$", re.MULTILINE)
RECOMMEND_LINE_RE = re.compile(r"^\s*Recommend(?:ed?)?\s*:?\s*(.*)$", re.IGNORECASE | re.MULTILINE)
LABELED_BLOCKER_RE = re.compile(r"^\[BLOCKER-(\d+)\]\s*(.*)$")
OBS_HEADER_RE = re.compile(r"^OBS-(\d+)\s+(.*)$")
CB_ITEM_RE = re.compile(r"^\s*CB-(\d+)\.\s+(.*)$")
HP_ITEM_RE = re.compile(r"^\s*HP-(\d+)\.\s+(.*)$")
MP_ITEM_RE = re.compile(r"^\s*MP-(\d+)\.\s+(.*)$")
SECTION_BREAK_RE = re.compile(r"^(={10,}|-{10,})\s*$")


_POINT_VERDICT_RE = re.compile(
    r"\b(" + "|".join(POINT_VERDICT_KEYWORDS) + r")\b", re.IGNORECASE
)


def is_point_verdict(verdict_text: str) -> bool:
    if not verdict_text:
        return False
    # Word-boundary match only — plain substring matching would false-positive
    # on words like "failover" (contains FAIL) or "warnings" (contains WARN).
    return bool(_POINT_VERDICT_RE.search(verdict_text))


@dataclass
class Point:
    id: str
    kind: str  # "labeled_finding" | "subcheck"
    severity: Optional[str]  # "CB" | "HP" | "MP" | "OBS" | "BLOCKER" | None
    part: int
    part_file: str
    test_number: Optional[int]
    test_name: Optional[str]
    label_raw: str
    title: str
    verdict: str
    recommendation: str
    recommendation_source: str  # "inline" | "test_level" | "none"
    is_point: bool
    source_line_start: int
    source_line_end: int
    notes: str = ""


def read_part(fname):
    path = os.path.join(SRC_DIR, fname)
    with open(path, "r") as f:
        return f.read().split("\n")


def collect_paragraph(lines, start_idx, stop_res):
    """Collect a run of lines starting at start_idx until a blank line
    followed by non-indented content, or until one of stop_res matches."""
    out = [lines[start_idx]]
    i = start_idx + 1
    while i < len(lines):
        line = lines[i]
        if any(r.match(line) for r in stop_res):
            break
        if line.strip() == "":
            # allow one blank line only if next line is still indented continuation
            if i + 1 < len(lines) and lines[i + 1].startswith((" ", "\t")) and lines[i + 1].strip():
                out.append(line)
                i += 1
                continue
            break
        out.append(line)
        i += 1
    return out, i


def parse_labeled_findings(lines, part_num, part_file):
    points = []

    # BLOCKER-NNN (Part 1 style, free-text paragraph after label)
    for idx, line in enumerate(lines):
        m = LABELED_BLOCKER_RE.match(line)
        if m:
            block, end_idx = collect_paragraph(
                lines, idx, [re.compile(r"^Impact:\s*$"), SECTION_BREAK_RE]
            )
            text = " ".join(l.strip() for l in block).strip()
            points.append(
                Point(
                    id=f"P{part_num}-BLOCKER-{m.group(1)}",
                    kind="labeled_finding",
                    severity="CB",  # a BLOCKER is a critical-blocker-class finding
                    part=part_num,
                    part_file=part_file,
                    test_number=None,
                    test_name=None,
                    label_raw=f"BLOCKER-{m.group(1)}",
                    title=text[:120],
                    verdict="BLOCKER",
                    recommendation=text,
                    recommendation_source="inline",
                    is_point=True,
                    source_line_start=idx + 1,
                    source_line_end=end_idx,
                    notes="Labeled with 'BLOCKER-' prefix rather than 'CB-'; "
                    "classified as Critical-Blocker-class. Likely the same "
                    "underlying issue later consolidated as CB-01 in Part 8 "
                    "(reconcile in closure phase, not here).",
                )
            )

    # OBS-NNN (Part 1 style: header line + indented bullets until next OBS-/section break)
    for idx, line in enumerate(lines):
        m = OBS_HEADER_RE.match(line)
        if m:
            stop_res = [OBS_HEADER_RE, SECTION_BREAK_RE]
            block, end_idx = collect_paragraph(lines, idx, stop_res)
            text = " ".join(l.strip() for l in block).strip()
            points.append(
                Point(
                    id=f"P{part_num}-OBS-{m.group(1)}",
                    kind="labeled_finding",
                    severity="OBS",
                    part=part_num,
                    part_file=part_file,
                    test_number=None,
                    test_name=None,
                    label_raw=f"OBS-{m.group(1)}",
                    title=m.group(2).strip()[:120],
                    verdict="OBSERVATION",
                    recommendation=text,
                    recommendation_source="inline",
                    is_point=True,
                    source_line_start=idx + 1,
                    source_line_end=end_idx,
                )
            )

    # CB-NN. (Part 8 style: Status/Impact/Action structured block)
    for idx, line in enumerate(lines):
        m = CB_ITEM_RE.match(line)
        if m:
            stop_res = [CB_ITEM_RE, SECTION_BREAK_RE, re.compile(r"^HIGH-PRIORITY ISSUES")]
            block, end_idx = collect_paragraph(lines, idx, stop_res)
            text = " ".join(l.strip() for l in block).strip()
            action_m = re.search(r"Action:\s*(.+)$", text)
            points.append(
                Point(
                    id=f"P{part_num}-CB-{m.group(1)}",
                    kind="labeled_finding",
                    severity="CB",
                    part=part_num,
                    part_file=part_file,
                    test_number=None,
                    test_name=None,
                    label_raw=f"CB-{m.group(1)}",
                    title=m.group(2).strip()[:120],
                    verdict="CRITICAL BLOCKER",
                    recommendation=action_m.group(1).strip() if action_m else text,
                    recommendation_source="inline",
                    is_point=True,
                    source_line_start=idx + 1,
                    source_line_end=end_idx,
                )
            )

    # HP-NN. / MP-NN. (Part 8 style: single-line, possibly wrapped)
    for regex, sev, stop_after in (
        (HP_ITEM_RE, "HP", re.compile(r"^MEDIUM-PRIORITY ISSUES")),
        (MP_ITEM_RE, "MP", re.compile(r"^TESTS THAT CANNOT")),
    ):
        for idx, line in enumerate(lines):
            m = regex.match(line)
            if m:
                stop_res = [regex, SECTION_BREAK_RE, stop_after]
                block, end_idx = collect_paragraph(lines, idx, stop_res)
                text = " ".join(l.strip() for l in block).strip()
                points.append(
                    Point(
                        id=f"P{part_num}-{sev}-{m.group(1)}",
                        kind="labeled_finding",
                        severity=sev,
                        part=part_num,
                        part_file=part_file,
                        test_number=None,
                        test_name=None,
                        label_raw=f"{sev}-{m.group(1)}",
                        title=text[:120],
                        verdict="HIGH PRIORITY" if sev == "HP" else "MEDIUM PRIORITY",
                        recommendation=text,
                        recommendation_source="inline",
                        is_point=True,
                        source_line_start=idx + 1,
                        source_line_end=end_idx,
                    )
                )

    return points


def parse_subchecks(lines, part_num, part_file):
    points = []
    excluded = []  # non-point subchecks (PASS / UNTESTABLE / etc.), kept for transparency

    current_test_num = None
    current_test_name = None
    test_level_recommend = {}  # test_num -> recommendation text

    # First pass: capture each test's aggregate Recommend / Operator Action block,
    # keyed by test number, to use as fallback recommendation source.
    i = 0
    while i < len(lines):
        m = TEST_HEADER_RE.match(lines[i].strip())
        if m:
            tnum = int(m.group(1))
            # scan forward for "Recommend" or "Operator Action Required" block
            # until next TEST # header or end of file
            j = i + 1
            rec_lines = []
            capturing = False
            while j < len(lines) and not TEST_HEADER_RE.match(lines[j].strip()):
                if re.match(r"^Recommend", lines[j].strip(), re.IGNORECASE) or re.match(
                    r"^Operator Action Required", lines[j].strip(), re.IGNORECASE
                ):
                    capturing = True
                    rec_lines.append(lines[j].strip())
                    j += 1
                    continue
                if capturing:
                    if lines[j].strip() == "" or re.match(r"^Artifacts:", lines[j].strip()):
                        capturing = False
                    else:
                        rec_lines.append(lines[j].strip())
                j += 1
            if rec_lines:
                test_level_recommend[tnum] = " ".join(rec_lines)
        i += 1

    i = 0
    while i < len(lines):
        raw = lines[i]
        stripped = raw.strip()

        m_test = TEST_HEADER_RE.match(stripped)
        if m_test:
            current_test_num = int(m_test.group(1))
            current_test_name = m_test.group(2).strip()
            i += 1
            continue

        m_sub = SUBCHECK_RE.match(raw)
        if m_sub and current_test_num is not None:
            subid = m_sub.group(1)
            rest = m_sub.group(2)
            start_idx = i

            # Try inline verdict style first (Part 1, tests 1-2): "Title : VERDICT (...)"
            inline = INLINE_VERDICT_RE.match(rest)
            if inline:
                title = inline.group(1).strip()
                verdict = inline.group(2).strip().upper()
                trail = inline.group(3).strip()
                block_lines = [raw]
                end_idx = i + 1
                recommendation = ""
                rec_source = "none"
                if trail:
                    recommendation = trail.lstrip(" -(").rstrip(")")
                    rec_source = "inline"
            else:
                # Multi-line block style: gather until next sub-check header,
                # "Overall VERDICT" line, or section break.
                stop_res = [SUBCHECK_RE, SECTION_BREAK_RE, re.compile(r"^Overall VERDICT")]
                block_lines, end_idx = collect_paragraph(lines, i, stop_res)
                block_text = "\n".join(block_lines)
                title = rest.strip()
                verdict = ""
                v_m = VERDICT_LINE_RE.search(block_text)
                if v_m:
                    # collapse the verdict + any immediately-following indented
                    # continuation lines already included in block_text
                    verdict = v_m.group(1).strip()
                recommendation = ""
                rec_source = "none"
                r_m = RECOMMEND_LINE_RE.search(block_text)
                if r_m and r_m.group(1).strip():
                    recommendation = r_m.group(1).strip()
                    rec_source = "inline"

            if not verdict:
                verdict = "(no verdict captured)"

            if not recommendation and current_test_num in test_level_recommend:
                recommendation = test_level_recommend[current_test_num]
                rec_source = "test_level"

            point_flag = is_point_verdict(verdict)

            p = Point(
                id=f"P{part_num}-T{current_test_num}-{subid}",
                kind="subcheck",
                severity=None,
                part=part_num,
                part_file=part_file,
                test_number=current_test_num,
                test_name=current_test_name,
                label_raw=subid,
                title=title[:160],
                verdict=verdict,
                recommendation=recommendation,
                recommendation_source=rec_source if recommendation else "none",
                is_point=point_flag,
                source_line_start=start_idx + 1,
                source_line_end=end_idx,
            )
            if point_flag:
                points.append(p)
            else:
                excluded.append(p)

            i = end_idx
            continue

        i += 1

    return points, excluded


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out", default=DEFAULT_OUT, help="output JSON manifest path")
    ap.add_argument(
        "--src-dir", default=SRC_DIR, help="directory containing the 8 real Part*.txt source files"
    )
    ap.add_argument(
        "--include-excluded",
        action="store_true",
        help="also write excluded (non-point, e.g. PASS/UNTESTABLE) sub-checks to a sibling file for transparency",
    )
    args = ap.parse_args()

    all_points = []
    all_excluded = []

    for fname, part_num in PARTS:
        path = os.path.join(args.src_dir, fname)
        if not os.path.isfile(path):
            print(f"ERROR: expected source file missing: {path}", file=sys.stderr)
            sys.exit(1)
        lines = read_part(fname) if args.src_dir == SRC_DIR else open(path).read().split("\n")

        labeled = parse_labeled_findings(lines, part_num, fname)
        subchecks, excluded = parse_subchecks(lines, part_num, fname)

        all_points.extend(labeled)
        all_points.extend(subchecks)
        all_excluded.extend(excluded)

    manifest = [asdict(p) for p in all_points]
    with open(args.out, "w") as f:
        json.dump(manifest, f, indent=2)

    if args.include_excluded:
        excl_path = os.path.splitext(args.out)[0] + "_EXCLUDED_NON_POINTS.json"
        with open(excl_path, "w") as f:
            json.dump([asdict(p) for p in all_excluded], f, indent=2)

    # ---- Summary ----
    from collections import Counter

    by_sev = Counter(p.severity or "SUBCHECK" for p in all_points)
    by_part = Counter(p.part for p in all_points)
    labeled_count = sum(1 for p in all_points if p.kind == "labeled_finding")
    subcheck_count = sum(1 for p in all_points if p.kind == "subcheck")

    print("=" * 70)
    print("Z.AI GTM Audit — Point Enumeration Summary")
    print("=" * 70)
    print(f"Total points: {len(all_points)}")
    print(f"  Labeled findings (BLOCKER/CB/HP/MP/OBS): {labeled_count}")
    print(f"  Sub-check points (FAIL/WARN/PARTIAL verdict): {subcheck_count}")
    print()
    print("By severity/type:")
    for sev in ["CB", "HP", "MP", "OBS", "SUBCHECK"]:
        print(f"  {sev:10s}: {by_sev.get(sev, 0)}")
    print()
    print("By source part:")
    for part_num in range(1, 9):
        print(f"  Part {part_num}: {by_part.get(part_num, 0)}")
    print()
    print(f"Sub-checks excluded (non-point verdicts: PASS/UNTESTABLE/UNVERIFIABLE/"
          f"BLOCKED/N/A/NOT TESTED/CONFIRMS): {len(all_excluded)}")
    print()
    print(f"Manifest written to: {args.out}")
    if args.include_excluded:
        print(f"Excluded non-points written to: {excl_path}")


if __name__ == "__main__":
    main()
