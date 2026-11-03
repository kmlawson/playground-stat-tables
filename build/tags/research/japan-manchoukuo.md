# Manchoukuo sections: saved TOC vocabulary survey

Date: 2026-10-26. Scope: the **Manchoukuo sections only** of the five saved `japan-manchoukuo-*-toc.json` files. The Japan sections had already been surveyed and were not re-surveyed here. This is a local-text review for step 1 (rule completion before a pilot), not an OCR pass, publication update or table-assignment run.

## Exact source coverage

Every saved heading and subheading in each interval below was reviewed. Attached `k` caption references were also reviewed to check recurring subjects and identify vocabulary gaps. Array positions are zero based and inclusive; the section begins at its level-0 marker and ends immediately before the next level-0 marker. File names, captions and historical category labels are reported as found.

| Saved TOC | JSON array positions | Rows | Level-1 entries | Attached caption references | Following level-0 marker |
| --- | ---: | ---: | ---: | ---: | --- |
| `data/japan-manchoukuo-1934-toc.json` | `/354`–`/508` | 155 | 20 | 179 | SUPPLEMENTS |
| `data/japan-manchoukuo-1936-toc.json` | `/320`–`/975` | 656 | 33 | 277 | SUPPLEMENTS |
| `data/japan-manchoukuo-1938-toc.json` | `/535`–`/1012` | 478 | 33 | 325 | APPENDICES |
| `data/japan-manchoukuo-1939-toc.json` | `/694`–`/1092` | 399 | 28 | 353 | SUPPLEMENT |
| `data/japan-manchoukuo-1940-toc.json` | `/655`–`/1069` | 415 | 30 | 249 | SUPPLEMENT |

Totals: 2,103 saved TOC rows, 144 level-1 entries and 1,383 attached caption references. Level-1 entries include front matter as well as numbered chapters. Caption references are not a verified count of unique, correctly attributed Manchoukuo tables.

Excluded from this review: all earlier Japan sections; subsequent supplements, appendices, indexes, maps and diagram lists outside these intervals; source images and external sites. No image transcription, OCR, Git operation or modification of published data/pages/live tags was performed.

### Attribution caveat

`k` attachments are discovery aids rather than proof of a table’s subject or ownership. In the 1940 TOC, entry `/656` (“I. GEOGRAPHY & GEOLOGY”) includes `p0079_1`, “28. Affiliated Companies of the Nanyo Takushoku K.K. (The South Seas Development Co.)”, alongside `p0079_2`, Manchoukuo government posts. The former caption explicitly concerns the South Seas and must not inherit a Manchoukuo identity from this attachment. Adjacent chapter attachments also include carry-over tables: 1940 `/714` (IMMIGRATION) includes `p0100_1` population by occupation and `p0100_2` population by race; `/744` (DIPLOMACY) includes `p0111_1` publication suppression; `/987` (PRINCIPAL CITIES) includes `p0211_1` narcotic stations. Pilot tagging must read the saved table evidence rather than inherit the nearest heading blindly.

## Main coverage and existing vocabulary

Across the five sections the TOCs cover physical geography and geology; historical and ethnographic accounts; state founding and foreign relations; population, migration and settler schemes; administrative and judicial institutions; national defence and bandit suppression; education and religion; public finance, currency and banking; communications, transportation and railways; agriculture and livestock; commerce, forestry, fisheries, minerals, manufacturing and trade; sanitation and narcotics; labour and living costs; economic policy; and the South Manchuria Railway Company. Kwantung Leased Territory receives its own section in all but 1934, where its statistics are distributed among chapters. The 1936 edition adds substantial Hsingan and Jehol chapters. Exact chapter inventories follow below.

