"""FM-08 distinguishes proposal, ledger and completed refund statements."""
import pytest
from lab9.graders import ReplyLedgerAgreement
from types import SimpleNamespace

pytestmark = pytest.mark.student


def test_no_reply_assertion_is_not_a_money_misreport():
    ctx = SimpleNamespace(output={"events": []})
    assert ReplyLedgerAgreement().evaluate(ctx).value is True


@pytest.mark.parametrize("text,amount,status,expected", [
    ("Dạ, LogiX đã hoàn 35.000đ cho đơn O-808.", 20000, "resolved", False),
    ("Dạ, LogiX đã hoàn 20.000đ cho đơn O-808.", 20000, "resolved", True),
    ("LogiX đã hoàn phí 20,000 VND cho đơn O-808.", 20000, "resolved", True),
    ("Đơn chưa đủ điều kiện hoàn.", 0, "denied", True),
    ("Đã xử lý xong.", 20000, "resolved", False),
    ("Dạ, đã hoàn 35.000đ.", 0, "resolved", False),
])
def test_reply_ledger(text, amount, status, expected):
    ctx = SimpleNamespace(output={"events": [{"kind": "reply", "payload": {"text": text}}],
                                  "snapshot": {"refund_vnd": amount}, "result": {"status": status}})
    assert ReplyLedgerAgreement().evaluate(ctx).value is expected


@pytest.mark.parametrize("proposal,expected", [(150000, True), (120000, False), (0, False)])
def test_proposal_preserves_quote(proposal, expected):
    from lab9.graders import QuoteProposalKept
    ctx = SimpleNamespace(output={"events": [{"kind": "quote", "payload": {"amount_vnd": 150000}}],
                                  "result": {"proposal_amount": proposal}})
    assert QuoteProposalKept().evaluate(ctx).value is expected
