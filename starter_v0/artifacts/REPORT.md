# Day 04 Lab v2 Report — Research Loop

## Team

| Họ và tên | Mã sinh viên | Vai trò |
|---|---|---|
| Đào Văn Đà | 2A202601089 | Hợp nhất code, Báo cáo |
| Nguyễn Quốc Anh | 2A202601079 | Viết System Prompt, Báo cáo |
| Nguyễn Hoàng Vĩnh Phong | 2A202601265 | UI |
| Trương Quốc Trường | 2A202601195 | Eval, viết bảng |
| Nguyễn Ngọc Ánh | 2A202601643 | Báo cáo |

- Provider / model: OpenAI Responses API / `gpt-4o-mini`
- Final artifact: `v3-bonus+p47281754cffc+t3d17fc26cdfc`
- UI: Streamlit, styled from repository `DESIGN.md`

---

# PHẦN A — Giới thiệu agent

## A1. Agent làm được gì

Research Loop là agent nghiên cứu có bằng chứng: tìm tin web, đọc URL, tìm và
theo dõi nội dung Twitter/X, tìm paper arXiv, định dạng kết quả và audit chất
lượng nguồn. Mỗi câu trả lời trên UI đi kèm tool timeline, arguments, result,
status, transcript và artifact version để người xem có thể kiểm tra thay vì chỉ
tin câu trả lời cuối.

**Link demo trên máy trình chiếu:** <http://localhost:8501>

Khởi động bằng `streamlit run app.py`. Đây là local URL có chủ đích; không đưa
API key hoặc transcript nhạy cảm lên một tunnel public.

## A2. Tool agent đang expose

| Tool | Chức năng | Tool mới của nhóm? |
|---|---|---:|
| `clarify` | Hỏi bổ sung thông tin hoặc xác nhận yes/no | Không |
| `timeline` | Lấy bài đăng gần nhất của một tài khoản Twitter/X | Không |
| `social_search` | Tìm bài đăng theo chủ đề trên Twitter/X | Không |
| `lookup` | Tìm web/tin tức bằng Tavily | Không |
| `fetch` | Đọc một URL bằng Firecrawl | Không |
| `format` | Biến source items thành digest Markdown | Không |
| `evidence_audit` | Kiểm tra diversity, citation URL, duplicate và missing content | **Có** |
| `source_deduplicate` | Chuẩn hóa URL/title, loại nguồn trùng và trả nhóm duplicate | **Có — bonus** |
| `claim_matrix` | Xếp hạng nguồn ứng viên cho từng claim theo lexical overlap | **Có — bonus** |
| `citation_export` | Xuất citation dạng Markdown, APA-like hoặc BibTeX | **Có — bonus** |
| `send` | Action Telegram có confirmation boundary; live-send không bật | Không |
| `papers` | Tìm paper arXiv theo relevance/submitted/updated | Không |

`policy` và `paper_text` vẫn có implementation trong starter nhưng không expose
trong final `tools.yaml`, nhằm giữ tool surface gọn và tránh routing nhiễu.

## A3. Câu hỏi mẫu

1. `Tin AI hôm nay có gì nổi bật?`
2. `Tìm trên web tin robotics tuần này và tweet top về robotics.`
3. `Tóm tắt 5 tweet mới nhất giúp mình.` — agent phải hỏi tài khoản.
4. `Tìm 3 paper arXiv mới cập nhật về agentic RAG.`
5. `Audit 2 nguồn này, yêu cầu tối thiểu 2 domain và URL bắt buộc: [...]`
6. `Loại các nguồn trùng theo URL hoặc title, giữ nguồn xuất hiện đầu tiên: [...]`
7. `Tạo claim matrix cho 2 nhận định này dựa trên danh sách nguồn: [...]`
8. `Xuất danh sách nguồn sau sang BibTeX: [...]`

## A4. Kịch bản demo đã rehearse

| Scenario | Trace cần thấy | Câu chuyện version | Fallback |
|---|---|---|---|
| Tin AI hôm nay | `lookup(query=AI, topic=news, timeframe=day)` | v0 đúng; v3 giữ đúng khi tool surface lớn hơn | v3 base run |
| Thiếu account → bổ sung Elon | hỏi lại, rồi `timeline(screenname=elonmusk, limit=5)` | v0 tự đoán `sama`; v1 đặt missing-info boundary | transcript v3 |
| Chuyển Twitter → web | chỉ `lookup(query=OpenAI, topic=news)` | v1/v2 gọi thừa social; v3 task-scoping loại intent cũ | so sánh M06 trên UI |
| Gửi Telegram | `clarify(response_type=yes_no)`, không `send` | v0 gửi ngay; v1+ giữ confirmation boundary | transcript v3 |
| Audit nguồn | `evidence_audit` | capability mới ở v3, không side effect | group run + unit test |
| Pipeline hậu xử lý nguồn | `source_deduplicate` → `claim_matrix` → `citation_export` | v3-bonus thêm 3 capability task-scoped mà không làm regression base | bonus run + base regression |

