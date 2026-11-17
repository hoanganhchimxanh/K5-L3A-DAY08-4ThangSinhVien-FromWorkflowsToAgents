"""Regression evidence for FM-03 C-002@11 documented in trace_case.md."""
from types import SimpleNamespace
import pytest
from lab9.trace_case import investigate
from lab9.graders import DbFactKept, RefundAmountCorrect

pytestmark = pytest.mark.student


@pytest.mark.parametrize("shape,correct,refund,status", [
    ("seeded_regression", False, 20000, "resolved"),
    ("fixed", True, 0, "denied"),
])
def test_c002_ticket_cannot_override_db(shape, correct, refund, status):
    case = investigate(shape, "C-002", 11)
    trial = case["trial"]
    ctx = SimpleNamespace(output=trial, expected_output=case["label"])
    assert DbFactKept().evaluate(ctx).value is correct
    assert RefundAmountCorrect().evaluate(ctx).value is correct
    assert trial["snapshot"]["refund_vnd"] == refund
    assert trial["result"]["status"] == status
    assert trial["lab8_pass"] is correct
    assert trial["events"][1]["payload"]["lookup_order"]["order"]["delay_days"] == 2
    if not correct:
        assert trial["events"][2] == {"kind": "model_override", "payload": {"delay_days": 5}}
