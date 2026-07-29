# v3-bonus — Research post-processing tools

## Mục tiêu

Vượt ngưỡng hơn ba tool do nhóm tự viết mà vẫn giữ catalog nhất quán, có thể kiểm thử và không làm giảm routing của bộ core. Ba tool mới nối tiếp `evidence_audit`, tạo thành pipeline:

`collect → deduplicate → audit/map claims → export citations`

## Thay đổi

### `source_deduplicate`

- Chuẩn hóa URL, bỏ tracking parameter và so khớp title.
- Hỗ trợ strategy `url`, `title`, `url_or_title`.
- Giữ thứ tự nguồn đầu tiên khi `preserve_order=true`.
- Trả về danh sách giữ lại, số lượng đã loại và duplicate groups để audit.
- Guardrail: đây là heuristic nhận diện trùng, không kết luận hai nội dung có cùng ý nghĩa.

### `claim_matrix`

- Ánh xạ từng claim tới các source candidate bằng lexical token overlap.
- Cho phép điều chỉnh `min_overlap` và `max_sources_per_claim`.
- Trả score/từ khóa khớp và các claim chưa có nguồn phù hợp.
- Guardrail: candidate match không phải fact verification hay entailment.

### `citation_export`

- Xuất Markdown, APA-like hoặc BibTeX.
- Chỉ dùng metadata thực sự có trong input; không tự tạo tác giả, ngày hay publisher.
- Có thể bao gồm hoặc bỏ abstract theo yêu cầu.
- Guardrail: APA-like là định dạng deterministic phục vụ lab, không cam kết bao phủ toàn bộ quy chuẩn APA.

## Registry và declaration

- Ba implementation được đăng ký trong `tools/__init__.py`.
- Schema và negative routing được khai báo trong `artifacts/tools.yaml`.
- `select_relevant_tools` chỉ expose nhóm tool bonus khi latest task có intent hậu xử lý tương ứng, hạn chế nhiễu cho core routing.
- Cùng với `evidence_audit`, artifact cuối có bốn tool team-authored.

## Kiểm thử và bằng chứng

| Bằng chứng | Phạm vi | Kết quả hợp lệ |
|---|---|---|
| `tests/test_bonus_tools.py` | Hành vi trực tiếp của ba tool | PASS |
| `tests/test_tool_selection.py` | Scope declaration theo latest task | PASS |
| `data/eval_bonus.json` | 3 single-turn + 3 multi-turn | 6/6 |
| `runs/v3-bonus_B_bonus_openai_20260729T113443811945.json` | Routing/args bonus, OpenAI `gpt-4o-mini` | `measured_cases=6`, `provider_error_cases=0`, accuracy `1.00` |
| `runs/v3-bonus_B_base_openai_20260729T113625222876.json` | Base regression sau mở rộng catalog | `measured_cases=20`, `provider_error_cases=0`, accuracy `1.00` |

Hai run `v3-bonus_B_bonus_openai_20260729T113340477986.json` và `v3-bonus_B_base_openai_20260729T113407768924.json` có provider errors nên không được dùng làm metric. Việc giữ lại chúng giúp audit đầy đủ lịch sử chạy.

## Kết luận

v3-bonus thêm một workflow hậu xử lý có tính kết nối thay vì ba tool rời rạc. Bonus suite đạt 100% và base regression vẫn 100%, vì vậy thay đổi mở rộng năng lực mà không tạo regression đo được trên tập bắt buộc.
