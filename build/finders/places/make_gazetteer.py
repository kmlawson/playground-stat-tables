"""Freeze the place names the Population page resolves against into build/finders/places/places.json.

Sources: build/places/japan_prefectures.json (prefectures, colonies) and the Japanese Empire map's gazetteer
(~/shell/interactive-japan-map: Korean provinces, Taiwanese shū/chō and gun, Manchukuo and Chinese provinces, South Seas
island groups, territories/countries, cities), through build_candidates.build_indexes so that the folding of names is
the same as the map links'. Run again when the map's gazetteer grows; the page build reads only the frozen file.

places.json = {"places": {id: {"en", "ja", "k" (kind), "up" (parent id)}}, "ix": {index name: {folded name: id}}}
"""
import csv, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))     # build/finders/places
BUILD = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, BUILD)
import build_candidates as BC  # noqa: E402
import maplinks as M  # noqa: E402

ROOT = BC.ROOT
T = os.path.join(ROOT, "texts", "territories")
rd = BC.read_csv
F = BC.Folder(M)

# Top-level units: id -> (en, ja, kind, parent, aliases). Aliases are matched after folding.
TOP = {
    "empire": ("Japanese Empire", "大日本帝國", "empire", None,
               ["Japanese Empire", "Empire of Japan", "Japan Empire", "Empire", "大日本帝國", "大日本帝国", "帝國", "帝国", "日本帝國", "Whole Empire", "Japan and colonies", "Japan (incl. colonies)"]),
    "japan": ("Japan proper", "内地", "region", "empire",
              ["Japan proper", "Japan", "Naichi", "内地", "內地", "日本", "日本内地", "日本內地", "Japan Proper", "Old Japan", "Japan (proper)", "全國", "全国", "本邦", "Nippon"]),
    "korea": ("Korea (Chōsen)", "朝鮮", "colony", "empire", ["Korea", "Chosen", "Chōsen", "Corea", "朝鮮", "Chosen (Korea)", "Korea (Chosen)", "全鮮", "全道", "韓國", "韓国", "Tyosen"]),
    "taiwan": ("Taiwan (Formosa)", "臺灣", "colony", "empire", ["Taiwan", "Formosa", "臺灣", "台湾", "台灣", "全島", "Taiwan (Formosa)", "Formosa (Taiwan)"]),
    "karafuto": ("Karafuto (south Sakhalin)", "樺太", "colony", "empire", ["Karafuto", "樺太", "Saghalien", "Sakhalin", "Japanese Saghalien", "South Saghalien", "Karafuto (Saghalien)"]),
    "kwantung": ("Kwantung Leased Territory", "關東州", "colony", "empire", ["Kwantung Leased Territory", "Kwantung", "Kwantung Province", "關東州", "関東州", "Kantōshū", "Kantoshu", "Kwantung Territory", "Kwantung Leased Territory (Kantōshū)", "Leased Territory", "Kwantung Peninsula"]),
    "smr": ("South Manchuria Railway Zone", "滿鐵附屬地", "region", "manchuria", ["South Manchuria Railway Zone", "Railway Zone", "S.M.R. Zone", "滿鐵附屬地", "満鉄附属地", "附屬地", "附属地", "Railway Area", "SMR Zone", "S.M.R. Zone", "Railway zone", "South Manchuria Railway Area"]),
    "nanyo": ("South Seas Mandate", "南洋群島", "colony", "empire", ["South Seas Mandate", "South Sea Islands", "South Seas Islands", "South Seas", "Nan'yō", "Nanyo", "南洋群島", "南洋", "南洋廳", "Japanese Mandated Islands", "Mandated Islands", "South Sea Islands under Japanese Mandate", "Nan'yō Guntō"]),
    "manchuria": ("Manchuria / Manchukuo", "滿洲", "region", None, ["Manchuria", "Manchukuo", "Manchoukuo", "滿洲", "満洲", "滿洲國", "満洲国", "Manchou-kuo", "Three Eastern Provinces", "東三省", "東北", "North-east China", "Manchoukuo (Manchuria)", "全滿", "Manchuria (Three Eastern Provinces)"]),
    "china": ("China", "中國", "country", None, ["China", "中國", "中国", "支那", "中華民國", "中華民国", "Republic of China", "Chinese Republic", "Chinese Empire", "China (Republic)", "清國", "Chinese Republic (total)"]),
    "chinaproper": ("China proper", "中國本部", "region", "china", ["China proper", "China Proper", "Eighteen Provinces", "本部", "支那本部", "中國本部", "Interior provinces"]),
    "world": ("Other countries", "", "world", None, ["World", "Total world", "世界", "World total"]),
}
# Places the map's gazetteer does not carry: settlements, leased territories and countries outside East Asia.
EXTRA = {
    "shanghai-is": ("Shanghai International Settlement", "上海公共租界", "settlement", "c-shanghai", ["Shanghai International Settlement", "International Settlement", "International Settlement (Shanghai)", "共同租界", "公共租界", "上海共同租界", "Shanghai Settlement", "Foreign Settlement"]),
    "shanghai-fc": ("Shanghai French Concession", "上海法租界", "settlement", "c-shanghai", ["Shanghai French Concession", "French Concession", "French Concession (Shanghai)", "法租界", "佛租界", "上海佛租界", "French Settlement"]),
    "shanghai-cn": ("Shanghai (Chinese city)", "上海華界", "settlement", "c-shanghai", ["Chinese City", "Greater Shanghai", "Chinese Municipality", "華界", "Chinese territory (Shanghai)", "Shanghai Special Municipality", "Chinese Area"]),
    "kiaochow": ("Kiaochow Leased Territory", "膠州灣", "colony", "china", ["Kiaochow Leased Territory", "Kiaochow", "Kiautschou", "膠州灣", "膠州", "Kiaochow Territory", "Tsingtao Leased Territory"]),
    "w-us": ("United States", "米國", "country", "world", ["United States", "U.S.A.", "USA", "U.S.", "America", "United States of America", "米國", "米国", "亞米利加", "北米合衆國", "合衆國", "United States (with Alaska)", "Americans"]),
    "w-canada": ("Canada", "加奈陀", "country", "world", ["Canada", "加奈陀", "カナダ", "Dominion of Canada"]),
    "w-uk": ("United Kingdom", "英國", "country", "world", ["United Kingdom", "Great Britain", "England", "Britain", "英國", "英国", "英吉利", "Great Britain and Ireland", "England and Wales", "U.K."]),
    "w-britishempire": ("British Empire", "大英帝國", "country", "world", ["British Empire", "大英帝國"]),
    "w-france": ("France", "佛國", "country", "world", ["France", "佛國", "仏国", "佛蘭西", "French Republic"]),
    "w-germany": ("Germany", "獨逸", "country", "world", ["Germany", "獨逸", "独逸", "German Empire", "德國", "ドイツ"]),
    "w-italy": ("Italy", "伊太利", "country", "world", ["Italy", "伊太利", "伊國"]),
    "w-spain": ("Spain", "西班牙", "country", "world", ["Spain", "西班牙"]),
    "w-portugal": ("Portugal", "葡萄牙", "country", "world", ["Portugal", "葡萄牙"]),
    "w-netherlands": ("Netherlands", "和蘭", "country", "world", ["Netherlands", "Holland", "和蘭", "蘭國", "オランダ"]),
    "w-belgium": ("Belgium", "白耳義", "country", "world", ["Belgium", "白耳義"]),
    "w-austria": ("Austria", "墺太利", "country", "world", ["Austria", "墺太利", "墺國", "Austria-Hungary", "Austria Hungary"]),
    "w-hungary": ("Hungary", "洪牙利", "country", "world", ["Hungary", "洪牙利"]),
    "w-switzerland": ("Switzerland", "瑞西", "country", "world", ["Switzerland", "瑞西"]),
    "w-sweden": ("Sweden", "瑞典", "country", "world", ["Sweden", "瑞典"]),
    "w-norway": ("Norway", "諾威", "country", "world", ["Norway", "諾威"]),
    "w-denmark": ("Denmark", "丁抹", "country", "world", ["Denmark", "丁抹"]),
    "w-poland": ("Poland", "波蘭", "country", "world", ["Poland", "波蘭"]),
    "w-czech": ("Czechoslovakia", "チェコスロヴァキア", "country", "world", ["Czechoslovakia", "Czecho-Slovakia", "チェッコスロヴァキア"]),
    "w-greece": ("Greece", "希臘", "country", "world", ["Greece", "希臘"]),
    "w-turkey": ("Turkey", "土耳古", "country", "world", ["Turkey", "土耳古", "Ottoman Empire"]),
    "w-egypt": ("Egypt", "埃及", "country", "world", ["Egypt", "埃及"]),
    "w-persia": ("Persia", "波斯", "country", "world", ["Persia", "Iran", "波斯"]),
    "w-brazil": ("Brazil", "伯剌西爾", "country", "world", ["Brazil", "伯剌西爾", "ブラジル", "伯國"]),
    "w-argentina": ("Argentina", "亞爾然丁", "country", "world", ["Argentina", "Argentine", "Argentine Republic", "亞爾然丁", "アルゼンチン"]),
    "w-peru": ("Peru", "秘露", "country", "world", ["Peru", "秘露", "ペルー"]),
    "w-mexico": ("Mexico", "墨西哥", "country", "world", ["Mexico", "墨西哥", "メキシコ"]),
    "w-chile": ("Chile", "智利", "country", "world", ["Chile", "智利"]),
    "w-southafrica": ("South Africa", "南阿", "country", "world", ["South Africa", "Union of South Africa", "南阿聯邦"]),
    "w-newzealand": ("New Zealand", "新西蘭", "country", "world", ["New Zealand", "新西蘭", "ニュージーランド"]),
    "w-russia": ("Russia", "露國", "country", "world", ["Russia", "Russian Empire", "露國", "露国", "露西亞", "露西亜", "ロシア", "Russia in Asia", "Siberia", "西比利亞"]),
    "w-korea-indep": ("Korea (Joseon/Korean Empire, before 1910)", "韓國", "country", "korea", []),
}
# Japanese regions (地方): under Japan proper
REGIONS = {"hokkaido": "Hokkaidō", "tohoku": "Tōhoku", "kanto": "Kantō", "hokuriku": "Hokuriku", "tosan": "Tōsan", "tokai": "Tōkai",
           "kinki": "Kinki", "kansai": "Kansai", "chugoku": "Chūgoku", "shikoku": "Shikoku", "kyushu": "Kyūshū", "chubu": "Chūbu",
           "kinai": "Kinai", "sanyo": "San'yō", "sanin": "San'in", "nankai": "Nankai", "saikai": "Saikai"}
