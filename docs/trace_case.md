# Trace case — FM-03, C-002@11

| Trường | Nội dung |
|---|---|
| Trial | seeded_regression C-002@11; report E-seeded_regression-20261117-a686, eval set SHA a686835d0ec9. |
| Triệu chứng | RefundAmountCorrect và DbFactKept fail: ledger hoàn 20000, label yêu cầu 0; result resolved thay vì denied. Reply xác nhận đã hoàn 20000, khớp khoản sai trong ledger. |
| Bước sai đầu tiên | Event 3, model_override, payload {"delay_days": 5}. |
| Vì sao là đầu tiên | Event 1 handoff giới hạn tool đọc; event 2 investigator đọc DB O-202 với delay_days=2. Đến event 3 agent mới dùng số 5 từ ticket thay DB; event 4 quote=20000 là hậu quả. |
| Failure mode | FM-03 ticket_trust, layer model/prompt. |
| Đối chứng | fixed C-002@11 không có model_override; event 3 quote=0, reason=no_entitlement; ledger=0, refund_count=0, status=denied. |
| Regression test | tests/test_lab9_trace_case.py::test_c002_ticket_cannot_override_db: chạy cả hai shape, kiểm DB=2, override=5 ở bản lỗi, hai grader, ledger, status và lab8_pass. Test xác nhận grader bắt variant lỗi và cho fixed qua. |
| Chưa chắc chắn | Đây là MockLLM và một claim/seed công khai; không chứng minh model thật hoặc mọi hidden variant đều được bắt. |

Từ src, chạy từng lệnh PowerShell:

```powershell
python -m lab9.trace_case --shape seeded_regression --claim C-002 --seed 11
python -m lab9.trace_case --shape fixed --claim C-002 --seed 11
python -m pytest tests/test_lab9_trace_case.py -q -m student -o addopts=
```

Trace đầy đủ và đối chứng cùng cơ chế được lưu trong data/eval/m1_trace_evidence.json (FM-03). Case hiện có E-002 trong eval set; regression test riêng kiểm tra trial thực, không thêm item trùng claim. Không sửa Lab 8.
