import mwxml
import bz2
import regex as re
import unicodedata
import json
from collections import Counter
from multiprocessing import Pool, cpu_count

# =====================
# CONFIG
# =====================
INPUT = "viwiki-latest-pages-articles.xml.bz2"

MAX_WORDS  = 100000
MAX_PAGES  = 150000
NUM_PROC   = 2          # i3-7100U → 2 process
MIN_FREQ  = 5

VOCAB_OUT = "vi_vocab.txt"
MAP_OUT   = "vi_map.json"

BATCH_SIZE = 20         # pages / task

word_re = re.compile(r"[a-zA-ZÀ-ỹ]{2,7}")

# =====================
# VIETNAMESE PHONOLOGY
# =====================
VN_VOWELS  = "aeiouyăâêôơư"
VN_INVALID = set("fjwz")

VN_ONSET = (
    "b|c|ch|d|đ|g|gh|gi|h|k|kh|l|m|n|ng|ngh|nh|"
    "p|ph|qu|r|s|t|th|tr|v|x"
)

VN_RHYME = (
    "a|ă|â|e|ê|i|o|ô|ơ|u|ư|y|"
    "ai|ao|au|ay|âu|ây|eo|êu|ia|iê|yê|oa|oe|oi|ơi|"
    "ua|uâ|ưa|ươ|ưu"
)

VN_CODA = "(c|ch|m|n|ng|nh|p|t)?"

VN_SYLLABLE_RE = re.compile(
    rf"^({VN_ONSET})?({VN_RHYME}){VN_CODA}$"
)

# =====================
# UTIL
# =====================
def remove_accent(text: str) -> str:
    return ''.join(
        c for c in unicodedata.normalize("NFD", text)
        if unicodedata.category(c) != "Mn"
    )

def is_real_vietnamese(word: str) -> bool:
    if len(word) < 2 or len(word) > 7:
        return False
    if any(c in VN_INVALID for c in word):
        return False
    if not any(v in word for v in VN_VOWELS):
        return False
    return VN_SYLLABLE_RE.match(remove_accent(word)) is not None

# =====================
# WORKER PROCESS
# =====================
def process_batch(texts):
    wc = Counter()
    mp = {}

    for text in texts:
        for w in word_re.findall(text.lower()):
            if not is_real_vietnamese(w):
                continue

            wc[w] += 1
            nd = remove_accent(w)
            mp.setdefault(nd, Counter())[w] += 1

    return wc, mp

# =====================
# READ WIKI & DISPATCH
# =====================
def read_wiki_batches():
    batch = []
    page_count = 0

    with bz2.open(INPUT, "rb") as f:
        dump = mwxml.Dump.from_file(f)

        for page in dump:
            if page.namespace != 0:
                continue

            page_count += 1
            if page_count >= MAX_PAGES:
                break

            for rev in page:
                if rev.text:
                    batch.append(rev.text)
                    break

            if len(batch) >= BATCH_SIZE:
                yield batch
                batch = []

    if batch:
        yield batch

# =====================
# MAIN
# =====================
if __name__ == "__main__":
    word_count = Counter()
    nodau_map  = {}

    with Pool(NUM_PROC) as pool:
        for wc, mp in pool.imap_unordered(process_batch, read_wiki_batches()):
            if len(word_count) < MAX_WORDS:
                word_count.update(wc)

            for nd, c in mp.items():
                nodau_map.setdefault(nd, Counter()).update(c)

            if len(word_count) >= MAX_WORDS:
                break

    # ===== FINAL CLEAN =====
    word_count = Counter({
        w: c for w, c in word_count.items()
        if c >= MIN_FREQ and is_real_vietnamese(w)
    })

    # ===== SAVE VOCAB =====
    with open(VOCAB_OUT, "w", encoding="utf-8") as f:
        for w, _ in word_count.most_common(MAX_WORDS):
            f.write(w + "\n")

    # ===== SAVE MAP =====
    valid_nd = {remove_accent(w) for w in word_count}
    final_map = {
        nd: c.most_common(1)[0][0]
        for nd, c in nodau_map.items()
        if nd in valid_nd
    }

    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(final_map, f, ensure_ascii=False, indent=2)

    print("✅ DONE")
    print("Từ tiếng Việt:", len(word_count))
    print("Đã lưu:", VOCAB_OUT, MAP_OUT)
