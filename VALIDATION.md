# Kết quả kiểm chứng

## Local

`python -m unittest -v`: 6 tests PASS, gồm tiến trình mới đọc lại JWT rồi session cookie sau cập nhật; kiểm tra lịch sử, chỉ inject giá trị hiện hành, lưu lặp, file hỏng và lỗi atomic replace.

`python -m pip check`: PASS.

## API thật — PASS

Đã gọi endpoint `https://api.mistral.ai/v1` với model `codestral-2508`. Kiểm tra native tool calling thành công (`ping`). Demo `python demo.py` chạy 4 tiến trình Python độc lập, không chia sẻ lịch sử hội thoại:

1. Session 1: model gọi `remember_convention` thành công, lưu `authentication = JWT`.
2. Session 2: memory inject là JWT; model trả lời `JWT` — chứng minh nhớ qua session mới.
3. Session 3: model gọi tool cập nhật `authentication = session cookie` thành công.
4. Session 4: memory inject là session cookie; model trả lời `session cookie`, không JWT — chứng minh cập nhật cho session sau.

Kiểm tra file cuối cùng có giá trị hiện hành session cookie và lịch sử JWT đã bị thay thế. Toàn bộ assertion của demo PASS.

Bằng chứng gốc: [artifacts/demo_result.json](artifacts/demo_result.json), chứa câu hỏi, câu trả lời, memory inject, kết quả tool và memory cuối. Timestamp ghi memory: 2026-10-22 UTC. Không chứa khóa API.

Để tái hiện, cung cấp khóa bằng biến môi trường an toàn, đặt `OPENAI_BASE_URL=https://api.mistral.ai/v1`, `MODEL_NAME=codestral-2508` và chạy theo README. Lần thử trước với ministral bị proxy chặn; kết quả PASS ở đây thuộc lần chạy mới với codestral, không xác nhận model ministral.