POLITY = {"Japan": "japan", "Republic of China": "china", "Occupied China": "china", "Free China": "china", "Chōsen": "korea",
          "Formosa": "taiwan", "Karafuto": "karafuto", "Manchukuo": "manchuria", "Kwantung Leased Territory": "kwantung",
          "Nan’yō": "nanyo", "Mengjiang": "china", "Sinkiang": "w-xinjiang", "Tibet": "w-tibet", "Hong Kong": "w-hongkong",
          "Macao": "w-macau", "British India": "w-britishindia", "Princely states": "w-britishindia", "Netherlands East Indies": "w-dei",
          "Dutch East Indies": "w-dei", "French Indochina": "w-indochina", "Philippine Islands (US)": "w-philippines",
          "Philippines": "w-philippines", "Siam": "w-siam", "Thailand": "w-siam", "USSR": "w-ussr", "Mongolia": "w-mongolia",
          "Australia": "w-australia", "Malaya": "w-malaya", "Straits Settlements": "w-malaya", "Ceylon": "w-ceylon",
          "Hawaii": "w-hawaii", "Burma": "w-britishindia", "Nepal": "w-nepal", "Kwangchowan": "w-guangzhouwan", "Guam": "w-guam"}
MANCH_CITY = {"mukden", "shenyang", "harbin", "changchun", "hsinking", "dairen", "dalian", "port arthur", "lushun", "antung", "andong",
              "kirin", "jilin", "tsitsihar", "qiqihar", "yingkou", "newchwang", "fushun", "anshan", "liaoyang", "tieling", "kaiyuan",
              "ssupingkai", "siping", "mutankiang", "mudanjiang", "chiamussu", "jiamusi", "jinzhou", "chinchow", "hailar", "manchouli",
              "manzhouli", "heihe", "heiho", "yenki", "yanji", "tunghua", "tonghua", "chengde", "jehol", "pengcheng", "benxi", "penhsihu",
              "fuxin", "liaoyuan", "chengchiatun", "taonan", "ulanhot", "wangyemiao", "suifenho", "beian", "peian", "lungchingtsun"}