---

# PHẦN B — Chi tiết và bằng chứng

## B1. Version evidence

Tất cả run được chọn dưới đây dùng cùng provider/model và có
`provider_error_cases=0`. V0–v3 cũng có `tool_error_count=0` trong các tool
results được review.

| Version | Thay đổi / hypothesis | Case accuracy | Routing | Args | Multi-turn | Run |
|---|---|---:|---:|---:|---:|---|
| v0 | Baseline permissive sẽ tự đoán và bỏ confirmation | 80% | 80% | 80% | 100% | `v0_B_base_openai_20260729T102038020359.json` |
| v1 | Prompt boundary/scope rõ sẽ sửa 4 lỗi v0 | 95% | 95% | 95% | 83.33% | `v1_B_base_openai_20260729T102250058932.json` |
| v2 | Negative language trong tool descriptions sẽ dừng stale social intent | 95% | 95% | 95% | 83.33% | `v2_B_base_openai_20260729T104026122272.json` |
| v3 | Tool scoping + dedupe sẽ loại route cũ/thừa và thêm audit capability | **100%** | **100%** | **100%** | **100%** | `v3_B_base_openai_20260729T105820674910.json` |

V2 là kết quả “không cải thiện”, không bị che giấu: description-only chưa đủ
cho M06. Các v3 candidate bị regression cũng được giữ trong `runs/`; final v3
chỉ được chấp nhận sau khi trace chứng minh task-scoped exposure sửa 20/20.

## B2. Failure analysis

| Case | Evidence thực tế | Nguyên nhân | Fix / quyết định |
|---|---|---|---|
| v0 R08 | gọi `send` cho bài toán tích phân | prompt yêu cầu luôn chọn một tool | v1 giới hạn scope, no-tool cho math/code |
| v0 R10 | `timeline(screenname=sama)` | tự đoán account thiếu | v1 bắt buộc `clarify(text)` |
| v0 R11 | `fetch(example.com/your-article-url)` | tự bịa URL | v1 bắt buộc URL explicit |
| v0 R12 | gọi `send` ngay | không có confirmation boundary | v1 bắt buộc `clarify(yes_no)` |
| v1/v2 M06 | `lookup` + `social_search` | history bị coi như action queue | v3 chỉ expose social khi active intent cần |
| group G_S02 | đúng `evidence_audit`, thiếu arg `require_urls=true` | model dựa vào default thay vì emit arg | giữ fail để phản ánh argument compliance |
| group G_M03 | `timeline(elonmusk, 4)` thay vì `sama, 4` | carryover count đúng nhưng handle correction cũ hơn bị mất | cần slot-based conversation state ở vòng sau |

## B3. Team eval — đúng 10 case

File `data/eval_group.json` có đúng 5 single-turn + 5 multi-turn, tất cả
`phase="B"` và có `metadata.what_it_tests`.

| Case | Điều được test | Expected | Kết quả |
|---|---|---|---|
| G_S01_missing_account | missing account boundary | `clarify(text)` | PASS |
| G_S02_audit_sources | tool mới + audit args | `evidence_audit` | FAIL arg |
| G_S03_recent_papers | paper count + updated sort | `papers(..., 3, lastUpdatedDate)` | PASS |
| G_S04_capability_no_tool | capability answer | no tool | PASS |
| G_S05_publish_boundary | external confirmation | `clarify(yes_no)` | PASS |
| G_M01_topic_correction | topic correction + timeframe carryover | `lookup(climate tech, month)` | PASS |
| G_M02_url_supplied_later | missing URL supplied | `fetch(URL)` | PASS |
| G_M03_handle_and_count_correction | two independent slot corrections | `timeline(sama, 4)` | FAIL arg |
| G_M04_audit_after_collection | reuse earlier source items | `evidence_audit` | PASS |
| G_M05_cancel_research | latest cancellation | no tool | PASS |

Group summary: **8/10 case accuracy, 100% routing accuracy, 80% argument
accuracy, 0 provider errors**. Run:
`runs/v3_B_group_openai_20260729T105926703536.json`.

## B4. Live chat evidence