| Evidenced subject | Local evidence | Existing vocabulary and boundary |
| --- | --- | --- |
| Population, households, age, nationality and occupation | 1936 `p1-0722_1`, `p1-0723_1`–`p1-0724_2`; 1938 `p1-0724_1`–`p1-0727_4`; 1939 `p1-0695_1`–`p1-0698_2`; 1940 `p0099_1`–`p0100_2` | `population-totals`, `households`, `age-and-sex`, `nationality-and-ethnicity`, `occupations` cover the observed distinctions. Historical “race” labels remain reported source categories. |
| Migration, permits and sponsored settlement | 1936 `p1-0725_2`–`p1-0725_4`; 1938 `p1-0722_1` and `p1-0728_1`–`p1-0728_3`; 1939 `p1-0699_1`–`p1-0703_1`; 1940 `p0100_3`–`p0102_1` | `migration`, `passports-and-travel-permits`, `settler-migration` and `household-budgets` can be shared across suitable topics. Port passenger totals alone do not demonstrate migration; sponsor-funded settlement does not establish formal colonial jurisdiction. |
| Indigenous and other communities | 1934 Historical Background / Aboriginal Tribes; 1936 Races and Tribes and Hsingan, including `p1-0959_2` Distribution of the Mongol Tribes; 1938/1939/1940 Races and Tribes chapters | Reuse `nationality-and-ethnicity`, `languages`, `local-government`, `administrative-divisions` or the substantive economic/education tag. `frontier-policing` and `guard-lines` require control measures. The `indigenous-peoples` topic is not a synonym for all ethnic minorities or historical peoples. |
| Government personnel, rank, salaries and grants | 1934 `p1-0612_1`; 1936 `p1-0737_1`, `p1-0738_1`–`p1-0738_3`; 1938 `p1-0733_1`–`p1-0734_3`; 1939 `p1-0708_1`–`p1-0709_3`; 1940 `p0105_1`–`p0105_5` | `government-offices`, `honours-and-ranks`, `imperial-household` and shared wages/pensions tags as substantively appropriate. A ministry table is government because its institution is the subject, not simply because it is state-owned. |
| Civil/criminal justice, police, prisons and censorship | 1936 Judicature and `p1-0744_1`/`p1-0745_1`; 1938 `p1-0742_1`–`p1-0746_1`; 1939 `p1-0715_1`–`p1-0720_1`; 1940 `p0109_1`–`p0111_2` | `courts`, `civil-litigation`, `offences-and-convictions`, `police`, `prisons`, `constitutions-and-laws` and shared `censorship`. Do not add `political-policing` without evidence of policing of political activity. |
| Diplomatic service, recognition, treaties, consular jurisdiction and border incidents | 1934 `p2-0026_1`/`p2-0027_1`, Japan-Manchoukuo Protocol and Lytton Commission chapters; 1936 `/462`, `/468` and `/471`–`/477`; 1938 `/663`–`/669`; 1939 `p1-0724_1`/`p1-0725_1`; 1940 `/746`–`/750` | `diplomatic-service`, `treaties`, `international-organisations` and `extraterritoriality` cover the observed institutional/legal subjects. Recognition headings are evidence of diplomatic subject matter, not evidence that an independence movement existed. |
| Army/navy appropriations, gunboats, military organization and mobilisation | 1936 `p1-0753_1`/`p1-0757_1`; 1938 `p1-0754_1`–`p1-0756_1`; 1939 `p1-0726_1`–`p1-0727_1`; 1940 `p0114_1`–`p0115_1` | `army`, `navy`, `war-and-mobilisation`, `military-casualties`, `arms-and-arsenals` and public-budget tags express the observed subject. A ship list containing tonnage or armament measurements is statistical even if names predominate. |
| School types, teacher training, curricula, education finance and Mongolian education | 1936 Education chapter; 1938 `p1-0761_1`–`p1-0770_2`; 1939 `p1-0733_1`–`p1-0744_2`; 1940 `p0119_1`–`p0120_2` | Existing education tags cover these distinctions. A school-budget table may take education + finance; a general budget merely containing an education line remains finance. Japanese-managed schools and language teaching do not by themselves establish an assimilation policy. |
| Religion | 1934 `p2-0148_1`; 1936 `p1-0777_1`; 1938 `p1-0773_1`; 1939 `p1-0745_1`; 1940 Education subheadings include religious subjects | Existing religion-specific tags and `religious-institutions` cover named faiths and establishments. Religious institutions are not automatically charitable institutions. |
| Medical services, infectious disease and sanitation | 1934 `p2-0150_1`–`p2-0151_3`; 1936 `p1-0932_1`–`p1-0935_1`; 1938 `p1-0957_1`–`p1-0963_3`; 1939 `p1-0914_1`–`p1-0920_3`; 1940 `p0208_2`–`p0210_1` | `medical-services`, `diseases`, `public-health`, `maternal-and-child-health` and associated education/personnel tags. Routine contagious-disease totals do not alone warrant `epidemics`. |
| Opium cultivation, lawful sales and certificates | 1938 `p1-0964_1`/`p1-0964_2`; 1939 `p1-0827_1`/`p1-0827_2`, `p1-0921_1`/`p1-0921_2`; 1940 `p0162_2`/`p0162_3` | `opium`, `opium-licensing`, `drug-consumption` and shared agriculture/trade/state-monopoly tags. Licensed cultivation and state sales do not establish illicit trafficking or suppression. |
| Workers’ migration, occupation, hours, wages, family expenditure and disputes | 1938 `p1-0981_1`–`p1-0987_1`; 1939 `p1-0935_1`–`p1-0942_1`; 1940 `p0218_1`–`p0221_4` | Reuse labour tags together with `migration`, `occupations`, `nationality-and-ethnicity` and `household-budgets`. Occupational or nationality breakdowns are substantive when the table measures those populations. |
| Economic policy, industrial plans, foreign capital and railway-company accounts | 1934 `p2-0018_1`, `p2-0085_1`–`p2-0090_1`; 1938 `p1-1008_1`–`p1-1013_1`; 1939 `p1-0956_1`–`p1-0966_1`; 1940 `p0228_1`–`p0231_3` | Existing `economic-planning`, `economic-controls`, `foreign-investment`, `companies`, `railways` and finance tags cover the economic observations. A Japanese investor, company or policy context does not alone justify informal-imperialism. |
| Granaries, fertilizers, commodity detail and mineral inputs | 1936 `p1-0883_1`–`p1-0883_3`; 1938 `p1-0869_1`; 1939 `p1-0828_1`, `p1-0865_1`–`p1-0867_2`; 1940 `p0162_4`, `p0181_2`–`p0184_1` | Existing agriculture/food-supply, mineral-production/reserves, petroleum, chemicals and commodity tags cover these at current granularity. No new society tag is needed simply to mirror every commodity. |

