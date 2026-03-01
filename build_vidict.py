import bz2
import regex as re
import json
from collections import Counter
from multiprocessing import Pool, cpu_count

# =====================
# CONFIG
# =====================
INPUT = "viwiki-latest-pages-articles.xml.bz2"

MAX_WORDS = 80000
MAX_PAGES = float("inf")
MIN_FREQ = 10

NUM_PROC   = 2
BATCH_SIZE = 500

VOCAB_OUT = "vi_vocab.txt"
MAP_OUT   = "vi_map.json"

# chỉ lấy từ 2–7 ký tự
word_re = re.compile(r"[a-zA-ZÀ-ỹ]{2,7}")

# =====================
# ACCENT TABLE (RẤT NHANH)
# =====================
ACCENT_TABLE = str.maketrans(
    "àáảãạăằắẳẵặâầấẩẫậ"
    "èéẻẽẹêềếểễệ"
    "ìíỉĩị"
    "òóỏõọôồốổỗộơờớởỡợ"
    "ùúủũụưừứửữự"
    "ỳýỷỹỵđ",
    "aaaaaaaaaaaaaaaaa"
    "eeeeeeeeeee"
    "iiiii"
    "ooooooooooooooooo"
    "uuuuuuuuuuu"
    "yyyyyd"
)

VN_INVALID = set("fjwz")
VN_VOWELS  = set("aeiouyăâêôơư")

ACCENT_CACHE = {}
VN_CACHE     = {}

def remove_accent(word):
    if word in ACCENT_CACHE:
        return ACCENT_CACHE[word]
    nd = word.translate(ACCENT_TABLE)
    ACCENT_CACHE[word] = nd
    return nd

VN_SYLLABLE_RE = re.compile(
    r"""
    ^(ngh|ng|gh|ch|nh|th|tr|ph|kh|qu|gi|
      b|c|d|đ|g|h|k|l|m|n|p|r|s|t|v|x)?   # phụ âm đầu

    (a|ă|â|e|ê|i|o|ô|ơ|u|ư|y|
     ai|ao|au|ay|âu|ây|eo|êu|
     ia|iê|yê|iu|
     oa|oe|oi|ơi|oai|oan|
     ua|uâ|uê|uơ|uôi|
     ưa|ươ|ươi|ưu|
     uy|uya|uye|uyên)                    # vần

    (c|ch|m|n|ng|nh|p|t)?$               # phụ âm cuối
    """,
    re.VERBOSE
)




def is_vietnamese(word):
    base = remove_accent(word)

    if not base.isalpha():
        return False

    if not VN_SYLLABLE_RE.fullmatch(base):
        return False

    return True


# =====================
# FAST XML READER
# =====================
TEXT_RE = re.compile(r"<text[^>]*>(.*?)</text>", re.DOTALL)

def read_batches():
    batch = []
    page_count = 0

    with bz2.open(INPUT, "rt", encoding="utf-8", errors="ignore") as f:
        buffer = ""

        for line in f:
            buffer += line

            if "</page>" in line:
                page_count += 1
                if page_count >= MAX_PAGES:
                    break

                texts = TEXT_RE.findall(buffer)
                if texts:
                    batch.append(texts[0])

                buffer = ""

                if len(batch) >= BATCH_SIZE:
                    yield batch
                    batch = []

    if batch:
        yield batch

# =====================
# WORKER: CHỈ ĐẾM
# =====================
def process_batch(texts):
    counter = Counter()
    local_findall = word_re.findall

    for text in texts:
        for w in local_findall(text.lower()):
            counter[w] += 1

    return counter

# =====================
# MAIN
# =====================
if __name__ == "__main__":

    total_counter = Counter()

    print("🚀 Counting words...")

    with Pool(NUM_PROC) as pool:
        for counter in pool.imap_unordered(process_batch, read_batches()):
            total_counter.update(counter)

        # 🧹 dọn rác nếu quá lớn
            if len(total_counter) > 600000:
                total_counter = Counter({
                    w: c for w, c in total_counter.items()
                    if c >= 2
            })
                print("🧹 Cleaned memory:", len(total_counter))


    print("🔎 Filtering Vietnamese words...")

    # Lấy nhiều hơn để phòng bị loại
    most_common = total_counter.most_common(300000)

    filtered = []
    for w, c in most_common:
        if c < MIN_FREQ:
            continue

        if not is_vietnamese(w):
            continue

        # loại tiếng anh không dấu và ít phổ biến
        if remove_accent(w) == w and c < 30:
            continue

        filtered.append((w, c))

        if len(filtered) >= MAX_WORDS:
            break

    # =====================
    # SAVE VOCAB
    # =====================
    with open(VOCAB_OUT, "w", encoding="utf-8") as f:
        for w, _ in filtered:
            f.write(w + "\n")

    # =====================
    # BUILD NODAU MAP
    # =====================
    nodau_map = {}
    for w, c in filtered:
        nd = remove_accent(w)
        if nd not in nodau_map or total_counter[nodau_map[nd]] < c:
            nodau_map[nd] = w

    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(nodau_map, f, ensure_ascii=False)

    print("✅ DONE")
    print("Từ tiếng Việt:", len(filtered))
