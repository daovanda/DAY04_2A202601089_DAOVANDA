# Day 04 Lab v2 Report — Research Agent

## Team

- Team: Đào Văn Đà
- Members: Đào Văn Đà, Nguyễn Quốc Anh, Nguyễn Hoàng Vĩnh Phong, Trương Quốc Trường, Nguyễn Ngọc Ánh
- Provider/model: OpenAI / `gpt-4o-mini`
- Artifact cuối: `v3-bonus+p47281754cffc+t3d17fc26cdfc`

---

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì?

Research Agent hỗ trợ tìm tin web và mạng xã hội, đọc URL, tìm paper arXiv, tổng hợp kết quả và kiểm tra chất lượng bằng chứng. Agent duy trì ngữ cảnh hội thoại, hỏi lại khi thiếu dữ liệu, không tự ý thực hiện hành động xuất bản, và có pipeline hậu xử lý gồm audit, loại nguồn trùng, ánh xạ claim–source và xuất citation.

**Link dùng thử:** chạy cục bộ bằng `streamlit run app.py`, mặc định tại `http://localhost:8501`.

## A2. Danh mục tool

| Tool | Chức năng | Phân loại |
|---|---|---|
| `clarify` | Hỏi lại khi thiếu URL, tài khoản, phạm vi hoặc cần xác nhận | Core built-in |
| `timeline` | Lấy bài đăng gần nhất của một tài khoản X/Twitter | Core built-in |
| `social_search` | Tìm kiếm bài đăng X/Twitter theo từ khóa | Core built-in |
| `lookup` | Tìm kiếm web/tin tức theo chủ đề và thời gian | Core built-in |
| `fetch` | Đọc và trích xuất nội dung từ URL cụ thể | Core built-in |
| `format` | Định dạng các item nghiên cứu thành digest | Core built-in |
| `send` | Gửi nội dung lên Telegram sau khi có xác nhận | Optional action |
| `papers` | Tìm paper arXiv theo truy vấn và thứ tự thời gian | Optional built-in |
| `evidence_audit` | Kiểm tra số nguồn, URL, domain độc lập và trường dữ liệu thiếu | Team-authored |
| `source_deduplicate` | Chuẩn hóa URL/title và loại nguồn trùng có audit trail | Team-authored bonus |
| `claim_matrix` | Gợi ý nguồn liên quan cho từng claim bằng lexical overlap | Team-authored bonus |
| `citation_export` | Xuất citation Markdown, APA-like hoặc BibTeX | Team-authored bonus |

## A3. Câu hỏi mẫu

1. `Lấy giúp mình 5 tweet mới nhất.` — agent phải hỏi tài khoản trước khi gọi `timeline`.
2. `Tin AI hôm nay có gì nổi bật?` — gọi `lookup` với `topic=news`, `timeframe=day`.
3. `Tóm tắt bài này: https://openai.com/news/` — gọi `fetch` đúng URL.
4. `Kiểm tra chất lượng các nguồn này, yêu cầu ít nhất 2 nguồn và bắt buộc URL: [...]` — gọi `evidence_audit`.
5. `Loại nguồn trùng theo URL rồi xuất citation dạng BibTeX: [...]` — minh họa pipeline bonus.

## A4. Kịch bản demo đã rehearse

| Scenario | Tool trace cần thấy | Cải thiện theo version | Bằng chứng dự phòng |
|---|---|---|---|
| Thiếu tài khoản rồi bổ sung | Turn 1 hỏi lại; turn 2 `timeline(screenname="elonmusk", limit=5)` | v1 bỏ hành vi đoán tài khoản của v0 | `transcripts/v3_openai_20260729T110217357623.transcript.json`, turn 1–2 |
| Tìm tin AI trong ngày | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | v3 giữ đúng route/args và không lặp tool | Cùng transcript, turn 3 |
| Gửi Telegram | `clarify(..., response_type="yes_no")`, chưa gọi `send` | v1 thêm confirmation boundary | Cùng transcript, turn 4 |
| Đọc URL trên UI | `fetch(url="https://openai.com/news/")` | v3 dùng URL người dùng cung cấp, không tìm rộng | `transcripts/v3_openai_ui_20260729T111352221959.transcript.json`, turn 2 |
| Hậu xử lý nguồn | `source_deduplicate`, `claim_matrix`, `citation_export` | v3-bonus thêm 3 tool nhưng vẫn giữ base 20/20 | `runs/v3-bonus_B_bonus_openai_20260729T113443811945.json` |

