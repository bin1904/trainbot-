1. Hàm levenshtein(a, b)
Chức năng:
Tính khoảng cách Levenshtein giữa hai chuỗi a và b, tức là số phép biến đổi ít nhất (xóa, thêm, thay thế ký tự) để chuyển a thành b.
Mục đích sử dụng:
Được dùng để đo mức độ giống nhau giữa các từ nhằm phục vụ cho việc sửa lỗi chính tả.
2. Tập từ vựng VOCAB
Chức năng:
Lưu trữ tập hợp các từ hợp lệ của hệ thống.
Cách xây dựng:
Lấy tất cả các từ trong tập luật rule_data
Lấy tất cả các từ trong danh sách từ khóa bot
Mục đích sử dụng:
Làm từ điển chuẩn để đối chiếu khi sửa lỗi chính tả, tránh sửa sang các từ không tồn tại.
3. Hàm has_vietnamese_char(word)
Chức năng:
Kiểm tra xem một từ có chứa ký tự tiếng Việt có dấu hay không.
Mục đích sử dụng:
Nếu từ đã có dấu tiếng Việt thì được coi là đúng và không thực hiện sửa lỗi, nhằm tránh làm sai các từ hợp lệ.
4. Hàm correct_sentence(sentence, vocab, max_dist=1)
Chức năng:
Thực hiện sửa lỗi chính tả cho toàn bộ câu đầu vào.
Nguyên lý hoạt động:
Tách câu thành các từ
Bỏ qua các từ đã có dấu hoặc tồn tại trong VOCAB
Với các từ còn lại, tìm từ gần nhất trong VOCAB bằng Levenshtein
Chỉ sửa nếu khoảng cách nhỏ hơn hoặc bằng max_dist
Mục đích sử dụng:
Chuẩn hóa câu đầu vào trước khi đưa vào các mô hình phân loại.
5. Hàm rule_predict(sentence)
Chức năng:
Dự đoán nhãn (label) của câu dựa trên tập luật định nghĩa sẵn.
Nguyên lý hoạt động:
Loại bỏ ký tự đặc biệt
So khớp từ hoặc cụm từ trong câu với các luật
Đếm tần suất nhãn xuất hiện và chọn nhãn phổ biến nhất
Kết quả:
Trả về nhãn dự đoán hoặc "Không xác định" nếu không có luật phù hợp.
6. Hàm test_train(sentence, lengthdata)
Chức năng:
Trích xuất vector đặc trưng cho câu.
Đặc trưng sử dụng:
Tỷ lệ số từ khóa xuất hiện trong câu
Tổng số từ khóa xuất hiện
Mục đích sử dụng:
Chuẩn bị dữ liệu cho mô hình KNN, áp dụng cho cả dữ liệu huấn luyện và dữ liệu kiểm tra.
7. Hàm knn_predict(text, k=5)
Chức năng:
Dự đoán nhãn của câu bằng thuật toán K-Nearest Neighbors (KNN).
Nguyên lý hoạt động:
Trích vector đặc trưng cho câu test
Tính khoảng cách Euclid tới các câu huấn luyện
Lấy k hàng xóm gần nhất
Chọn nhãn xuất hiện nhiều nhất trong k hàng xóm
8. Hàm check_sensitive(text)
Chức năng:
Kết hợp toàn bộ hệ thống để dự đoán nhãn cuối cùng cho câu đầu vào.
Quy trình xử lý:
Sửa lỗi chính tả
Dự đoán bằng rule-based
Dự đoán bằng KNN
Ưu tiên kết quả từ rule, nếu không có thì dùng KNN
Kết quả trả về:
Danh sách gồm:
Câu sau khi sửa
Nhãn cuối cùng
Nguồn dự đoán (RULE hoặc KNN)
9. Khối main
Chức năng:
Cho phép người dùng nhập câu từ bàn phím, sau đó thực hiện toàn bộ quá trình xử lý và in ra kết quả dự đoán.
