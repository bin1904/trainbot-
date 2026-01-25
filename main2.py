import json
import re
import math
import datasentence
import arraytrainbot

# ======================
# LOAD DATA
# ======================

# Đọc dữ liệu luật từ file JSON
# rule_data: dict {từ / cụm từ : nhãn}
with open("data.json", "r", encoding="utf-8") as f:
    rule_data = json.load(f)

# sentence_data: dict dữ liệu huấn luyện cho KNN
# {câu huấn luyện : label}
sentence_data = datasentence.bot()
# bot: danh sách từ khóa dùng để trích đặc trưng cho KNN
bot = arraytrainbot.bot()
# ======================
# ==== SPELL CORRECT ===
# ======================
# Hàm tính khoảng cách Levenshtein
# Dùng để đo số phép biến đổi ít nhất
# để chuyển từ chuỗi a sang chuỗi b
def levenshtein(a, b):
    n, m = len(a), len(b)                # Độ dài 2 chuỗi
    dp = [[0]*(m+1) for _ in range(n+1)] # Bảng quy hoạch động

    # Khởi tạo: chuyển chuỗi a -> rỗng
    for i in range(n+1):
        dp[i][0] = i
    # Khởi tạo: chuyển rỗng -> chuỗi b
    for j in range(m+1):
        dp[0][j] = j
    # Tính dp cho từng ký tự
    for i in range(1, n+1):
        for j in range(1, m+1):
            # Nếu ký tự giống nhau thì không mất chi phí
            cost = 0 if a[i-1] == b[j-1] else 1

            dp[i][j] = min(
                dp[i-1][j] + 1,      # Xóa ký tự
                dp[i][j-1] + 1,      # Thêm ký tự
                dp[i-1][j-1] + cost  # Thay thế ký tự
            )

    # Trả về khoảng cách Levenshtein
    return dp[n][m]
# Tạo tập từ vựng để sửa lỗi
# Bao gồm tất cả từ trong luật và bot
VOCAB = set()

# Lấy từ trong rule_data
for k in rule_data:
    for w in k.split():
        VOCAB.add(w)

# Lấy từ trong bot
for k in bot:
    for w in k.split():
        VOCAB.add(w)
#Hàm phân biệt các ký tự tiếng viêt
def has_vietnamese_char(word):
    # Danh sách ký tự tiếng Việt có dấu
    viet_chars = "ăâđêôơưđáàảãạấầẩẫậéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ"
    # Kiểm tra xem từ có chứa ký tự tiếng Việt không
    return any(c in viet_chars for c in word.lower())
# Hàm sửa lỗi chính tả cho cả câu
def correct_sentence(sentence, vocab, max_dist=1):
    # Tách câu thành danh sách các từ
    words = sentence.split()
    # Danh sách lưu các từ sau khi sửa
    new_words = []
    # Duyệt từng từ trong câu
    for w in words:
        # ======================
        # BƯỚC 0: NẾU TỪ CÓ DẤU TIẾNG VIỆT → KHÔNG SỬA
        # ======================
        if has_vietnamese_char(w):
            new_words.append(w)
            continue
        # ======================
        # BƯỚC 1: KIỂM TRA TỪ ĐÃ ĐÚNG CHƯA
        # ======================
        if w.lower() in [v.lower() for v in vocab]:
            new_words.append(w)
            continue

        # ======================
        # BƯỚC 2: TÌM TỪ GẦN NHẤT
        # ======================
        best_word = w
        best_dist = max_dist + 1

        for v in vocab:
            d = levenshtein(w.lower(), v.lower())
            if d < best_dist:
                best_dist = d
                best_word = v

        # ======================
        # BƯỚC 3: QUYẾT ĐỊNH SỬA
        # ======================
        if best_dist <= max_dist:
            new_words.append(best_word)
        else:
            new_words.append(w)

    return " ".join(new_words)


# ======================
# ========= RULE MODEL
# ======================

def rule_predict(sentence):
    # sentence: câu đầu vào cần dự đoán

    # Loại bỏ các ký tự đặc biệt trong câu
    test = re.sub(r"[.*+?!${},]", " ", sentence)

    # Tách từ
    split_test = test.split()

    # results: lưu danh sách label tìm được theo luật
    results = []

    # countelement: đếm số lần xuất hiện của mỗi label
    countelement = {}

    # Hàm đếm tần suất phần tử
    def count(arr):
        for x in arr:
            countelement[x] = countelement.get(x, 0) + 1

    # Duyệt từng luật
    for key in rule_data:
        # Nếu là cụm từ
        if len(key.split()) > 1:
            if key.lower() in test.lower() or test.lower() in key.lower():
                results.append(rule_data[key])
        else:
            # Nếu là từ đơn
            for w in split_test:
                if key.lower() == w.lower():
                    results.append(rule_data[key])

    # Nếu tìm được label
    if results:
        count(results)
        return max(countelement, key=countelement.get)

    return "Không xác định"

# ======================
# ========= KNN MODEL
# ======================

# dataset: vector đặc trưng câu train
dataset = {}

# testsen: vector đặc trưng câu test
testsen = {}

def test_train(sentence, lengthdata):
    # sentence: câu cần trích đặc trưng
    # lengthdata: phân biệt train / test

    sentence_lower = sentence.lower()
    test = []

    # Duyệt danh sách từ khóa bot
    for item in bot:
        if len(item) >= 8:
            for w in item.split():
                if w.lower() in sentence_lower:
                    test.append(w.lower())
        else:
            if item.lower() in sentence_lower:
                test.append(item.lower())

    # Loại bỏ trùng
    ans = list(dict.fromkeys(test))
    # Tách từ
    words = sentence.split()
    # Train
    if lengthdata > 2:
        dataset[sentence] = [len(ans)/len(words) if words else 0, len(ans)]
    else:
        # Test
        testsen[sentence] = [len(ans)/len(words) if words else 0, len(ans)]

# Huấn luyện
for s in sentence_data:
    test_train(s, len(sentence_data))

def knn_predict(text, k=5):
    # Trích đặc trưng cho câu test
    test_train(text, 1)

    knn_result = {}

    # Tính khoảng cách Euclid
    for s in dataset:
        dist = math.sqrt(
            (dataset[s][0] - testsen[text][0])**2 +
            (dataset[s][1] - testsen[text][1])**2
        )
        knn_result[s] = dist
    # Lấy k hàng xóm gần nhất
    nearest = sorted(knn_result, key=knn_result.get)[:k]
    # Lấy label
    labels = [sentence_data[s] for s in nearest]
    return max(set(labels), key=labels.count)

# ======================
# ========= KẾT HỢP
# ======================

def check_sensitive(text):
    # Sửa lỗi chính tả trước
    fixed_text = correct_sentence(text, VOCAB)

    print("Câu gốc :", text)
    print("Câu sửa :", fixed_text)

    # Dự đoán rule
    rule_label = rule_predict(fixed_text)

    # Dự đoán KNN
    knn_label = knn_predict(fixed_text)

    # Ưu tiên rule
    if rule_label != "Không xác định":
        final_label = rule_label
        source = "RULE"
    else:
        final_label = knn_label
        source = "KNN"

    print("Rule predict:", rule_label)
    print("KNN predict :", knn_label)
    print("➡ Label cuối:", final_label, f"(from {source})")

    return [fixed_text, final_label, source]

# ======================
# ========= CHẠY
# ======================

if __name__ == "__main__":
    text = input("Nhập câu: ")
    result = check_sensitive(text)

    print("\nKết quả cuối:")
    print(result)
