sơ đồ hoạt động build.vidict.py
START
  │
  ▼
Đọc CONFIG
(MAX_WORDS, MIN_FREQ, NUM_PROC, ...)
  │
  ▼
Mở file viwiki-latest-pages-articles.xml.bz2
  │
  ▼
read_batches()
  │
  ├─ Đọc từng dòng file
  ├─ Gom text trong <page>
  ├─ Lấy nội dung <text>
  └─ Gom 500 trang → yield 1 batch
  │
  ▼
Multiprocessing Pool (2 process)
  │
  ▼
process_batch(batch)
  │
  ├─ text.lower()
  ├─ regex bắt từ 2–7 ký tự
  ├─ Counter[w] += 1
  └─ Trả về Counter
  │
  ▼
total_counter.update(counter)
  │
  ├─ Gộp tất cả batch lại
  └─ Nếu > 600k từ → dọn rác RAM
  │
  ▼
Hoàn tất đếm toàn bộ từ
  │
  ▼
Lấy top 300.000 từ phổ biến
(most_common)
  │
  ▼
BẮT ĐẦU LỌC
  │
  ├─ Nếu c < MIN_FREQ (10) → loại
  ├─ Nếu sai cấu trúc âm tiết VN → loại
  ├─ Nếu không dấu & c < 30 → loại
  │
  ▼
Giữ lại tối đa 80.000 từ
(filtered)
  │
  ▼
GHI FILE vi_vocab.txt
  │
  ▼
TẠO nodau_map
  │
  ├─ remove_accent(w)
  ├─ Nếu nhiều từ trùng không dấu
  └─ Chọn từ có count lớn nhất
  │
  ▼
GHI FILE vi_map.json
  │
  ▼
IN:
"Từ tiếng Việt: ..."
  │
  ▼
END

