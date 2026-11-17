"""Integrity must reject manipulated evidence even when summary metrics are green."""
import copy
import pytest
from lab9.gate import integrity_check

pytestmark = pytest.mark.student


def fixture_report():
    return {"manifest": {"items": 2, "seeds": [1, 2]},
            "rows": [{"item_id": i, "seed": s, "pass_rate": True, "slices": ["money"]}
                     for i in ("a", "b") for s in (1, 2)],
            "metrics": {"pass_rate": 1.0}, "evaluator_failures": []}


SPEC = {"eval_set_version": "v2", "metrics": [
    {"id": "pass_rate", "blocking": True, "threshold": {"min": .8, "no_significant_drop": True}}],
    "slices": [{"name": "money", "metric": "pass_rate", "min": .9, "blocking": True}]}


@pytest.mark.parametrize("mutation", ["duplicate", "green_error", "missing", "slice", "infinite"])
def test_green_report_tampering(mutation):
    base = fixture_report()
    pr = copy.deepcopy(base)
    if mutation == "duplicate":
        pr["rows"][-1] = copy.deepcopy(pr["rows"][0])
    elif mutation == "green_error":
        pr["evaluator_failures"] = ["grader crashed"]
    elif mutation == "missing":
        pr["rows"][0]["pass_rate"] = None
    elif mutation == "slice":
        pr["rows"][0]["slices"] = []
    else:
        pr["metrics"]["pass_rate"] = float("inf")
    assert integrity_check(pr, base, SPEC)


@pytest.mark.parametrize("mutation", ["drop_metric", "drop_slice", "drop_blocking", "drop_ci", "lower_floor"])
def test_ratchet(mutation):
    loose = copy.deepcopy(SPEC)
    if mutation == "drop_metric":
        loose["metrics"] = []
    elif mutation == "drop_slice":
        loose["slices"] = []
    elif mutation == "drop_blocking":
        loose["slices"][0]["blocking"] = False
    elif mutation == "drop_ci":
        loose["metrics"][0]["threshold"].pop("no_significant_drop")
    else:
        loose["metrics"][0]["threshold"]["min"] = .5
    base = fixture_report()
    assert integrity_check(base, base, loose, SPEC)