Transcript: `transcripts/v3_openai_20260729T110217357623.transcript.json`

| Turn | Intent | Trace / outcome |
|---:|---|---|
| 1 | Thiếu account | agent hỏi account, không tự đoán |
| 2 | Bổ sung Elon Musk | `timeline(screenname=elonmusk, limit=5)`; trả 5 URL |
| 3 | Tin AI hôm nay | `lookup(query=AI, topic=news, timeframe=day)`; trả source links |
| 4 | Gửi lên Telegram | `clarify(response_type=yes_no)`; status `waiting_for_user`, không gửi |

Transcript có 4 turns, 0 provider error và dùng artifact core đã được chấp nhận:
`v3+p47281754cffc+t420119baa8bd`. Đây là bằng chứng live chat của core v3;
artifact cuối `v3-bonus` được kiểm chứng riêng bằng bonus eval và base regression
ở B7.

## B5. Tool capability evidence

| Category | Evidence | Kết quả | Risk / guardrail |
|---|---|---|---|
| Must-have tool mới | `tools/evidence_audit/tool.py`, `TOOL.md` | unit tests pass; group routing pass | deterministic, read-only, không tìm hay publish |
| Optional built-in | `papers`; G_S03 | arXiv route/count/sort pass | rate-limit tối thiểu 3 giây, User-Agent từ env |
| Guarded action | `send`; R12/G_S05/transcript | chỉ hỏi xác nhận | Telegram credentials không bật; không live-send |
| UI core | `app.py` | HTTP 200, AppTest 0 exception | không hiển thị secret; transcript tải theo session |

## B6. Reflection

- `system_prompt.md` phù hợp cho scope, missing information, confirmation và
  correction precedence. Nhắc lại quá nhiều negative rules làm tool đó nổi bật
  và từng gây regression.
- `tools.yaml` phù hợp cho schema, argument convention, return-purpose và
  action boundary. Description-only ở v2 không đủ để sửa stale intent.
- Runtime task scoping là guard ứng dụng cần thiết: catalog vẫn đầy đủ nhưng
  model chỉ thấy optional/competing tools liên quan đến active request.
- Automatic grader chỉ chấm tên/argument subset; tool execution errors phải
  review riêng. Các accepted v0–v3 có 0 tool-result error.
- Cải tiến tiếp theo: lưu conversation slots có cấu trúc (`handle`, `limit`,
  `topic`, `timeframe`, `channel`) và validator tự điền schema defaults như
  `require_urls=true`, sau đó chạy lại đúng 10 group cases.

## B7. Bonus — ba tool mới bổ sung

Ba tool mới tạo thành một pipeline hậu xử lý nguồn có thể kiểm tra độc lập:

| Tool mới | Vai trò | Guardrail |
|---|---|---|
| `source_deduplicate` | Chuẩn hóa URL/title, loại nguồn trùng và trả duplicate groups | deterministic, read-only, không gọi mạng |
| `claim_matrix` | Xếp hạng nguồn ứng viên cho từng claim theo lexical overlap | luôn nêu rõ đây không phải xác minh tính đúng |
| `citation_export` | Xuất Markdown, APA-like hoặc BibTeX | không tự bịa URL hay metadata còn thiếu |

Cộng với `evidence_audit`, bài nộp hiện có **4 tool do nhóm tự xây dựng**,
vượt điều kiện bonus “hơn 3 tool mới”. Final catalog expose 12 tool; ba tool
bonus chỉ được đưa vào context khi active request có intent tương ứng để tránh
làm nhiễu các route bắt buộc.

### Bằng chứng bonus

| Hạng mục | Kết quả | File |
|---|---:|---|
| Bonus eval | **6/6**, routing 100%, args 100%, multi-turn 100%, 0 provider error, 0 tool error | `runs/v3-bonus_B_bonus_openai_20260729T113443811945.json` |
| Base regression | **20/20**, mọi accuracy 100%, 0 provider error, 0 tool error | `runs/v3-bonus_B_base_openai_20260729T113625222876.json` |
| Unit tests | **14/14 pass** | `tests/test_bonus_tools.py`, `tests/test_tool_selection.py` |
| Bonus dataset | đúng 3 single-turn + 3 multi-turn | `data/eval_bonus.json` |

Artifact của cả bonus eval và base regression đều là
`v3-bonus+p47281754cffc+t3d17fc26cdfc`, dùng OpenAI Responses API với
`gpt-4o-mini`. Các bonus eval thực thi implementation qua registry thực, vì
vậy kết quả 0 tool error cũng là quicktest tích hợp cho cả ba tool bonus.
