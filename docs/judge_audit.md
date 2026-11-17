# Judge audit

Chạy: `python -m lab9.judge --csv <file> --audit 5`

| Tiêu chí | n | κ | Precision | Recall | Đạt FLOORS (κ≥0.6, P≥0.8, R≥0.7)? | Quyết định |
|---|---|---|---|---|---|---|
| tone_ok | 100 | 0.757 | 0.857 | 0.800 | Có | Dùng cho tiêu chí tone trên phạm vi đã calibration |
| helpful | 100 | 0.375 | 1.000 | 0.300 | Không: κ và recall dưới ngưỡng | Loại khỏi gate ở phiên bản hiện tại |

FAIL là lớp dương; nhãn human là tham chiếu. Tone có TP=24, FP=4, FN=6, TN=66; helpful có TP=9, FP=0, FN=21, TN=70. Tỷ lệ FAIL quan sát → Rogan–Gladen hiệu chỉnh: tone 0.28 → 0.30; helpful 0.09 → 0.30.

## ≥5 case audit thủ công
Đối chiếu reply và các cột note/human_failure trong hai CSV công khai. Với helpful, số tiền ledger dưới đây lấy từ note của dữ liệu calibration, không phải từ một lần chạy agent mới.

| # | Case | Judge nói | Người nói | Ai đúng? / Bằng chứng | Sửa rubric đề xuất |
|---|---|---|---|---|---|
| 1 | H-008 | PASS | FAIL | Human: “Em ... anh ... nha, anh check” quá suồng sã theo quy chuẩn tone trong dữ liệu; judge nhầm thân mật với phù hợp. | Nêu rõ cách xưng hô, mức thân mật được phép; thêm ví dụ FAIL cho “nha”, “anh check giúp em” trong ngữ cảnh này. |
| 2 | H-017 | PASS | FAIL | Human: note xác định khách lớn tuổi; “bạn ơi ... rồi nha” không phù hợp. Tuổi khách không thể suy ra chỉ từ reply. | Cung cấp ngữ cảnh khách cho judge; dùng “anh/chị” khi thiếu ngữ cảnh, không tự suy đoán tuổi. |
| 3 | H-029 | PASS | FAIL | Human: “không cần nhắn thêm” mang giọng ra lệnh dù mở đầu “Dạ, vui lòng”. | Chấm toàn bộ nội dung; từ lịch sự không bù được câu ra lệnh hoặc ngăn khách trao đổi. |
| 4 | H-042 | FAIL | PASS | Human: câu ngắn nhưng lịch sự, thông báo số tiền và thời gian; note cho biết judge phạt vì thiếu xin lỗi. Đây chỉ là đánh giá tone, không xác minh số tiền. | Không bắt buộc xin lỗi trong mọi phản hồi; không phạt độ ngắn khi câu vẫn lịch sự và đủ ý. |
| 5 | H-051 | FAIL | PASS | Human: từ “refund” được quy chuẩn CS trong dữ liệu cho phép; dùng tiếng Anh không tự động là lỗi tone. | Thêm danh sách thuật ngữ được phép và ví dụ PASS; không cấm tiếng Anh một cách máy móc. |
| 6 | HL-015 | PASS | FAIL | Human: reply báo 55000 nhưng note ledger ghi 40000; đây là FN về tính đúng của số tiền. | Tách factual correctness khỏi tone; số tiền đã hoàn phải khớp ledger, kiểm bằng code. |
| 7 | HL-016 | PASS | FAIL | Human: lời xin lỗi dài nhưng reply báo 55000, ledger ghi 35000. Lịch sự không sửa được thông tin sai. | Sai tiền là điều kiện FAIL độc lập; không cộng điểm lịch sự để bù lỗi tiền. |
| 8 | HL-020 | PASS | FAIL | Human: reply báo 90000 nhưng ledger ghi 120000. Judge bỏ sót sai lệch dù câu trôi chảy. | Cấp dữ liệu ledger cho bước kiểm tra; so chính xác tiền bằng code trước đánh giá ngôn ngữ. |
| 9 | HL-028 | PASS | FAIL | Human: reply xin lỗi lặp lại, báo 50000 trong khi ledger ghi 35000. | Không xem độ dài hoặc số lần xin lỗi là bằng chứng helpful; yêu cầu thông tin đúng, liên quan và không lặp. |
| 10 | HL-035 | PASS | FAIL | Human: reply báo 50000 nhưng ledger ghi 35000, kèm nhiều câu xin lỗi. | Ưu tiên kiểm tra hành động và số liệu; thêm cặp ví dụ câu lịch sự nhưng sai tiền phải FAIL. |

## Kết luận
- **Dùng tone trong phạm vi đã calibration:** κ=0.757, P=0.857, R=0.800 đều vượt floors. Vẫn có 6 lỗi bị bỏ sót và 4 báo lỗi nhầm; kết quả PASS không có nghĩa judge hoàn hảo hoặc chấm được tiền/approval.
- **Không dùng helpful làm gate:** TP=9, FP=0, FN=21, TN=70. Judge chỉ tìm được 9/30 lỗi, bỏ sót 70% lỗi thật; κ=0.375 và recall=0.300 dưới ngưỡng 0.6 và 0.7. Precision=1 chỉ nói các lần judge báo FAIL đều đúng, không bảo đảm những lần PASS an toàn. Accuracy=79% cũng không khắc phục được recall thấp. Các case audit cho thấy judge cho qua lời trả lời lịch sự nhưng sai tiền, tạo nguy cơ merge regression.
- **Rogan–Gladen không cứu được gate:** helpful có sensitivity=0.3 và specificity=1, nên tỷ lệ lỗi quan sát 0.09 được hiệu chỉnh thành 0.30. Hiệu chỉnh ước lượng tỷ lệ lỗi tổng thể không sửa được verdict từng case hoặc phục hồi 21 FN, nên không thay thế điều kiện calibration.
- **Phân công grader:** tiền, ledger và approval chấm bằng code; judge tone chỉ đánh giá ngôn ngữ. Có thể thiết kế lại helpful với tiêu chí tách biệt và ngữ cảnh đầy đủ, rồi calibration lại trước khi cân nhắc dùng.
- **Giới hạn:** dữ liệu đang replay công khai; chưa có nhãn người mới làm held-out thật. Các sửa rubric ở bảng mới là đề xuất, chưa chạy judge mới và không làm verdict CSV tự thay đổi. Cần đánh giá phiên bản mới trên dữ liệu held-out độc lập; không sửa nhãn để ép PASS.