def strip_paren(s):
    return re.split(r"\s*[(（]", s or "")[0].strip()


def main():
    ix, polity = BC.build_indexes(F, M)
    places = {}

    def add(pid, en, ja, k, up):
        places.setdefault(pid, {"en": en, "ja": ja, "k": k, "up": up})

    top_ix = {}
    for pid, (en, ja, k, up, al) in TOP.items():
        add(pid, en, ja, k, up)
        for a in al + [en, ja]:
            if a:
                top_ix.setdefault(F.prov(a), pid)
                top_ix.setdefault(F.base(a), pid)
    for pid, (en, ja, k, up, al) in EXTRA.items():
        if not al:
            continue
        add(pid, en, ja, k, up)
        for a in al + [en, ja]:
            if a:
                top_ix.setdefault(F.prov(a), pid)
                top_ix.setdefault(F.base(a), pid)
    for k, en in REGIONS.items():
        add("r-" + k, en + " region", "", "region", "japan")
    # prefectures (JIS codes)
    P = json.load(open(os.path.join(BUILD, "places", "japan_prefectures.json")))["places"]
    pref_ix = {}
    colmap = {"karafuto": "karafuto", "taiwan": "taiwan", "chosen": "korea", "kwantung": "kwantung", "nanyo": "nanyo"}
    for pid, p in P.items():
        if pid.isdigit():
            add("jp" + pid, p["en"], p["ja"] + ("" if p["ja"].endswith(("都", "道", "府")) else "縣"), "prefecture", "japan")
    for name, pid in M.place_index().items():
        pref_ix[name] = ("jp" + pid) if pid.isdigit() else colmap.get(pid, pid)
    # Korean provinces
    for r in rd(os.path.join(T, "sub-units", "korea.csv")):
        add("kr-" + r["key"], strip_paren(r["en"]), strip_paren(r["ja"]), "province", "korea")
    # Taiwan
    for r in rd(os.path.join(T, "sub-units", "taiwan.csv")):
        ja = strip_paren(r["ja"])
        if re.search(r"[州廳]$", ja):
            add("tw-" + r["key"], strip_paren(r["en"]), ja, "prefecture", "taiwan")
    for r in rd(os.path.join(T, "sub-units", "taiwan.csv")):
        ja = strip_paren(r["ja"])
        if not re.search(r"[州廳]$", ja):
            up = "tw-" + r["shu"] if ("tw-" + r.get("shu", "")) in places else "taiwan"
            add("tw-" + r["key"], strip_paren(r["en"]), ja, "city" if ja.endswith("市") else "district", up)
    for r in rd(os.path.join(T, "sub-units", "manchukuo.csv")):
        add("mk-" + r["key"].replace(" ", ""), strip_paren(r["en"]), strip_paren(r["ja"]), "province", "manchuria")
    for r in rd(os.path.join(T, "sub-units", "china.csv")):
        add("cn-" + r["key"], strip_paren(r["en"]), r["zh"], "province", "china")
    for r in rd(os.path.join(T, "sub-units", "mandate-groups.csv")):
        add("ss-" + r["key"], strip_paren(r["en"]), strip_paren(r["ja"]), "island", "nanyo")
    # single islands of the mandate, under their group (Saipan the island, not the branch office: see ISLAND_GROUP)
    ISLAND_GROUP = {"Saipan": "Marianas", "Tinian": "Marianas", "Rota": "Marianas", "Pagan": "Marianas", "Agrihan": "Marianas",
                    "Anatahan": "Marianas", "Babeldaob": "Palau", "Peleliu": "Palau", "Angaur": "Palau", "Weno": "Chuuk",
                    "Kwajalein": "Marshalls", "Majuro": "Marshalls", "Jaluit": "Marshalls", "Wotje": "Marshalls",
                    "Enewetak": "Marshalls", "Bikini": "Marshalls", "Ebon": "Marshalls"}
    isl_ix = {}
    ISL_EXTRA = {"Babeldaob": ["Babelthuap", "Babelthaup", "バベルダオブ", "バベルトアプ"], "Weno": ["Moen", "Moen Island", "春島", "Haru Island", "Harushima"],
                 "Angaur": ["アンガウル", "Angaur Island"], "Peleliu": ["ペリリュー", "Pelelew"], "Rota": ["ロタ", "Luta"], "Tinian": ["テニアン"],
                 "Saipan": ["サイパン島", "Saipan Island"], "Kwajalein": ["クェゼリン"], "Wotje": ["ウォッゼ"], "Enewetak": ["Eniwetok", "ブラウン"]}
    for r in rd(os.path.join(T, "sub-units", "mandate-islands.csv")):
        k = r["key"]
        if k not in ISLAND_GROUP:
            continue
        add("si-" + k, strip_paren(r["en"]) + (" Island" if k in ("Saipan", "Rota", "Tinian") else ""), strip_paren(r.get("ja")), "island", "ss-" + ISLAND_GROUP[k])
        for a in [k, r["en"], r.get("ja"), r.get("zh")] + ISL_EXTRA.get(k, []):
            if a:
                for a2 in BC.alternatives(a):
                    isl_ix.setdefault(F.prov(a2), "si-" + k)
    # countries / territories
    TOPMAP = {"chosen": "korea", "formosa": "taiwan", "karafuto": "karafuto", "kwantung": "kwantung", "nanyo": "nanyo",
              "mandate_jp": "nanyo", "china": "china", "manchuria": "manchuria", "japan": "japan"}
    for y in ("1930", "1942"):
        for r in rd(os.path.join(T, y + ".csv")):
            if r["id"] in TOPMAP or r["id"] in ("other", "contested", "ryukyu", "ogasawara", "chishima"):
                continue
            up = "china" if r.get("cat") == "chinese" else "world"
            add("w-" + r["id"], strip_paren(r["en"]) if not r["en"].startswith("Guam —") else r["en"], strip_paren(r.get("ja")), "country", up)
    # cities
    names = {}
    for r in rd(os.path.join(ROOT, "texts", "city-names.csv")):
        names[r["id"]] = (strip_paren(r["en"]), strip_paren(r.get("ja_kyu") or r.get("ja")) or r.get("zh", ""))
    for n in ("cities.csv", "cities-1942.csv", "cities-1930.csv"):
        for r in rd(os.path.join(ROOT, "data", n)):
            if r["id"] in names and names[r["id"]][1]:
                continue
            names[r["id"]] = (strip_paren(r["name_en"]) or names.get(r["id"], ("", ""))[0], r.get("name_local") or "")
    for r in rd(os.path.join(ROOT, "texts", "sites", "sites.csv")):
        if r["id"] in polity and not names.get(r["id"], ("", ""))[1]:
            names[r["id"]] = (names.get(r["id"], (strip_paren(r["en"]), ""))[0] or strip_paren(r["en"]), strip_paren(r.get("ja")))
    for cid, pol in polity.items():
        en, ja = names.get(cid, (cid, ""))
        up = POLITY.get(pol, "world")
        if up == "china" and cid in MANCH_CITY:
            up = "manchuria"
        if up.startswith("w-") and up not in places:
            up = "world"
        add("c-" + cid, en or cid, ja, "city", up)
    # Manchurian cities listed under China in the 1930 data
    for cid in MANCH_CITY:
        if "c-" + cid in places and places["c-" + cid]["up"] == "china":
            places["c-" + cid]["up"] = "manchuria"
    out_ix = {
        "top": top_ix, "pref": pref_ix,
        "korea": {k: "kr-" + v for k, v in ix["korea"].items()},
        "taiwan-shu": {k: "tw-" + v for k, v in ix["taiwan-shu"].items()},
        "taiwan-gun": {k: "tw-" + v for k, v in ix["taiwan-gun"].items()},
        "manchukuo": {k: "mk-" + v.replace(" ", "") for k, v in ix["manchukuo"].items()},
        "china": {k: "cn-" + v for k, v in ix["china"].items()},
        "mandate": {k: "ss-" + v for k, v in ix["mandate"].items()},
        "countries": {k: ("w-" + v if "w-" + v in places else TOPMAP.get(v, "w-" + v)) for k, v in ix["countries"].items()},
        "regions": {k: "r-" + v for k, v in ix["regions"].items()},
        "islands": isl_ix,
        "cities": {k: "c-" + v for k, v in ix["cities"].items()},
    }
    # names that are cities, not provinces ("Canton Province", "Mukden Province" fold to the city's name), and
    # Kwantung, which in these books is the Leased Territory, not Kwangtung (Guangdong)
    for k in ("canton", "mukden", "kwantung", "guangzhou", "shenyang"):
        out_ix["china"].pop(k, None)
        out_ix["manchukuo"].pop(k, None)
    # Taiwan's gun without their suffix ("Byoritsu" for Byoritsu-gun), Korea's provinces as "North/South X"
    for k, v in list(out_ix["taiwan-gun"].items()):
        b = re.sub(r"(-gun|-jun|郡)$", "", k)
        if b != k and len(b) >= 2:
            out_ix["taiwan-gun"].setdefault(b, v)
    for k, v in list(out_ix["korea"].items()):
        m = re.match(r"^([a-z]+?)(hoku|nan)$", k)
        if m and m.group(1) not in ("", "k"):
            b, d = m.group(1), {"hoku": "north", "nan": "south"}[m.group(2)]
            D = d.capitalize()
            for f in (f"{D} {b}", f"{b} {D}", f"{D[0]}. {b}", f"{b}-{m.group(2)}-do", f"{b} {m.group(2)}", f"{D} {b}-do"):
                out_ix["korea"].setdefault(F.prov(f), v)
    # CJK city names exactly as printed, without 市 (堺, 津, 甲府: too short for the folded index)
    cja = {}
    for pid, p in places.items():
        if pid.startswith("c-") and p.get("ja"):
            for a in re.split(r"[・/、]", p["ja"]):
                a = re.sub(r"市$", "", a.strip()).translate(BC.OLD)
                if a and re.match(r"^[\u3400-\u9fff]+$", a):
                    cja.setdefault(a, pid)
    for r in rd(os.path.join(ROOT, "texts", "city-names.csv")):
        for fld in ("ja", "ja_kyu", "zh"):
            a = strip_paren(r.get(fld) or "")
            a = re.sub(r"市$", "", a).translate(BC.OLD)
            if a and re.match(r"^[\u3400-\u9fff]+$", a) and ("c-" + r["id"]) in places:
                cja.setdefault(a, "c-" + r["id"])
    out_ix["cities-ja"] = cja
    for name, v in list(out_ix["countries"].items()):
        if v not in places:
            del out_ix["countries"][name]
    json.dump({"_doc": __doc__.strip(), "places": places, "ix": out_ix}, open(os.path.join(HERE, "places.json"), "w"),
              ensure_ascii=False, indent=0, sort_keys=True)
    print(len(places), "places;", {k: len(v) for k, v in out_ix.items()})


if __name__ == "__main__":
    main()
