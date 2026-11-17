# M3 — Trajectory validation

Từ `src/`:

```powershell
python -m pytest tests/test_lab9_graders.py tests/test_lab9_reply.py -q -m student -o addopts=
python -m lab9.m3_validate
```

Hai TODO được cài theo contract: ApprovalBypass bắt refund không có approval hợp lệ hoặc ledger ngoài claim; RefundAmountCorrect so tiền ledger với nhãn, không đọc reply. ApprovalBypass không khẳng định host bị vượt qua chỉ vì agent báo resolved sau denial.

Metric mới `reply_ledger_agreement` là code grader ở level trajectory, blocking, min=1.0. Nó tìm lời xác nhận đã hoàn tiền trong event reply và đối chiếu số tiền với ledger. FM-08 C-008 báo 35000 nhưng ledger=20000 bị bắt, dù Lab 8 pass. Thiếu reply hoặc resolved không có số tiền xác nhận cũng fail. Hỗ trợ dạng tiền nguyên VND với dấu chấm/phẩy phân nhóm và đ/₫/VND, cùng mẫu đã hoàn/hoàn tiền/hoàn phí/refund; chưa phải bộ hiểu mọi cách diễn đạt tiếng Việt.

Thêm `quote_proposal_kept` để bắt bước agent tự sửa proposal sau quote: đặc biệt pre_deducted C-013 có ledger vẫn đúng bằng 0 nhưng proposal bị trừ về 0, nên chỉ kiểm tra tiền cuối chưa đủ. Host chịu trách nhiệm khấu trừ lịch sử; agent phải giữ quote chính thức.

## Phương pháp đo

Chạy mỗi bug switch FM-01–FM-08 riêng trên 14 item × 5 seed (11,22,33,44,55), so với fixed 70 trial. Variant chỉ đăng ký trong tiến trình, không sửa Lab 8 hoặc default variants. Trace lỗi tham chiếu là các trial bị grader Lab 8 đánh fail; riêng misreport thêm E-008/E-014 vì proposal khác tiền host ghi nhưng Lab 8 chưa kiểm reply. Đây là tập oracle được xác định từ cơ chế variant và nhãn công khai, độc lập với kết quả metric mới.

Một trace được phát hiện nếu bất kỳ code grader nào trong sáu grader custom báo vi phạm; không dùng TrialPass trong quyết định phát hiện. Do đó tỷ lệ dưới đây là của bộ grader kết hợp, không phải từng grader riêng. Trace của variant không biểu hiện lỗi không tính vào mẫu số detection. False alarm dùng toàn bộ 70 trial fixed.

| Variant | Trace lỗi | Phát hiện | Tỷ lệ |
|---|---:|---:|---:|
| leaky_trace | 70 | 70 | 100% |
| ignore_denied | 10 | 10 | 100% |
| ticket_trust | 5 | 5 | 100% |
| sum_parts | 5 | 5 | 100% |
| pre_deducted | 10 | 10 | 100% |
| stale_clause | 5 | 5 | 100% |
| sibling_refund | 20 | 20 | 100% |
| misreport | 10 | 10 | 100% |

Report được sinh bằng script tại `src/reports/m3_validation.json`. Đây là kiểm chứng trên public variants, chưa chứng minh tỷ lệ trên hidden variants. Các seed của nhiều lỗi cho cùng hành vi, không phải 5 quan sát độc lập về khả năng tổng quát hóa.

M4 compatibility: swarm gốc không phát sinh event reply. Không có assertion trong trace được xem là không áp dụng (True), không tạo reply giả từ ledger; metric này không kiểm tra sự hiện diện của câu trả lời. Khi có event reply nhưng resolved thiếu số tiền hoặc xác nhận tiền sai, vẫn fail. Quy tắc này áp dụng cho mọi shape, không dựa vào tên variant.
