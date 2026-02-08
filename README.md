sơ đồ hoạt động build.vidict.py
                FILE WIKIPEDIA (.bz2)
        viwiki-latest-pages-articles.xml.bz2
                           │
                           ▼
                Đọc từng trang Wikipedia
                           │
        (chỉ lấy namespace = 0 → bài viết thật)
                           │
                           ▼
                Gom trang thành batch
                (20 trang = 1 batch)
                           │
                           ▼
        Gửi batch cho các process xử lý song song
              ┌───────────────┬───────────────┐
              │               │               │
              ▼               ▼               ▼
        Process 1        Process 2        Process N
        xử lý batch      xử lý batch      xử lý batch
              │               │               │
              └───────┬───────┴───────┬───────┘
                      ▼               ▼
                Xử lý từng từ trong batch
                      │
        ┌─────────────┴─────────────┐
        ▼                           ▼
  Tách từ bằng regex        Bỏ qua từ không hợp lệ
 (2–7 ký tự)                (không đúng tiếng Việt)
        │
        ▼
   Từ hợp lệ
        │
        ├───────────────► Đếm tần suất từ
        │                     word_count[w]++
        │
        └───────────────► Tạo map không dấu
                              an → ăn, ấn, ân
 Sau khi các process xử lý xong                             
        Gộp kết quả từ tất cả process
                   │
                   ▼
           Lọc từ xuất hiện ≥ 5 lần
                   │
                   ▼
        ┌─────────────────────────┐
        │                         │
        ▼                         ▼
   Tạo vi_vocab.txt        Tạo vi_map.json
 (danh sách từ đúng)     (không dấu → có dấu)