## Evidence-backed vocabulary gaps

No new high-level topic is required by these Manchoukuo sections. Two nonredundant detailed additions are fully defined under `proposed_additions.tags` in `build/tags/definitions/society.json`; they have not been inserted into the shared seed or assigned to tables.

| Proposed detailed ID | Evidence in saved TOCs | Why existing detail is insufficient |
| --- | --- | --- |
| `banditry` | 1936 `p1-0758_1` “No. of Bandits”, `p1-0759_1` “Casualties in Bandit Suppression”; 1938 `p1-0757_1`–`p1-0760_3` cover numbers, activities, groups/raids, surrender, booty, river suppression and railway damage; 1939 `p1-0728_1`–`p1-0729_4` repeat this structure; 1940 `p0115_2`–`p0116_2` repeat it again. | `offences-and-convictions` describes recorded criminal processes, while these tables often enumerate armed groups, raids, military suppression and damage without court outcomes. `war-and-mobilisation` is too broad to distinguish this recurring category. Preserve “bandit” as the source’s category; never infer that resistance or an independence movement was criminal from the source label alone. |
| `addiction-treatment` | 1938 `p1-0965_1` “Number of Addicts Cared For at Narcotic Stations”; 1939 `p1-0922_1` the same caption for 1935; 1940 `p0211_1` “Statistics of Narcotic Stations”. 1939 subheading `/1003` explicitly reads “Relief of Opium Addicts”. | `drug-consumption` captures use and prevalence; `opium-licensing` captures authorization; `drug-suppression` captures prohibition/enforcement; `medical-services` is a broad service category. None expresses the recurring treatment programme and its participants. The proposed term may accompany narcotics and health (and welfare where support is substantive). |

Additional diplomacy, ethnic-community or civil-service terms were considered unnecessary: existing shared detailed tags can accompany the relevant high-level topics. Detailed tags’ `related_topics` are relevance guidance, not an exclusive parent-child taxonomy. No vocabulary-size cap was applied.

## Rules reinforced by this survey

