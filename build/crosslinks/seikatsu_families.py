"""Similar-table families for the 國民生活時間調査 1943 volumes (series japan-seikatsu-jikan), made by script:
the volumes print the same kinds of table for different populations, with uniform printed titles, so tables are
matched on (kind, whole country / region, sex, age group, marital status, region) parsed from the titles.
Run after a volume's first build: python3 build/crosslinks/seikatsu_families.py  (reads data/<slug>.json)."""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from chapters import SERIES

H = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
S = SERIES["japan-seikatsu-jikan"]
REG = {"北海道": "Hokkaidō", "東北": "Tōhoku", "北陸": "Hokuriku", "關東": "Kantō", "東山": "Tōsan", "東海": "Tōkai",
       "近畿": "Kinki", "中國": "Chūgoku", "四國": "Shikoku", "九州": "Kyūshū"}
GROUP = {"俸給生活者": "salaried", "工場勞務者": "factory", "工場労務者": "factory", "世帶主": "shop", "營業使用人": "shop"}


def norm(s):
    return s.replace("歲", "歳").replace(" ", "").replace("　", "")


def key(t):
    ch, ti = t.get("chapter") or "", norm(t.get("title") or "")
    sex = "women" if ("女子" in ti) else "men" if "男子" in ti else None
    m = re.search(r"(\d+)歳—(\d+)歳", ti)
    age = f"{m[1]}–{m[2]}" if m else "61 and over" if "61歳以上" in ti else None
    mar = "unmarried" if "(無配)" in ti else "married" if "(有配)" in ti else None
    reg = None
    tail = re.sub(r"^\(.*?\)", "", re.split(r"歳|以上", ti)[-1])
    if tail and all(x in REG for x in tail.split("・")):
        reg = tail
    if ch == "時刻別行爲別人員數百分比表":
        kind = "act"
    elif ch.startswith("行爲別一人一日"):
        kind = "budget-nat" if "全國" in ti else "budget-reg"
        return (kind, sex if kind == "budget-nat" else None, None, None, None)
    elif ch.startswith("時刻別聽取適否參考表"):
        kind = "radio"
    elif ch == "調査の要綱":
        return ("outline", ti, None, None, None)
    else:
        return None
    if kind == "act" and t.get("table_no", "").startswith("I ") and reg is None:
        reg = "whole"
    if not sex or not age:
        return None
    return (kind, sex, age, mar, reg)


def label(k):
    kind, sex, age, mar, reg = k
    if kind == "budget-nat":
        return f"Time spent per person per day by activity, whole country: {sex}"
    if kind == "budget-reg":
        return "Time spent per person per day by activity, by region"
    who = f"{sex} aged {age}" + (f" ({mar})" if mar else "")
    where = "whole country" if reg == "whole" else " · ".join(REG[x] for x in reg.split("・"))
    if kind == "act":
        return f"Activity by time of day, {where}: {who}"
    return f"Suitability of each time of day for radio listening, {where}: {who}"


TOPIC = {"act": "Activity by time of day", "budget-nat": "Time budgets", "budget-reg": "Time budgets",
         "radio": "Radio-listening suitability", "outline": "Survey outline"}
OUTLINE = {"調査地區名": "Surveyed districts", "世帶調査": "Household survey: districts and households surveyed",
           "職場調査": "Workplace survey: workplaces and persons surveyed", "記入用語": "Diary terms (activity classification)"}

fam = {}
for slug in S["books"]:
    f = os.path.join(H, "data", slug + ".json")
    if not os.path.exists(f):
        continue
    for t in json.load(open(f, encoding="utf-8")):
        k = key(t)
        if not k:
            continue
        if k[0] == "outline":
            lab = next((v for x, v in OUTLINE.items() if x in k[1]), None)
            if not lab:
                continue
            k = ("outline", lab, None, None, None)
        fam.setdefault(k, []).append(f"{slug}/{t['id']}")
out = {}
for k, mem in fam.items():
    if len({m.split("/")[0] for m in mem}) < 2:
        continue
    lab = k[1] if k[0] == "outline" else label(k)
    note = ""
    if k[0] == "act":
        note = "Same layout in each volume: the whole-country tables split every activity into indoors/outdoors; the regional tables give single activity columns plus indoors and outdoors. The activities differ by population (e.g. 農事 farm work, 從業 work, 内職 piecework)."
    out.setdefault(TOPIC[k[0]], []).append({"label": lab[0].upper() + lab[1:], "members": mem, "note": note})
d = os.path.join(os.path.dirname(__file__), "families")
for topic, fams in out.items():
    fn = "japan-seikatsu-jikan--" + re.sub(r"[^a-z0-9]+", "-", topic.lower()).strip("-")
    json.dump({"listing": fn, "families": sorted(fams, key=lambda x: x["label"])},
              open(os.path.join(d, fn + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(fn, len(fams), "families")
