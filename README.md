# Challenge A — Persistent memory

Agent lưu quy ước dự án giữa các session, cập nhật quy ước cùng chủ đề và giữ lịch sử giá trị bị thay thế. Phát triển từ mã mẫu ChallengeA_CodeOnly.zip; phạm vi là Challenge A, slide 14–15.

## Cài đặt và chạy

```bash
python -m venv .venv
.venv/bin/python -m pip install -r requirements.lock.txt
# Nhập khóa vào terminal, không ghi vào mã nguồn hoặc commit:
read -rsp 'Mistral API key: ' OPENAI_API_KEY; echo
export OPENAI_API_KEY
export OPENAI_BASE_URL=https://api.mistral.ai/v1
export MODEL_NAME=codestral-2508
.venv/bin/python main.py --show-memory
```

Lệnh `/memory` in chính xác JSON quy ước hiện hành được inject vào context; `/exit` đóng session. Có thể dùng `--ask 'câu hỏi' --show-memory` để chạy một lượt với session mới. `MODEL_NAME` ưu tiên hơn `OPENAI_MODEL`. API key chỉ lấy từ môi trường.

## Chứng minh đúng yêu cầu

```bash
.venv/bin/python -m unittest -v  # Không gọi API
.venv/bin/python demo.py        # Gọi API thật, cần khóa; phát sinh phí sử dụng
```

Demo tạo file memory tạm riêng, chạy **4 tiến trình Python độc lập**, không chia sẻ lịch sử chat:

1. Session 1 yêu cầu lưu `authentication = JWT`; model phải gọi tool thành công.
2. Session 2 nạp JSON đã lưu và trả lời JWT — chứng minh 1.
3. Session 3 đổi cùng key thành `session cookie`; model phải gọi tool cập nhật.
4. Session 4 nạp giá trị mới và trả lời session cookie, không JWT — chứng minh 2.

Demo kiểm tra câu trả lời, memory đã inject, tool ghi thành công và lịch sử JWT. Kết quả chi tiết ở `artifacts/demo_result.json` chỉ được ghi sau khi toàn bộ assertion pass. File memory demo được xóa sau lần chạy; không thay đổi memory đang dùng của bạn. Có thể chạy lại độc lập.

## Thiết kế

- **Ghi:** model gọi `remember_convention` khi user chỉ định quy ước. Key cùng chủ đề phải được dùng lại khi cập nhật.
- **Lưu:** JSON mặc định `project_memory.json` bên cạnh mã nguồn; đổi bằng `AGENT_MEMORY_FILE`. Ghi file tạm rồi atomic replace để tránh ghi dở.
- **Đọc:** nạp từ đĩa lúc mở session và trước mỗi lượt; cập nhật context sau tool call.
- **Thay đổi:** mỗi key có một `value` hiện hành, timestamp UTC, nguồn `user` và `history` có `superseded_at`. Chỉ value hiện hành vào context.
- **Lỗi:** memory hỏng không bị coi là rỗng rồi ghi đè; tool lỗi không trả thành công. Giới hạn 8 vòng tool, timeout API 45 giây.

Giới hạn: bản demo cho một người ghi tại một thời điểm; chưa có khóa liên tiến trình để xử lý ghi đồng thời. Nhận biết hai tên key đồng nghĩa dựa trên model, chưa có bộ chuẩn hóa ngữ nghĩa. Không phải mọi lời khẳng định từ model đều bảo đảm đúng, vì vậy demo kiểm tra cả dữ liệu lưu thực tế.
