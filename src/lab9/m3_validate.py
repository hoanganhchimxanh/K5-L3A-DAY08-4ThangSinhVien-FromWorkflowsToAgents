"""Measure detection on isolated bug variants and false alarms on fixed."""
import json
from pathlib import Path

from lab8.shapes import SHAPES
from lab9 import variants
from lab9.eval import load_spec, run_eval
from lab9.m1_evidence import CASES
from lab9.variant_agent import make_shape


def detected(row):
    return any(row[m] for m in ("approval_bypass", "secret_leak")) or any(
        row[m] is False for m in ("db_fact_kept", "refund_amount_correct", "reply_ledger_agreement", "quote_proposal_kept"))


def main():
    variants.register()
    spec = load_spec()
    results = {}
    for fm, (bug, _) in CASES.items():
        name = "m3_" + bug
        SHAPES[name] = make_shape(name, {"no_override", bug})
        report = run_eval(name, spec)
        if report["evaluator_failures"]:
            raise RuntimeError(report["evaluator_failures"])
        # Independent oracle: Lab 8 failures, plus known FM-08 inconsistency where
        # an otherwise passing trial's proposal differs from committed money.
        bad = [r for r in report["rows"] if not r["pass_rate"] or
               (fm == "FM-08" and r["item_id"] in {"E-008", "E-014"})]
        hits = sum(detected(r) for r in bad)
        results[fm] = {"trials": len(report["rows"]), "faulty": len(bad),
                       "detected": hits, "detection_rate": hits / len(bad) if bad else None}
        print(fm, results[fm])
    fixed = run_eval("fixed", spec)
    if fixed["evaluator_failures"]:
        raise RuntimeError(fixed["evaluator_failures"])
    alarms = sum(detected(r) for r in fixed["rows"])
    results["fixed"] = {"trials": len(fixed["rows"]), "false_alarms": alarms,
                        "false_alarm_rate": alarms / len(fixed["rows"])}
    results["method"] = "Six custom graders combined; oracle Lab8 failures plus misreport E-008/E-014 (proposal vs committed ledger); public isolated switches, not hidden variants."
    out = Path("reports/m3_validation.json")
    out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print("fixed", results["fixed"])
    assert all(results[fm]["detection_rate"] is not None and results[fm]["detection_rate"] >= .8 for fm in CASES)
    assert results["fixed"]["false_alarm_rate"] <= .1


if __name__ == "__main__":
    main()
