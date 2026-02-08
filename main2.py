import json
import re
import math
import datasentence
import arraytrainbot

# ======================
# LOAD DATA
# ======================

with open("data.json", "r", encoding="utf-8") as f:
    rule_data = json.load(f)

sentence_data = datasentence.bot()
bot = arraytrainbot.bot()

# ======================
# LOAD VOCAB FILES
# ======================

vocab = set()

# vocab từ txt (vd: vi_vocab.txt)
with open("vi_vocab.txt", encoding="utf-8") as f:
    VI_VOCAB = set(w.strip() for w in f if w.strip())

with open("vi_map.json", encoding="utf-8") as f:
    VI_MAP = json.load(f)

# vocab từ rule json
for k in rule_data:
    for w in k.lower().split():
        vocab.add(w)

# vocab từ bot + sentence
for k in bot:
    for w in k.lower().split():
        vocab.add(w)

for s in sentence_data:
    for w in s.lower().split():
        vocab.add(w)


# ======================
# SPELL CORRECT (VOCAB-BASED)
# ======================
import unicodedata

def remove_diacritics(text):
    return ''.join(
        c for c in unicodedata.normalize('NFD', text)
        if unicodedata.category(c) != 'Mn'
    )

def has_vietnamese_char(word):
    viet = "ăâđêôơưáàảãạấầẩẫậéèẻẽẹíìỉĩịóòỏõọúùủũụýỳỷỹỵ"
    return any(c in viet for c in word.lower())

def remove_repeat_chars(word):
    return re.sub(r'(.)\1+', r'\1', word)

def normalize_word(word):
    # nếu đã có trong vocab → giữ nguyên
    if word in vocab:
        return word

    # giảm ký tự lặp
    w = remove_repeat_chars(word)
    if w in vocab:
        return w

    return w

def correct_sentence(sentence):
    sentence = sentence.lower()
    words = sentence.split()
    out = []
    i = 0

    while i < len(words):
        # 🔹 ưu tiên ghép 2 từ
        if i + 1 < len(words):
            pair = words[i] + " " + words[i+1]
            key = remove_diacritics(pair)

            if key in VI_MAP:
                out.append(VI_MAP[key])  # ❗ KHÔNG [0]
                i += 2
                continue

        # 🔹 xử lý 1 từ
        w = words[i]
        key = remove_diacritics(w)

        if key in VI_MAP:
            out.append(VI_MAP[key])  # ❗ KHÔNG [0]
        else:
            out.append(remove_repeat_chars(w))

        i += 1

    return " ".join(out)
# ======================
# RULE MODEL
# ======================

def rule_predict(text):
    text = text.lower()
    rules = sorted(rule_data.items(), key=lambda x: len(x[0]), reverse=True)

    for key, label in rules:
        if key.lower() in text or text in key.lower():
            return label

    return "Không xác định"

# ======================
# KNN MODEL
# ======================

dataset = {}
testsen = {}

def extract_feature(sentence):
    sentence = sentence.lower()
    hit = []

    for item in bot:
        if item.lower() in sentence:
            hit.append(item.lower())

    words = sentence.split()
    return [
        len(hit) / len(words) if words else 0,
        len(hit)
    ]

for s in sentence_data:
    dataset[s] = extract_feature(s)

def knn_predict(text, k=5):
    test_vec = extract_feature(text)
    dist = {}

    for s in dataset:
        d = math.sqrt(
            (dataset[s][0] - test_vec[0])**2 +
            (dataset[s][1] - test_vec[1])**2
        )
        dist[s] = d

    nearest = sorted(dist, key=dist.get)[:k]
    labels = [sentence_data[s] for s in nearest]
    return max(set(labels), key=labels.count)

# ======================
# PIPELINE
# ======================
def check_sensitive(text):
    fixed = correct_sentence(text)

    rule_label = rule_predict(fixed)
    knn_label = knn_predict(fixed)

    # ưu tiên rule
    if rule_label != "Không xác định":
        final = rule_label
        src = "RULE"
    else:
        final = knn_label
        src = "KNN"
    print("Câu gốc     :", text)
    print("Câu sau sửa :", fixed)
    print("Rule predict:", rule_label)
    print("KNN predict :", knn_label)
# ======================
# RUN
# ======================

if __name__ == "__main__":
    text = input("Nhập câu: ")
    print(check_sensitive(text))
