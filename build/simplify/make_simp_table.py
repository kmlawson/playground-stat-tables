"""Build build/simplify/tables.json: the character tables behind the site-wide "Simplified characters" option.

  nice -n 15 uv run --with opencc python3 build/simplify/make_simp_table.py /path/to/Unihan_Variants.txt

Two character-for-character tables (so text keeps its length and layout):
  zh  traditional -> Chinese simplified (jianti), for Chinese books (slug china-*)
  ja  old forms (kyūjitai) -> Japanese new forms (shinjitai), for every other book
Sources: OpenCC t2s / t2jp, run character by character over all CJK code points; characters OpenCC
leaves alone are tried again through their Unicode z-variant (Unihan kZVariant, e.g. 敎→教, 靑→青,
淸→清), which catches the old print forms common in NDL-era type; then the hand list in EXTRA.
"""
import sys, json, re, unicodedata
import opencc

ROOT = __file__.rsplit('/build/', 1)[0]
# Hand additions (both directions checked by eye). Key: mode -> {old: new}
EXTRA = {
    "zh": {"鑛": "矿", "衞": "卫", "蔴": "麻", "刋": "刊", "敍": "叙", "荳": "豆", "迺": "乃", "廼": "乃",
           "痲": "麻", "寗": "宁", "呉": "吴", "欵": "款", "郞": "郎", "兪": "俞", "鬪": "斗", "鬬": "斗",
           "闘": "斗", "愼": "慎", "窰": "窑", "峩": "峨", "塲": "场", "傚": "效", "楡": "榆", "犂": "犁",
           "濶": "阔", "値": "值", "寃": "冤", "賛": "赞", "憇": "憩", "畧": "略", "隂": "阴", "鴈": "雁",
           "擧": "举", "蔵": "藏", "烱": "炯", "砲": "炮", "嶋": "岛", "髙": "高", "淸": "清", "靑": "青",
           "尙": "尚", "敎": "教", "硏": "研", "卽": "即", "戶": "户", "旣": "既", "娛": "娱",
           "鷄": "鸡", "麪": "面", "塡": "填", "剝": "剥", "顚": "颠", "揷": "插", "屛": "屏"},
    "ja": {"敎": "教", "淸": "清", "尙": "尚", "靑": "青", "强": "強", "娛": "娯", "旣": "既", "塡": "填",
           "剝": "剥", "屛": "屏", "顚": "顛", "揷": "挿", "髙": "高", "鬪": "闘", "鬬": "闘", "硏": "研",
           "卽": "即", "戶": "戸", "瀆": "涜", "囊": "嚢", "拋": "抛", "簞": "箪", "敍": "叙",
           "衞": "衛", "鑛": "鉱", "刋": "刊", "郞": "郎", "愼": "慎", "擧": "挙", "畧": "略",
           "塲": "場", "鷄": "鶏", "麪": "麺", "祕": "秘", "竝": "並", "曾": "曽", "搔": "掻", "吞": "呑",
           "噓": "嘘", "攢": "攅", "蟬": "蝉", "繡": "繍", "醬": "醤", "鹽": "塩"},
}
# Never convert (legitimate in modern use, or a different word when simplified)
KEEP = {"zh": set("瓩糎粁竰甅瓱糀乾"), "ja": set("瓩糎粁竰甅瓱糀嶋曺乭乫濾填枡穎暨鱉")}

def zvariants(path):
    zv = {}
    for line in open(path, encoding="utf-8"):
        if "\tkZVariant\t" not in line:
            continue
        a, _, v = line.rstrip("\n").split("\t")
        c = chr(int(a[2:], 16))
        zv[c] = [chr(int(x.split("<")[0][2:], 16)) for x in v.split()]
    return zv

def ranges():
    for a, b in [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF), (0x20000, 0x2FA1F)]:
        yield from range(a, b + 1)

def build(unihan):
    zv = zvariants(unihan)
    conv = {"zh": opencc.OpenCC("t2s"), "ja": opencc.OpenCC("t2jp")}
    out = {}
    for mode, cv in conv.items():
        m = {}
        for cp in ranges():
            c = chr(cp)
            n = unicodedata.normalize("NFC", c)  # compatibility ideographs → unified
            o = cv.convert(n)
            if o == n:
                for v in zv.get(n, []):
                    ov = cv.convert(v)
                    if ov != v:
                        o = ov
                        break
            if len(o) == 1 and o != c and c not in KEEP[mode]:
                m[c] = o
        for k, v in EXTRA[mode].items():
            if k != v:
                m[k] = v
            else:
                m.pop(k, None)
        out[mode] = m
    return out

if __name__ == "__main__":
    t = build(sys.argv[1])
    json.dump(t, open(f"{ROOT}/build/simplify/tables.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0, sort_keys=True)
    print({k: len(v) for k, v in t.items()}, "→ build/simplify/tables.json (simp.js is written by inject.py during the build)")
