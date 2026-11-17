"""Reproduce isolated M1 failure traces without changing Lab 8 or default shapes."""
import json
from pathlib import Path

from lab8.shapes import SHAPES
from lab9.trace_case import investigate
from lab9.variant_agent import make_shape

CASES = {
    "FM-01": ("leaky_trace", "C-002"),
    "FM-02": ("ignore_denied", "C-007"),
    "FM-03": ("ticket_trust", "C-002"),
    "FM-04": ("sum_parts", "C-014"),
    "FM-05": ("pre_deducted", "C-014"),
    "FM-06": ("stale_clause", "C-006"),
    "FM-07": ("sibling_refund", "C-001"),
    "FM-08": ("misreport", "C-008"),
}


def main():
    evidence = {}
    for fm, (bug, claim) in CASES.items():
        name = "m1_" + bug
        SHAPES[name] = make_shape(name, {"no_override", bug})
        evidence[fm] = {"shape": name, "claim_id": claim, "seed": 11,
                        "bug": investigate(name, claim, 11),
                        "fixed": investigate("fixed", claim, 11)}
    out = Path("data/eval/m1_trace_evidence.json")
    out.write_text(json.dumps(evidence, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out}")
    for fm, case in evidence.items():
        t = case["bug"]["trial"]
        print(fm, case["claim_id"], t["lab8_reason"])
        for n, event in enumerate(t["events"], 1):
            if event["kind"] != "investigator":
                print(n, json.dumps(event, ensure_ascii=True))
        print("snapshot", t["snapshot"], "unexpected", t["unexpected_rows"])


if __name__ == "__main__":
    main()