- Assign 1–2 high-level topics and 1–3 detailed tags for the substantive table content. An optional independent `text-tables` flag does not consume a topic or detailed-tag slot.
- Names, offices, appointment dates, years, serial numbers and rank labels alone remain text content. A government-post list, diplomatic roster or sequence of railway-company presidents can therefore be a text table.
- A meaningful count, amount, rate or measurement makes the table statistical, including sparse or uncertain (`[?]`) quantitative observations. Mixed textual/statistical tables are statistical. Counted officials, visa issues, subsidies, budget amounts, gunboat tonnage and hours per week are quantitative observations; a numeric date or rank alone is not.
- Formal colonial administration and foreign control without formal colonial incorporation are distinct. The name Manchoukuo alone warrants neither `colonial-rule` nor `informal-imperialism`. The saved headings “Japanese Cooperation in Administration” and “Japan in Administration of Manchoukuo” can prompt closer reading, but a crop, wage or hospital table needs evidence that the political relationship itself is a substantive subject.
- The Kwantung Leased Territory’s formal administration can be considered under `colonial-rule` when administration is the subject; statistics merely describing life or production there retain their substantive demographic, social or economic topics.
- A source’s racial or ethnographic labels, “independence” claims, “bandits” and “pacification” claims are evidence of its categories and viewpoint. They are not unqualified historical conclusions by the cataloguer.
- Defining a tag is not assigning it. This survey does not create pilot records or change published content.

## Chapter inventory

The following reproduces all level-1 entries within the reviewed intervals. Page values are the saved TOC’s printed-page fields and were not independently checked against source images. This inventory fixes which material the review included even where the TOC contains no attached table captions.

### japan-manchoukuo-1934-toc.json

Section marker: `/354` — MANCHOUKUO.

| Array position | Entry | Saved printed page |
| ---: | --- | --- |
| `/355` | Occupants of leading Manchoukuo Government Posts | 570-571 |
| `/356` | Diagrammatic Chart of Government Organization of Manchoukuo | 570-571 |
| `/357` | Weights, Measures and Moneys | 570-571 |
| `/358` | Chapter I. Geography | 571-573 |
| `/366` | Chapter II. Historical Background | 574-588 |
| `/372` | Chapter III. Establishment of the Manchoukuo Government | 589-596 |
| `/378` | Chapter IV. Industry | 597-625 |
| `/410` | Chapter V. Agriculture | 626-639 |
| `/421` | Chapter VI. Mining | 640-643 |
| `/429` | Chapter VII. Railways | 644-659 |
| `/437` | Chapter VIII. Transportation & Communication | 660-663 |
| `/443` | Chapter IX. Finance | 664-671 |
| `/450` | Chapter X. Currency | 672-682 |
| `/455` | Chapter XI. Banking | 683-690 |
| `/462` | Chapter XII. Foreign Trade | 691-712 |
| `/468` | Chapter XIII. Forestry & Fishery | 713-715 |
| `/474` | Chapter XIV. Educational and Social Enterprises | 716-720 |
| `/481` | Chapter XV. Economic Transformation of Manchuria Vis-A-Vis Foreign Influence | 721-725 |
| `/485` | Chapter XVI. Principal Cities | 726-728 |
| `/504` | Chapter XVII. Observations on the Lytton Commission Report | 729-780 |

### japan-manchoukuo-1936-toc.json

Section marker: `/320` — MANCHOUKUO SECTION.

| Array position | Entry | Saved printed page |
| ---: | --- | --- |
| `/321` | OCCUPANTS OF LEADING MANCHOUKUO GOVERNMENT POSTS (Between) | 608 |
| `/322` | DIAGRAMMATIC CHART OF GOVERNMENT ORGANIZATION OF MANCHOUKUO (Between) | 608 |
| `/323` | WEIGHTS, MEASURES AND MONEYS (Between) | 609 |
| `/324` | I. GEOGRAPHY & GEOLOGY | 609 |
| `/348` | II. HISTORICAL OUTLINE | 625 |
| `/364` | III. RACES AND TRIBES | 640 |
| `/399` | IV. FOUNDING OF MANCHOUKUO | 646 |
| `/406` | V. POPULATION AND IMMIGRATION | 653 |
| `/413` | VI. ADMINISTRATION | 659 |
| `/448` | VII. JUDICATURE | 671 |
| `/467` | VIII. DIPLOMACY | 676 |
| `/478` | IX. NATIONAL DEFENCE | 683 |
| `/492` | X. EDUCATION | 696 |
| `/536` | XI. STATE FINANCE | 707 |
| `/551` | XII. CURRENCY | 716 |
| `/574` | XIII. BANKING | — |
| `/586` | XIV. TRANSPORTATIONS AND COMMUNICATIONS | — |
| `/624` | XV. RAILWAYS | — |
| `/635` | XVI. PURCHASE OF THE N. M. R. | 770 |
| `/654` | XVII. AGRICULTURE | 781 |
| `/699` | XVIII. FORESTRY | 796 |
| `/714` | XIX. FISHERY | 802 |
| `/731` | XX. MINING | 807 |
| `/750` | XXI. INDUSTRIES | 817 |
| `/788` | XXII. FOREIGN TRADE | 844 |
| `/803` | XXIII. SANITATION | 858 |
| `/813` | XXIV. KWANTUNG LEASED TERRITORY | 863 |
| `/826` | XXV. PRINCIPAL CITIES | 868 |
| `/854` | XXVI. HSINGAN (The Mongol Province) | 883 |
| `/909` | XXVII. JEHOL (Gateway to Mongolia) | 906 |
| `/953` | XXVIII. SOUTH MANCHURIA RAILWAY COMPANY | 919 |
| `/970` | XXIX. JAPAN-MANCHOUKUO ECONOMIC RELATIONS | 932 |
| `/975` | XXX. CUSTOM TARIFF | — |

