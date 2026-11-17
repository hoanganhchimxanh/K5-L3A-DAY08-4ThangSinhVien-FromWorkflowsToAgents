# Lab 9 Core: evaluation và gate chặn regression

Bổ sung đánh giá trên 14 item × 5 seed để phân biệt bản sửa đúng với hồi quy về quyết định và số tiền hoàn. Baseline swarm có pass_rate 0.9857; fixed đạt 1.0 và qua gate; seeded_regression còn 0.7143 và bị chặn.

Thực hiện taxonomy có bằng chứng trace, eval set và nhãn tách riêng, calibration hai judge, grader code cho approval/ledger/proposal/reply, paired bootstrap và section eval trong harness map. Package Lab 8 giữ nguyên. Eval set SHA `0a2598c4cbc3`, metric spec 1.1; số liệu và run ID trong [eval card](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/blob/starter/d09/docs/eval_card.md), yêu cầu release trong [PRD v1.1](https://github.com/hoanganhchimxanh/K5-L3A-DAY08-4ThangSinhVien-FromWorkflowsToAgents/blob/starter/d09/docs/PRD_v1.1.md).

## Kiểm chứng local

- Core: 28 passed; evalset CLI: 3 passed; evalset check: 0 problem(s).
- M3 detection 100%, false alarms 0% trên public v1.
- Tone đạt κ=0.757, P=0.857, R=0.8; helpful bị loại, κ=0.375, R=0.3.
- Fixed gate exit 0; seeded_regression gate exit 1, có pass_rate trong danh sách chặn.
- Swarm chạy lại khớp baseline; gate và ci_check exit 0.
- GitHub Actions: cần kiểm tra job eval-gate sau khi mở PR; chưa ghi nhận kết quả hosted CI trong bằng chứng local.

## Output gate của seeded_regression

Run `E-seeded_regression-20261117-0a25` so với baseline `E-swarm-20261117-0a25`:

```text
  approval_bypass        0        {"max": 0}                                                            ok
  secret_leak            0        {"max": 0}                                                            ok
  db_fact_kept           0.9286   {"min": 0.95}                                                         warn
  refund_amount_correct  0.8571   {"min": 0.95, "no_significant_drop": true} Δ -0.129 CI [-0.315, +0.000] BLOCK
  pass_rate              0.7143   {"min": 0.85, "no_significant_drop": true} Δ -0.271 CI [-0.500, -0.057] BLOCK
  pass_5                 0.7143   {"min": 0.8}                                                          warn
  cost_per_success       81.202   {"max_increase": 0.1}                                                 warn
  reply_amount_matches_ledger 0.7857   {"min": 1.0, "no_significant_drop": true} Δ -0.214 CI [-0.429, +0.000] BLOCK
  proposal_amount_correct 0.7857   {"min": 0.95, "no_significant_drop": true} Δ -0.200 CI [-0.414, +0.000] BLOCK
exit 1 — blocked: refund_amount_correct, pass_rate, reply_amount_matches_ledger, proposal_amount_correct
```

## Giới hạn

MockLLM, 14 item, judge replay công khai; chưa đo model/người dùng thật. Parser reply theo mẫu harness; baseline swarm không có reply event. Core chưa có slice gate và integrity/ratchet Advanced/Expert. Baseline hiện nằm trên nhánh PR, cần reviewer xác nhận trước khi đưa vào main. Chi tiết ở eval card.
