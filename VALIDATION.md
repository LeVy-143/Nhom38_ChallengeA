# Kết quả kiểm chứng

## Local

`python -m unittest -v`: 6 tests PASS, bao gồm tiến trình mới đọc lại JWT rồi session cookie sau cập nhật. Kiểm tra thêm lịch sử, chỉ inject quy ước hiện hành, ghi lặp không đổi dữ liệu, file hỏng không bị ghi đè và bảo toàn dữ liệu khi atomic replace thất bại.

`python -m pip check`: PASS.

## API thật — chưa hoàn tất

Đã thử gọi Mistral với model `ministral-3b-2512` và khóa do người dùng cung cấp. Kết nối bị egress proxy chặn: CONNECT tunnel trả `403 Forbidden` trước khi tới API. Không có bằng chứng khóa sai hoặc model không tồn tại; chưa có câu trả lời từ model và chưa pass demo end-to-end.

Đã lưu draft bổ sung `api.mistral.ai`, hướng dẫn cài/chạy và biến cấu hình không bí mật. Cần review/save trong Environment settings và publish môi trường; thao tác lưu draft không tự áp dụng quyền mạng. Sau khi mạng được áp dụng, nhập khóa an toàn vào môi trường của terminal và chạy `python demo.py` theo README. Không lưu khóa trong cấu hình mã nguồn hoặc gói nộp bài.

File `artifacts/demo_result.json` chỉ xuất hiện khi demo thật pass toàn bộ kiểm tra. Không dùng kết quả local để thay thế bằng chứng model qua API.