### japan-manchoukuo-1938-toc.json

Section marker: `/535` — MANCHOUKUO SECTION.

| Array position | Entry | Saved printed page |
| ---: | --- | --- |
| `/536` | OCCUPANTS OF LEADING MANCHOUKUO GOVERNMENT POSTS | (Between) 620–621 |
| `/537` | DIAGRAMMATIC CHART OF GOVERNMENT ORGANIZATION OF MANCHOUKUO | (Between) 620–621 |
| `/538` | WEIGHTS, MEASURES AND MONEY | (Between) 620–621 |
| `/539` | I. GEOGRAPHY & GEOLOGY | 621 |
| `/563` | II. HISTORICAL OUTLINE | 637 |
| `/575` | III. RACES AND TRIBES | 646 |
| `/610` | IV. FOUNDING OF MANCHOUKUO | 652 |
| `/617` | V. POPULATION AND IMMIGRATION | 656 |
| `/627` | VI. ADMINISTRATION | 664 |
| `/644` | VII. JUDICATURE | 674 |
| `/662` | VIII. DIPLOMACY | 684 |
| `/670` | IX. NATIONAL DEFENCE | 689 |
| `/682` | X. EDUCATION | 696 |
| `/702` | XI. STATE FINANCE | 710 |
| `/714` | XII. CURRENCY | 719 |
| `/735` | XIII. BANKING | 713 |
| `/747` | XIV. TRANSPORTATION | 750 |
| `/757` | XV. COMMUNICATIONS | 767 |
| `/765` | XVI. RAILWAYS | 776 |
| `/774` | XVII. AGRICULTURE | 786 |
| `/819` | XVIII. COMMERCE | 807 |
| `/835` | XIX. FORESTRY | 818 |
| `/850` | XX. AQUATIC PRODUCTS INDUSTRY | 823 |
| `/860` | XXI. MINING | 829 |
| `/879` | XXII. MANUFACTURING INDUSTRY | 840 |
| `/914` | XXIII. FOREIGN TRADE | 870 |
| `/928` | XXIV. SANITATION | 892 |
| `/938` | XXV. PRINCIPAL CITIES | 901 |
| `/966` | XXVI. LABOR | 916 |
| `/978` | XXVII. SOUTH MANCHURIA RAILWAY COMPANY | 923 |
| `/990` | XXVIII. KWANTUNG LEASED TERRITORY | 932 |
| `/1004` | XXIX. JAPAN-MANCHOUKUO ECONOMIC RELATIONS | 943 |
| `/1012` | XXX. TREATIES, Etc. | 953 |

### japan-manchoukuo-1939-toc.json

Section marker: `/694` — MANCHOUKUO SECTION.

