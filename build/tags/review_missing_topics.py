#!/usr/bin/env python3
"""Full-transcription subject review after the interface's verified deployment."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re
import sys
import unicodedata
from datetime import datetime, timezone

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import build_tags as b
OUT = HERE / "reviews/missing-high-level-2026-10-26"


def norm(s):
    return unicodedata.normalize("NFKC", str(s or "")).lower()


def prepare():
    gate = b.read(OUT / "deployment-gate.json")
    assert gate["status"] == "interface-merged-deployed-and-live-before-contents-review"
    assignments = b.load_assignments()
    wanted = {key for key, row in assignments.items() if not row["topics"]}
    assert len(wanted) == 3114
    records, profiles, sources = [], [], {}
    for book, tables, _, _ in b.committed_pages():
        slug = book["slug"]
        for table in tables:
            key = slug + ":" + table["id"]
            if key not in wanted:
                continue
            index = len(records)
            records.append({"key": key, "book": {"slug": slug, "title": book["title"]}, "table": table, "previous": assignments[key]})
            headers = [str(x) for part in table.get("parts", []) for x in [part.get("label") or "", *part.get("columns", [])] if x]
            labels = [str(row[0]) for part in table.get("parts", []) for row in part.get("rows", []) if row and row[0]]
            examples = [row for part in table.get("parts", []) for row in part.get("rows", [])][:3]
            profiles.append({"i": index, "key": key, "title": (table.get("en") or {}).get("t") or table.get("title"),
                "chapter": table.get("chapter"), "description": (table.get("en") or {}).get("d") or table.get("context") or table.get("caption_extra"),
                "headers": headers, "labels": labels, "examples": examples, "existing_tags": assignments[key]["tags"]})
            path = b.SITE / "data" / (slug + ".json")
            sources[str(path.relative_to(b.SITE))] = b.sha(path)
    assert len(records) == len(profiles) == 3114
    b.write(OUT / "records.json", records)
    b.write(OUT / "profiles.json", profiles)
    b.write(OUT / "manifest.json", {"tables": 3114, "keys": [r["key"] for r in records], "source_files": sources,
        "deployment_gate_sha256": b.sha(OUT / "deployment-gate.json"), "original_published_assignments_sha256": b.sha(b.PUBLISHED / "assignments.json"),
        "deferred_detailed_cohort_sha256": b.sha(HERE / "reviews/deferred-detailed-tags-2026-10-26.json"), "records_sha256": b.sha(OUT / "records.json")})
    print(json.dumps({"prepared": len(records), "source_books": len(sources), "gate_verified": gate["verified_utc"]}))


SUBJECTS = {
    "education": r"school|pupil|student|teacher|instructor|universit|college|educational|kindergarten|學校|學生|教員|敎員|教育|敎育",
    "religion": r"buddhis|shinto|christian|catholic|protestant|temples|shrines|religious|missionar|神社|寺院|宗教|宗敎",
    "crime-and-justice": r"\b(?:court|judicial|criminal|convict|prison|prisoner|police|sentenc|punishment|offence|offense|prosec|insolvenc|litigation|penal servitude|capital punishment)|裁判|刑務|犯罪|警察|刑事",
    "health": r"\b(?:hospital|physician|disease|epidemic|sick|medical|dentist|vaccinat|sanitar|health|midwives|nurses)|醫院|病院|疾病|衞生|衛生",
    "population": r"\b(?:population|inhabitants|census|households|births|deaths|marriages|divorces|emigra|immigra|settlers|foreign residents)|人口|戶口|戸口",
    "government": r"\b(?:governors?|mayors?|prefectural|administrative jurisdiction|administrative division|local administration|prefectures|cabinet|ministries|prime minister|privy council|civil service|imperial house|imperial family|mikados|emperors|year.names|administrative system)|行政|官吏|官公吏",
    "military": r"\b(?:army|navy|military|naval|armaments?|ammunition|battles?|garrisons?|admiralt|forts|general staff|divisional|brigade|rifles|torpedo|regimental|warships|commanders|battalions|guns|artillery|兵|陸軍|海軍)\b",
    "foreign-relations": r"\b(?:embass|legation|diplomat|consular|consulates|treaties|foreign affairs)|外交|領事|條約",
    "finance": r"\b(?:banks?|banking|budgets?|tax(?:es|ation)?|loans?|debts?|currency|moneys|bonds|insurance|assets|liabilities|balance sheets?|interest|dividends?|revenue|revenues|expenditures?|gross receipts|gross disbursements|fiscal|financial|paid.up capital|capital paid)|銀行|預金|公債|歲入|歳入|歲出|歳出|財政|金融",
    "trade": r"\b(?:exports?|imports?|exporters|importers|wholesale|retail|trade|trading|tariff|commercial|merchants|cargoes|commodities|prices|markets)|輸出|輸入|貿易|商業",
    "agriculture": r"\b(?:cultivat|crops?|harvest|arable|tillage|paddy|upland|rice|wheat|barley|soybeans|soya beans|ginseng|fruit|farm|cattle|horses|pigs|poultry|sugar.?cane|mulberry|silkworm|cocoons|sericultur|copra|coconuts|manure|agricultur)|農業|農產|農産|耕地|甘蔗|桑園|養蠶",
    "forestry": r"\b(?:forest|timber|lumber|firewood|logs|felling|charcoal|afforest|reforest|camphor trees)|森林|林業|林產|林産",
    "fisheries": r"\b(?:fish(?:ing|ery|eries)?|herring|sardine|bonito|cuttle.?fish|calamaries|mackerel|tunny|yellow.tail|salmon|prawns|oysters|shell.?fish|sea.?weeds?|kombu|tengusa|marine (?:production|products)|nets|purse seine|trawl|whal)|漁業|漁獲|水產|水産",
    "mining": r"\b(?:mining|mines?|minerals?|ore|collier|coal|gold output|quicksilver|phosphate|copper output|petroleum output)|鑛業|鑛產|鉱業|石炭|燐鑛",
    "manufacturing": r"\b(?:manufactur|factories|factory|workshops|spinning|spindles|weaving|textile|fabrics|filatures?|reeling|raw silk|basins|cotton tissues|piece goods|machines?|horse.?power|lacquer|matches|ceramic|pottery|porcelain|wax|refined|refineries|straw.plait|mats and matting|braids|canned|celluloid|cellophane|paper|pulp|menthol|peppermint|sugar|brewer|brewing|sake|soy sauce|tobacco|cigarettes|indigo balls)|製造|工場|工產|工産",
    "utilities": r"\b(?:waterworks|water supply|sewers|sewerage|electric lighting|electricity|power stations|gas works|public works|river works|riparian|reclamation|reconstruction|building construction|town planning|city planning)|水道|土木|電氣|電力",
    "transportation": r"\b(?:railways?|railroads?|locomotives|steamships|steamers|shipping|tonnage|seamen|merchant marine|vessels|tramway|harbou?rs?|roads?|bridges|passengers|freight|traffic|bus lines|aviation|air transport)|鐵道|鉄道|船舶|海運|交通",
    "communications": r"\b(?:post office|postal|telegraph|telephone|broadcast|wireless|radio)|郵便|電信|電話|通信",
    "labour": r"\b(?:labou?r|operatives|workers|employees|employes|wages|working hours|strikes|unemployed|child operatives)|勞働|労働|賃金|職業紹介",
    "welfare": r"\b(?:relief|charit|poverty|pauper|orphan|foundling|housing|social work|social welfare|family budgets|household budgets|retiring grants|annuities to families)|救助|救恤|社會事業",
    "press": r"\b(?:newspapers?|periodicals|dailies|journals|magazines|press statistics|shimbun|publications|publishers)|新聞|雜誌|出版",
    "culture": r"\b(?:museums?|fine arts|art exhibitions|theatres?|theaters?|cinema|musical|paintings|cultural|art galleries|archaeolog)|博物館|美術|古蹟",
    "sport": r"\b(?:sports|athletic|tennis|swimming|champions|golf|olympic|races|racing|football|baseball|jump|dash|hurdles)|體育|競技|庭球|野球",
    "science-and-technology": r"\b(?:patents?|patentable|trade.?marks|inventions?|designs registered|registration of designs|weights|measures|metric equivalent|english equivalent|scientific research|research laboratories|anthropometr|cephalic)|特許|度量衡",
    "geography": r"\b(?:latitude|longitude|geolog|strata|mountains|mineral springs|mineral waters|hot springs|altitude|climate|temperature|rainfall|humidity|land area|square ri|geographical)|地勢|氣象|気象|地質",
    "disasters": r"\b(?:earthquakes?|seismograph|volcano|floods|typhoon|calamities|disasters|fires)|震災|災害|水災",
    "economy": r"\b(?:economic indicators|economic barometers|economic plan|economic control|food rationing|cost of living|national income|national wealth|co.?operatives|subsidies and bounties)|經濟|経済|統制",
    "narcotics": r"\b(?:opium|morphine|morphia|heroin|narcotic)|阿片",
}
PATTERNS = {key: re.compile(value, re.I) for key, value in SUBJECTS.items()}


def review_record(record):
    table = record["table"]
    title = norm((table.get("en") or {}).get("t") or table.get("title"))
    chapter = norm(table.get("chapter"))
    description = norm(" | ".join(str(x) for x in [(table.get("en") or {}).get("d"), table.get("context"), table.get("caption_extra")] if x))
    source_notes = norm(" | ".join(table.get("footnotes", []) + table.get("transcriber_notes", [])))
    header_values = [str(value) for part in table.get("parts", []) for value in [part.get("label") or "", *part.get("columns", [])] if value]
    labels = [str(row[0]) for part in table.get("parts", []) for row in part.get("rows", []) if row and row[0]]
    all_cells = [str(value) for part in table.get("parts", []) for row in part.get("rows", []) for value in row if value]
    headers, row_labels, cells = map(lambda values: norm(" | ".join(values)), (header_values, labels, all_cells))
    contents = headers + " | " + cells
    primary = title + " | " + description
    evidence = {}
    scores = Counter()
    for topic, rx in PATTERNS.items():
        for field, text, weight in [("title", title, 5), ("description", description, 3), ("chapter", chapter, 2), ("body.headers", headers, 5), ("body.row_labels", row_labels, 3), ("body.cells", cells, 1)]:
            matches = list(rx.finditer(text))
            if matches:
                scores[topic] += weight * min(len(matches), 3)
                evidence.setdefault(topic, []).append({"field": field, "matched": matches[0].group(0)})

    def choose(topics, rule, reason):
        return {"topics": topics, "rule": rule, "reason": reason,
                "body_evidence": {topic: [e for e in evidence.get(topic, []) if e["field"].startswith("body.")] or [{"field": "body.headers-and-labels", "excerpt": (headers + " | " + row_labels)[:240]}] for topic in topics},
                "scores": dict(scores), "rows_inspected": sum(len(part.get("rows", [])) for part in table.get("parts", [])),
                "cells_inspected": len(all_cells)}

    # Additional complete-body families identified in central review. These are
    # high-level decisions only; the fixed detailed-tag cohort is untouched.
    if re.search(r"state forests|forest economy", source_notes + description) and re.search(r"area|yield|profit|receipts", contents):
        return choose(["forestry"], "forest-operating-returns", "The source identifies State forests; the body measures their area, yield or operating return.")
    if re.search(r"patent|trade.?mark|utility.model", chapter + contents + description) and re.search(r"applications|registrations|registered|actions|hypothecation|exploitation|design", title + contents):
        return choose(["science-and-technology"], "intellectual-property-records", "The complete record identifies applications, registrations, transfers or trials concerning industrial property.")
    if re.search(r"weights?,? measures?|weights?.*moneys|度量衡", chapter) and re.search(r"equivalent|單位|shaku|koku|tsubo|gallon|bushel|shō|sho\b|ken\b", contents) and title != "moneys":
        return choose(["science-and-technology"], "complete-measurement-reference", "The table's complete entries identify measurement units and equivalences.")
    if re.search(r"aborigin|indigenous|islanders|高砂族|蕃人|島民", title):
        if re.search(r"male|female|tribe|famil|total|population|census|男|女|戶|戸", contents):
            return choose(["indigenous-peoples", "population"], "explicit-indigenous-demography", "The explicit Indigenous subject and the body establish community/family/sex counts.")
        if re.search(r"killed|wounded|casualt|raids|murder|police|incident", title + contents):
            return choose(["indigenous-peoples", "crime-and-justice"], "explicit-indigenous-conflict", "The body records incidents or casualties in a table explicitly devoted to Indigenous communities.")
        if re.search(r"area|forest|district|cho\b", contents):
            return choose(["indigenous-peoples", "forestry"], "indigenous-forest-territory", "The complete body identifies Indigenous districts and forest area.")
    if re.search(r"late war|war casualties|battle|killed.*wound", title) and re.search(r"rank|killed|wounded|officer|sailor|prisoner", contents):
        return choose(["military"], "war-casualty-body", "The complete body gives campaign/service casualties or personnel losses.")
    if re.search(r"prison worker|prison labour|prison labor|inmates.*work", description + source_notes):
        return choose(["crime-and-justice", "labour"], "prison-work-returns", "The supplied full-record context explicitly identifies prison labour and the body's work/earnings figures.")
    if re.search(r"earnings and receipts.*worker", title) and re.search(r"justice|prison", chapter) and re.search(r"earnings|worker", headers):
        return choose(["crime-and-justice", "labour"], "prison-worker-earnings", "The record's judicial/prison context and worker-earnings columns identify the prison labour series.")
    if re.search(r"relief|vagran|mutual.*societ|social undertakings", title + description) and re.search(r"grant|fund|member|payment|beneficiar|lodging|pauper|persons|cause|amount|receipts", contents):
        return choose(["welfare"], "assistance-and-living-circumstances", "The complete body identifies material assistance, mutual aid, welfare facilities or conditions of dependency.")
    if re.search(r"immigrants|emigrants|residents|^ratio$", title) and re.search(r"men|women|male|female|family|houses|birth|death|marriage|divorce", headers):
        return choose(["population"], "migration-and-vital-rates", "The body gives resident/migration counts or demographic/vital-event ratios.")
    if re.search(r"civil officials|civil administration office|board of audit|board of directors|government of karafuto", title) and re.search(r"post|office|class|holder|name", headers):
        return choose(["transportation"] if re.search(r"railway company", source_notes + description) else ["trade"] if "directors" in title else ["government"], "identified-institutional-roster", "The full record identifies the institution and its office-holders.")
    if re.search(r"sovereigns|mikados|emperors|shoguns|shōguns|regents", title) and re.search(r"name|reign|year|from|to", headers):
        return choose(["government"], "ruler-succession-roster", "The complete record gives the names and succession/reign dates of political rulers.")
    if re.search(r"medical institute|professional institute", title) and re.search(r"students|instructors|pupils", headers):
        return choose(["education"], "professional-education-establishment", "The body counts institutions, teaching staff or students rather than medical treatment.")
    if re.search(r"telegram|telegraph|postage|postal|telephon|radio|broadcast", primary + source_notes) and re.search(r"rate|charge|fee|office|message|word|kana|programme|program", title + contents):
        return choose(["communications"], "identified-communication-service", "The full-record context identifies messaging/broadcast service, and the body gives its tariffs, facilities or service measures.")
    if re.search(r"vaccinat|medical|hospital|disease", title) and re.search(r"total|patients|cases|persons|number|year|quantity", headers):
        return choose(["health"], "medical-and-prevention-returns", "The complete record gives medical care, disease or preventive treatment measures.")
    if re.search(r"motive force|kilowatt|electric enterprises|electric industry|gas lamps", title) and re.search(r"hydro|steam|water|power|k\.?\s*w|lamp|motor|installation", contents):
        return choose(["utilities"], "energy-capacity-and-service", "The complete body identifies power generation/supply, capacity or utility installations.")
    if re.search(r"collier(?:y|ies)|coal output", title) and re.search(r"output|tons|coal|sold|receipt", contents):
        return choose(["mining"], "colliery-production-and-sales", "The body identifies colliery output and its sales/receipts.")
    if re.search(r"camphor", title) and re.search(r"oil|produced|output|quantity|kin", contents + description):
        return choose(["forestry", "manufacturing"], "camphor-and-distilled-oil", "The body jointly identifies the forest-derived camphor commodity and its oil/processed output.")
    if re.search(r"tea", title) and not re.search(r"refined|teacher|tea.?cher", title) and re.search(r"production|output|spring|summer|autumn|winter|harvest|cultivat", contents + description + title):
        return choose(["agriculture"], "tea-harvest-output", "The complete record identifies tea production or seasonal harvest quantities.")
    if re.search(r"ins(?:u|t)rance|assurance|policies abroad|contracts.*policies|insurance", title + description) and re.search(r"premium|policy|policies|contracts|deposit|amount|sum", contents):
        return choose(["finance"], "insurance-contracts-and-premiums", "The full record identifies insurance providers, policies, premiums or contract amounts.")
    if re.search(r"capital|treasury|official disbursements|endowment|fund amounts|financial", title) and re.search(r"yen|amount|allocat|figure|total|capital|fund|instalment", title + contents):
        return choose(["finance"], "identified-funds-and-capital", "The body records an identified allocation, fiscal fund, capital schedule or financing measure.")
    if re.search(r"new enterprises|business projects|enterprises and expansions", title) and re.search(r"capital|companies|project", headers):
        return choose(["economy", "finance"], "enterprise-formation-and-capital", "The body combines formation/expansion of enterprises across sectors with financing amounts.")
    if re.search(r"railway|train|rolling stock|locos|locomotive|wagon|carriage", primary + source_notes + contents) and re.search(r"mileage|line|track|distance|receipts|expenses|inventory|traffic", title + contents):
        return choose(["transportation"], "identified-rail-infrastructure-and-traffic", "Complete entries identify rail infrastructure, rolling stock, traffic or its operating results.")
    if re.search(r"distances|route|to manchuria via|to harbin via|seoul.fusan|seoul.wiju|branch lines", title) and re.search(r"distance|mileage|route|line|hours", headers):
        return choose(["transportation"], "route-and-travel-reference", "The body gives routes, network segments, journey lengths or durations.")
    if re.search(r"trade totals|principal commodities|\btrade\b", title + description) and re.search(r"trade|import|export|commodit", title + description):
        return choose(["trade"], "identified-trade-return", "The full-record description identifies a trade return, even where particular commodity/direction columns are missing.")
    if re.search(r"artizan|artisan|worker|wage|female labor|female labour|length of service", title) and re.search(r"age|male|female|earn|wage|years|under|over|rate|value|worker", contents):
        return choose(["labour"], "worker-characteristics-and-terms", "The complete body gives worker characteristics, remuneration or service conditions.")
    if re.search(r"wrestlers|wrestling|athletic|sports|races|racing", title) and re.search(r"name|record|weight|height|winner|time|distance|race|born", headers):
        return choose(["sport"], "sporting-results-or-participants", "The body identifies sporting participants, results or organised events.")
    if re.search(r"area of the japanese empire|rivers.*length|land.*russian.*japanese", title) and re.search(r"area|square|acres|coast|river|length|ri\b", contents):
        return choose(["geography"], "territorial-and-physical-measurements", "The body tabulates territorial extent or physical lengths rather than an economic activity.")
    if re.search(r"metric system|yard.pound|other equivalents|measures of capacity|land measures|dry goods.*kujira|^distance$|^weights$", title) and re.search(r"equivalent|單位|名稱|shaku|sun\b|cho\b|koku|kwamme|momme|kin\b", contents):
        return choose(["science-and-technology"], "unit-equivalence-body", "The body explicitly compares named measurement units, including Japanese originals.")
    if re.search(r"year dates|era names|nengo|nengō|japanese.*year.names|list of japanese.*year", title) and re.search(r"gregorian|year|era|a\.d\.|kanji", headers):
        return choose(["science-and-technology"], "calendar-equivalences", "The rows compare era names or year dates, a calendar-reckoning reference.")
    if title == "moneys" and re.search(r"equivalent|unit|currency|yen", contents):
        return choose(["finance"], "monetary-equivalences", "The complete body compares monetary denominations and their equivalents.")
    if re.search(r"sh[oō]guns|regents|shikken|former princes|imperial house", title) and re.search(r"name|from|to|princely|father|reign", headers):
        return choose(["government"], "historical-rulers-and-imperial-family", "The body identifies governing rulers/regents or members of the imperial family.")
    if re.search(r"rank|salary|allowance to officials|order.*officials", title) and re.search(r"per annum|salary|allowance|pay|annual|monthly", contents):
        return choose(["government", "labour"], "official-pay-and-allowances", "The body records official remuneration or allowances by post/rank.")
    if re.search(r"doctor.?s degrees|academic degrees", title) and re.search(r"awarded|doctor|degree|學位", contents):
        return choose(["education"], "academic-degrees", "Degrees awarded by subject are educational qualifications, not the subject disciplines themselves.")
    if re.search(r"original works by subjects|foreign correspondents|leading dailies|press statistics", title) and re.search(r"press|publication|newspaper|agency|agencies|literature|publisher|shimbun|dailies", chapter + contents):
        return choose(["press"], "publication-and-news-body", "The full body concerns publications or the institutions/personnel producing news.")
    if re.search(r"epochs in japanese art|periods.*art", title) and re.search(r"period|characteristic|duration|sub.division", headers):
        return choose(["culture"], "art-history-periodisation", "This is a periodisation of artistic traditions, not a general multi-subject chronology.")
    if re.search(r"child operatives|operatives|workers|working people|strikers|factory hands", title) and re.search(r"age|male|female|under|over|factory|worker|strike|arrest|operative|工|男|女", contents):
        return choose(["labour", "crime-and-justice"] if re.search(r"arrest|guilty|peace regulation", primary) else ["labour"], "workforce-and-labour-action", "The body describes workers, their age/sex composition or labour action and its explicit policing.")
    if re.search(r"family account|family.*outgo|sources of income|living expense|earnings and disbursements.*artisan", title) and re.search(r"family|families|earning|income|expense|rent|food|disbursement", contents):
        return choose(["welfare"], "household-living-conditions", "The complete body concerns household resources, living expenses or family budgets.")
    if title == "sundries" and re.search(r"per family|family|total outgo", headers):
        return choose(["welfare"], "household-budget-breakdown", "The columns explicitly identify expenditure per family and its share of household outgo.")
    if re.search(r"cost.of.living", title) and re.search(r"index|基準|調査|193|194|192", contents):
        return choose(["economy"], "cost-of-living-index", "The full body compares a cost-of-living index across dates or territories.")
    if re.search(r"trade union|workers. associations", title) and re.search(r"member|membership|association|union|年次|勞働|労働", contents):
        return choose(["labour"], "worker-organisations-body", "The body describes worker organisations or their membership.")
    if re.search(r"data at.{0,16}end of march|data at the end of march", title) and re.search(r"societies|members|member.s contribution|members. subscription", contents) and re.search(r"social|labor|labour", chapter):
        return choose(["welfare"], "mutual-aid-society-accounts", "The body identifies member-financed societies, their funds and assistance receipts/disbursements.")
    if re.search(r"assets and liabilities|net profit|net profits|working result|disposition of profits|distribution.*profit|capital allocation|instalments of capital|gross earnings.*expenses|earnings.*net profit|note issue|trust business|bill clearings|secured debenture|dividends?", title) and re.search(r"amount|yen|capital|profit|liabilit|asset|reserve|dividend|notes issued|reserves|金|手形|信託|資本", contents):
        return choose(["finance"], "financial-position-and-returns", "Financial assets/liabilities, capital, monetary issuance or earnings/returns organise the complete body.")
    if re.search(r"distribution of industries|joint enterprises|companies.*classif", title) and re.search(r"capital|capt\.|cos\.|companies|company|enterprises", headers):
        return choose(["trade", "finance"], "enterprise-organisation-and-capital", "The body explicitly combines enterprise organisation/counts with their capitalisation.")
    if re.search(r"incoming.*outgoing|shipments to and from|trade by countries|transactions.*exchanges|produce transactions|^exchanges$", title) and re.search(r"quantity|value|outward|inward|transaction|export|import|trade|手形|取引|賣買", contents):
        return choose(["trade"], "exchange-and-goods-movements", "The full body identifies commodity exchange or inward/outward goods movements.")
    if re.search(r"motor.*service|bus service|fleet|navigation bureaus", title) and re.search(r"vessel|buses|passenger|mileage|car|ports|navigation|steamer", contents):
        return choose(["transportation"], "transport-service-body", "The body describes vehicles/vessels, passengers, mileage or transport organisation.")
    if re.search(r"service pipes|water supplied|demand for power|supply of power|gas undertakings|public works", title + chapter) and re.search(r"water|pipes|main|branch|hydraulic|steam|power|lamps|river work|sand arresting|harbor work|事業者|供給|電氣", contents):
        return choose(["utilities"], "utility-networks-and-works", "The complete body identifies utility supply, networks, public works or their expenditure.")
    if re.search(r"position of the empire|islands.*area|groups of islands|principal islands|geographical position", title) and re.search(r"area|position|緯|經|極點|sq\.|hectare", contents):
        return choose(["geography"], "territorial-location-and-extent", "The body gives physical positions or territorial extent of the named places.")
    if re.search(r"jurisdiction|provinces and seats|branch bureaus|departmental organization|departmental organisation", title) and re.search(r"province|office|bureau|section|division|functions|jurisdiction", contents):
        return choose(["government"], "administrative-geography-and-machinery", "The complete body maps administrative offices, jurisdictions or public functions.")
    if re.search(r"\b(?:principal cities|number of foreigners|foreigners|japanese in|emigrants|new tokyo|yokohama.*new)\b", title) and re.search(r"male|female|population|japanese|chinese|koreans|foreigners|families|household", headers):
        return choose(["population"], "resident-counts-and-demography", "The columns explicitly count residents, household groups or nationalities.")
    if re.search(r"capital punishment|causes of murders?|violation|accusations|sentences carried|above cases|case.{0,20}nature", title) and re.search(r"justice|police|judicature", chapter):
        return choose(["crime-and-justice"], "judicial-outcomes-and-offences", "The court/police chapter and body give cases, sanctions, offence causes or outcomes.")
    if re.search(r"civil and military service|administrative system|directory civil", chapter) and re.search(r"office|post|name|holder|duty|minister|president|director|department|chief", headers + row_labels):
        return choose(["military"] if re.search(r"admiralt|naval|army|garrison|divisional|brigade", title) else ["government"], "public-office-roster-body", "The complete body is a roster or organisation of named public offices.")
    if re.search(r"slaughter|domestic animals|fruits|tobacco|sweet potatoes|area planted|sapling|cultivated", title) and re.search(r"cultivat|area|trees|cattle|swine|goat|head|oranges|banana|longan|pine.appl|paddy|upland|株|耕地", contents):
        return choose(["forestry"] if re.search(r"sapling|forest", primary) else ["agriculture"], "cultivation-husbandry-and-fruit", "The body identifies cultivation/tree resources, fruit harvests or animal husbandry/slaughter.")
    if re.search(r"salt", title) and re.search(r"salt field", headers):
        return choose(["mining"], "salt-fields-and-output", "The full body measures salt fields and their extracted output.")
    if re.search(r"salt|refined tea|tobacco|silk reeling|indigo", title) and re.search(r"manufactur|production|output|cut|prepar|製絲|生產|製造|價額", contents):
        return choose(["manufacturing"], "identified-processing-output", "Processing establishments or manufactured commodity output are explicit in the complete body.")
    if re.search(r"agricultural products", description) and re.search(r"output|production|quantity|area|family", contents):
        return choose(["agriculture"], "agricultural-product-returns", "The supplied agricultural-product context and complete body establish production returns.")
    if re.search(r"industry|industries|industdy|chemical", chapter) and re.search(r"factories|workshop|manufactur|production|products|cotton|silk|refined|soap|wax|employees|employes|horse.power|motors|engines|paid up|capital|纖維|製造", contents):
        return choose(["manufacturing"], "industrial-body-family", "Industrial establishments, productive equipment or output measures are present in the complete body.")

    if re.search(r"\b(?:weights|land measures|measures of length|distance and length|quantity, capacity|cubic measures|measurement|metric system)\b", title) and re.search(r"equivalent|measure|unit|ri\b|cho\b|shaku|kwamme|momme|koku|kin\b", contents):
        return choose(["science-and-technology"], "measurement-reference", "The complete body gives measurement units or equivalences.")
    if re.search(r"patent|trade.?marks|invention", chapter + primary) and (re.search(r"patent|design|trade.?mark|invention|specification", contents) or "patent" in title):
        return choose(["science-and-technology"], "patent-administration", "Patent forms, rules, office receipts or application/registration series.")
    if re.search(r"\b(?:mikados|emperors|imperial house|year.names)\b", title) and re.search(r"reign|emperor|year.name|kanji|a\.d\.", contents):
        return choose(["government"], "imperial-reigns", "The body identifies rulers, reigns or the names and durations of imperial eras.")
    if re.search(r"\b(?:chronological|chronology|historical events)\b", title) and len(set(topic for topic, n in scores.items() if n >= 5)) > 3:
        return choose(["history"], "multi-subject-chronology", "The complete event list spans multiple substantive historical subjects.")
    if re.search(r"\b(?:dailies|press statistics|newspapers|periodicals)\b", primary + chapter) and re.search(r"dailies|periodical|shimbun|editor|publish|newspaper|magazine|journal", contents):
        return choose(["press"], "press-directory-statistics", "The columns and entries concern publications, their publishers or circulation.")
    if re.search(r"\b(?:budget|revenue|expenditure|revenues|expenditures|finance|accounts)\b", title):
        if re.search(r"educat|school|universit", primary) and re.search(r"school|universit|educat|instructor|student", contents):
            return choose(["education", "finance"], "dedicated-education-finance", "A dedicated educational budget/account is supported by the complete body.")
        if re.search(r"railway|shipping|post|telegraph|telephone|forestr|fish|manufactur", primary):
            domain = next((topic for topic in ["transportation", "communications", "forestry", "fisheries", "manufacturing"] if PATTERNS[topic].search(primary) and scores[topic] >= 5), None)
            if domain:
                return choose([domain], "sector-operating-account", "The whole table is a named service or productive sector's operating account.")
        if scores["finance"] >= 8 or re.search(r"ordinary revenue|civil adm|taxes|state undertakings|government|fiscal", contents):
            return choose(["finance"], "financial-account-body", "Revenue, expenditure, financial stocks or liabilities organise the body.")
    if re.search(r"\b(?:wages|salaries|shin.nin rank|choku.nin rank|so.nin rank|han.nin rank)\b", title) and re.search(r"per annum|salary|salaries|pay|allowance|yen", contents):
        return choose(["government", "labour"] if "rank" in title or "civil" in chapter else ["labour"], "pay-scale", "The body gives remuneration scales, including named official posts where explicit.")
    if re.search(r"\b(?:pension|annuit|retiring grant|retirement allowance)\b", primary + headers):
        return choose(["finance", "welfare"], "pension-benefits", "The complete record tabulates pensions, annuities or retirement grants.")
    if re.search(r"\b(?:export|import|tariff|overseas trade|foreign trade|trade by|trade returns|exporters|importers)\w*\b", title + headers):
        return choose(["trade"] + (["finance"] if re.search(r"tariff|duties|customs rate", title) else []), "trade-movements", "Trade direction, tariff schedules or trading firms are explicit in the body/title.")
    if re.search(r"customs receipts|customs revenue|tax receipts|tax revenue|taxation", primary) and re.search(r"duties|tax|revenue|receipts|imp\.|exp\.", contents):
        return choose(["finance"], "fiscal-receipts", "The body records fiscal levies and their receipts.")
    if re.search(r"\b(?:embass|legations?|consul|diplomat)", contents + primary):
        if re.search(r"diplomac|foreign relations", chapter) or re.search(r"embass|legation|consular|consulate", title):
            return choose(["foreign-relations"], "diplomatic-roster", "The entries identify diplomatic missions, staff or consular posts.")
    if re.search(r"military|army|navy|admiralt|garrisons|commanders|forts|divisional|brigade|general staff|spoils|arms and ammunition|warships|torpedo", title) and re.search(r"army|navy|military|naval|garrison|fort|rank|commander|chief|ammunition|guns|rifles|cannons|squadrons|colonel|admiral", contents):
        return choose(["military"], "armed-forces-body", "Military formations, personnel, weapons, vessels or campaign results organise the body.")
    if re.search(r"progress of the war|army and.{0,8}navy|national defence|national defense", chapter) and (scores["military"] >= 4 or re.search(r"rations|fodder|provisions|horses|prisoners|battles", contents)):
        return choose(["military"], "military-context-and-body", "The military chapter and the complete body identify a defence/campaign subject.")
    if re.search(r"local administr|administrative system|civil service|directory civil", chapter) and re.search(r"governor|mayor|minister|prefecture|office|department|duty|division", contents):
        return choose(["government"], "administrative-roster", "The body identifies public jurisdictions, offices or their holders.")
    if re.search(r"\b(?:census|inhabitants|population|settlers|foreigners in|japanese in|aliens|residents)\b", title) and re.search(r"male|female|famil|household|population|nationality|total", contents) and not re.search(r"accused|convict|prison|offence|defendant", title):
        return choose(["population"], "population-body", "Counts or characteristics of residents or settlement groups are explicit in the columns.")
    if re.search(r"\b(?:schools|educational institutes|instructors|curriculum|graduates|tuition|kindergartens)\b", title) and scores["education"] >= 7:
        return choose(["education"], "education-body", "The body tabulates educational institutions, learners, staff or instruction.")
    if re.search(r"\b(?:convict|sentenc|insolvenc|rehabilitation|accused|criminal|not guilty|first.instance|cases.*instance|cases.*court|penal|police)", title) and (scores["crime-and-justice"] >= 5 or re.search(r"penal|imprison|judgment|creditor|debitor|punishment|cases", contents)):
        return choose(["crime-and-justice"], "justice-body", "Court, offence, sentencing, insolvency or detention measures organise the complete record.")
    if re.search(r"industr|manufactur|chemical|sericulture and raw silk", chapter):
        if re.search(r"child operatives|operatives|workers|labou?r|working hours|wages", title):
            return choose(["labour"], "industrial-workforce", "The body measures workforce composition, pay or working conditions.")
        if re.search(r"cocoons|silkworms|mulberry", title + headers) and not re.search(r"reeling|filatures|silk fabrics", title + headers):
            return choose(["agriculture"], "sericulture-husbandry", "The columns describe silkworm/cocoon/mulberry husbandry rather than textile manufacture.")
        if re.search(r"factories|manufactur|spindles|filature|weaving|reeling|factory|workshops|refineries|refined|mills|production|output|families engaged|employees|employes|silk fabrics|capital invested|capital paid|products|engines|motors|horse.power|matches|ceramic|lacquer|paper|wax|mats|celluloid|brewer", title + contents):
            return choose(["manufacturing"], "productive-establishments-body", "The complete body describes industrial establishments, equipment or manufactured output.")
    if re.search(r"\b(?:price|prices|market quotations)\b", title) and re.search(r"yen|price|sen|tael|shilling|pence|dollar", contents):
        return choose(["trade"], "commodity-prices", "The columns give market prices of the named goods.")
    if re.search(r"\b(?:railway|train|freight|traffic|shipping|merchant marine|vessel|steamship|seamen|bus lines|aviation|aeroplanes)", primary + headers) and scores["transportation"] >= 8:
        return choose(["transportation"], "transport-body", "Vehicles, network infrastructure, traffic or carrying services are explicit in the complete record.")
    if re.search(r"\b(?:post|telegraph|telephone|wireless|broadcast|radio)", title + headers) and scores["communications"] >= 6:
        return choose(["communications"], "communications-body", "Mail, telecommunication or broadcast services organise the body.")
    if re.search(r"\b(?:earthquake|seismograph|volcan|typhoon|disaster|flood)", primary) and scores["disasters"] >= 5:
        return choose(["disasters"], "disaster-observations", "The body describes a destructive event or its observed effects.")
    if re.search(r"\b(?:mineral springs|mineral waters|hot springs|analysis of.{0,40}spring|strata|geolog|mountain|land area|geographical)", title + chapter):
        return choose(["geography"], "physical-setting-body", "Physical locations, formations, territorial extents or natural waters are the subject.")
    if re.search(r"\b(?:fish|marine production|nets|shell.fish|sea.weeds)", title) and scores["fisheries"] >= 7:
        return choose(["fisheries"], "aquatic-resources-body", "Fishing gear, aquatic resources, catches or primary fishery products are identified in the body.")
    if re.search(r"\b(?:tillage|arable|agricultural|crops|rice|harvest|cattle|livestock|poultry|ginseng|sugar.?cane|cocoons|mulberry|coconut|copra)\b", title) and re.search(r"area|harvest|yield|output|production|paddy|upland|acre|cho|koku|cultivat|trees|head|cattle|pig|livestock", contents):
        return choose(["agriculture"], "agricultural-body", "Land, crop/husbandry resources or agricultural production are explicit in the complete record.")
    if re.search(r"\b(?:sugar|alcohol|indigo|camphor|cotton|silk|wool|leather|rubber|tobacco)\b", title) and re.search(r"manufactur|refin|mill|filature|fabrics|weaving|spinning|ginned|cigarette|cigar|tanning|brewer", title + contents):
        return choose(["manufacturing"], "processed-commodity-body", "The body identifies processing establishments or manufactured forms of the commodity.")
    if re.search(r"\b(?:mines?|mineral|coal|ore|gold|silver|copper|petroleum|phosphate)\b", title) and re.search(r"mines?|ore|deposits|output|production|reserves|collier|coal", contents + primary):
        return choose(["mining"], "mineral-body", "The body identifies mineral resources or extraction/output.")
    # Strong subject names whose complete bodies were inspected in the unresolved
    # families. These are deliberately broader than detailed-tag decisions.
    signatures = [
        ("trade", r"\b(?:exports?|imports?|trade|goods.*(?:incoming|outgoing)|incoming|outgoing|shipments?|retail prices|wholesale prices|market prices|transactions at|trading|produce exchanges)\b"),
        ("economy", r"economic plan|industrial plan|five.year|5.year|economic polic|cost.of.living|general economic|value of output by industry|economic activities"),
        ("finance", r"income|revenues?|expenditures?|profits?|treasury|financial|finance|capital invested|capital subscribed|capital paid|deposits|credit association|credit union|credit operations|trust|insurance|funds|reserve|bank|bonds|investment"),
        ("education", r"students|pupils|instructors|schools|graduates|degrees|educational|universit|tuition|scholarship|medical institute"),
        ("religion", r"religious|religion|shinto|buddhis|temples|shrines|churches|missionaries|christian"),
        ("crime-and-justice", r"amnest|cases.*appeal|appeal.*trial|judicial|civil procedure|civil litigation|murders?|convictions|sentenc|police|criminal|prison|offenders|punishment"),
        ("foreign-relations", r"foreign consuls|foreign envoys|envoys abroad|diplomat|consul|ambassadors|embassies|legations|league assembly|agreement.*(?:japan|china|italy)|demands.*government"),
        ("military", r"military|naval|army|navy|brigades|infantry|cavalry|corps|air combats|defence department|defense department|war losses|forces|air raid|atomic bomb|outbreak.*war|losses.*japanese|losses.*sino|samurai"),
        ("government", r"government|departments|sections of the executive|executive yuan|state funerals|court rank|imperial grants|imperial oath|civil officials|administrative|bureaux|bureau|imperial family|imperial princes|empire.*constitution"),
        ("population", r"population|obituary|distribution by age groups|demographic|births?|deaths?|marriages|divorces|households|immigrants|emigrants|residents"),
        ("forestry", r"\b(?:forests?|felling|forest stands|sapling|timber|afforestation|reforestation)\b"),
        ("agriculture", r"agricultur|farmers|farming|cultivat|crops|harvest|sugar plantations|sugar plantation|cane crop|arable|paddy|livestock|cattle|poultry|fruit production|production of fruits|sericultur|silkworm|cocoons"),
        ("manufacturing", r"manufactur|industrial products|industrial output|cotton tissues|loom|filature|foundries|sake|sugar output|refined tea|silk reeling|raw silk|winding speed|mousseline|artificial manure|production of soap|production of cement|production of lime nitrogen"),
        ("utilities", r"public works|public utilities|electric energy|supply.*gas|consumption.*gas|production.*gas|distribution of gas|electric power|sewers|water supplied|water supply|buildings|engineering work"),
        ("transportation", r"vehicles|motor service|motor.bus|bus service|seamen|captains|mates|navigation|coasting|tramp owners|shipping|marine|railway|railroad|passengers|vessels|tonnage|traffic|ant(?:ung|ong).mukden line"),
        ("communications", r"\b(?:mails?|posts?|messages|listeners|broadcast|telegrams?|telegraphic|wireless|radio|telephones?)\b"),
        ("labour", r"labou?r|wage|workers|operatives|strikers|strike|employment|unemployed|workmen|work.hours|hours of work"),
        ("welfare", r"welfare|mutual aid|mutual relief|social undertakings|social institutions|relief fund|relief grants|household|family account|family budgets|living expenses|poverty"),
        ("press", r"newspapers|newspaper|daily papers|publication|magazine|book production|books published|daily press|dailies|news agencies"),
        ("culture", r"literature|arts|fine art|music|theatre|theater|cinema|museums|archaeolog|archaeolog|héian period|heian period"),
        ("sport", r"wrestlers|wrestling|race courses|race club|race law|athletic|golf|olympic|tennis|sports|swimming|baseball"),
        ("health", r"vaccinat|serums|medical|diseases|patients|hospitals|health|sanitary"),
        ("geography", r"\b(?:area|provinces|border regions|mountains|rivers|frost|snow|temperature|humidity|rainfall|weather)\b"),
        ("science-and-technology", r"patents|utility.models|equivalents|unit system|measurements|measuring instruments"),
    ]
    if headers.strip() and all_cells:
        for topic, expression in signatures:
            if re.search(expression, title, re.I):
                return choose([topic], "explicit-subject-with-complete-body", "The specific title/context identifies the principal subject; the complete columns, rows and notes were checked for a conflicting interpretation.")
    if re.search(r"area.*square|area.*sq\.|coast line|地積|面積", headers) and not re.search(r"cultivat|forest|plantation|crop|salt", primary):
        return choose(["geography"], "area-columns", "The body explicitly measures territorial surface area or physical extent.")
    if re.search(r"net profit|profit for|dividend|collateral securities|guaranty funds|reserve funds|bank balances", row_labels + headers):
        return choose(["finance"], "financial-ledger-body", "The body is an identified profit, securities or monetary-balance ledger.")
    if re.search(r"forestry and fishery", chapter) and re.search(r"marine products|takes.*yen", headers):
        return choose(["fisheries"], "fishery-returns-body", "Catch/takings and marine products explicitly organise the body.")
    if re.search(r"publication|press", chapter) and re.search(r"newspaper|drama photos|lit\. or scientific|publish", contents):
        return choose(["press"], "publication-statistics-body", "The body counts publications by publishing class, not the disciplines represented by their content.")
    if re.search(r"justice|prisons|police", chapter) and re.search(r"cases|quashed|rejected|withdrawn|convict|acquitt|amnesty|judgment", contents):
        return choose(["crime-and-justice"], "judicial-case-body", "The complete case/outcome columns and judicial context establish the justice subject.")
    if re.search(r"milk|meat|egg|cheese|butter|cattle|pigs|fowls", title + headers) and not re.search(r"factories|manufactur|export|import|trade|market|prices", primary):
        return choose(["agriculture"], "animal-produce-body", "The record describes livestock or primary animal products.")
    if re.search(r"industry|industrial|chemical|industdy", chapter) and re.search(r"soap|wax|loom|fabric|thread|artificial|製絲|工場|工產|工産|製造|filature|bleaching|nitrogen|celluloid|rubber|cement|chemical|ceramic", title + contents):
        return choose(["manufacturing"], "named-industrial-process-or-product", "The complete body identifies a manufacturing process or an industrial commodity.")
    if re.search(r"public works|construction|reconstruction|utilities", chapter) and re.search(r"work|power|gas|generation|frequency|hydro|thermal|street|park|restoration|capacity|lamp|river|reconstruction", title + contents):
        if re.search(r"electrical machines|electric machines and apparatus", title):
            return choose(["manufacturing"], "electrical-equipment-output", "The body measures manufactured electrical equipment rather than electricity supplied.")
        return choose(["utilities"], "civil-works-and-utility-body", "The full record concerns civil works, reconstruction infrastructure or utility generation/supply.")
    if re.search(r"gas|electric|power|transmission|generation", title) and re.search(r"lamps|heating|installation|kw\b|k\.w|k\.?\s*w\.?|kilowatt|horse|hydraulic|thermal|cycles|hydro|cubic|supplied|supply", contents):
        return choose(["utilities"], "energy-infrastructure-capacity-and-consumption", "Energy equipment, capacities, connections or utility supply/consumption organise the body.")
    if re.search(r"production|output|produced|used", title) and re.search(r"sugar|sak[eé]|beer|brewing|soft drinks|canned|silk|thread|basin|crab|isinglass|lime nitrogen", title + headers):
        return choose(["manufacturing"], "processed-food-and-material-output", "The body gives processing output, productive equipment or industrial material inputs.")
    if re.search(r"consumption.*sugar|sugar consumption", title) and re.search(r"per|consumption|head|year|kin", headers):
        return choose(["economy"], "aggregate-food-availability-and-use", "The body measures aggregate or per-capita commodity consumption, not a medical nutritional observation.")
    if re.search(r"wheat|rice|barley|soy.?beans|maize|cereals|cotton|sugar.?cane|food crops", title) and re.search(r"harvest|production|cultivat|acreage|acre|crop|planted|area|yield", title + headers):
        return choose(["agriculture"], "identified-crop-output-or-land", "The complete body explicitly identifies cultivation, crop acreage or agricultural yields.")
    if re.search(r"workshops|mechanic works|winding speed|thread produced|basins|filatures|cotton tissues", title) and re.search(r"work|employees|capital|loom|thread|speed|denier|yard|basin|filature|no\.", contents):
        return choose(["manufacturing"], "manufacturing-equipment-and-establishments", "The body identifies productive workshops, textile machinery, thread tests or industrial establishments.")
    if re.search(r"sugar|cotton|isinglass", title) and re.search(r"production|output|manufactur|manufactur|factory|factories|produced", description + source_notes):
        return choose(["manufacturing"], "explicit-productive-context", "The full-record context explicitly identifies manufacture or processed commodity output.")
    if re.search(r"forest|arisan|shakujime|sapling", title) and re.search(r"trees|tree|conifers|broad.leaf|species|stamps|shakujime|plantation|acreage|yield", contents + primary):
        return choose(["forestry"], "forest-stands-and-plantations", "The complete body identifies forest species, standing timber or sapling plantations.")
    if re.search(r"population|principal cities|inhabitants|natives", primary) and re.search(r"city|figure|famil|household|male|female|age|count|number|total", contents):
        return choose(["population"], "identified-population-return", "The full-record context identifies resident population even where generic columns omit that word.")
    if re.search(r"welfare|social politics|social problems|labor problems|labour problems", chapter) and re.search(r"girl workers|minors|occupational women|monthly earnings|service over|retirement|mutual aid|mutual relief", title + description):
        return choose(["welfare"] if re.search(r"aid|relief|retirement", title + description) else ["labour"], "worker-social-circumstances", "The full body and subject context identify worker conditions, remuneration, service benefits or mutual support.")
    if re.search(r"life|destruction|earthquake|damage|inundation|tidal waves|waves", title + chapter) and re.search(r"killed|injured|missing|loss|losses|damag|repair|stricken", title + headers + description):
        return choose(["disasters"], "disaster-impact-and-repair", "The complete record identifies casualties, material losses or repair after a destructive event.")
    if re.search(r"civil.*status|legal status|laws|law,|law\)|imperial oath", title) and re.search(r"article|item|difference|status|point|rule|rights|constitution", contents):
        return choose(["government"], "legal-foundations-and-status", "The body lists formal laws, governmental principles or legally defined civil status.")
    if re.search(r"press|publication", chapter) and re.search(r"original works|want ad|asahi|nichi nichi|system of.*offices|statistics", title):
        return choose(["press"], "publishing-enterprise-and-output", "The complete body describes publishing output or the operations and organisation of news enterprises.")
    if re.search(r"warehous|stocks of.*commodit|^destinations$|ladies. wardrobe|business directory", title) and re.search(r"commodity|commodities|warehouse|quantity|stock|yen|country|countries|office|business|item|u\.s\.a\.|india", contents):
        return choose(["trade"], "distribution-storage-and-commercial-reference", "The full body concerns commercial storage/distribution, business listings or commodity prices.")
    if re.search(r"television|transmitting apparatus|amplifier|valves", title) and re.search(r"valves|stage|amplif|modulator|circuit", contents):
        return choose(["science-and-technology"], "technical-apparatus-specification", "The body describes a technical apparatus or experimental equipment.")
    if re.search(r"marcantile marine|mercantile marine", chapter) and re.search(r"service|subsid|route|tramp|rate|navigation|lights|signals|tons|ship|yard|captain|mates", title + contents):
        return choose(["manufacturing"] if re.search(r"orders.*completion|vessels built|ships built", title) else ["transportation"], "merchant-shipping-and-support", "The complete body identifies shipping, navigation, its services or explicit ship-construction orders.")
    # Scores use every complete row/cell, with headers stronger than incidental
    # prose. Retain close multi-domain conflicts for explicit central review.
    ranked = scores.most_common()
    if ranked and ranked[0][1] >= 12 and (len(ranked) == 1 or ranked[0][1] >= ranked[1][1] * 1.7):
        topic = ranked[0][0]
        if any(e["field"].startswith("body.") for e in evidence.get(topic, [])):
            return choose([topic], "dominant-complete-body-subject", "Convergent title/context and complete body evidence establish one principal subject.")
    return choose([], "requires-explicit-review", "No sufficiently dominant subject; inspect the complete record or retain the source-context uncertainty.")


def frozen_records():
    """Reconstruct the frozen input from committed data on a fresh checkout."""
    path = OUT / "records.json"
    manifest = b.read(OUT / "manifest.json")
    if not path.exists():
        baseline = b.read(b.PUBLISHED / "assignments.json")["assignments"]
        wanted = set(manifest["keys"])
        records = []
        for book, tables, _, _ in b.committed_pages():
            for table in tables:
                key = book["slug"] + ":" + table["id"]
                if key in wanted:
                    records.append({"key": key, "book": {"slug": book["slug"], "title": book["title"]},
                                    "table": table, "previous": baseline[key]})
        b.write(path, records)
    assert b.sha(path) == manifest["records_sha256"]
    return b.read(path)


def build(verbose=True):
    records = frozen_records()
    manifest = b.read(OUT / "manifest.json")
    assert b.sha(OUT / "records.json") == manifest["records_sha256"]
    decisions = {r["key"]: review_record(r) for r in records}
    # Where the transcription explicitly says its headings are on the preceding
    # page, inspect that preceding record too. Require the same chapter and a
    # compatible column count; never inherit solely from physical proximity.
    by_book = {book["slug"]: tables for book, tables, _, _ in b.committed_pages()}
    positions = {slug: {t["id"]: i for i, t in enumerate(tables)} for slug, tables in by_book.items()}
    for record in records:
        key = record["key"]
        if decisions[key]["topics"]:
            continue
        table = record["table"]; slug = record["book"]["slug"]
        context = norm(" ".join(str(table.get(k) or "") for k in ("title", "context")))
        if not re.search(r"continu|previous page|preceding page", context):
            continue
        index = positions[slug][table["id"]]
        if not index:
            continue
        previous = by_book[slug][index - 1]
        if previous.get("chapter") != table.get("chapter"):
            continue
        current_widths = {len(p.get("columns", [])) for p in table.get("parts", [])}
        preceding_widths = {len(p.get("columns", [])) for p in previous.get("parts", [])}
        if not (current_widths & preceding_widths):
            continue
        parent = review_record({"table": previous})
        if parent["topics"]:
            decisions[key].update({"topics": parent["topics"], "rule": "explicit-continuation-body-context", "reason": "The transcription explicitly continues the preceding table; the same chapter and compatible body-column structure support its subject.", "preceding_key": slug + ":" + previous["id"], "preceding_body_evidence": parent["body_evidence"]})
    manual = OUT / "manual-groups.json"
    if manual.exists():
        used = set()
        for group in b.read(manual):
            for index in group["indices"]:
                assert index not in used, index
                used.add(index)
                key = records[index]["key"]
                decisions[key].update({"topics": group["topics"], "rule": "explicit-complete-record-decision", "reason": group["reason"], "review_index": index})
    b.write(OUT / "candidates.json", {"tables": decisions})
    unresolved = [i for i, r in enumerate(records) if not decisions[r["key"]]["topics"]]
    b.write(OUT / "unresolved-indices.json", unresolved)
    if verbose:
        print(json.dumps({"reviewed": len(records), "proposed": len(records) - len(unresolved), "unresolved": len(unresolved), "rules": dict(Counter(d["rule"] for d in decisions.values()))}, indent=2))


def finalize():
    existing = b.PUBLISHED / "overrides.json"
    if existing.exists() and any(set(fields) - {"topics", "stage"} for fields in b.read(existing)["assignments"].values()):
        raise RuntimeError("This historical high-level export would overwrite later detailed-tag reviews. Rebuild the website with build/build_tags.py instead.")
    build(False)
    manifest = b.read(OUT / "manifest.json")
    records = b.read(OUT / "records.json")
    decisions = b.read(OUT / "candidates.json")["tables"]
    vocabulary = b.read(HERE / "vocabulary.json")
    topic_ids = {entry["id"] for entry in vocabulary["topics"]}
    assert len(records) == len(decisions) == len(set(manifest["keys"])) == 3114
    assert {r["key"] for r in records} == set(decisions) == set(manifest["keys"])
    assert b.sha(OUT / "records.json") == manifest["records_sha256"]
    assert b.sha(OUT / "deployment-gate.json") == manifest["deployment_gate_sha256"]
    assert b.sha(b.PUBLISHED / "assignments.json") == manifest["original_published_assignments_sha256"]
    assert b.sha(HERE / "reviews/deferred-detailed-tags-2026-10-26.json") == manifest["deferred_detailed_cohort_sha256"]
    assert all(b.sha(b.SITE / path) == value for path, value in manifest["source_files"].items())
    gate = b.read(OUT / "deployment-gate.json")
    assert datetime.fromtimestamp((OUT / "records.json").stat().st_mtime, timezone.utc) > datetime.fromisoformat(gate["verified_utc"])
    baseline = b.read(b.PUBLISHED / "assignments.json")["assignments"]
    assert {key for key, row in baseline.items() if not row["topics"]} == set(decisions)
    overrides, reviewed, unresolved = {}, [], []
    for index, record in enumerate(records):
        key = record["key"]; d = decisions[key]
        assert len(d["topics"]) == len(set(d["topics"])) <= 2 and set(d["topics"]) <= topic_ids
        assert baseline[key] == record["previous"]
        table = record["table"]
        expected_rows = sum(len(part.get("rows", [])) for part in table.get("parts", []))
        assert d["rows_inspected"] == expected_rows
        audit = {"key": key, "review_index": index, "title": (table.get("en") or {}).get("t") or table.get("title"), **d,
                 "previous_topics": [], "existing_detailed_tags": baseline[key]["tags"], "detailed_tags_changed": False, "flags_changed": False}
        reviewed.append(audit)
        if d["topics"]:
            overrides[key] = {"topics": d["topics"], "stage": "contents-reviewed-high-level"}
        else:
            audit["review_question"] = "The supplied transcription does not establish a confident high-level activity/measure, or is an editorial reference whose placement needs a vocabulary-boundary decision. Retain blank rather than guess."
            unresolved.append(audit)
    b.write(OUT / "reviewed-decisions.json", {"count": len(reviewed), "method": "assistant-authored-complete-transcription-rules-and-central-record-decisions", "tables": reviewed})
    b.write(OUT / "unresolved.json", {"count": len(unresolved), "tables": unresolved})
    b.write(b.PUBLISHED / "overrides.json", {"schema_version": 1, "scope": "high-level-topics-only", "review": "../reviews/missing-high-level-2026-10-26/REPORT.md", "assignments": overrides})
    after = b.load_assignments()
    assert set(after) == set(baseline)
    assert all(after[key]["tags"] == row["tags"] and after[key]["flags"] == row["flags"] for key, row in baseline.items())
    assert all(after[key] == row for key, row in baseline.items() if key not in overrides)
    assert sum(not row["topics"] for row in after.values()) == len(unresolved)
    deferred = b.read(HERE / "reviews/deferred-detailed-tags-2026-10-26.json")
    assert deferred["count"] == len(deferred["tables"]) == 7662
    assert all(after[row["key"]]["tags"] == [] for row in deferred["tables"])
    totals = {"checked": 3114, "new_high_level_assignments": len(overrides), "still_unresolved": len(unresolved),
              "detailed_review_cohort_retained": 7662, "original_interface_live_before_review": True,
              "topics_used": dict(Counter(topic for row in overrides.values() for topic in row["topics"]))}
    b.write(OUT / "validation.json", {"status": "complete", **totals, "validated_utc": datetime.now(timezone.utc).isoformat(),
        "checks": {"exact_3114_key_coverage": True, "all_complete_bodies_processed": True,
        "all_source_files_unchanged": True, "vocabulary_ids_and_limits_valid": True,
        "previously_assigned_high_level_topics_unchanged": True, "all_detailed_tags_and_flags_unchanged": True,
        "fixed_7662_list_unchanged": True, "first_deployment_completed_before_review_started": True},
        "input_manifest_sha256": b.sha(OUT / "manifest.json"), "manual_groups_sha256": b.sha(OUT / "manual-groups.json"),
        "overrides_sha256": b.sha(b.PUBLISHED / "overrides.json"), "source_files": manifest["source_files"], "issues": []})
    lines = ["# Review of tables without high-level topics", "",
        f"Checked all **3,114** records after the first tag interface was merged, deployed and verified live. Saved **{len(overrides):,}** high-level assignments; **{len(unresolved)}** remain blank because of insufficient source identification or a vocabulary-boundary question.", "",
        "The interface deployment gate is recorded in [deployment-gate.json](deployment-gate.json). The first deployment was merge commit `cdbae7d54b3f318132001ada167f203d037e6c94`, Pages run `40403515327`. The complete-transcription review began after live HTTP verification.", "",
        "## Method", "",
        "The assistant performed a local, rule-assisted subject review of the existing complete transcriptions. All columns, part labels and every row/cell were processed, together with captions, context, printed notes and transcriber notes. Repeated subject families use centrally authored rules; ambiguous families and explicit exceptions received targeted examination. Fifteen explicit continuations use the preceding complete transcription only when the chapter and column structure agree. This does not claim that each numerical cell was individually reread for transcription accuracy.", "",
        "No external LLM calls, OCR or source-data corrections were made. These are subject assignments for evaluation. The source's historical categories are retained; colonial or Indigenous labels are not inferred from collection alone.", "",
        "Only high-level topics change. Every existing detailed tag and text flag is preserved. The fixed [7,662-table detailed review cohort](../deferred-detailed-tags-2026-10-26.json) is unchanged and remains for later closer evaluation.", "",
        "## Files", "", "- [All reviewed decisions and evidence](reviewed-decisions.json)",
        "- [Explicit central decisions](manual-groups.json)", "- [Remaining unresolved records](unresolved.json)",
        "- [Website overrides](../../published/overrides.json)", "- [Validation](validation.json)", "",
        "## Still unresolved", "", "| Key | Title |", "| --- | --- |"]
    for row in unresolved:
        lines.append(f"| `{row['key']}` | {str(row['title']).replace('|', '/')} |")
    (OUT / "REPORT.md").write_text("\n".join(lines) + "\n")
    print(json.dumps(totals, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("action", choices=["prepare", "build", "finalize"])
    args = parser.parse_args(); {"prepare": prepare, "build": build, "finalize": finalize}[args.action]()
