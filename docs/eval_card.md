# Eval card — LogiX-VN refund agent, Core v1

## Phiên bản và bằng chứng

- Ngày tổng hợp: 17/11/2026, Asia/Saigon.
- Mã nguồn đo đã chốt ở commit `f88d2f907b46069e34e5564cb4be76ffdb14d4bd`; grader ở commit `92f519ba5165e4a727659ae258ac0b7658350423`. Commit tiếp theo chỉ bổ sung tài liệu.
- Eval set v1, SHA `0a2598c4cbc3`, nguồn `lab8_public`, 14 item × 5 seed = 70 trial mỗi shape; seeds 11/22/33/44/55. Nhãn nằm riêng trong `labels_v1.json`.
- Metric spec 1.1, harness map 1.2; Python 3.13.18, MockLLM offline, judge replay; không cần API key.
- Baseline swarm: `E-swarm-20261117-0a25` — [baseline_v1.json](../src/reports/baseline_v1.json).
- Bản fixed: `E-fixed-20261117-0a25` — [eval_fixed.json](../src/reports/eval_fixed.json).
- Bản regression: `E-seeded_regression-20261117-0a25` — [eval_seeded_regression.json](../src/reports/eval_seeded_regression.json).
- Mọi số đo trong bảng dưới lấy từ các report trên; threshold lấy từ [metric_spec.yaml](../src/config/metric_spec.yaml). Report do script sinh, không sửa tay.

## Metric và kết quả

| Metric | Ngưỡng | Chặn merge? | Baseline swarm | Fixed | Seeded regression |
|---|---|---|---|---|---|
| approval_bypass | ≤ 0 | Có | 0 | 0 | 0 |
| secret_leak | ≤ 0 | Có | 0 | 0 | 0 |
| db_fact_kept | ≥ 0.95 | Không | 0.9857 | 1.0000 | 0.9286 |
| refund_amount_correct | ≥ 0.95; CI của Δ không nằm hoàn toàn dưới 0 | Có | 0.9857 | 1.0000 | 0.8571 |
| pass_rate | ≥ 0.85; CI của Δ không nằm hoàn toàn dưới 0 | Có | 0.9857 | 1.0000 | 0.7143 |
| pass_5 | ≥ 0.8 | Không | 0.9286 | 1.0000 | 0.7143 |
| cost_per_success | ≤ 1.10 × baseline | Không | 49.5670 | 48.7157 | 81.2020 |
| reply_amount_matches_ledger | ≥ 1.0; CI của Δ không nằm hoàn toàn dưới 0 | Có | 1.0000 | 1.0000 | 0.7857 |
| proposal_amount_correct | ≥ 0.95; CI của Δ không nằm hoàn toàn dưới 0 | Có | 0.9857 | 1.0000 | 0.7857 |

`approval_bypass` và `secret_leak` là số vi phạm, không phải tỷ lệ đạt. `cost_per_success` là chi phí mô phỏng của harness, không phải giá API hoặc tiền thực. Metric không blocking vẫn được báo cáo khi dưới ngưỡng.

## Paired bootstrap

Δ = PR − baseline. Tính trung bình qua 5 seed cho từng item rồi bootstrap các cặp cùng item; đơn vị lấy mẫu là 14 item, không phải 70 trial độc lập. Cấu hình: percentile, 1000 resample, RNG 2027, confidence 95%.

| Phiên bản | Metric | Δ | CI 95% |
|---|---|---|---|
| fixed | refund_amount_correct | +0.014 | [+0.000, +0.043] |
| seeded_regression | refund_amount_correct | -0.129 | [-0.315, +0.000] |
| fixed | pass_rate | +0.014 | [+0.000, +0.043] |
| seeded_regression | pass_rate | -0.271 | [-0.500, -0.057] |
| fixed | reply_amount_matches_ledger | +0.000 | [+0.000, +0.000] |
| seeded_regression | reply_amount_matches_ledger | -0.214 | [-0.429, +0.000] |
| fixed | proposal_amount_correct | +0.014 | [+0.000, +0.043] |
| seeded_regression | proposal_amount_correct | -0.200 | [-0.414, +0.000] |

Gate cho `fixed` qua (exit 0). Gate chặn `seeded_regression` (exit 1) ở: refund_amount_correct, pass_rate, reply_amount_matches_ledger, proposal_amount_correct. Với pass_rate, CI nằm hoàn toàn dưới 0; các metric có CI chạm 0 vẫn có thể bị chặn do không đạt sàn tuyệt đối.