---

# PHẦN B — Chi tiết và bằng chứng

Chỉ dùng run có `provider_error_cases=0` và `measured_cases=total_cases` để báo cáo metric. Các candidate v3 trung gian được giữ để thể hiện quá trình thử nghiệm; candidate được chấp nhận là run 20/20. Run Gemini bị quota và hai run OpenAI lỗi provider không được dùng làm bằng chứng chất lượng.

## B1. Version evidence

| Version | Thay đổi prompt/tool | Giả thuyết | Metric | Trước | Sau | Run được chấp nhận |
|---|---|---|---|---:|---:|---|
| v0 | Baseline permissive | Đo các lỗi đoán thông tin, vượt phạm vi và bỏ xác nhận | Base case accuracy | — | 0.80 (16/20) | `runs/v0_B_base_openai_20260729T102038020359.json` |
| v1 | Siết system prompt về missing-info, scope và confirmation | Quy tắc rõ sẽ thay đoán/unsafe action bằng `clarify` | Base case accuracy | 0.80 | 0.95 (19/20) | `runs/v1_B_base_openai_20260729T102250058932.json` |
| v2 | Thêm negative routing language vào tool declaration | Declaration sẽ ngăn replay intent Twitter đã bị thay thế | Base case accuracy | 0.95 | 0.95 (19/20) | `runs/v2_B_base_openai_20260729T104026122272.json` |
| v3 | Thêm `evidence_audit`, task-scoped tool exposure và chống duplicate/stale route | Chỉ đưa tool liên quan vào context sẽ sửa lỗi M06 mà không phá multi-source | Base case accuracy | 0.95 | 1.00 (20/20) | `runs/v3_B_base_openai_20260729T105820674910.json` |
| v3-bonus | Thêm 3 tool hậu xử lý và scope theo intent | Mở rộng catalog nhưng không làm giảm routing core | Bonus / base regression | — / 1.00 | 1.00 (6/6) / 1.00 (20/20) | `runs/v3-bonus_B_bonus_openai_20260729T113443811945.json`; `runs/v3-bonus_B_base_openai_20260729T113625222876.json` |

## B2. Failure analysis

| Case | Version | Actual tool call | Vấn đề | Fix / kết quả |
|---|---|---|---|---|
| `R08_out_of_scope` | v0 | `send` | Câu hỏi toán ngoài phạm vi lại bị chuyển thành action tool | v1 yêu cầu trả lời trực tiếp/giải thích giới hạn; PASS |
| `R10_missing_handle` | v0 | `timeline(screenname="sama")` | Đoán tài khoản khi người dùng chưa cung cấp | v1 bắt buộc `clarify`; PASS |
| `R11_missing_url` | v0 | `fetch` với URL mẫu | Tự tạo URL thay vì hỏi lại | v1 bắt buộc `clarify`; PASS |
| `R12_confirm_before_send` | v0 | `send` | Gửi ra ngoài khi chưa xác nhận | v1 thêm confirmation boundary; PASS |
| `M06_switch_tool` | v1, v2 | `lookup` và thừa `social_search` | Intent mới đã thay intent cũ nhưng tool cũ vẫn bị replay | v3 task scoping + suppression; PASS |
| `G_S02_audit_sources` | group v3 | `evidence_audit` thiếu `require_urls=true` | Route đúng nhưng bỏ một constraint | Cần tăng trọng số các constraint tường minh trong prompt/declaration |
| `G_M03_handle_and_count_correction` | group v3 | `timeline(screenname="elonmusk", limit=4)` | Sửa count đúng nhưng giữ stale handle | Cần quy tắc latest correction thắng cho từng slot |

Các lỗi execution phải review thủ công qua `tool_results`. Routing PASS chỉ chứng minh model chọn đúng declaration và args; không tự động chứng minh API bên ngoài trả dữ liệu đúng.

## B3. Team eval cases

Bộ `data/eval_group.json` có đúng 10 case do nhóm viết: 5 single-turn và 5 multi-turn. Run `v3_B_group_openai_20260729T105926703536.json` đo đủ 10 case, không có provider error, đạt 8/10.