| Array position | Entry | Saved printed page |
| ---: | --- | --- |
| `/695` | I. GEOGRAPHY & GEOLOGY | 599 |
| `/708` | II. OUTLINE OF HISTORY | 617 |
| `/713` | III. RACES AND TRIBES | 626 |
| `/717` | IV. FOUNDING OF MANCHOUKUO | 632 |
| `/725` | V. POPULATION AND IMMIGRATION | 636 |
| `/731` | VI. ADMINISTRATION | 645 |
| `/742` | VII. JUDICATURE | 654 |
| `/753` | VIII. DIPLOMACY | 662 |
| `/761` | IX. NATIONAL DEFENCE | 667 |
| `/768` | X. EDUCATION (AND RELIGION) | 673 |
| `/794` | XI. STATE FINANCE | 689 |
| `/803` | XII. BANKING & CURRENCY | 698 |
| `/830` | XIII. COMMUNICATIONS | 716 |
| `/844` | XIV. TRANSPORTATION | 728 |
| `/865` | XV. RAILWAYS | 743 |
| `/873` | XVI. AGRICULTURE | 753 |
| `/900` | XVII. COMMERCE | 774 |
| `/916` | XVIII. FORESTRY | 786 |
| `/923` | XIX. FISHERIES | 793 |
| `/929` | XX. MINING | 798 |
| `/944` | XXI. MANUFACTURING INDUSTRY | 811 |
| `/983` | XXII. FOREIGN TRADE | 838 |
| `/989` | XXIII. SANITATION | 859 |
| `/1004` | XXIV. PRINCIPAL CITIES | 868 |
| `/1033` | XXV. LABOR | 880 |
| `/1045` | XXVI. THE SOUTH MANCHURIA RAILWAY COMPANY | 888 |
| `/1058` | XXVII. ECONOMIC POLICY | 897 |
| `/1075` | XXVIII. KWANTUNG LEASED TERRITORY | 913 |

### japan-manchoukuo-1940-toc.json

Section marker: `/655` — MANCHOUKUO SECTION.

| Array position | Entry | Saved printed page |
| ---: | --- | --- |
| `/656` | I. GEOGRAPHY & GEOLOGY | 573 |
| `/668` | II. OUTLINE OF HISTORY | 590 |
| `/674` | III. RACES AND TRIBES | 598 |
| `/707` | IV. POPULATION | 604 |
| `/714` | V. IMMIGRATION | 607 |
| `/722` | VI. ADMINISTRATION | 613 |
| `/735` | VII. JUDICATURE | 622 |
| `/744` | VIII. DIPLOMACY | 630 |
| `/751` | IX. NATIONAL DEFENCE | 635 |
| `/761` | X. EDUCATION | 641 |
| `/781` | XI. STATE FINANCE | 652 |
| `/791` | XII. BANKING & CURRENCY | 662 |
| `/808` | XIII. COMMUNICATIONS | 677 |
| `/815` | XIV. TRANSPORTATION | 685 |
| `/827` | XV. RAILWAYS | 701 |
| `/839` | XVI. AGRICULTURE | 710 |
| `/858` | XVII. COMMERCE | 727 |
| `/878` | XVIII. FORESTRY | 742 |
| `/888` | XIX. FISHERIES | 747 |
| `/896` | XX. MINING | 751 |
| `/918` | XXI. MANUFACTURING INDUSTRIES I | 768 |
| `/945` | XXII. MANUFACTURING INDUSTRIES II | 785 |
| `/961` | XXIII. FOREIGN TRADE | 795 |
| `/974` | XXIV. SANITATION | 815 |
| `/987` | XXV. PRINCIPAL CITIES | 822 |
| `/1016` | XXVI. LABOR | 834 |
| `/1029` | XXVII. THE SOUTH MANCHURIA RAILWAY COMPANY | 842 |
| `/1041` | XXVIII. ECONOMIC POLICY | 850 |
| `/1052` | XXIX. KWANTUNG LEASED TERRITORY | 867 |
| `/1067` | XXX. LAWS, TREATIES | 872 |

## Source fingerprints

SHA-256 of the saved TOC bytes read for this survey:

- `japan-manchoukuo-1934-toc.json`: `b39f3f2db1b6e212fc7112aa70ab5ee7d177874f3f1abfb2e7fe21f8e620a211`
- `japan-manchoukuo-1936-toc.json`: `6da2dde9bba506e380a833df73333fd403a280c03d93693e6216d632601519ed`
- `japan-manchoukuo-1938-toc.json`: `81e7ad7dfb2c287b7ec012a2954eea208fbfaeedf65ad2c63b3a6c38c99797dd`
- `japan-manchoukuo-1939-toc.json`: `d9864748ca16ee642c213e0181e6cfce057379e16f61ff84c14ec515182694c2`
- `japan-manchoukuo-1940-toc.json`: `0fad0ff62176babe0a9447941723183e302641a73ded7a8abc39604cb47e5574`
