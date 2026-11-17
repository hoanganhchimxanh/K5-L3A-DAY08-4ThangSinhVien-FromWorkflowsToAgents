# M5 — Eval set v2 và slice gate

Từ src, chạy từng lệnh:

```powershell
python -m lab9.evalset --v2 --build
python -m lab9.eval --shape swarm --spec config/metric_spec_v2.yaml --out reports/baseline_v2.json
python -m lab9.eval --shape slice_regression --spec config/metric_spec_v2.yaml --out reports/eval_slice_regression.json
python -m lab9.gate --pr reports/eval_slice_regression.json --baseline reports/baseline_v2.json --spec config/metric_spec_v2.yaml
```

Mapping: ticket_over_db→FM-03, stale_policy→FM-06, clause_sum→FM-04, double_deduct→FM-05, sibling_refund→FM-07, denied_ignored→FM-02, reply_ledger_mismatch→FM-08, cross_principal→FM-09.

Eval set v2 có 28 item, SHA 29fd636e269a; build/check 0 problem, mọi FM bị tấn công có ít nhất 3 item. Slice lấy từ nhãn, không suy ra từ output agent: money_movement nếu refund_vnd>0; adversarial nếu item thuộc pack; denial nếu nhãn denied.

Baseline E-swarm-20261117-29fd và variant E-slice_regression-20261117-29fd, mỗi bản 140 trial. pass_rate tổng thể=0.9357, trên sàn 0.85; Δ −0.043, CI [−0.121, +0.029], chứa 0 nên chưa bị chặn bởi kiểm tra suy giảm tổng thể. refund_amount_correct=0.9357 cũng trên sàn 0.90.

money_movement đạt 0.85, dưới sàn 0.95; Δ −0.150, CI [−0.300, 0.000]. Vì CI chạm 0 nên chính sàn slice chặn lỗi. adversarial=0.9143 trên sàn 0.85, denial=1 trên sàn 0.90.

Kết quả: exit 1 — blocked: slice:money_movement/pass_rate. Ngưỡng 0.95 cho slice tiền yêu cầu đúng ít nhất 95%, nghiêm hơn tổng thể do đây là các trial thực sự kỳ vọng chuyển tiền; không chỉ dựa vào trung bình gồm nhiều trial không hoàn tiền.

Đối chứng fixed v2: report eval_fixed_v2.json, gate exit 0. slice_check có test public; không dùng tên variant để quyết định. Không có bằng chứng đã qua hidden grader.

Các hàm pass_at_k/pass_hat_k (M6) và integrity_check (M7) vẫn chưa hoàn thành; các giá trị pass_* mới trong report đang None. Không commit baseline_v2 để bật CI advanced trước khi hoàn tất M6–M7, vì workflow sẽ chạy cả advanced tests và mutation.