| Case | Kiểm tra | Kỳ vọng | Kết quả |
|---|---|---|---|
| `G_S01_missing_account` | Thiếu tài khoản | `clarify(response_type="text")` | PASS |
| `G_S02_audit_sources` | Audit nguồn có sẵn | `evidence_audit(min_sources=2, require_urls=true)` | FAIL: thiếu `require_urls` |
| `G_S03_recent_papers` | Paper mới, đúng số lượng | `papers(max_results=3, sort_by="lastUpdatedDate")` | PASS |
| `G_S04_capability_no_tool` | Câu hỏi năng lực | Không gọi tool | PASS |
| `G_S05_publish_boundary` | Xác nhận trước Telegram | `clarify(response_type="yes_no")` | PASS |
| `G_M01_topic_correction` | Chủ đề mới + giữ timeframe | `lookup(query="climate tech", timeframe="month")` | PASS |
| `G_M02_url_supplied_later` | URL được bổ sung | `fetch` đúng URL | PASS |
| `G_M03_handle_and_count_correction` | Sửa handle và count | `timeline(screenname="sama", limit=4)` | FAIL: giữ handle cũ |
| `G_M04_audit_after_collection` | Reuse nguồn từ turn trước | `evidence_audit(min_sources=2, require_urls=true)` | PASS |
| `G_M05_cancel_research` | Hủy intent cũ | Không gọi tool | PASS |

## B4. Live chat evidence

| Scenario/turn | Version | Tool call + args | Transcript | Outcome |
|---|---|---|---|---|
| CLI turn 1 | v3 | Không gọi retrieval; hỏi tài khoản | `v3_openai_20260729T110217357623.transcript.json` | Không đoán dữ liệu |
| CLI turn 2 | v3 | `timeline(screenname="elonmusk", limit=5)` | Cùng file | Trả 5 bài đăng |
| CLI turn 3 | v3 | `lookup(query="AI", topic="news", timeframe="day", max_results=5)` | Cùng file | Trả digest có liên kết |
| CLI turn 4 | v3 | `clarify(response_type="yes_no")` | Cùng file | Dừng ở trạng thái `waiting_for_user`, chưa gửi Telegram |
| UI turn 2 | v3 | `fetch(url="https://openai.com/news/")` | `v3_openai_ui_20260729T111352221959.transcript.json` | Đọc và tóm tắt URL trong Streamlit |

## B5. Tool capability evidence

| Category | Evidence | Hoạt động đã chứng minh | Risk / guardrail |
|---|---|---|---|
| Team-authored bắt buộc: `evidence_audit` | `tests/test_evidence_audit.py`, group run | Audit số nguồn, URL, domain và trường thiếu | Không thay thế fact-check; kết quả phụ thuộc item đầu vào |
| Optional built-in: `papers` | `G_S03_recent_papers` trong group run | Route đúng arXiv, count và sort mới cập nhật | Metadata/availability phụ thuộc arXiv |
| Optional action: `send` | CLI transcript turn 4 | Agent yêu cầu xác nhận trước action | Không gửi nếu chưa có confirmation và credential |
| Bonus: `source_deduplicate`, `claim_matrix`, `citation_export` | `tests/test_bonus_tools.py`, bonus run 6/6 | Pipeline hậu xử lý deterministic | Dedup là heuristic; claim matrix không xác minh chân lý; citation không bịa metadata |

## B6. Reflection

- `system_prompt.md` phù hợp với quy tắc hành vi xuyên tool: thiếu thông tin phải hỏi lại, latest intent/correction thắng, hủy intent cũ, xác nhận trước side effect và không lặp call.
- `tools.yaml` phù hợp với schema, mô tả route, negative routing, tham số bắt buộc và ranh giới giữa các tool cạnh tranh.
- Execution failure, chất lượng nội dung nguồn và action bên ngoài cần review thủ công; automatic grader chỉ chấm routing/args/text boundary.
- Cải thiện tiếp theo: thêm eval cho từng slot bị sửa giữa nhiều turn, bắt buộc giữ các constraint boolean như `require_urls`, kiểm tra provenance sâu hơn và mock API để test execution ổn định.

## Kết luận

Artifact cuối đạt 100% trên base (20/20) và bonus (6/6), không có provider error, đồng thời có UI và transcript chạy thật. Bộ group khó hơn đạt 80% (8/10) và để lại hai lỗi cụ thể, có thể tái hiện, làm đầu vào rõ ràng cho vòng cải tiến tiếp theo.