## Judge và trace case

- Tone: κ=0.757, Precision=0.857, Recall=0.8; đạt FLOORS cho tiêu chí giọng điệu trên tập replay.
- Helpful: κ=0.375, Precision=1.0, Recall=0.3; loại khỏi gate vì bỏ sót 21 lỗi. Hiệu chỉnh tỷ lệ lỗi không sửa verdict từng case.
- [Judge audit](judge_audit.md) có 10 bất đồng và hành động sửa rubric. Tiền và approval luôn dùng code.
- [Trace case](trace_case.md): C-002@11, bước sai đầu tiên là event 3 `model_override`; bản fixed không ghi đè DB và PASS. Regression test nằm ở `tests/test_lab9_trace_case.py`.
- [Failure taxonomy](failure_taxonomy.md) có bằng chứng cho FM-01 đến FM-08. FM-09 và anchor key riêng chưa được kiểm chứng bằng bộ chấm ẩn.

## Kiểm chứng local và vận hành gate

- Test Core: 28 passed; test CLI evalset: 3 passed; evalset check: 0 problem(s).
- M3: detection 100%, false alarms 0% trên bộ public v1, theo định nghĩa của `lab9.mutation --detect`.
- Các report đều đủ 70 dòng và không có evaluator failures. Swarm chạy lại khớp baseline, gate exit 0 và `lab9.ci_check` exit 0.
- Đầu mối xử lý gate đề xuất: Nguyễn Tuấn Hiếu, lead tổng hợp theo [TEAM.md](../TEAM.md); reviewer của PR xác nhận phân công và kết quả trước merge.
- Gate exit 1: tác giả PR tìm trial lỗi và bước sai đầu tiên, sửa grader/code Lab 9 phù hợp rồi sinh lại report. Giữ nguyên Lab 8, các variant/trap và các ngưỡng đã chốt trên cùng eval-set version.
- GitHub Actions chưa được chạy trong phiên local này. Cần push `starter/d09`, mở PR vào `main` và kiểm tra job `eval-gate`.

## Phạm vi và giới hạn

- Pilot hiện tại là đánh giá offline trên public v1: phí ship do giao trễ, hàng hỏng đã xác minh và các tình huống từ chối/thiếu thông tin; không chuyển tiền thật.
- Chủ thể chỉ được xử lý đơn của mình. Host áp dụng approval cùng claim, hạn mức approval/paid, lịch sử hoàn tiền theo order và một hiệu ứng cho mỗi claim; không đặt hạn mức sản phẩm mới trong Lab 9.
- Ngoài phạm vi bằng chứng: dữ liệu người dùng thật, hiệu năng model thật, latency, khiếu nại nhiều đơn, và đánh giá an toàn production.
- MockLLM và 14 item cho CI rộng; chỉ bắt chắc được regression đủ lớn. Năm seed không bảo đảm phát hiện mọi lỗi hiếm; một lỗi chỉ xảy ra với xác suất 1/3 mỗi lần vẫn có thể bị bỏ sót, và các seed của MockLLM không đại diện cho mẫu ngẫu nhiên từ LLM thật.
- Judge replay đã công khai, chưa có held-out mới có nhãn người. Tone đạt calibration không có nghĩa nội dung tài chính đúng.
- ReplyAmountMatchesLedger kiểm tra lời khẳng định số tiền đã hoàn theo mẫu của harness. Swarm Lab 8 không có reply event nên metric trả True khi không có mâu thuẫn để kiểm; số 1.0 của baseline không chứng minh đã kiểm tra chất lượng reply. Tiền viết bằng chữ, thiếu đơn vị hoặc mẫu câu khác cần mở rộng parser và dữ liệu.
- Core chưa cài slice gate, integrity/ratchet M7 hoặc độ ổn định pass^k M6. Các kết quả hiện tại không chứng minh chống được report bị làm đẹp.
- Đổi item, nhãn hoặc nội dung đánh giá phải tăng eval-set version và sinh baseline tương ứng; đổi metric/ngưỡng tăng metric-spec version. Cùng eval-set version chỉ siết ngưỡng, không nới để cho regression qua. Sinh JSONL với LF để SHA giữ nguyên sau checkout trên Windows/Linux.
