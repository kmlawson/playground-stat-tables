#!/usr/bin/env python3
"""Build the stat-tables site: a landing page plus one table browser per book.

For each book in BOOKS, reads <book dir>/_work/tables/*.json and writes
<slug>/index.html (self-contained) and data/<slug>.json. Books without tables yet are listed
as "in progress" on the landing page. Scan links point to the online scan where one exists.
"""
import json, glob, os, re, html, datetime, sys
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]")  # never italicise Asian text (user, 2026-10-22)
from pathlib import Path

SCRIPTS = os.path.dirname(os.path.abspath(__file__))  # build/: scripts, leaf maps, docs (not deployed)


def version_line():
    """'Version 1 update N · last updated DD Month YYYY, HH:MM' from build/VERSION.json (see build/bump_version.py)."""
    import datetime
    f = os.path.join(SCRIPTS, "VERSION.json")
    if not os.path.exists(f):
        return ""
    v = json.load(open(f))
    t = datetime.datetime.strptime(v["updated"], "%Y-%m-%dT%H:%M%z")
    return f'Version {v["major"]} update {v["update"]} · last updated {t.strftime("%d %B %Y, %H:%M")}'
HERE = os.path.dirname(SCRIPTS)  # site root: everything here except build/, CLAUDE.md and .git is deployed
# Folder holding the book folders. A worktree placed elsewhere (e.g. the far-east-1941 branch)
# must set STAT_TABLES_ROOT to the Manchoukuo folder, or relative book dirs resolve wrongly.
ROOT = os.environ.get("STAT_TABLES_ROOT") or os.path.dirname(HERE)

BOOKS = [
    {"slug": "japan-directory-1884", "dir": "Japan_Directory_1884", "model": "GPT-6.1 Sol (most pages) and Gemini 3.8 Flash",
     "title": "The Japan Directory 1884", "subtitle": "The Japan Directory for the Year 1884",
     "publisher": "Printed and published at the office of the \"Japan Gazette\", Yokohama, January 1884",
     "blurb": "The Japan Gazette's annual directory of the foreign community and of the Japanese government for 1884. A front appendix gives the reigning family and a chronological list of the emperors, a calendar for 1884 with Yokohama high water, phases of the moon, daily anniversaries and three years of exchange rates, the British government, and tables of latitude and longitude, area, land classification, agricultural products, administrative divisions, population, vital statistics, climate, distances, measures, foreign moneys, life assurance and annuities. The directory proper lists, port by port (Yokohama with the Bluff, Tokio, Hiogo (Kobe), Osaka, Kioto, Nagasaki, Hakodate, Niigata, and the Corean ports of Yuen-san and Fusan), the diplomatic and consular bodies, the Japanese government offices and their officials, customs, post and telegraphs, foreign naval squadrons, banks, insurance agencies, clubs, churches and missions, and the foreign and principal Japanese firms with their staff; an alphabetical list of the foreign residents of Japan and Corea follows. Back appendices give the Penal Code and Code of Criminal Procedure, the Tariff Convention of 1866 with the import and export tariffs, bonded warehouse regulations, treaties with China and Corea and the Corean customs tariff.",
     "source": "LLM-transcribed from the National Diet Library scan (public domain).",
     "gaps": "All tables and directory lists are transcribed: the front appendix tables (including the twelve calendar months), every port directory, the alphabetical list of residents, the Mitsu Bishi and Kiodo Unyu fleet lists and timetables, and the import, export, storage and Corean tariffs. The running text is not: the Penal Code, the Code of Criminal Procedure, treaties, conventions and regulations, the prose on the imperial family and on the Corean ports, the code of signals and house flags, and the advertisements. Pages were found from contact sheets; each two-page spread was read once, from whole-page and half-page images, by GPT-6.1 Sol (Codex) or, for about a fifth of the spreads, by Gemini 3.8 Flash (Antigravity), with no checking by eye; the reader of each spread is not marked. The two models group directory entries slightly differently (one entry per person or one per office). Unreadable figures or words are marked [?]. Several pages of the alphabetical list are bound out of order in this copy; entries keep the printed page numbers. The table of foreign moneys (p. 25 of the appendix) is printed sideways and was turned upright before reading.",
     "scan": "https://dl.ndl.go.jp/pid/2937065/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/2937065",
     "blank_marking": True},
    {"slug": "japan-tokyo-trade-1940", "dir": "Tokyo_Trade_Directory_1940", "model": "GPT-6.1 Sol (firms), Gemini 3.8 Flash (index) and Claude Sonnet 5.5",
     "title": "Trade Directory of Tokyo 1940", "subtitle": "東京貿易業者名鑑 (Tokyo Commercial & Industrial Museum)",
     "publisher": "Tokyo Commercial & Industrial Museum (府立東京商工奨勵館), Tokyo, December 1939",
     "blurb": "A bilingual directory of the Tokyo firms engaged in export and import, compiled by the prefectural Tokyo Commercial and Industrial Museum for foreign buyers. Its 1,305 numbered firm entries (pp. 1–218, with a supplement) give each firm's name and address in English and in Japanese, its kind of business (manufacturers, traders), cable address, telegraph codes and bankers, and what it exports and imports, usually with the countries traded with. An alphabetical index of articles, separately for exports and imports, lists the firm numbers dealing in each commodity, from abrasives to zip fasteners.",
     "source": "LLM-transcribed from the National Diet Library scan (public domain).",
     "gaps": "The firm entries and the index of articles are transcribed; the foreword, the description of the museum and the alphabetical index of firms (which only repeats names and numbers) are not. Each two-page spread was read once: the firm entries by GPT-6.1 Sol (Codex), the index of articles by Gemini 3.8 Flash (Antigravity), with no checking by eye. Japanese characters the first reader could not make out (about 6% of firms had one) were re-read by Claude Sonnet 5.5 from the page image, which filled all but one; a reading was accepted only if it changed nothing but the unreadable characters. Japanese names and addresses keep the old character forms as printed. Firm numbers are as printed, including the book's own gaps in the numbering (e.g. nos. 516 and 798); the index of articles also cites nos. 798 and 1313, which have no entry in the directory. Firm numbers in the index link to the firm's entry.",
     "scan": "https://dl.ndl.go.jp/pid/1036387/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1036387",
     "dir_only": True, "dir_index": "Index of Articles", "blank_marking": True},
    {"slug": "japan-railways-1931", "dir": "Railways_Annual_Report_1931", "model": "GPT-6.1 Sol and Gemini 3.8 Flash",
     "title": "Department of Railways Annual Report 1931", "subtitle": "Annual Report for the Year Ending March 31st, 1931 (English edition)",
     "publisher": "Department of Railways, Government of Japan, Tokyo, 1931",
     "blurb": "The Japanese Department of Railways' English-language report on the State Railways for the fiscal year 1930–31: general regime, organization and staff, finance and the financial result of working, traffic and improvements in traffic service, transport, the railway steamers and hotels, accidents, construction, open-line improvement, maintenance, rolling stock, workshops, electricity, research, training, medical treatment, the relief association and the railway workers' committee, with nineteen statistical tables (staff and pay, capital, revenue, coaching and goods traffic by region, principal commodities hauled, season and party tickets, shipping, safety arrangements, accidents, locomotive, coaching and wagon stock, railway hospitals, physical examinations, mortality and casualties of employees). Section II covers the local railways and tramways of Japan proper; an appendix reports on the railways of Chosen, Taiwan, South Karafuto and the South Manchuria Railway; closing tables trace the progress of the State Railways year by year since 1872.",
     "source": "LLM-transcribed from the National Diet Library scan (public domain).",
     "gaps": "All tables are transcribed, including the small tables in the text of each chapter; the running text, photographs, the organisation chart, the eleven diagrams (graphs) and the folding railway map are not. Pages were found from contact sheets; tables printed sideways were turned upright before reading. Each two-page spread was read once, from whole-page and half-page images, by GPT-6.1 Sol (Codex) or Gemini 3.8 Flash (Antigravity), with no checking by eye; the readers re-added printed totals and noted those that do not reconcile. Long tables continued over several spreads appear as separate parts marked continued. Only one cell could not be read.",
     "scan": "https://dl.ndl.go.jp/pid/1678089/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1678089",
     "blank_marking": True},
    {"slug": "japan-commercial-1900", "dir": "Commercial_Japan_1900", "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "title": "Commercial Japan in 1900", "subtitle": "Area, population, production, railways, telegraphs, transportation routes, foreign commerce, and commerce of the United States with Japan",
     "publisher": "U.S. Treasury Department, Bureau of Statistics (Summary of Commerce and Finance, December 1901), Washington, 1901",
     "blurb": "A U.S. government survey of Japan as a market, compiled by the Treasury's Bureau of Statistics under O. P. Austin. It opens with a review of Japan's commerce, finance, industry, transport and education, followed by a history of Japanese commerce from the earliest times (with tables on industry, factories, wages, trade and shipping), an account of the adoption of the gold standard in 1897 with the Finance Minister's report, consular reports on commercial conditions and American trade prospects, the Japanese weights and measures, and the customs import tariff of 1899 in full. A statistical appendix gives Japan's foreign commerce 1881–1900 and the share of the United States and Britain, U.S.–Japan trade by article and customs district, imports by article and country, trade by port, shipping, foreigners in Japan, population and cities, crops, manufactures, wages, prices, mining, post, telegraphs and telephones, banks, companies, insurance, schools, the budget and the public debt.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive scan (Cornell University Library copy).",
     "gaps": "Pages with tables were found from contact sheets; no table is printed sideways. Each page was read once, from full-resolution crops, by Claude Haiku 5.5 (text pages with small tables) or Claude Sonnet 5.5 (the large tables, the tariff and the statistical appendix, each read in three bands), and not checked by eye. Unreadable figures are marked [?]; tables continued over pages are joined where the columns match. Only tables are transcribed; the running text and the regulations are not. The scan repeats printed pp. 2224–2225 (leaves 17–19); they were read once.",
     "scan": "https://archive.org/details/cu31924023453818/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/cu31924023453818",
     "blank_marking": True},
    {"slug": "japan-sanitary-1877", "dir": "Japan_Sanitary_Bureau_1877", "model": "Claude Sonnet 5.5",
     "title": "Central Sanitary Bureau Report on Cholera 1877", "subtitle": "Report of the Director of the Central Sanitary Bureau to H.E. the Minister of the Home Department on Choleraic Diseases in Japan during the 10th Year of Meiji (1877)",
     "publisher": "Central Sanitary Bureau, Home Department, Tokyo, 1877",
     "blurb": "Nagayo Sensai's English-language report on the cholera epidemic of 1877, the first nationwide epidemic handled by the new Central Sanitary Bureau: a short history of cholera in Japan, the course of the epidemic in Yokohama, Nagasaki, Tokyo, Osaka, Kobe, Kagoshima, Kyoto and other ports and prefectures, the army and navy and the Mitsu Bishi steamers, the measures taken (quarantine, disinfection, isolation hospitals), and the government notifications. Its appendix table gives cases, deaths and rates per 10,000 inhabitants in each fu and ken for the last four months of the year.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive scan (Countway Library of Medicine copy).",
     "gaps": "The single appendix table is transcribed (read once by Claude Sonnet 5.5, not checked by eye; its printed totals, 13,710 attacked and 7,967 dead, agree with the text). The running text and the government notifications are not transcribed.",
     "scan": "https://archive.org/details/reportofdirector00toky/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/reportofdirector00toky", "blank_marking": True},
    {"slug": "japan-sanitary-institutions-1898", "dir": "Japan_Sanitary_Institutions_1898", "model": "GPT-6.1-Sol (Codex)",
     "title": "Sanitary Institutions of the Imperial Government of Japan 1898",
     "publisher": "Central Sanitary Bureau, Home Department, Tokyo (printed by the Yokohama Bunsha), 1898",
     "blurb": "An English account, prepared by the Central Sanitary Bureau, of the sanitary institutions of Meiji Japan as they stood in 1898: the organization of the sanitary administration and the 1874 medical regulations (medical schools, teachers, physicians, apothecaries), the Central Sanitary Bureau, the Hygienic Laboratories, the Tokyo Medicine Manufactory, the botanical garden of medical plants, the Sanitary Museum, the Central Board of Health, the Serum Institute, the Vaccine Farm, the Institute for Infectious Diseases and local sanitary administration; the prevention of infectious diseases and the epidemic regulations; vaccination; public health (syphilis examination, patent medicines, foods and dyes, burial, cleansing, water works and sewerage, industrial health); and the medical professions, licensing, the supervision of medicines, opium and hospitals. Its few tables give laboratory examination fees, serum and opium prices and the staffing of epidemic hospitals.",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol via the Codex CLI) from the Internet Archive scan (Wellcome Library copy).",
     "gaps": "Every page was read once by GPT-6.1-Sol (low reasoning effort) from full-resolution crops, six pages per job, and not checked by eye; unreadable figures are marked [?]. Only tables are transcribed; the running text (most of the book) is not.",
     "scan": "https://archive.org/details/b28717855/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/b28717855", "blank_marking": True},
    {"slug": "japan-20th-century-1904", "dir": "Japan_20th_Century_1904", "model": "GPT-6.1-Sol (Codex); hard pages GPT-6-Astra",
     "title": "Japan in the Beginning of the 20th Century 1904",
     "publisher": "Department of Agriculture and Commerce, Tokyo, 1904",
     "blurb": "A survey of Meiji Japan compiled by the Department of Agriculture and Commerce, with material from the other ministries, for the Louisiana Purchase Exposition at St. Louis (1904). Its eight parts cover geography, population, the administrative system and land tenure; agriculture, forestry, mining and fishery; manufacturing industry, industrial education and industrial property; foreign trade; national and local finance, loans, currency, the money market, banks and clearing houses; the army and navy; post, telegraph, telephone, railways and shipping; and education, with a supplement on Formosa. The several hundred tables give production, trade, finance and institutional statistics, mostly for the 1890s to 1902.",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol and GPT-6-Astra via the Codex CLI) from the Internet Archive scan (Cornell University Library copy).",
     "gaps": "Every page was read once by GPT-6.1-Sol (low reasoning effort) from full-resolution crops; the 63 pages with dense or difficult tables were read again by GPT-6-Astra (low effort) and that second reading is used. Nothing was checked by eye; unreadable figures are marked [?]. Only tables are transcribed; the running text (most of the book) is not.",
     "scan": "https://archive.org/details/cu31924023438587/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/cu31924023438587", "blank_marking": True},
    {"slug": "japan-industrial-labour-1933", "dir": "Industrial_Labour_Japan_1933", "model": "GPT-6.1-Sol (Codex)",
     "title": "Industrial Labour in Japan 1933",
     "subtitle": "International Labour Office, Studies and Reports, Series A (Industrial Relations), No. 37",
     "publisher": "International Labour Office (League of Nations), Geneva, 1933; P. S. King & Son, London",
     "blurb": "The International Labour Office's survey of industrial labour in Japan at the end of the 1920s, in six parts: the land and people, the rise of industrialism and the economic structure; industrial relations, employers' organisations, trade unionism and conciliation; labour legislation and administration; conditions of work (recruitment and discharge, hours and night work, wages and the cost of living, accidents and compensation, health and safety, social insurance); unemployment and migration; and welfare, workers' education and co-operation. Its 106 numbered statistical tables, mostly compiled from Japanese official statistics for about 1909 to 1931, cover factories and operatives, labour disputes, trade unions, wages and family budgets, hours, accidents, morbidity, health insurance, employment exchanges, emigration, technical education and co-operative societies.",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol via the Codex CLI) from the Internet Archive scan (Digital Library of India copy, Allahabad University Library).",
     "gaps": "Every page was surveyed on contact sheets and the 122 pages with tables were read once by GPT-6.1-Sol (low reasoning effort) from 360-dpi crops; the six tables printed sideways were turned upright before reading. All 106 numbered tables and 28 unnumbered ones are transcribed; the running text (most of the book) is not. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?]. The scan appears to lack printed page 294.",
     "scan": "https://archive.org/details/in.ernet.dli.2015.229044/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/in.ernet.dli.2015.229044", "blank_marking": True},
    {"slug": "japan-ussbs-urban-economy-1947", "dir": "USSBS_Urban_Economy_1947", "model": "Gemini 4 Argon and Gemini 3.8 Flash (agy)",
     "title": "The Effects of Air Attack on Japanese Urban Economy 1947",
     "subtitle": "United States Strategic Bombing Survey, Urban Areas Division — Summary Report",
     "publisher": "United States Strategic Bombing Survey, Washington, March 1947",
     "blurb": "The Strategic Bombing Survey's summary of how the air attack affected the economy of Japan's cities: the concentration of industry in the urban areas, production in plants hit and not hit, the loss of labour time and of productive hours, the decline of output in individual industries and cities, and pre-raid and post-raid data for the bombed urban areas. Its 30 tables give figures by industry and by city, mostly for 1944 and 1945.",
     "source": "LLM-transcribed (Google Gemini 4 Argon and Gemini 3.8 Flash via the Antigravity CLI) from the Internet Archive scan.",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the pages with tables were read once: by Gemini 4 Argon (low) where the tables are dense or printed sideways, by Gemini 3.8 Flash otherwise. The seven sideways pages were turned upright before reading. All 30 numbered tables and 3 unnumbered ones are transcribed; the running text and the graphs are not. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?].",
     "scan": "https://archive.org/details/effectsofairatta55unit/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/effectsofairatta55unit", "blank_marking": True},
    {"slug": "japan-military-industries-1922", "author": "KOBAYASHI Ushisaburō", "dir": "Military_Industries_Japan_1922", "model": "Gemini 4 Argon and Gemini 3.8 Flash (agy)",
     "title": "Military Industries of Japan 1922",
     "subtitle": "Ushisaburō Kobayashi — Japanese Monographs, ed. Baron Y. Sakatani; Carnegie Endowment for International Peace, Division of Economics and History",
     "publisher": "Oxford University Press, American Branch, New York, 1922",
     "blurb": "A Carnegie Endowment monograph on Japan's military industries from the Tokugawa period to about 1920: the historical survey of the army and navy arsenals, dockyards and military factories before and after the Russo-Japanese War, their organisation, output, workers and wages, and the economic effects of military industry on Japanese industry and finance. Its tables, most of them small ones set in the text, give arsenal capital, expenditure and revenue, production of arms, munitions, cloth and ships, workmen and wages, and imports of metals.",
     "source": "LLM-transcribed (Google Gemini 4 Argon and Gemini 3.8 Flash via the Antigravity CLI) from the Internet Archive scan.",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the pages with tables were read once: by Gemini 4 Argon (low) where the tables are dense or printed sideways, by Gemini 3.8 Flash otherwise. The eleven sideways pages were turned upright before reading. The book does not number its tables; all 82 are transcribed (sub-tables printed under one heading are parts of one table). The running text is not transcribed. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?].",
     "scan": "https://archive.org/details/militaryindustri0000ushi/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/militaryindustri0000ushi", "blank_marking": True},
    {"slug": "japan-ussbs-war-economy-1946", "dir": "USSBS_War_Economy_1946", "model": "Gemini 4 Argon, Gemini 3.8 Flash (agy) and GPT-6-Astra (Codex)",
     "title": "The Effects of Strategic Bombing on Japan's War Economy 1946",
     "subtitle": "United States Strategic Bombing Survey, Over-all Economic Effects Division — with Appendixes A, B, C",
     "publisher": "United States Strategic Bombing Survey, Washington, December 1946 (Government Printing Office)",
     "blurb": "The Strategic Bombing Survey's over-all report on the Japanese war economy: the road to Pearl Harbor, the economy under the stress of war, the air attack and its effects, the surrender and a postscript on target selection, followed by appendixes on Allied economic intelligence, Japan's gross national product, and a long statistical appendix compiled from Japanese records. Its 259 numbered tables cover national product and war expenditure, labour, raw materials, coal, iron and steel, light metals, chemicals, oil, electric power, munitions, aircraft and shipbuilding, shipping and rail transport, food, prices and finance, mostly by month or fiscal year from the 1930s to 1945.",
     "source": "LLM-transcribed (Google Gemini 4 Argon and Gemini 3.8 Flash via the Antigravity CLI, and OpenAI GPT-6-Astra via the Codex CLI) from the Internet Archive scan (Boston Public Library copy).",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the 182 pages with tables were read once: by Gemini 4 Argon (low) where the tables are dense or printed sideways, by Gemini 3.8 Flash otherwise, and the last twelve batches by GPT-6-Astra (low). The 25 sideways pages were turned upright before reading. All numbered tables (1–28, A-1–A-11, B-1–B-15, C-1–C-205) and 8 unnumbered ones are transcribed; the running text is not. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?].",
     "scan": "https://archive.org/details/effectsofstrateg53unit/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/effectsofstrateg53unit", "blank_marking": True},
    {"slug": "japan-population-pressure-1937", "author": "ISHII Ryoichi", "dir": "Population_Pressure_Japan_1937", "model": "GPT-6.1-Sol (Codex)",
     "title": "Population Pressure and Economic Life in Japan 1937",
     "subtitle": "Ryoichi Ishii, Ph.D. (石井了一)",
     "publisher": "P. S. King & Son, London, 1937",
     "blurb": "A study of Japan's population problem from the Tokugawa era to the 1930s: the trend of population before 1868, the economic effects of the Meiji reformation, population policies and methods of estimating the population, regional and occupational distribution, a demographic analysis of births, deaths, marriage and survival with projections to 1960, the rural economic situation, food supply, colonization and emigration, industrialization, and birth control. Its 101 numbered tables and many footnote tables cover population and density, occupations, prefectures and cities, vital statistics, rice supply and consumption, agricultural production, the Japanese in the colonies and abroad, and industrial growth, mostly from Japanese official statistics up to about 1935.",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol via the Codex CLI) from the Internet Archive scan (Digital Library of India copy).",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the 120 pages with tables were read once by GPT-6.1-Sol (low reasoning effort) from 360-dpi crops; the seven tables printed sideways were turned upright before reading. All 101 numbered tables and 35 unnumbered ones (most of them in footnotes) are transcribed; the running text is not. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?].",
     "scan": "https://archive.org/details/in.ernet.dli.2015.90303/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/in.ernet.dli.2015.90303", "blank_marking": True},
    {"slug": "japan-labor-conditions-1928", "author": "HARADA Shuichi", "dir": "Labor_Conditions_Japan_1928", "model": "Gemini 3.8 Flash (agy)",
     "title": "Labor Conditions in Japan 1928",
     "subtitle": "Shuichi Harada, Ph.D.",
     "publisher": "Columbia University Press, New York; P. S. King & Son, London, 1928",
     "blurb": "A Columbia doctoral study of Japanese industrial labour in the 1920s, in two parts: the economic background (the transition from feudalism to capitalism, raw materials, industrial capital, industrial organisation and marketing, the agrarian movement and food problem, population and labour) and industrial relations (a survey of labour conditions, wages and the cost of living, hours of work, the labour movement, employers and employees, and the government's attitude toward labour). Its 36 numbered tables and a dozen smaller ones, compiled from Japanese official statistics, cover imports of raw materials, capital, factories and workers by size and industry, child and women workers, dormitories, wages, prices, hours, disputes and unions.",
     "source": "LLM-transcribed (Google Gemini 3.8 Flash via the Antigravity CLI) from the Internet Archive scan (Mills College Library copy).",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the 50 pages with tables were read once by Gemini 3.8 Flash from page crops; the one table printed sideways was turned upright before reading. All 36 numbered tables and 14 unnumbered ones are transcribed; the running text is not. Two fold-out tables (XXI and XXVII) are cut off at the right edge in the scan, so their last columns are missing. Nothing was checked by eye apart from spot checks; unreadable figures are marked [?].",
     "scan": "https://archive.org/details/laborconditionsi0000unse_l4j9/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/laborconditionsi0000unse_l4j9", "blank_marking": True},
    {"slug": "japan-hotels-1935", "dir": "Hotels_in_Japan_1935", "model": "GPT-6.1-Sol (Codex)", "dir_first": True,
     "title": "Hotels in Japan 1935",
     "publisher": "Japanese Government Railways, Tokyo, c. 1935",
     "blurb": "An illustrated English guide to the foreign-style hotels of Japan and its empire, issued by the Japanese Government Railways for foreign visitors. Hotel by hotel, from Tokyo, Yokohama, Hakone, Nikkō, Karuizawa, Kyoto, Osaka and Kobe to Unzen, Beppu, Hokkaido, Taiwan, Korea, the Kwantung Leased Territory and Manchukuo, it gives the address, access, cable address, telephone, management, number of rooms, capacity, room and meal charges, and a description of each house (an asterisk marks members of the Japan Hotel Association), followed by hints for visitors to Japanese inns and the offices of the Board of Tourist Industry and the Japan Tourist Bureau. Undated; the Internet Archive item dates it to the first half of 1935 (it mentions the Biwako Hotel, completed in November 1934, and the coming summer season of 1935).",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol via the Codex CLI) from the Internet Archive scan.",
     "gaps": "Every spread with hotel entries or lists was read once by GPT-6.1-Sol (low reasoning effort) from four crops per spread. Each hotel is given twice: as a directory entry with every printed field and its description verbatim, and as a row of the hotels table for its spread. The cover, preface, index and map are not transcribed. Nothing was checked by eye apart from spot checks; unreadable words are marked [illegible] or [?].",
     "scan": "https://archive.org/details/hotels-in-japan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/hotels-in-japan", "blank_marking": True},
    {"slug": "japan-coupon-ryokan-1936", "dir": "Coupon_Ryokan_1936", "model": "Claude Opus 5.5",
     "title": "クーポン旅館一覧 1936",
     "subtitle": "Kūpon ryokan ichiran (List of Coupon Ryokan), 昭和十一年十一月 (November 1936)",
     "publisher": "社團法人ジャパン・ツーリスト・ビューロー（日本旅行協會）, 東京 (昭和十一年)",
     "blurb": "A pamphlet of the Japan Tourist Bureau listing the ryokan (Japanese inns) that accepted its accommodation coupons, prefecture by prefecture: the six great cities, Karafuto and Hokkaidō, every prefecture of Japan proper, and Taiwan, Korea, Manchuria and North China. Each entry gives the place, the inn, the rate per night with two meals, the telephone exchange and number, and the location; a mark ※ points to a short transport guide at the back. The pamphlet also lists the Bureau's head office, branches and inquiry offices, and explains how to buy and use the coupons.",
     "source": "LLM-transcribed from the Internet Archive scan (photographs of the pamphlet).",
     "gaps": "All ryokan listings (50 tables, one per prefecture or territory as printed), the Bureau's offices, the transport guide (one row per place) and the colophon are transcribed; the prose on buying and using coupons and the reply forms are not. The column headings printed on p. 6 are used for every listing, as the pamphlet does not repeat them. The telephone numbers are printed in very small stacked kanji numerals; those that could not be read with confidence are marked [?]. Read by Claude Opus agents, one spread per mission; not checked by a second reader.",
     "scan": "https://archive.org/details/20220423_20220423_1107/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/20220423_20220423_1107", "blank_marking": True, "kanji_full": "cells"},
    {"slug": "japan-sanitary-1907-08", "dir": "Japan_Sanitary_Bureau_1907", "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "title": "Annual Report of the Central Sanitary Bureau 1907-08", "subtitle": "The Annual Report of the Central Sanitary Bureau of the Department for Home Affairs of the Imperial Japanese Government for the 40th and 41st Years of Meiji",
     "publisher": "Central Sanitary Bureau, Department for Home Affairs, Tokyo, 1910",
     "blurb": "The Home Ministry's public-health report for 1907 and 1908, in English with bilingual (Japanese and English) statistical tables. The report covers the bureau and its hygienic laboratories, the Institute for Infectious Diseases and the Central Board of Health; the supervision of food and drink, water-works, sewerage, sweeping and cleaning, slaughter-houses, infectious and contagious diseases (cholera, dysentery, typhoid, smallpox, diphtheria, scarlet fever, plague), port quarantine, vaccination, insane persons, poisoning, the health examination of prostitutes and the prevention of leprosy; physicians, pharmacists, midwives, drugs and patent medicines; and population, marriages, births and deaths with international comparisons. The 127 appended statistical tables give most of these by prefecture and month for each of the two years, many with ten-year series.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive (Google Books, University of Michigan) scan.",
     "gaps": "All tables are transcribed: the small tables in the English text and the 127 numbered statistical tables (most printed once for 1907 and once for 1908, often across two facing pages, which were read as one table). Titles, headings and row labels are given in the English printed beside the Japanese. The Japanese version of the report bound at the back of the volume, whose tables duplicate the bilingual ones, and the running text are not transcribed. Each page or spread was read once by Claude Haiku 5.5 (text pages) or Claude Sonnet 5.5 (statistical tables) through the llm CLI, with no check by eye; three pages whose first reading was malformed were re-read by Sonnet. Unreadable figures are marked [?]. Although catalogued as a run of reports from 1878, this scan holds the 1907–08 report only.",
     "scan": "https://archive.org/details/bub_gb_kpJNAAAAMAAJ/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_kpJNAAAAMAAJ", "blank_marking": True},
    {"slug": "taiwan-aborigines-1911", "dir": "Formosa_Aborigines_1911", "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "title": "Report on the Control of the Aborigines in Formosa 1911",
     "publisher": "Bureau of Aboriginal Affairs, Government of Formosa, Taihoku, 1911",
     "blurb": "The Government-General's English-language account of its 'control of the savages' to November 1909: the nine aboriginal groups recognized at the time (Taiyal, Saisett, Bunun, Tsuou, Tsarisen, Paiwan, Piyuma, Ami and Yami), the history of Chinese and Japanese policy, the aiyu-sen (guard-line) and its guardsmen, the advance of the guard-line by conciliation and by force, and eleven punitive expeditions and campaigns from 1897 to 1909, illustrated with over a hundred photographs and maps. Its tables give aboriginal villages and population by prefecture and group, police stations and schools for aboriginal children, the advance of the guard-line 1903–09, and damage inflicted by the aborigines 1896–1909, with diagrams of population, the length of the guard-line and casualties.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive scan (Cornell University Library, Wason Collection).",
     "gaps": "The four tables and the figures printed on the three diagrams are transcribed; the running text, the photographs and the maps are not. Tables I and II are printed sideways and were turned upright before reading. Each page was read once by Claude Sonnet 5.5 (tables) or Haiku 5.5 (diagrams and text pages) through the llm CLI, with no check by eye; the printed population totals of Table I agree with the diagram. The report's terms ('savages', 'barbarous') are those of the colonial government and are kept as printed.",
     "scan": "https://archive.org/details/cu31924023511185/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/cu31924023511185", "blank_marking": True},
    {"slug": "korea-education-1920", "dir": "Chosen_Education_Manual_1920", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Manual of Education in Chosen 1920",
     "publisher": "Bureau of Education, Government-General of Chosen, Seoul, 1920",
     "blurb": "The Government-General's English outline of the history and condition of education in colonial Korea, with statistics to the end of May 1918. Volume I covers the education of Koreans: education before and after annexation, the Chosen Educational Ordinance of 1911, common schools, high schools and girls' high schools, industrial, agricultural and commercial schools, special schools, private and mission schools, sohtang (village schools of Chinese classics), text books, Koreans studying in Japan, the Keigaku-in and educational expenditure; Volume II the schools for Japanese in Chosen (primary schools, kindergartens, middle, girls' high and commercial schools); Volume III administration, teachers' meetings and examinations. Its tables give schools, classes, teachers, pupils and expenditure by province and type of school for 1912–1918, and the appendix of ordinances and regulations includes the curricula (subjects and weekly hours) of each kind of school.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive (Google Books, University of California) scan.",
     "gaps": "Each page was read once by Claude Haiku 5.5 through the llm CLI from full-resolution crops, with no check by eye; pages with sideways tables were turned upright and read by Claude Sonnet 5.5, as were two pages whose first reading was malformed. Unreadable figures are marked [?]. Only tables are transcribed; the running text and photographs are not. Several fold-out tables were scanned folded, so only their left-hand columns appear (e.g. the provincial table of industrial schools, p. 71, the private schools table, p. 92, and the appendix to the expenditure table): those columns are transcribed and the rest is missing. The scan repeats printed p. 69 (read once).",
     "scan": "https://archive.org/details/manualeducation00gakugoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/manualeducation00gakugoog", "blank_marking": True},
    {"slug": "taiwan-education-1908", "author": "Julean H. Arnold", "dir": "Formosa_Education_1908", "model": "Claude Haiku 5.5",
     "title": "Education in Formosa 1908", "subtitle": "By Julean H. Arnold. U.S. Bureau of Education Bulletin, 1908, No. 5",
     "publisher": "U.S. Bureau of Education, Washington, 1908",
     "blurb": "An American consular officer's account of education in Taiwan, from the Chinese period (public, private and quasi-public schools and the schools for aborigines under the Qing) to the Japanese system after 1895: the public schools for Chinese, the language school and its normal and academic departments, the schools for Japanese children, the medical, industrial and agricultural schools, the middle school, the schools for aborigines, and educational finance. Its tables give the schools of the Chinese period, the population and children of school age in 1905, school attendance, study schedules (hours per week by subject and year) for each kind of school, school expenditure, and school statistics for 1900–1906.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive scan.",
     "gaps": "Each page was read once by Claude Haiku 5.5 through the llm CLI from full-resolution crops, with no check by eye. Unreadable figures are marked [?]. Only tables are transcribed; the running text and photographs are not.",
     "scan": "https://archive.org/details/educationinformo00arno/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/educationinformo00arno", "blank_marking": True},
    {"slug": "japan-education-1891", "dir": "Mombusho_1891", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1891",
     "subtitle": "Nineteenth Annual Report of the Minister of State for Education, for the Twenty-fourth Year of Meiji (1891)",
     "publisher": "Department of Education (Mombushō), Tokyo, 1893",
     "blurb": "The English edition of the Mombushō's annual report for 1891, the year after the Imperial Rescript on Education and the revised Elementary School Ordinance. Part I covers the business of the Department (elementary, normal and middle schools, school officials, text-books, expenditure); Part II the educational report proper: a general summary, elementary schools, kindergartens, normal and middle schools, higher female schools, the Imperial University, special and technical schools, schools for the blind and dumb, libraries, the Academy, teachers, text-books, students abroad and public school finance. Part III is a statistical summary of 35 tables by Fu and Ken: school districts and population, children of school age attending and not attending school, elementary schools, teachers and pupils, graduates, kindergartens, normal, middle, higher female, special and miscellaneous schools, the income and expenditure of public schools of each kind, school property, voluntary contributions, teachers' salaries, and the condition of education in each province.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections and the first half of the statistics) or a Claude Sonnet 5.5 agent (the dense statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Most statistical tables are printed across two facing pages and are given here as two tables (left and right halves); right halves carry the row labels of the facing page. Only tables are transcribed; the running text is not. The scan repeats printed pp. 144–145 (read once).",
     "scan": "https://archive.org/details/annualreportmin03monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin03monbgoog", "blank_marking": True},
    {"slug": "japan-education-1895", "dir": "Mombusho_1895", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1895",
     "subtitle": "Twenty-third Annual Report of the Minister of State for Education, for the Twenty-eighth Year of Meiji (1895)",
     "publisher": "Department of Education (Mombushō), Tokyo, 1897",
     "blurb": "The English edition of the Mombushō's annual report for 1895, the year of the Sino-Japanese War. Part I sketches the business of the Department and its officials and expenditure; Part II reports on elementary schools, apprentices' schools, supplementary technical schools, schools for the blind and dumb, kindergartens, normal, middle and higher schools, higher female schools, the Imperial University, special, technical and miscellaneous schools, libraries, teachers' licences, foreign instructors, school inspectors and committees, the Tokyo Academy, the Earthquake Investigation Committee, school books, educational societies, degrees, meteorology, pensions and public school finance. Part III gives 71 statistical tables, mostly by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools by size and course, teachers and their salaries, classes, pupils, attendance, graduates and fees; each kind of secondary, normal, higher and special school; libraries; teachers' examinations and licences; years of service and salaries of school officials; and the expenditure, income and property of the public schools of Fu and Ken, Gun, cities, towns and villages, with pensions.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections and the first statistical tables) or a Claude Sonnet 5.5 agent (the dense statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan is defective in Part III: it repeats several runs of pages (read once here) and lacks printed pp. 140, 143, 146–147, 151, 154–155, 250–255, 272–277 and 316–317, so Tables 9, 46, 47, 53 and 54 are missing and Tables 3–6, 8, 55 and 69 are incomplete.",
     "scan": "https://archive.org/details/annualreportmin00monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin00monbgoog", "blank_marking": True},
    {"slug": "japan-education-1896", "dir": "Mombusho_1896", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1896",
     "subtitle": "Twenty-fourth Annual Report of the Minister of State for Education, for the Twenty-ninth Year of Meiji (1896)",
     "publisher": "Department of Education (Mombushō), Tokyo, 1898",
     "blurb": "The English edition of the Mombushō's annual report for 1896. Part I sketches the business of the Department and its officials and expenditure; Part II reports on elementary schools, apprentice schools, supplementary technical schools, schools for the blind and dumb, kindergartens, normal, middle and higher schools, higher female schools, the Imperial University, special, technical and miscellaneous schools, libraries, teachers' licences, foreign instructors, local educational officials, the Tokyo Academy, the Earthquake Investigation Committee, the Central Meteorological Observatory, school books, educational societies, degrees, pensions, the new additional salaries for long service and public school finance. Part III gives 44 statistical tables, mostly by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools by size, teachers, classes, pupils, attendance, graduates and fees; apprentice, technical, blind and dumb schools and kindergartens; normal, middle, higher female, higher, special, technical and miscellaneous schools and the Imperial University; libraries; and public school expenditure, income and property.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan repeats several runs of pages (read once here) and lacks printed pp. 140–141 and 188–193, so Table 3 is missing and Tables 27–31 (ordinary middle schools) are incomplete.",
     "scan": "https://archive.org/details/annualreportmin02monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin02monbgoog", "blank_marking": True},
    {"slug": "japan-education-1901-02", "dir": "Mombusho_1901", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1901–02",
     "subtitle": "Twenty-ninth Annual Report of the Minister of State for Education, for the Thirty-fourth Statistical Year of Meiji (1901–2), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1903",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1901–02. Part I gives general remarks, the business of the Department, officials and expenditure; Part II reports on elementary schools, kindergartens, schools for the blind and dumb, normal, middle and higher female schools, the higher schools, the Imperial Universities of Tokyo and Kyoto, special, technical and miscellaneous schools, school hygiene (with tables of pupils' physique and eyesight), libraries, teachers' licences, the Tokyo Academy, the Earthquake Investigation Committee, the Meteorological Observatory, the Geodetic Committee, the latitude observatory, school books, educational societies, pensions, the Educational Fund, additional salaries and public school finance. Part III, with its own page numbers, gives the statistics by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, kindergartens, blind and dumb, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school expenditure and income.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan repeats a few pages (read once here) and lacks Part III pp. 42–45, so the middle-school statistics are missing.",
     "scan": "https://archive.org/details/annualreportmin04monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin04monbgoog", "blank_marking": True},
    {"slug": "japan-education-1899", "dir": "Mombusho_1899", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1899",
     "subtitle": "Twenty-seventh Annual Report of the Minister of State for Education, for the Thirty-second Year of Meiji (1899)",
     "publisher": "Department of Education (Mombushō), Tokyo, 1900",
     "blurb": "The English edition of the Mombushō's annual report for 1899, the year of the Middle School, Higher Female School, Technical School and Private School Ordinances. Part I sketches the business of the Department, its officials and expenditure; Part II reports on elementary schools, schools for the blind and dumb, kindergartens, normal, higher female, middle and higher schools, the Imperial Universities of Tokyo and Kyoto, special, technical and miscellaneous schools, foreign instructors, school hygiene (with tables of pupils' physique), libraries, degrees, teachers' licences, local educational officials, the Tokyo Academy, the Earthquake Investigation Committee, the Meteorological Observatory, the Geodetic Committee, school books, educational societies, pensions, additional salaries and public school finance. Part III gives the statistical tables, mostly by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, blind and dumb schools, kindergartens, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school finance.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan is defective: it repeats several runs of pages (read once here, using the clearer copy), two re-photographed pages are ruined, and it lacks printed pp. 112–113, 178–181 and everything after p. 208 (the end of Table 35 onward). The page of the printed contents listing Tables 17 onward is also missing, so those tables have no contents entries.",
     "scan": "https://archive.org/details/annualreportmin05monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin05monbgoog", "blank_marking": True},
    {"slug": "japan-education-1900-01", "dir": "Mombusho_1900", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1900–01",
     "subtitle": "Twenty-eighth Annual Report of the Minister of State for Education (1900–1901)",
     "publisher": "Department of Education (Mombushō), Tokyo, 1902",
     "blurb": "The English edition of the Mombushō's annual report for the statistical year 1900–01, the year of the revised Elementary School Ordinance that abolished fees for ordinary elementary schools. Part I sketches the business of the Department, its officials and expenditure; Part II reports on elementary schools, kindergartens, schools for the blind and dumb, normal, middle and higher female schools, higher schools, the Imperial Universities of Tokyo and Kyoto, special, technical and miscellaneous schools, school hygiene (with tables of pupils' physique and eyesight), libraries, teachers' licences, the Tokyo Academy, the Earthquake Investigation Committee, the Meteorological Observatory, the Geodetic Committee, the latitude observatory, school books, educational societies, pensions, the Educational Fund, additional salaries and public school finance. Part III gives 35 statistical tables by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, kindergartens, blind and dumb, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school expenditure, income and property.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan repeats printed pp. 64–65 in place of pp. 72–73, which are missing; the last property tables (Tables 34–35) are badly degraded and largely unreadable.",
     "scan": "https://archive.org/details/annualreportmin01monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin01monbgoog", "blank_marking": True},
    {"slug": "japan-education-1902-03", "dir": "Mombusho_1902", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1902–03",
     "subtitle": "Thirtieth Annual Report of the Minister of State for Education, for the Thirty-fifth Statistical Year of Meiji (1902–3), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1904",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1902–03, the year of the Special Schools Ordinance and of state-compiled elementary textbooks. Part I gives general remarks, the business of the Department, officials and expenditure; Part II reports on elementary schools, kindergartens, schools for the blind and dumb, the higher normal schools and special institutes for training teachers, normal, middle and higher female schools, higher schools, the Imperial Universities of Tokyo and Kyoto, special, technical and miscellaneous schools, school hygiene (with tables of pupils' physique and eyesight), libraries, teachers' licences, the Tokyo Academy, the Earthquake Investigation, Geodetic and Japanese Language committees, the Meteorological and latitude observatories, school books, educational societies, pensions, the Educational Fund and public school expenditure and property. Part III, with its own page numbers, gives the statistics by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, kindergartens, blind and dumb, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school expenditure, income and property.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The Google scan repeats printed pp. 84–85 (read once). The miscellaneous schools table in Part II (p. 122) is destroyed in the scan and is not transcribed, and the stacked small figures of the school stock property table (Part III pp. 68–69) are largely unreadable.",
     "scan": "https://archive.org/details/annualreportmin06monbgoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportmin06monbgoog", "blank_marking": True},
    {"slug": "japan-education-1903-04", "dir": "Mombusho_1903", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1903–04",
     "subtitle": "Thirty-first Annual Report of the Minister of State for Education, for the Thirty-sixth Statistical Year of Meiji (1903–4), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1906",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1903–04, the year of state-compiled elementary textbooks and the outbreak of the Russo-Japanese War. Part I gives general remarks, the business of the Department, officials and expenditure; Part II reports on elementary schools, kindergartens, schools for the blind and dumb, the higher normal schools, special institutes for training teachers, normal, middle and higher female schools, higher schools, the Imperial Universities, special, technical and miscellaneous schools, school hygiene (with tables of pupils' physique and eyesight), libraries, teachers' licences, the medical examination committee, the Tokyo Academy, the earthquake, meteorological, geodetic and latitude boards, the scientific-literature and Japanese-language committees, educational societies, pensions, the Educational Fund and public school expenditure and property. Part III, with its own page numbers, gives the statistics by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, kindergartens, blind and dumb, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school expenditure, income and property.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan, which binds this report with the Thirty-second.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. On the last pages of Part III (school stock property) many tiny stacked figures are too blurred to read.",
     "scan": "https://archive.org/details/bub_gb_awkOAAAAYAAJ_2/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_awkOAAAAYAAJ_2", "blank_marking": True},
    {"slug": "japan-education-1904-05", "dir": "Mombusho_1904", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1904–05",
     "subtitle": "Thirty-second Annual Report of the Minister of State for Education, for the Thirty-seventh Statistical Year of Meiji (1904–5), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1906",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1904–05, the year of the Russo-Japanese War. Part I gives general remarks, the business of the Department, officials and expenditure; Part II reports on elementary schools, kindergartens, schools for the blind and dumb, the higher normal schools, special institutes for training teachers, normal, middle and higher female schools, higher schools, the Imperial Universities of Tokyo and Kyoto, special schools (medicine, foreign languages, fine art, music, agriculture, commerce), technical schools and the higher technical schools, apprentices' and supplementary industrial schools, miscellaneous schools, school hygiene (school physicians, pupils' physique and eyesight), libraries, teachers' licences, the medical examination committee, the Tokyo Academy, the earthquake, meteorological and geodetic boards, school books, educational societies, pensions, the Educational Fund and public school finance. Part III, with its own page numbers, gives the statistics by Fu and Ken: school population, children receiving and not receiving instruction, elementary schools, teachers, classes, pupils, attendance and graduates, kindergartens, blind and dumb, normal, middle, higher female, higher, special, technical and miscellaneous schools, the universities, and public school expenditure, income and property.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan, which binds this report after the Thirty-first.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the statistical tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Many statistical tables are printed across two facing pages and are given as two tables (left and right halves). Only tables are transcribed; the running text is not. The scan lacks printed pp. 30–31 and 50–51. Many tiny stacked figures (foreigners, branch schools) in the dense tables and on the last property pages are too blurred to read.",
     "scan": "https://archive.org/details/bub_gb_awkOAAAAYAAJ_2/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_awkOAAAAYAAJ_2", "blank_marking": True},
    {"slug": "japan-education-1905-06", "dir": "Mombusho_1905", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1905–06",
     "subtitle": "Thirty-third Annual Report of the Minister of State for Education, for the Thirty-eighth Statistical Year of Meiji (1905–6), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1908",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1905–06, the year of the end of the Russo-Japanese War. Part I gives general remarks, the business of the Department, officials and expenditure; Part II reports, with the statistics in the text, on elementary schools, kindergartens, schools for the blind and dumb, the higher normal schools and higher normal school for girls, special institutes for training teachers, normal and middle schools, high schools for girls, high schools, the Imperial Universities of Tokyo and Kyoto, special schools (medicine, foreign languages, fine art, music, agriculture, commerce), technical schools and the higher technical schools, institutes for training technical teachers, miscellaneous schools, school hygiene (school physicians, pupils' physique and eyesight), libraries, teachers' licences, the medical examination committee, the Tokyo Academy, the earthquake, meteorological and geodetic boards, school books, educational societies, pensions, the Educational Fund and public school finance. This abridged edition has no separate statistical part.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan, which binds this report with the Thirty-fourth.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the denser tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Only tables are transcribed; the running text, the errata list, and the maps and diagrams at the end are not.",
     "scan": "https://archive.org/details/bub_gb_JwgOAAAAYAAJ_2/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_JwgOAAAAYAAJ_2", "blank_marking": True},
    {"slug": "japan-education-1906-07", "dir": "Mombusho_1906", "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "title": "Annual Report of the Minister of State for Education 1906–07",
     "subtitle": "Thirty-fourth Annual Report of the Minister of State for Education, for the Thirty-ninth Statistical Year of Meiji (1906–7), abridged",
     "publisher": "Department of Education (Mombushō), Tokyo, 1909",
     "blurb": "The abridged English edition of the Mombushō's annual report for the statistical year 1906–07, the eve of the extension of compulsory schooling to six years. Part I covers general remarks and the business of the Department: inspection, the Higher Council of Education, summer institutes, degrees, students abroad, teachers' licences, honours, school books, state aid to technical education, associations and foundations, buildings and repairs, officials and expenditure. Part II reports, with the statistics in the text, on elementary schools, kindergartens, schools for the blind and dumb, the higher normal schools and the higher normal school for girls, special institutes for training teachers, normal and middle schools, high schools for girls, high schools, the Imperial Universities of Tokyo and Kyoto, special schools (medicine, foreign languages, fine art, music, agriculture, commerce), technical schools and the higher technical schools, miscellaneous schools, school hygiene, libraries, teachers' licences, the medical examination committee, the Imperial Academy, the earthquake, meteorological and geodetic boards, educational societies, pensions, the Educational Fund and public school finance. This abridged edition has no separate statistical part.",
     "source": "Transcribed by Claude agents from the Internet Archive (Google Books) scan, which binds this report after the Thirty-third.",
     "gaps": "Each page was read once by a Claude Haiku 5.5 agent (the text sections) or a Claude Sonnet 5.5 agent (the denser tables), from full-resolution crops, with sideways pages turned upright; pages the first Haiku reader marked hard were read again from scratch by a Sonnet 5.5 agent, whose reading replaces the first. Nothing was checked by eye. Unreadable figures are marked [?]; totals that do not add up are kept as printed. Only tables are transcribed; the running text and the charts at the end are not.",
     "scan": "https://archive.org/details/bub_gb_JwgOAAAAYAAJ_2/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_JwgOAAAAYAAJ_2", "blank_marking": True},
    {"slug": "japan-1905", "dir": "Japan_Year_Book_1905", "title": "The Japan Year Book 1905",
     "publisher": "The \"Japan Year Book\" Office, Tokyo, 1905",
     "blurb": "The first edition of The Japan Year Book, compiled during the Russo-Japanese War: geography, population, the Imperial Court, politics, finance, banking, industry, trade, education, the army and navy, communications, a Who's Who (\"Contemporary Worthies\"), diplomacy, the press, Formosa, Korea, and an appended import tariff.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of a New York Public Library copy).",
     "gaps": "The dated narrative of the \"Progress of the War\" chapter (pp. 315-347) was transcribed separately and is not included; the statistical tables printed in that chapter (spoils, prisoners, warships lost) are. Advertisements, the contents and the Index were skipped, as were law and treaty texts. The Import Tariff List in the Appendix is given one table per page. The \"Contemporary Worthies\" Who's Who, the Imperial family and the steamship-company sketches are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1905/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1905"},
    {"slug": "japan-1906", "dir": "Japan_Year_Book_1906", "model": "Haiku 5.5", "title": "The Japan Year Book 1906",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1906",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1906/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1906",
     "blank_marking": True},
    {"slug": "japan-1907", "dir": "Japan_Year_Book_1907", "model": "Haiku 5.5", "title": "The Japan Year Book 1907",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1907",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1907/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1907",
     "blank_marking": True},
    {"slug": "japan-1908-09", "dir": "Japan_Year_Book_1908", "model": "Haiku 5.5", "title": "The Japan Year Book 1908-09",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1908",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1908-1909/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1908-1909",
     "blank_marking": True},
    {"slug": "japan-fea-1901", "dir": "Japan_Financial_Annual_1901", "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "title": "The Financial and Economic Annual of Japan 1901", "subtitle": "Financial Annual of Japan, No. I",
     "publisher": "Department of Finance, Tokyo (Government Press), 1901",
     "blurb": "The first issue of the Japanese Finance Ministry's English-language statistical annual, then titled Financial Annual of Japan: the budget for 1901–02, revenue and expenditure of the general account from 1867–68, taxation, the Formosan special account, prefectural and municipal finance, the national debt and local loans, receipts from public undertakings, debentures and capital of companies, the capitals, deposits and advances of the Bank of Japan, Yokohama Specie Bank and other banks, money in circulation, clearing houses and interest rates, foreign trade by commodity and country, shipping, railways, posts and telegraphs, postal savings, prices of bonds, shares and commodities, wages and population, most series running from the 1860s or 1870s to 1900.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive (Google Books) scan.",
     "gaps": "Only tables are transcribed; the running text and notes are not. Table pages were found from contact sheets; no table is printed sideways. Most tables run across two facing pages (years and first columns on the left, further columns on the right), so each two-page spread was read as one image set and such tables joined into one. Each spread or page was read once by Claude Sonnet 5.5 (large tables) or Claude Haiku 5.5 (simpler pages) through the llm CLI, with no second reading and no check by eye. Unreadable figures are marked [?]. The scan repeats printed pp. 28–29 (read once) and lacks pp. 38–39 (reserve against convertible notes and the start of the clearing-house table).",
     "scan": "https://archive.org/details/financialandeco00kugoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/financialandeco00kugoog", "blank_marking": True},
    {"slug": "japan-fea-1902", "dir": "Japan_Financial_Annual_1902", "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "title": "The Financial and Economic Annual of Japan 1902", "subtitle": "Financial and Economical Annual of Japan, No. II",
     "publisher": "Department of Finance, Tokyo (Shūeisha), 1902",
     "blurb": "The second issue, retitled Financial and Economical Annual of Japan and arranged in six parts: finance (the budget for 1902–03, state revenue and expenditure from 1867–68, taxes with notes on their history and rates, public undertakings, local finance, national debts and local loans, coins and paper money), agriculture, industry and commerce (crops, marine products, minerals, manufactures, factories, companies, insurance, wages and prices), foreign trade (by commodity and country, gold and silver, steam and sailing vessels), banking and the money market (every class of bank, postal savings, note reserve, clearing houses, interest and exchange rates, bond and share prices), communications (posts, telegraphs, telephones, railways, shipping) and Formosa.",
     "source": "LLM-transcribed (Claude via the API) from the Internet Archive (Google Books) scan.",
     "gaps": "Only tables are transcribed; the running text and notes are not. Table pages were found from contact sheets; no table is printed sideways. Most tables run across two facing pages (years and first columns on the left, further columns on the right), so each two-page spread was read as one image set and such tables joined into one. Each spread or page was read once by Claude Sonnet 5.5 (large tables) or Claude Haiku 5.5 (simpler pages) through the llm CLI, with no second reading and no check by eye. Unreadable figures are marked [?].",
     "scan": "https://archive.org/details/financialandeco01kugoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/financialandeco01kugoog", "blank_marking": True},
    {"slug": "japan-fea-1904", "dir": "Japan_Financial_Annual_1904", "model": "Haiku 5.5",
     "title": "The Financial and Economic Annual of Japan 1904",
     "subtitle": "The Fourth Financial and Economic Annual of Japan",
     "publisher": "Department of Finance, Tokyo, 1904",
     "blurb": "The Japanese Ministry of Finance's English-language statistical annual for 1904, with figures mostly to 1903: area and population, national and local finance (budgets, taxes, public debt), agriculture, industry and commerce, foreign trade, banking and the money market, communications (railways, shipping, post and telegraph) and Taiwan (Formosa), with an appendix including the import tariff.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive (Google Books) scan.",
     "gaps": "Only tables are transcribed; the running text, the map and the diagrams are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked tables printed across two facing pages; those were read as one table. Each table page was read once by Claude Haiku 5.5 from full-resolution crops, with no second reading and no check by eye. Printed totals are checked automatically and differences noted; figures the model could not read are marked [?].",
     "note": "Bound with the Fifth Annual (1905) in the same scan.",
     "scan": "https://archive.org/details/bub_gb_wYk9AQAAMAAJ/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_wYk9AQAAMAAJ",
     "blank_marking": True},
    {"slug": "japan-fea-1905", "dir": "Japan_Financial_Annual_1905", "model": "Haiku 5.5",
     "title": "The Financial and Economic Annual of Japan 1905",
     "subtitle": "The Fifth Financial and Economic Annual of Japan",
     "publisher": "Department of Finance, Tokyo, 1905",
     "note": "Bound with the Fourth Annual (1904) in the same scan.",
     "blurb": "The Japanese Ministry of Finance's English-language statistical annual for 1905, during the Russo-Japanese War, with figures mostly to 1904: area and population, national and local finance (budgets, taxes, war loans and public debt), agriculture, industry and commerce, foreign trade, banking and the money market, communications (railways, shipping, post and telegraph) and Taiwan (Formosa).",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive (Google Books) scan, where it is bound with the Fourth Annual (1904).",
     "gaps": "Only tables are transcribed; the running text, the map and the diagrams are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked tables printed across two facing pages; those were read as one table. Each table page was read once by Claude Haiku 5.5 from full-resolution crops, with no second reading and no check by eye. Printed totals are checked automatically and differences noted; figures the model could not read are marked [?].",
     "scan": "https://archive.org/details/bub_gb_wYk9AQAAMAAJ/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_wYk9AQAAMAAJ",
     "blank_marking": True},
    {"slug": "japan-fea-1908", "dir": "Japan_Financial_Annual_1908", "model": "Haiku 5.5",
     "title": "The Financial and Economic Annual of Japan 1908",
     "subtitle": "The Eighth Financial and Economic Annual of Japan",
     "publisher": "Department of Finance, Tokyo, 1908",
     "blurb": "The Japanese Ministry of Finance's English-language statistical annual: area and population, national and local finance (budgets, taxes, public debt), agriculture, industry and commerce (land, crops, silk, mining, companies, prices and wages), foreign trade, banking and the money market, communications (railways, shipping, post and telegraph), and Taiwan and Karafuto, with an appendix.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive (Google Books) scan.",
     "gaps": "Only tables are transcribed; the running text, the map and the diagrams are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked tables printed across two facing pages; those were read as one table. Each table page was read once by Claude Haiku 5.5 from full-resolution crops, with no second reading and no check by eye (one table was spot-checked against the scan and agreed, except that a point printed as a thousands separator was written as a comma). Printed totals are checked automatically and differences noted; figures the model could not read are marked [?].",
     "scan": "https://archive.org/details/bub_gb_8jDRAAAAMAAJ/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_8jDRAAAAMAAJ",
     "blank_marking": True},
    {"slug": "japan-1910", "dir": "Japan_Year_Book_1910", "title": "The Japan Year Book 1910",
     "publisher": "The Japan Year Book Office, Tokyo, 1910",
     "blurb": "The fifth annual edition, compiled by Y. Takenob and K. Kawakami: geography, population, the Imperial Court, a Who's Who, arts and crafts, education, religion, justice, agriculture, mining, industry, finance, diplomacy, politics, trade, banking, the army and navy, communications, shipping, railways, the press, Formosa, Karafuto, South Manchuria and Korea.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of the 2013 Edition Synapse facsimile, University of Minnesota copy).",
     "gaps": "The scan is low resolution, so more figures are left blank than in later volumes; each blank is explained in a transcriber's note. Advertisements, the contents and the Index were skipped. The Who's Who, the Imperial family and the art and pottery sketches are on the Who's Who & Directories page; the Diary of 1908-9 is on the Chronologies page. Treaty texts and law articles are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1910/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1910"},
    {"slug": "japan-1911", "dir": "Japan_Year_Book_1911", "model": "Haiku 5.5", "title": "The Japan Year Book 1911",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1911",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1911/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1911",
     "blank_marking": True},
    {"slug": "japan-1912", "dir": "Japan_Year_Book_1912", "model": "Haiku 5.5", "title": "The Japan Year Book 1912",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1912",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1912/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1912",
     "blank_marking": True},
    {"slug": "japan-1913", "dir": "Japan_Year_Book_1913", "model": "Haiku 5.5", "title": "The Japan Year Book 1913",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1913",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1913/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1913",
     "blank_marking": True},
    {"slug": "japan-1914", "dir": "Japan_Year_Book_1914", "model": "Haiku 5.5", "title": "The Japan Year Book 1914",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1914",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1914/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1914",
     "blank_marking": True},
    {"slug": "japan-1915", "dir": "Japan_Year_Book_1915", "model": "Haiku 5.5", "title": "The Japan Year Book 1915",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1915",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1915/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1915",
     "blank_marking": True},
    {"slug": "japan-1916", "dir": "Japan_Year_Book_1916", "model": "Haiku 5.5", "title": "The Japan Year Book 1916",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1916",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1916/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1916",
     "blank_marking": True},
    {"slug": "japan-1917", "dir": "Japan_Year_Book_1917", "model": "Haiku 5.5", "title": "The Japan Year Book 1917",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1917",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1917/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1917",
     "blank_marking": True},
    {"slug": "japan-1918", "dir": "Japan_Year_Book_1918", "model": "Haiku 5.5", "title": "The Japan Year Book 1918",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1918",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1918/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1918",
     "blank_marking": True},
    {"slug": "japan-1919-20", "dir": "Japan_Year_Book_1919", "model": "Haiku 5.5", "title": "The Japan Year Book 1919-20",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1920",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1919-1920/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1919-1920",
     "blank_marking": True},
    {"slug": "japan-1920-21", "dir": "Japan_Year_Book_1920", "title": "The Japan Year Book 1920-21",
     "publisher": "The Japan Year Book Office, Tokyo, 1920",
     "blurb": "The fifteenth annual edition: geography, history, population, the Imperial Court, a Who's Who, education, labour, communications, railways, shipping, banking, the army and navy, diplomacy, trade, agriculture, industry, finance, politics, the colonies, and a business directory.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of a University of California copy).",
     "gaps": "Advertisements, the contents pages and the Index contain no tables and were skipped. The Who's Who, Business Directory, Learned & Social Institutions and the Imperial family and charity institutions are on the Who's Who & Directories page; the Diary, Obituary and chronological lists are on the Chronologies page. On printed p. 171 of the Who's Who an entry begins mid-text: its heading was never printed, so the surviving text is recorded in a note, not as an entry.",
     "scan": "https://archive.org/details/japan-year-book-1920/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1920"},
    {"slug": "japan-1923", "dir": "Japan_Year_Book_1923", "model": "Haiku 5.5", "title": "The Japan Year Book 1923",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1923",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1923/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1923",
     "blank_marking": True},
    {"slug": "japan-1924-25", "dir": "Japan_Year_Book_1924", "model": "Haiku 5.5", "title": "The Japan Year Book 1924-25",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1925",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1924-1925/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1924-1925",
     "blank_marking": True},
    {"slug": "japan-1927", "dir": "Japan_Year_Book_1927", "model": "GPT-6.1-Sol (Codex) and Claude Haiku 5.5", "title": "The Japan Year Book 1927",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1927",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (OpenAI GPT-6.1-Sol via the Codex CLI, and Claude Haiku 5.5 agents) from the Internet Archive scan (Google Books, University of Wisconsin copy).",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by GPT-6.1-Sol, so small tables set into the prose may be missing. Each page was read once from full-resolution crops (the tables and part of the Who's Who by GPT-6.1-Sol at low reasoning effort, the rest of the directories by Claude Haiku 5.5, five table pages by Claude Sonnet 5.5) and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1927/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1927",
     "blank_marking": True},
    {"slug": "japan-1928", "dir": "Japan_Year_Book_1928", "model": "Claude Haiku 5.5 and Sonnet 5.5", "title": "The Japan Year Book 1928",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1928",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 agents) from the Internet Archive scan (Google Books, University of California copy).",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Haiku 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; 14 difficult or blurred pages were read again by Claude Sonnet 5.5, whose reading is used (the climate tables on pp. 7–10 and the table of companies classified by organization remain mostly [?]); unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page. The scan repeats p. 543 (leaf 599) and lacks pp. 32–33 of the Who's Who.",
     "scan": "https://archive.org/details/japan-year-book-1928/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1928",
     "blank_marking": True},
    {"slug": "japan-1929", "dir": "Japan_Year_Book_1929", "model": "Claude Haiku 5.5 and Sonnet 5.5", "title": "The Japan Year Book 1929",
     "publisher": "Y. Takenob (ed.); Tokyo: The Japan Year Book Office, 1929",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 agents) from the Internet Archive scan (Google Books copy).",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Haiku 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; 29 blurred, smudged or show-through pages were read again by Claude Sonnet 5.5, whose reading is used. Much of this scan is faint or blotted, so many cells are [?] (the climate tables, parts of Industry and Chosen are the worst); unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The directories are on the Who's Who & Directories page. The obituary lists are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1929/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1929",
     "blank_marking": True},
    {"slug": "japan-1930", "dir": "Japan_Year_Book_1930", "title": "The Japan Year Book 1930",
     "publisher": "The Japan Year Book Office, Tokyo, 1930",
     "blurb": "Comprehensive English-language reference on the Japanese Empire in 1930, covering geography, population, government, defence, education, labour, justice, communications, railways, shipping, banking, finance, agriculture, industry, trade, the six premier cities and the colonies.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Advertisements and the Index contain no tables. The Who's Who, Business Directory and Learned & Social Institutions (Appendices A–C) are transcribed as entries on the Who's Who & Directories page. The shop and restaurant lists in Appendix D are included; the physicians' lists are not. On p. 439 the right edge of the scan cuts off the 1927 export figures, so those cells are blank.",
     "scan": "https://archive.org/details/japan-year-book-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1930"},
    {"slug": "japan-1935", "dir": "Japan_Year_Book_1935", "title": "The Japan Year Book 1935",
     "publisher": "K. Inahara, ed.; Tokyo: The Foreign Affairs Association of Japan, 1935",
     "blurb": "English-language annual on the Japanese Empire in 1935, covering geography, population, government, defence, finance, banking, trade, agriculture, industry, communications, social affairs, education, the colonies and Manchoukuo.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and lists are transcribed; prose, the Chronicle of Important Events, the Chronological Index and the Calendar of Annual Events are not. Printed pp. 81 and 683 are missing from the scan (repeat scans of other pages were skipped). The heavy bold type makes 3 and 8 hard to tell apart: such digits are blank unless a printed total settles them, so many cells are empty. The List of Clubs, Societies and Associations is on the Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1935/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1935"},
    {"slug": "japan-1937", "dir": "Japan_Year_Book_1937", "model": "Haiku 5.5", "title": "The Japan Year Book 1937",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1937",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/the-japan-year-book-1937/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/the-japan-year-book-1937",
     "blank_marking": True},
    {"slug": "japan-1939-40", "dir": "Japan_Year_Book_1939-40", "title": "The Japan Year Book 1939-40",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1939",
     "blurb": "The wartime edition of the standard English-language reference on the Japanese Empire.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan often repeats a leaf in place of the next one, so about 90 printed pages are missing, among them pp. 273–274, 277–278, 283–284 (part of the 1937-38 budget and Banking Tables 1–3), 380–381 (Balance of International Payments), 778–779, 784, 787–788, 793, 796–797, 802–803, 808, 811, 814, 817, 820–821, 825, 830–832, 843–844, 847, 850, 853–854, 861, 866, 869, 873, 876, 879, 886, 888, 893, 896–897, 901, 904, 908–909, 912, 918–919, 928–929, 934, 937, 940–941, 947–948, 951–952 (including the opening of the Karafuto chapter), 956, 959, 962–963, 967, 970–971, 1023, 1026–1027, 1033–1034, 1039, 1123, 1130, 1135–1137 and 1142. Tables that run onto a missing page are incomplete and say so. Page 363 is heavily over-inked, leaving about 90 blank cells in the census table there. Lists are included as well as tables; the Clubs & Societies list is on the directory page. The bibliography, index and advertisements are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1939-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1939-1940", "dir_label": "Clubs & Societies Directory"},
    {"slug": "japan-1942-43", "dir": "Japan_Year_Book_1942", "model": "Haiku 5.5", "title": "The Japan Year Book 1942-43",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1943",
     "blurb": "An edition of the English-language reference annual on Japan: geography, population, the Imperial House, government, the Diet and political parties, foreign relations, the army and navy, finance, banking and insurance, agriculture, forestry, fisheries, mining and industry, trade, communications, railways and shipping, education, religion, justice, the colonies and dependencies, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/1942-43-the-japan-year-book/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/1942-43-the-japan-year-book",
     "blank_marking": True},
    {"slug": "japan-1946-48", "dir": "Japan_Year_Book_1946-48", "title": "The Japan Year Book 1946-48",
     "publisher": "The Foreign Affairs Association of Japan, 1949",
     "blurb": "The first post-war edition, covering occupied Japan.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The scan is complete: no printed pages are missing and no leaves repeat. Part I runs to p. 614; the Appendix (SCAP directives, the new Constitution and post-war laws, documents of 1945–47, the war-crimes indictment and a List of Emperors) is paged again from 1. The Appendix is almost all legal text, so only its lists are transcribed. A few cells on folding inserts are lost in the fold and are left blank. The index, advertisements and a short run of church-group entries (printed pp. 489–490) are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1946-1948/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1946-1948"},
    {"slug": "korea-1907", "dir": "Korea_Annual_Report_1907", "model": "Haiku 5.5",
     "title": "Annual Report on Reforms and Progress in Korea 1907",
     "publisher": "H.I.J.M.'s Residency General, Seoul, December 1908",
     "blurb": "The Japanese Residency General's first English-language annual report on Korea under the protectorate (for 1907): the new agreement and the Residency General, administration, judiciary, police and the army, finance, currency and banking, foreign trade and shipping, communications, public undertakings, agriculture and industry, sanitation and education, with statistical tables of trade, shipping, finance and communications.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables and columnar lists are transcribed; the running text, photographs, maps, organisation charts and the contents are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked pages printed sideways; those were turned upright before reading. Each table page was read once by Claude Haiku 5.5 through the API from full-resolution crops, with no second reading and no check by eye. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. Figures the model could not read are marked [?]. Chapters follow the printed contents (also read by Haiku).",
     "scan": "https://archive.org/details/bub_gb_CiRRAAAAYAAJ/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/bub_gb_CiRRAAAAYAAJ",
     "blank_marking": True},
    {"slug": "korea-1908-09", "dir": "Korea_Annual_Report_1908", "model": "Haiku 5.5",
     "title": "Annual Report on Reforms and Progress in Korea 1908-09",
     "publisher": "H.I.J.M.'s Residency General, Seoul, December 1909",
     "blurb": "The Residency General's second annual report (1908-09): the imperial household, central and local administration, justice, police, finance and taxation, currency and banking, communications, foreign commerce, agriculture, trade and industry, mining, forestry and fishery, sanitation and education, with an appendix of statistical tables.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables and columnar lists are transcribed; the running text, photographs, maps, organisation charts and the contents are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked pages printed sideways; those were turned upright before reading. Each table page was read once by Claude Haiku 5.5 through the API from full-resolution crops, with no second reading and no check by eye. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. Figures the model could not read are marked [?]. Chapters follow the printed contents (also read by Haiku).",
     "scan": "https://archive.org/details/thesecondannualreportonreformsandprogressinkorea19089/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/thesecondannualreportonreformsandprogressinkorea19089",
     "blank_marking": True},
    {"slug": "korea-1909-10", "dir": "Korea_Annual_Report_1909", "model": "Haiku 5.5",
     "title": "Annual Report on Reforms and Progress in Korea 1909-10",
     "publisher": "Government-General of Chosen, Seoul, December 1910",
     "blurb": "The third annual report (1909-10), the last of the protectorate years, compiled after annexation by the Government-General: administration, justice, police, finance, currency and banking, government undertakings, communications, foreign commerce, agriculture, mining, forestry and fishing, sanitation, education and the Japanese settlements, with an appendix of statistical tables.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables and columnar lists are transcribed; the running text, photographs, maps, organisation charts and the contents are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked pages printed sideways; those were turned upright before reading. Each table page was read once by Claude Haiku 5.5 through the API from full-resolution crops, with no second reading and no check by eye. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. Figures the model could not read are marked [?]. Chapters follow the printed contents (also read by Haiku).",
     "scan": "https://archive.org/details/thethirdannualreportonreformsandprogressinkorea190910/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/thethirdannualreportonreformsandprogressinkorea190910",
     "blank_marking": True},
    {"slug": "korea-1910-11", "dir": "Korea_Annual_Report_1910", "model": "Haiku 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen (Korea) 1910-11",
     "publisher": "Government-General of Chosen, Keijo (Seoul), December 1911",
     "blurb": "The Government-General's first annual report after the annexation of Korea (1910-11): geography, central and local administration, charities, justice, police, finance, currency and banking, government undertakings, communications, commerce, agriculture, trade and industry, mining, forestry and fishery, sanitation and education, with an appendix of statistical tables.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables and columnar lists are transcribed; the running text, photographs, maps, organisation charts and the contents are not. Table pages were found from contact sheets by Claude Sonnet 5.5, which also marked pages printed sideways; those were turned upright before reading. Each table page was read once by Claude Haiku 5.5 through the API from full-resolution crops, with no second reading and no check by eye. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. Figures the model could not read are marked [?]. Chapters follow the printed contents (also read by Haiku).",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191011/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191011",
     "blank_marking": True},
    {"slug": "korea-1911-12", "dir": "Korea_Annual_Report_1911", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1911-12",
     "publisher": "Government-General of Chosen, Keijo, 1912",
     "blurb": "The Government-General's English-language annual report for the second year of Japanese rule: central and local administration, the 1911 census, justice and prisons, police and the suppression of insurgents, finance and taxation, currency and banking, government monopolies and undertakings, harbours, roads and railways, posts and telegraphs, foreign trade, agriculture, forestry, mining, fisheries, sanitation and education. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan (a Google scan of a Princeton copy).",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and the legal appendices are not. Every text page was read. The scan ends at about printed p. 230, so Appendices E–F and the 21 general statistical tables at the back of the book (pp. 257–272) are not in it. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and the few cells where the readings differed went to a third reader (agreement is used, otherwise [?]). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191112/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191112",
     "blank_marking": True},
    {"slug": "korea-1912-13", "dir": "Korea_Annual_Report_1912", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1912-13",
     "publisher": "Government-General of Chosen, Keijo, December 1914",
     "blurb": "The Government-General's English-language report for fiscal 1912: officials, local finance and the Imperial Donation Fund by province, justice, prisons and police, the budget, taxes by province, monopolies, banking and money, railways, roads, posts and shipping, trade, agriculture, forestry, mining, fisheries, sanitation and schools, with the import, export and frontier tariffs and twenty-two statistical tables. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts and the appendix regulations are not. Every text page was read. Two pages are scanned twice (images 142-143 repeat 140-141) and were read once. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191213/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191213",
     "blank_marking": True},
    {"slug": "korea-1913-14", "dir": "Korea_Annual_Report_1913", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1913-14",
     "publisher": "Government-General of Chosen, Keijo, July 1915",
     "blurb": "The Government-General's English-language report for fiscal 1913: officials, local and municipal finance, the Imperial Donation Fund and school associations by province, justice and police, accounts and budgets, taxes by province, customs, Yoktun lands and monopolies, banking and money, railways, posts and shipping, trade by country and port, companies, agriculture, mining, forestry and fisheries, hospitals and epidemics, schools, tobacco-tax rates, and eleven statistical tables. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, diagrams, the organisation chart and the appendix regulations are not. Every text page was read. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191314/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191314",
     "blank_marking": True},
    {"slug": "korea-1914-15", "dir": "Korea_Annual_Report_1914", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1914-15",
     "publisher": "Government-General of Chosen, Keijo, July 1916",
     "blurb": "The Government-General's English-language report for fiscal 1914: officials and land survey, local and municipal finance, the Imperial Donation Fund and school associations by province, justice and police, accounts and budgets, taxes, customs and Yoktun lands, monopolies, banking and money, railways, posts, telegraphs and shipping, trade by country and port, agriculture, factories, mining and fisheries, hospitals and epidemics, schools, and eighteen statistical tables. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, diagrams and the organisation chart are not. Every text page was read. Two pages of the statistical tables are scanned twice and were read once; Statistical Table XVIII is cut off at the right edge in both scans, so only its left-hand columns are given. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191415/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191415",
     "blank_marking": True},
    {"slug": "korea-1915-16", "dir": "Korea_Annual_Report_1915", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1915-16",
     "publisher": "Government-General of Chosen, Keijo, July 1917",
     "blurb": "The Government-General's English-language report for fiscal 1915: land survey and officials, provincial, municipal and village finance, the Imperial Donation Fund and Japanese school associations, courts, census and prisons, police, accounts and budgets, taxes, Yoktun lands and public loans, banking and money, the ginseng, salt, coal and lumber undertakings, roads, railways, posts, telegraphs and lighthouses, trade by country and port, agriculture and live-stock, companies, markets and factories, mining, forestry, fisheries, hospitals and epidemics, and schools. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, diagrams and the organisation chart (cut off at the right edge in the scan) are not. Every text page was read; this edition has no statistical appendix. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191516/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191516",
     "blank_marking": True},
    {"slug": "korea-1916-17", "dir": "Korea_Annual_Report_1916", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1916-17",
     "publisher": "Government-General of Chosen, Keijo, July 1918",
     "blurb": "The Government-General's English-language report for fiscal 1916: officials, the general and special accounts and budgets, taxes, customs, Yoktun lands and public loans, the ginseng, salt, coal, lumber and printing undertakings, banking, money and clearing houses, trade by country and port, railways, tramways, shipping, posts, telegraphs and lighthouses, roads, agriculture, sericulture and live-stock, companies, markets, factories and prices, mining, forestry and fisheries, schools and text-books, courts, census and police, hospitals and epidemics, waterworks and land survey, and municipal, provincial and village finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, bar-chart diagrams and the fold-out organisation chart (cut off at the right edge in the scan) are not. Every text page was read; this edition has no statistical appendix. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191617/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191617",
     "blank_marking": True},
    {"slug": "korea-1917-18", "dir": "Korea_Annual_Report_1917", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1917-18",
     "publisher": "Government-General of Chosen, Keijo, July 1920",
     "blurb": "The Government-General's English-language report for fiscal 1917: products 1910 and 1917, officials, military expenditure and subsidies, settled accounts and the 1918 budget, taxes, customs, Yoktun lands and public loans, the ginseng, salt, coal and lumber undertakings, money, the Bank of Chosen, bank-notes, clearing houses and banks, foreign trade by country and port, railways, tramways, shipping, posts, telegraphs and telephones, agriculture, cotton, fruit, sericulture and live-stock, companies, markets, factories and prices, mining, forestry and fisheries, schools and text-books, courts, census and police, epidemics and hospitals, waterworks and land survey, and municipal, provincial, myen and guild finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and diagrams are not. Every text page was read; this edition has no statistical appendix. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191718/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191718",
     "blank_marking": True},
    {"slug": "korea-1930-32", "dir": "Korea_Annual_Report_1930", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Chosen 1930-32",
     "publisher": "Government-General of Chosen, Keijo, December 1932",
     "blurb": "The Government-General's English-language annual report for 1930-32: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193032/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193032",
     "blank_marking": True},
    {"slug": "korea-1932-33", "dir": "Korea_Annual_Report_1932", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Chosen 1932-33",
     "publisher": "Government-General of Chosen, Keijo, December 1933",
     "blurb": "The Government-General's English-language annual report for 1932-33: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193233/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193233",
     "blank_marking": True},
    {"slug": "korea-1933-34", "dir": "Korea_Annual_Report_1933", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Chosen 1933-34",
     "publisher": "Government-General of Chosen, Keijo, December 1934",
     "blurb": "The Government-General's English-language annual report for 1933-34: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193334/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193334",
     "blank_marking": True},
    {"slug": "korea-1934-35", "dir": "Korea_Annual_Report_1934", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Chosen 1934-35",
     "publisher": "Government-General of Chosen, Keijo, December 1935",
     "blurb": "The Government-General's English-language annual report for 1934-35: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193435/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193435",
     "blank_marking": True},
    {"slug": "korea-1935-36", "dir": "Korea_Annual_Report_1935", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Chosen 1935-36",
     "publisher": "Government-General of Chosen, Keijo, December 1936",
     "blurb": "The Government-General's English-language annual report for 1935-36: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance, and the rural self-help movement. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193536/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193536",
     "blank_marking": True},
    {"slug": "korea-1936-37", "dir": "Korea_Annual_Report_1936", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Tyosen 1936-37",
     "publisher": "Government-General of Tyosen, Keijo, December 1937",
     "blurb": "The Government-General's English-language annual report for 1936-37: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance, and the rural self-help movement. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annual-report-on-administration-of-chosen-1936-37/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annual-report-on-administration-of-chosen-1936-37",
     "blank_marking": True},
    {"slug": "korea-1937-38", "dir": "Korea_Annual_Report_1937", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Tyosen 1937-38",
     "publisher": "Government-General of Tyosen, Keizyo, December 1938",
     "blurb": "The Government-General's English-language annual report for 1937-38: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance, and the rural self-help movement. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193738/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea193738",
     "blank_marking": True},
    {"slug": "korea-1938-39", "dir": "Korea_Annual_Report_1938", "model": "Haiku 5.5",
     "title": "Annual Report on Administration of Tyosen 1938-39",
     "publisher": "Government-General of Tyosen, Keizyo, December 1939",
     "blurb": "The Government-General's English-language annual report for 1938-39: population and towns, the budget and accounts, taxes, customs and monopolies, banking, currency and trade, schools, industries and mining, communications, public hygiene, justice, local administration and provincial finance, and the rural self-help movement. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps, organisation charts, the contents and the list of illustrations are not. Table pages were found from contact sheets by Claude Haiku 5.5 and re-checked by Claude Sonnet 5.5; small tables set into the prose may still be missing. Each table page was read twice independently by Haiku from full-resolution crops, and a third time where the two readings differed; a figure stands where at least two readings agree and is otherwise marked unreadable. Tables continued over pages were joined where the column headings match. Printed totals are checked automatically and differences noted; they are kept as read. The one-sentence context notes are written by the model from the text on the same page. This volume was not checked by eye.",
     "scan": "https://archive.org/details/annual-report-on-reforms-and-progress-in-chosen-korea-1938-39/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annual-report-on-reforms-and-progress-in-chosen-korea-1938-39",
     "blank_marking": True},
    {"slug": "korea-1918-21", "dir": "Korea_Annual_Report_1918", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1918-21",
     "publisher": "Government-General of Chosen, Keijo, 1921",
     "blurb": "The Government-General's English-language report for 1918-21, the years of the March First movement and the switch to 'cultural rule': population, government organization, finance and the budget, trade and banking, the government monopolies, education, religion and missions, industry, agriculture and mining, railways and communications, police and the independence agitation, sanitation, justice and local administration, followed by 50 statistical tables. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and the appendices (treaty, rescripts, proclamations) are not. Every text page and the whole statistics section were read. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and cells where the two readings differed went to a third reader (agreement is used, otherwise [?]). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191821/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea191821",
     "blank_marking": True},
    {"slug": "korea-1921-22", "dir": "Korea_Annual_Report_1921", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1921-22",
     "publisher": "Government-General of Chosen, Keijo, 1923",
     "blurb": "The Government-General's English-language report for 1921-22: population, government organization, finance and the budget, taxation, the monopolies, banking and trade, education, religion, industry and agriculture, civil engineering, communications, police and the independence movement, sanitation, justice and local administration, followed by 49 statistical tables. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and the appendices (treaty, rescripts, proclamations) are not. Every text page and the whole statistics section were read. Printed totals that do not add up are kept as printed and noted; every such table, and every table with an unreadable cell, was transcribed a second time independently, and cells where the two readings differed went to a third reader (agreement is used, otherwise [?]). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192122/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192122",
     "blank_marking": True},
    {"slug": "korea-1922-23", "dir": "Korea_Annual_Report_1922", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1922-23",
     "publisher": "Government-General of Chosen, Keijo, 1924",
     "blurb": "The Government-General's English-language report for 1922-23: population, government organization, finance, budgets and taxation, the monopolies, banking and trade, education, religion, industry, mining and agriculture, communications, police and the independence movement, sanitation, justice and local administration. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and the appendices (treaty, rescripts, speeches) are not. Every text page was read. Unlike some other years, this volume has no statistical appendix. Printed totals that do not add up are kept as printed and noted; every such table, and every table with an unreadable cell, was transcribed a second time independently, and cells where the two readings differed went to a third reader (agreement is used, otherwise [?]). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192223/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192223",
     "blank_marking": True},
    {"slug": "korea-1923-24", "dir": "Korea_Annual_Report_1923", "model": "Sonnet 5.5",
     "title": "Annual Report on Reforms and Progress in Chosen 1923-24",
     "publisher": "Government-General of Chosen, Keijo, 1925",
     "blurb": "The Government-General's English-language report for 1923-24: population and occupations, finance, budgets and taxation, monopolies, banking and trade, agriculture, fisheries, mining and industry, education, religion, sanitation, communications, police, justice and local administration. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, maps and the appendices (treaty, rescripts, speeches) are not. Every text page was read. This volume has no statistical appendix. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and both readings agreed on every figure. The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192324/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192324",
     "blank_marking": True},
    {"slug": "korea-1924-25", "dir": "Korea_Annual_Report_1924", "model": "Sonnet 5.5",
     "title": "Annual Report on Administration of Chosen 1924-26",
     "publisher": "Government-General of Chosen, Keijo, December 1927",
     "blurb": "The Government-General's English-language report for 1924-26 (a double-length issue covering two fiscal years): population by occupation, the annual accounts and budgets, taxes and monopolies, banking and trade, fisheries, mining and companies, schools, epidemics, shipping, telephones and postal savings, criminal justice, provinces, local councils and finance, and the populations of principal cities and towns. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive item is labelled 1924-25; the cover reads 1924-26. Only tables are transcribed; the running text, photographs, the map and the appendix documents (treaty, rescripts, speeches) are not. Every text page was read. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192425/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192425",
     "blank_marking": True},
    {"slug": "korea-1926-27", "dir": "Korea_Annual_Report_1926", "model": "Sonnet 5.5",
     "title": "Annual Report on Administration of Chosen 1926-27",
     "publisher": "Government-General of Chosen, Keijo, 1928",
     "blurb": "The Government-General's English-language report for 1926-27: population by occupation, the annual accounts and budgets, taxes and monopolies (ginseng, tobacco, salt), banking, note issue and trade, fisheries, mining and companies, schools, opium and epidemics, railways, shipping, telephones and postal savings, criminal justice, provinces, councils, provincial and municipal finance, and the populations of principal cities and towns. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, the map and the appendix documents (treaty, rescripts, speeches) are not. Every text page was read. The scan ends partway through the appendix list of town populations (after North Keisho); the following page is missing. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192627/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192627",
     "blank_marking": True},
    {"slug": "korea-1927-28", "dir": "Korea_Annual_Report_1927", "model": "Sonnet 5.5",
     "title": "Annual Report on Administration of Chosen 1927-28",
     "publisher": "Government-General of Chosen, Keijo, December 1929",
     "blurb": "The Government-General's English-language report for 1927-28 (the series was renamed from 'Reforms and Progress' to 'Administration'): population by province and occupation, the annual accounts and budgets, taxes, customs and monopolies, banking, note issue and trade, fisheries, mining and companies, schools, opium and epidemics, railways, shipping, telephones and postal savings, criminal justice, provinces, councils, provincial and municipal finance, and school associations. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, photographs, the map and the appendix documents (treaty, rescripts, proclamations) are not. Every text page was read. The book's errata slip (pp. 46-51) is noted on the tables it affects. Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192728_202004/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192728_202004",
     "blank_marking": True},
    {"slug": "korea-1928-29", "dir": "Korea_Annual_Report_1928", "model": "Sonnet 5.5",
     "title": "Annual Report on Administration of Chosen 1928-29",
     "publisher": "Government-General of Chosen, Keijo, December 1930",
     "blurb": "The Government-General's English-language report for 1928-29: climate, population by province and occupation, governors-general, the annual accounts and budgets, taxes, customs and monopolies, banking, note issue and trade, leading exports and imports, fisheries, mining and companies, schools, opium and epidemics, cattle exports, railways, shipping, telephones and postal savings, criminal justice, provinces, councils, provincial and municipal finance, and public schools. Each table carries a one-sentence note on its context in the report.",
     "source": "LLM-transcribed from the Internet Archive scan (the Internet Archive item is labelled 1927-28, but its title page reads 1928-1929).",
     "gaps": "Only tables are transcribed; the running text, photographs, the map and the appendix documents (treaty, rescripts, proclamations) are not. Every text page was read. Printed page 54 is missing from the scan (a photograph plate is in its place), so the trade-by-year table lacks its first part (1923-1929). Printed totals that do not add up are kept as printed and noted; every such table was transcribed a second time independently, and disputed cells went to a third reader (agreement settles a cell; otherwise it is marked unreadable). The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192728/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192728",
     "blank_marking": True},
    {"slug": "korea-1929-30", "dir": "Korea_Annual_Report_1929-30",
     "title": "Annual Report on Administration of Chosen 1929-30",
     "publisher": "Government-General of Chosen, Keijo, 1931",
     "blurb": "The Government-General's English-language annual report on colonial Korea: population, finance, banking, trade, education, industry, communications, police, public health and local administration.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan is missing the text page beside each photo plate (printed pp. 66, 74, 82, 92, 96, 100, 104, 140, 152 and 172), as well as the appendix tables of weights and measures and of governors. On p. 13 the Total column is in a different typeface from the rest of the table, which may mean the scan was retouched.",
     "scan": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/annualreportonreformsandprogressinchosenkorea192930"},
    {"slug": "korea-nenkan-1926", "dir": "Chosen_Nenkan_1925",
     "title": "朝鮮年鑑 1926", "subtitle": "Chōsen nenkan (Korea Yearbook), 大正十五年版 (Taishō 15 edition), published 1925",
     "publisher": "朝鮮ガイダンス社, 1925 (大正十四年十一月發行)",
     "blurb": "A Japanese-language annual of colonial Korea: land and population, administration and officials, schools, courts and police, communications, finance, banking, agriculture, fisheries, forestry, sericulture, companies, newspapers and prices. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Running text is not transcribed: legal clauses (官制, 事務分掌), the tax-rate section (税率), 間島及琿春, the preface and contents, and the 歴代年號對照表 chronology; small inline tables in the 間島及琿春 text are included. Lists (officials, councillors, schools, post offices, police stations, companies, newspapers) are tables; the imperial household, grain-dealers' associations, exchanges and banks are on the directory page. Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping could not be read with certainty the cell is blank, and every figure changed in the check pass was confirmed by a second, blind reading or left blank. 手形交換高表 (p. 275) is almost entirely blank for this reason. Land distances keep the printed 「、」 between 里 and 町 (2、18 = 2里18町). The vegetable-crop table printed on p. 414 belongs to the agriculture chapter.",
     "scan": "https://dl.ndl.go.jp/pid/976190/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/976190"},
    {"slug": "korea-tokanfu-1908", "dir": "Tokanfu_Tokei_1908",
     "title": "第一次統監府統計年報 1908", "subtitle": "Tōkanfu tōkei nenpō (Statistical Annual of the Residency-General of Korea), first annual, mainly 明治39年 (1906)",
     "publisher": "統監官房文書課, 京城, 1908 (明治四十一年一月二十三日發行)",
     "blurb": "The first statistical annual of the Japanese Residency-General in Korea (統監府), published in January 1908 with figures mainly for 1906 (明治39年) and comparisons back to about 1902. Its 217 numbered tables cover land and climate, population (Japanese residents, Koreans and other foreigners), education, charities, police and prisons, civil and criminal justice, banking and money, industry and agriculture, fisheries, companies and factories, trade, railways, post, telegraph and telephone, finance (the Residency-General, the Korean government and the Japanese settlements) and officials.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 14472133).",
     "gaps": "Only tables are transcribed; the contents, 凡例 and the folding map are not. Figures are printed as kanji numerals in vertical type and are given here in Arabic numerals; tables are turned into ordinary rows and columns. Where the only doubt was how a stack of 一/二/三 strokes groups and exactly one reading made a printed total reconcile, that reading is used and noted. Every figure that a transcriber changed after a total check was read again by a second, independent reader. The two densest bank tables (第一〇三表 and 第一〇六表) were transcribed twice independently and every disagreement was judged by a third reader; cells on which the readings could not be reconciled are marked [?]. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/14472133/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/14472133",
     "blank_marking": True},
    {"slug": "korea-tokanfu-1939", "dir": "Chosen_Sotokufu_Tokei_1939",
     "title": "朝鮮總督府統計年報 1939", "subtitle": "Chōsen Sōtokufu tōkei nenpō (Statistical Annual of the Government-General of Korea), 昭和十四年 (Shōwa 14), published 1941",
     "publisher": "朝鮮總督府, 京城, 1941 (昭和十六年三月刊行)",
     "blurb": "The Government-General of Korea's statistical annual for 1939 (昭和14年), published in March 1941: a general summary table followed by 441 numbered tables in 21 chapters — land, population, agriculture, forestry, fisheries, mining and manufacturing, commerce and banking, trade, prices and wages, public works and water transport, posts and telegraphs, railways, the government monopolies, shrines and education, religion and social work, police, public health, courts, registration and deposits, prisons, public finance, and officials and pensions — with a table of weights and measures. Most tables give a run of years from about 1930 (some from 1910) and a breakdown by province for 1939; manufacturing output is given item by item and province by province for both 1939 and 1938. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1452398).",
     "gaps": "All tables are transcribed, including the summary boxes on the chapter title pages and the appendix of weights and measures; the contents pages and the 凡例 are not. Tables printed across both pages of a spread are joined into one; a few very long tables were read in sections by different readers and joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted, as are a few printed numbering errors (tables 88 and 89 are headed 103 and 104 in the book; table 168 is listed in the contents without a title or page). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. About 160 of some 245,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. Two spot checks, in which a second model re-transcribed six tables independently, agreed on 99.8% of figure cells.",
     "scan": "https://dl.ndl.go.jp/pid/1452398/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1452398",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "korea-boeki-1939", "dir": "Chosen_Boeki_Tokei_1939",
     "title": "朝鮮防疫統計 1939", "subtitle": "Chōsen bōeki tōkei (Epidemic Prevention Statistics of Korea), 昭和十四年 (Shōwa 14), published 1941",
     "publisher": "朝鮮總督府警務局, 京城, 1941 (昭和十六年四月一日發行)",
     "blurb": "The Police Bureau of the Government-General of Korea's annual of epidemic-prevention statistics for 1939 (昭和14年), published in April 1941: 76 numbered tables in three parts. Acute infectious diseases (傳染病, tables 1–65) — cholera, dysentery, typhoid, paratyphoid, smallpox, typhus, scarlet fever, diphtheria and epidemic meningitis — are given by province, by month, by age group and by occupation, each split between Japanese (內), Koreans (鮮) and foreigners (外), with a run of years back to 1910 or the 1920s; then cases and rates in the main cities, examinations of disease carriers, isolation of patients, infectious-disease hospitals, port quarantine, the supply of sera, vaccines and oral vaccines, preventive inoculations and smallpox vaccination. Chronic infectious diseases (慢性傳染病, 66–74) cover tuberculosis deaths by province, age and occupation, tuberculosis and leprosy institutions, leprosy patients (including the Sorokdo leprosarium) and trachoma examinations; endemic diseases (地方病, 75–76) lung fluke and malaria. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1880961).",
     "gaps": "All 76 tables are transcribed; the 凡例, the contents and the map of Korea are not. Each table is printed across both pages of a spread and is given here as one table, including those that run over several spreads. The book has an unusual number of printed totals that do not add up (a check of the scan confirmed several, e.g. a monthly total of 189 where the parts give 280): they are kept as printed and noted in each table, as are a few printed numbering and heading errors. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Province names and a few characters are given in the old forms the book uses (忠淸, 慶尙, 黃, 齡, 檢査). 17 of about 130,000 figure cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1880961/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1880961",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "korea-boeki-1938", "dir": "Chosen_Boeki_Tokei_1938",
     "title": "朝鮮防疫統計 1938", "subtitle": "Chōsen bōeki tōkei (Epidemic Prevention Statistics of Korea), 昭和十三年 (Shōwa 13), published 1939",
     "publisher": "朝鮮總督府警務局, 京城, 1939 (昭和十四年十月十五日發行)",
     "blurb": "The Police Bureau of the Government-General of Korea's annual of epidemic-prevention statistics for 1938 (昭和13年), published in October 1939: 76 numbered tables in three parts, laid out exactly as in the following year's edition. Acute infectious diseases (傳染病, tables 1–65) — cholera, dysentery, typhoid, paratyphoid, smallpox, typhus, scarlet fever, diphtheria and epidemic meningitis — are given by province, by month, by age group and by occupation, each split between Japanese (內), Koreans (鮮) and foreigners (外), with a run of years back to the 1910s or 1920s; then cases and rates in the main cities (1934–38), examinations of disease carriers, isolation of patients, infectious-disease hospitals, port quarantine, the supply of sera, vaccines and oral vaccines, preventive inoculations and smallpox vaccination. Chronic infectious diseases (慢性傳染病, 66–74) cover tuberculosis deaths by province, age and occupation, tuberculosis and leprosy institutions, leprosy patients (including the Sorokdo leprosarium) and trachoma examinations; endemic diseases (地方病, 75–76) lung fluke and malaria. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1880962).",
     "gaps": "All 76 tables are transcribed; the 凡例 and the contents are not. Each table is printed across both pages of a spread and is given here as one table, including those that run over several spreads. As in the 1939 edition, many printed totals do not add up: they are kept as printed and noted in each table, as are printed heading and label errors (for example 全鮮北道 for 全羅北道 in table 30, and table 52 headed 道別 where the contents has 病別). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Province names and a few characters are given in the old forms the book uses (忠淸, 慶尙, 黃, 齡, 檢査). 30 of about 77,000 figure cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1880962/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1880962",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "korea-nenkan-1940", "dir": "Chosen_Nenkan_1939",
     "title": "朝鮮年鑑 1940", "subtitle": "Chōsen nenkan (Korea Yearbook), 昭和十五年度版 (Shōwa 15 edition), published 1939",
     "publisher": "京城日報社, 京城, 1939 (昭和十四年十月一日發行)",
     "blurb": "Chōsen nenkan (朝鮮年鑑), 1940 (Shōwa 15) edition, published by the Keijō nippō newspaper in October 1939, is a Japanese-language annual of colonial Korea. Its 36 sections run from the imperial house, the Korean royal family and the Japanese cabinets through Korean history and the Government-General's record, land, climate, population and defence, to administration, finance, the economy (banking, companies, trade, prices), industries (agriculture, sericulture, livestock, forestry, fisheries, mining, manufacturing), transport, posts and telegraphs, justice, prisons, police, public health, religion, education, public works, social work, labour, the press and publishing, arts and letters, cities, historic sites, sport, the armed forces of the world and international affairs. Most figures are for 1937–38 with series back to 1910. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text, chronologies, the 目次, advertisements, maps and organisation charts are not. The statistics are printed in very small, condensed kanji numerals, often two or three digits to one character space, and the scan is heavily compressed: many stacks of 一/二/三 strokes cannot be grouped with certainty, so about 8% of figure cells are marked unreadable (red hatching); a plain empty cell is empty in the original. Where the grouping was the only doubt and exactly one reading made the printed total reconcile, that reading is used and noted in the table's notes. A partial check pass re-read the cells flagged by the first readers; every figure it changed was confirmed by a second, blind reading or marked unreadable. Printed totals that do not add up are kept as printed and noted. Weather tables print sub-zero temperatures without a sign, as in the original. The separately printed supplement 朝鮮人名錄 is not part of this copy.",
     "scan": "https://dl.ndl.go.jp/pid/1708348/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1708348",
     "blank_marking": True},
    {"slug": "korea-1935", "dir": "Chosen_Jijo_1935",
     "title": "朝鮮事情 1935", "subtitle": "Chōsen jijō (Conditions in Korea), 昭和十年版 (Shōwa 10 edition)",
     "publisher": "朝鮮總督府, 京城, 1934 (昭和九年十二月發行)",
     "blurb": "Chōsen jijō (朝鮮事情), 1935 (Shōwa 10) edition, published by the Government-General of Korea in December 1934, is the colonial government's official handbook on Korea, surveying in 23 chapters its geography and population, transport and communications, local administration, social work, education, public finance and banking, government monopolies, agriculture, commerce, industry, trade, forestry, mining, fisheries, rites and religion, police, public health, justice, mapping, historical research and military affairs, and Koreans in Manchuria. Its tables give mostly 1933–34 figures: population and households by province, occupation and Japanese home prefecture; railways, shipping, postal savings and utilities; tax rates; schools; banks and financial associations; tobacco, ginseng, salt and opium; crops, grain inspection, livestock and warehouses; companies, industrial output and trade by country, port and commodity; forestry and erosion control; mining claims and output; fisheries; royal halls, tombs and Confucian academies; police and medical personnel; and the deployment of the army in Korea. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text (most of the book) and the photo plates are not, and the folding map was not photographed in the scan. Inline tax-rate schedules are given as tables. Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping could not be read with certainty the cell is blank, and every figure changed in the check pass was confirmed by a second, blind reading or left blank. The postal money-order table (p. 27) is thin for this reason. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1225098/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1225098"},
    {"slug": "korea-1940", "dir": "Chosen_Jijo_1940",
     "title": "朝鮮事情 1940", "subtitle": "Chōsen jijō (Conditions in Korea), 昭和十五年版 (Shōwa 15 edition)",
     "publisher": "朝鮮總督府, 京城, 1939 (昭和十四年十二月發行)",
     "blurb": "Chōsen jijō (朝鮮事情), 1940 (Shōwa 15) edition, is the Government-General of Korea's official handbook on the colony, surveying in 27 chapters its geography and population, administration, finance and taxation, education, justice, police, public health, monopolies, transport and communications, banking, agriculture, forestry, fisheries, mining, industry, commerce, trade, social work, wartime mobilization and military affairs, and Koreans abroad. The tables in the text give mostly 1938–39 figures (population and households, tax rates, schools, medical facilities, railways and shipping, banks, crops and livestock, erosion-control plans, mining claims, trade by country and port, Korean settlers in Manchuria), while the appendix of 84 reference statistical tables sets 1910–11 against 1938 figures, often alongside Japan proper and the other colonies. A list of cities, counties and islands printed on the back of the folding map completes the set. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text (most of the book), the photo plates and the folding map are not. Inline tax-rate schedules are tables; the fold-out organisation chart of the Government-General is given as a list, and the list of 府・郡・島 on the back of the map is included. Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping could not be read with certainty the cell is blank, and every figure changed in the check pass was confirmed by a second, blind reading or left blank. The postal money-order and savings tables (p. 179) are mostly blank because their type is too small on this scan. The appendix errata slip is transcribed as a table; its corrections are noted but not applied, and three of its quoted errors do not match what the page prints.",
     "scan": "https://dl.ndl.go.jp/pid/1114413/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1114413"},
    {"slug": "korea-1942", "dir": "Chosen_Jijo_1942",
     "title": "朝鮮事情 1942",
     "subtitle": "Chōsen jijō (Conditions in Korea), 昭和十七年版 (Shōwa 17 edition)",
     "publisher": "朝鮮總督府, 京城, 1941 (昭和十六年十二月發行)",
     "blurb": "Chōsen jijō (朝鮮事情), 1942 (Shōwa 17) edition, published in December 1941, is the Government-General of Korea's official handbook on the colony, surveying in 27 chapters its geography and population, administration, finance, banking, agriculture, forestry, fisheries, mining, industry, commerce, trade, monopolies, transport and communications, shrines and religion, education, justice, social work, military relief, police, public health, the National Total Strength Movement, mobilization, price control, propaganda, the compilation of Korean history, military affairs, and Koreans abroad. The tables in the text give mostly 1939–41 figures (population by province, the Government-General's organization and budget, banks and financial associations, crops and sericulture, forestry and erosion control, mining claims, companies, trade, railway, tramway and motor lines, postal services, schools, medical facilities, military districts, Korean settlers in Manchuria), while the appendix of 74 reference statistical tables sets 1910–11 against late-1930s or 1940 figures, often alongside Japan proper and the other colonies. A list of cities, islands and counties printed on the back of the folding map completes the set. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text (most of the book), the photo plates and the folding map are not. The fold-out organisation chart is given as a list, and the list of 府・島・郡 on the back of the map is included. Printed pp. 265–266 are missing from the scan (placeholder sheets). Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping could not be read with certainty the cell is blank, and every figure changed in the check pass was confirmed by a second, blind reading or left blank. A heavy ink stroke in the original hides the figures of appendix table 54 (緬羊). Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1141394/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1141394"},
    {"slug": "korea-1943", "dir": "Chosen_Jijo_1943",
     "title": "朝鮮事情 1943",
     "subtitle": "Chōsen jijō (Conditions in Korea), 昭和十八年版 (Shōwa 18 edition)",
     "publisher": "朝鮮總督府, 京城, 1942 (昭和十七年十二月發行)",
     "blurb": "Chōsen jijō (朝鮮事情), 1943 (Shōwa 18) edition, published in December 1942, is the Government-General of Korea's official handbook on the colony, surveying in 27 chapters its geography and population, administration, agriculture, forestry, fisheries, mining, industry, commerce, finance and banking, trade, monopolies, transport and communications, shrines and religion, education, justice, social work, military relief, police, public health, the National Total Strength Movement, mobilization, price control, propaganda, the compilation of Korean history, military affairs, and Koreans abroad. The tables in the text give mostly 1940–42 figures (population by province and occupation, the Government-General's organization and budget, crops and sericulture, forestry and erosion control, mining claims, banks and financial associations, taxes, railway, tramway and motor lines, postal services, schools, medical facilities, military districts, Korean settlers in Manchuria), while the appendix of 69 reference statistical tables sets 1910–11 against 1940 or 1941 figures, often alongside Japan proper and the other colonies. A list of cities, islands and counties printed on the back of the folding map completes the set. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text (most of the book), the photo plates and the folding map are not. The fold-out organisation chart is given as a list, and the list of 府・島・郡 on the back of the map is included. Entries blacked out in the original (wartime censorship) are marked [墨消]. Unreadable cells are marked with red hatching; a plain empty cell is empty in the original. Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping was the only doubt and exactly one reading made the printed total reconcile, that reading is used and noted in the table's notes; otherwise the cell is marked unreadable. Every figure changed in the check pass was confirmed by a second, blind reading or marked unreadable. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1141412/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1141412",
     "blank_marking": True},
    {"slug": "korea-1944", "dir": "Chosen_Jijo_1944",
     "title": "朝鮮事情 1944", "subtitle": "Chōsen jijō (Conditions in Korea), 昭和十九年版 (Shōwa 19 edition)",
     "publisher": "朝鮮總督府, 京城, 1943 (昭和十八年十二月發行)",
     "blurb": "Chōsen jijō (朝鮮事情), 1944 (Shōwa 19) edition, is the Government-General of Korea's official handbook on the colony, surveying in 27 chapters its geography and population, administration, agriculture, forestry, fisheries, mining, industry, commerce, finance and banking, trade, monopolies, transport and communications, shrines and religion, education, justice, social work, military relief, police, public health, wartime mobilization, price control and propaganda, military affairs, and Koreans abroad. The tables in the text give mostly 1941–43 figures (population by province and occupation, crops and sericulture, forestry and erosion control, mining claims, banks and financial associations, railway and tramway lines, postal services, schools, medical facilities, military districts, Korean settlers in Manchuria), while the appendix of 69 reference statistical tables sets 1910–11 against early-1940s figures, often alongside Japan proper and the other colonies. A list of cities, islands and counties printed on the back of the folding map completes the set. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan.",
     "gaps": "Only tables and lists are transcribed; the running text (most of the book), the photo plates, the organisation chart and the folding map are not; the list of 府・島・郡 on the back of the map is included. Many figures are printed as tiny stacks of 一/二/三 strokes: where the grouping could not be read with certainty the cell is blank, and every figure changed in the check pass was confirmed by a second, blind reading or left blank. Printed totals that do not add up are kept as printed and noted. Some pages carry a reader's pencil marks; one figure hidden under a pencil circle is blank.",
     "scan": "https://dl.ndl.go.jp/pid/1141430/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1141430"},
    {"slug": "manchuria-1929", "dir": "Manchuria_Progress_1929",
     "title": "Report on Progress in Manchuria 1929", "subtitle": "Report on Progress in Manchuria, 1907–1928",
     "publisher": "The South Manchuria Railway, Dairen, March 1929",
     "blurb": "The South Manchuria Railway Company's English-language review of Manchuria's development over its first twenty years, 1907–1928: geography and population, historical background, the Kwantung Leased Territory and Railway Zone, the Railway Company's own lines, ports, mines, works and finances, trade, agriculture, mining, forestry and fishery, manufacturing, currency and credit, education and sanitation, with appended treaties and agreements. Tables give the Company's accounts and traffic, Kwantung revenue and posts, foreign trade by country, port and commodity, crops, livestock, timber, salt, industry, note issues, schools and hospitals, mostly as series from 1907 to 1927.",
     "source": "LLM-transcribed from the Internet Archive scan (University of Illinois copy).",
     "gaps": "Only tables and lists are transcribed; the running text, photographs, maps, charts without printed figures, the contents and the index are not. The pages with tables were found from contact sheets and only those pages were read. Printed pp. 7–8 are missing from the scan. The Internet Archive item also contains the Second Report on Progress in Manchuria to 1930, bound in after this report (from leaf 326); it is not included here. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/report-on-progress-in-manchuria-1907-1928/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/report-on-progress-in-manchuria-1907-1928",
     "blank_marking": True},
    {"slug": "manchuria-1931", "dir": "Manchuria_Progress_1931",
     "title": "Second Report on Progress in Manchuria 1931", "subtitle": "Second Report on Progress in Manchuria to 1930",
     "publisher": "The South Manchuria Railway, Dairen, 1931",
     "blurb": "The South Manchuria Railway Company's second English-language review of Manchuria, bringing its 1929 report up to 1930: geography and population, history, the Kwantung Leased Territory and Railway Zone, communications, the Railway Company's lines, ports, mines, iron works and finances, trade, agriculture, mining, forestry and fishery, manufacturing and labour, currency and banking, education and sanitation, with appended treaties and the 1930 Sino-Japanese tariff agreement. Tables give series mostly from 1907 to 1929: trade by country, port and commodity, the Company's accounts and traffic, crops, livestock, timber, salt, wages and hours, note issues, banks, schools and hospitals.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and lists are transcribed; the running text, photographs, maps, charts without printed figures, the contents and the index are not. The pages with tables were found from contact sheets and only those pages were read. Most scan images are two-page spreads. The inset table on the Port of Dairen fold-out is too small to read in this scan; most of its figures were read from the second copy of this report bound into the Internet Archive item of the 1929 report (leaf 700), and four remain unreadable. Printed totals that do not add up are kept as printed and noted; several recur unchanged from the 1929 report.",
     "scan": "https://archive.org/details/second-report-on-progress-in-manchuria-to-1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/second-report-on-progress-in-manchuria-to-1930",
     "blank_marking": True},
    {"slug": "manchuria-1936", "dir": "Manchuria_Progress_1936",
     "title": "Fifth Report on Progress in Manchuria 1936", "subtitle": "Fifth Report on Progress in Manchuria to 1936",
     "publisher": "The South Manchuria Railway, Dairen, 1936",
     "blurb": "The South Manchuria Railway Company's fifth English-language report, covering Manchoukuo's first years to 1936 in nine chapters: political development, financial rehabilitation (currency reform, banking, taxes, the salt gabelle), construction, transport and communications, development of resources, industrial expansion, foreign trade, immigration and settlement, and education, with appendices on the Railway Company, statistics on Manchuria and documentary material including the revised import and export tariff. Tables give budgets, bank and Central Bank statements, railway, bus, river and air services, crops, livestock, minerals, salt, fisheries, new corporations, trade by country and port, immigration and schools, mostly for 1931–1935.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and lists are transcribed; the running text, photographs, maps, charts without printed figures, the contents and the index are not. The pages with tables were found from contact sheets and only those pages were read. Most scan images are two-page spreads. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/fifth-report-on-progress-in-manchuria-to-1936/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/fifth-report-on-progress-in-manchuria-to-1936",
     "blank_marking": True},
    {"slug": "manchuria-1939", "dir": "Manchuria_Progress_1939",
     "title": "Sixth Report on Progress in Manchuria 1939", "subtitle": "Sixth Report on Progress in Manchuria to 1939",
     "publisher": "The South Manchuria Railway, Dairen, 1939",
     "blurb": "The South Manchuria Railway Company's sixth English-language report, on Manchoukuo to 1939 in eight chapters: political development, judicial reorganization, the abolition of extraterritoriality, industrial expansion under the Five-Year Plan, financial rehabilitation, foreign trade, construction and Japanese immigration and settlement, with appendices on the Railway Company, statistics on Manchuria and documentary material, including the revised customs tariff of 1938. Tables give provinces, police and courts, companies and factories, investments, banking, trade, railways and highways, settlements and immigrants, and appendix series mostly for 1932–1938.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and lists are transcribed; the running text, photographs, maps, charts without printed figures, the contents and the index are not. The pages with tables were found from contact sheets and only those pages were read. Most scan images are two-page spreads. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/sixth-report-on-progress-in-manchuria-to-1939/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/sixth-report-on-progress-in-manchuria-to-1939",
     "blank_marking": True},
    {"slug": "manchuria-year-book-1931", "dir": "Manchuria_Year_Book_1931", "model": "Haiku 5.5", "title": "The Manchuria Year Book 1931", "publisher": "Tōa Keizai Chōsakyoku (East-Asiatic Economic Investigation Bureau), Tokyo, 1931", "blurb": "The first edition of the Tokyo bureau's English-language yearbook on Manchuria, compiled before the Manchurian Incident: geography, history, administration, judicial administration, military and diplomatic affairs, finance, agriculture, forestry, fisheries, mining, industry, transport and communications, domestic and foreign trade, banking and currency, foreign investment, labour and immigration, and education and religion.", "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.", "gaps": "Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading) and tables printed across two facing pages (read as one table from both pages together). Each page was read once by Claude Haiku 5.5 from full-resolution crops, with instructions to place figures by counting the lines of each block rather than by position, because columns in this book are often printed slightly out of line with their row labels; it was not checked by eye. Unreadable figures are marked, printed totals that do not add up are noted and kept as read, and tables continued over pages were joined where the column headings match. Only tables and columnar lists are transcribed; the running text, photographs, maps, the contents and the index are not. The chronology of 1925–1930 (Appendix) is on the Chronologies page, each page read once by Claude Haiku 5.5; dates carried over from a year or month heading are written out in full. The lists of banks and of social welfare institutions are on the Directories page.", "scan": "https://archive.org/details/the-manchuria-year-book-1931/page/n{leaf}/mode/1up", "item": "https://archive.org/details/the-manchuria-year-book-1931", "blank_marking": True},
    {"slug": "manchuria-year-book-1932-33", "dir": "Manchuria_Year_Book_1932", "model": "Haiku 5.5", "title": "The Manchuria Year Book 1932-33", "publisher": "Tōa Keizai Chōsakyoku (East-Asiatic Economic Investigation Bureau), Tokyo, 1932", "blurb": "The second edition, rewritten after the Manchurian Incident and the founding of Manchoukuo (some two hundred statistical tables): geography, history, administration, judicial administration, military and foreign affairs, finance, agriculture, fisheries, mining, industry, transport and communications, business organization, foreign trade by port and commodity, currency and banking, foreign investment, labour and immigration, education and religion, and medicine and sanitation.", "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.", "gaps": "Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading) and tables printed across two facing pages (read as one table from both pages together). Each page was read once by Claude Haiku 5.5 from full-resolution crops, with instructions to place figures by counting the lines of each block rather than by position, because columns in this book are often printed slightly out of line with their row labels; it was not checked by eye. Unreadable figures are marked, printed totals that do not add up are noted and kept as read, and tables continued over pages were joined where the column headings match. Only tables and columnar lists are transcribed; the running text, photographs, maps, the contents and the index are not. The two appendices (a table of outstanding events in Manchurian history, and a chronology from January 1931 to October 1932) are on the Chronologies page, each page read once by Claude Haiku 5.5; dates carried over from a year or month heading are written out in full, and ditto marks are replaced by the date above. A short list of social welfare institutions is on the Directories page.", "scan": "https://archive.org/details/manchuria-year-book-1932-33/page/n{leaf}/mode/1up", "item": "https://archive.org/details/manchuria-year-book-1932-33", "blank_marking": True},
    {"slug": "manchoukuo-1934", "dir": "Manchoukuo_Year_Book_1934", "model": "Haiku 5.5", "title": "The Manchoukuo Year Book 1934", "note": "Incomplete scan: ends at printed p. 640", "publisher": "Tōa Keizai Chōsakyoku (East-Asiatic Economic Investigation Bureau), Tokyo, June 1934", "blurb": "The third edition, renamed for the new state: geography and population, history, administration, maintenance of internal peace, judicial administration, defence, foreign affairs, finance, agriculture, forestry, fisheries, mining, industry, transport and communications, business organization, foreign trade, currency and banking, and the start of the chapter on foreign investment.", "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.", "gaps": "Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading) and tables printed across two facing pages (read as one table from both pages together). Each page was read once by Claude Haiku 5.5 from full-resolution crops, with instructions to place figures by counting the lines of each block rather than by position, because columns in this book are often printed slightly out of line with their row labels; it was not checked by eye. Unreadable figures are marked, printed totals that do not add up are noted and kept as read, and tables continued over pages were joined where the column headings match. Only tables and columnar lists are transcribed; the running text, photographs, maps, the contents and the index are not. Incomplete scan: the scan ends at printed p. 640, early in Chapter XIX (Foreign Investments), so Chapters XX–XXIV (labour and immigration, education, religion, medicine and sanitation, social welfare), the appendices (directory of government offices, institutions, businesses and newspapers; Who's Who in Manchoukuo; customs tariff; chronology) and the index are missing.", "scan": "https://archive.org/details/manchoukuo-year-book-1934/page/n{leaf}/mode/1up", "item": "https://archive.org/details/manchoukuo-year-book-1934", "blank_marking": True},
    {"slug": "manchuria-jinmeiroku-1935", "dir": "Manchuria_Jinmeiroku_1935", "model": "Gemini 4 Argon (most pages) and Claude Opus 5.5",
     "title": "在滿日滿人名録 1935", "subtitle": "Zaiman Nichi-Man jinmeiroku, with 在滿主要機關職員表 (supplement to the 1936 edition of the Manshū nenkan)",
     "publisher": "滿洲日日新聞社 (Manshū Nichinichi Shinbunsha), Dairen, November 1935",
     "blurb": "A pocket directory of about 3,270 Japanese and Manchurian (Chinese) residents of Manchuria in office or business as of 1 October 1935, issued as a supplement to the Manshū nenkan (滿洲年鑑) for 1936. The people's list (pp. 1–90) gives each person's posts, firm and address; Japanese names are in kana (gojūon) order and Manchurian names follow, ordered by the number of strokes. Military personnel are excluded. The second part, 在滿主要機關職員表 (pp. 91–108), lists the staff of the principal offices: the Japanese Embassy and consulates, the Kwantung Bureau and Kwantung Government, police, courts, schools, the Dairen and Port Arthur city offices, the South Manchuria Railway, the Manchukuo government ministries and provincial offices, city administrations, the Central Bank of Manchou, chambers of commerce and local committees, and a table of county heads and councillors (縣長參事官一覽) by province. Entries are given in Japanese with the old character forms as printed.",
     "source": "LLM-transcribed from the National Diet Library scan (public domain).",
     "gaps": "Everything in the two lists is transcribed; the title page, preface, contents and colophon are not. Each two-page spread was read once, from four half-page crops, by Claude Opus 5.5 (printed pp. 1–17) or Gemini 4 Argon (pp. 18–108), with no checking by eye. Unreadable characters are marked [?] (39 in all). In a test spread read by eye, Opus misread no names; Argon misread three of 73, choosing a plausible character where the print is unclear instead of marking it, so names on pp. 18–108 deserve a look at the scan. Entries running over from one spread to the next are joined; in the staff lists, 同 (same post as above) is written out with (同) after it.",
     "scan": "https://dl.ndl.go.jp/pid/1916917/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1916917",
     "dir_only": True, "blank_marking": True},
    {"slug": "manchukuo-directory-1938", "dir": "Manchukuo_Directory_1938",
     "title": "Manchukuo Directory 1938-9", "subtitle": "The Directory of Manchoukuo / 滿洲商工年鑑, 1938–39",
     "publisher": "The Orient Publishing Company (Manchuria Daily News), Dairen, 1938",
     "blurb": "A bilingual (English and Japanese) business directory of Manchukuo, with descriptions of the country and its cities. The directory lists firms, offices, banks, hospitals, schools and officials city by city — Manchouli, Hailar, Tsitsihar, Peian, Taoan, Harbin, Kirin, Hsinking, Kungchuling, Antung, Mukden, Fushun, Liaoyang, Yingkou, Pulantien, Dairen, Port Arthur and Rashin — each entry printed first in English and then in Japanese, with trade, telephone, address and proprietor or manager; a list of German firms in Japan and Manchukuo closes the book. Tables give Manchukuo's area, population, finance, production and trade, South Manchuria Railway statistics, and city facts and fares.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only the directory entries and the tables are transcribed; the city descriptions, advertisements, photographs and maps are not. Each directory entry keeps the English and Japanese printings of a firm together, so a firm can be found by either name; where the two printings disagree (telephone numbers, addresses, a different Japanese name) both are kept as printed and the entry has a note. Doubtful Japanese names were re-read at high zoom; unreadable characters are marked [?]. Many printed pages are missing from the scan (among them parts of Taoan, Taonan, Peian to Imienpo, Kungchuling, Ssupingkai, Kaiyuan, Tieling, Liaoyang, Anshan, Tashihchiao and Pulantien), so those cities are incomplete or absent.",
     "scan": "https://archive.org/details/manchukuo-directory-1938-9/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/manchukuo-directory-1938-9",
     "dir_cards": True,
     "dir_pinyin": {"Dairen": "Dalian", "Mukden": "Fengtian", "Hsinking": "Xinjing", "Antung": "Andong", "Port-Arthur": "Lüshun", "Tsitsihar": "Qiqihar", "Kirin": "Jilin", "Manchouli": "Manzhouli", "Peian": "Bei'an", "Taoan": "Tao'an", "Liao-Yang": "Liaoyang", "Pulantien": "Pulandian", "Rashin": "Rajin", "Kungchuling": "Gongzhuling"},
     "dir_places": ["Dairen", "Mukden", "Harbin", "Hsinking", "Antung", "Fushun", "Hailar", "Port-Arthur", "Yingkou", "Tsitsihar", "Kirin", "Manchouli", "Peian", "Taoan", "Liao-Yang", "Pulantien", "Rashin", "Kungchuling"],
     "blank_marking": True},
    {"slug": "japan-jutaku-1942", "dir": "Jutaku_Mondai_1942",
     "title": "住宅問題統計調査資料 1942", "subtitle": "Jūtaku mondai tōkei chōsa shiryō (Statistical Materials on the Housing Problem)",
     "publisher": "住宅營團研究部 編 (Housing Corporation, Research Department), 住宅營團, Tokyo, 昭和17年7月 (July 1942); printed by 一成社",
     "blurb": "A compilation of housing statistics made by the research department of the Housing Corporation (Jūtaku Eidan), the wartime public body set up in 1941 to build workers' housing. It brings together figures on urban population growth, the 1930 census returns on dwellings by rooms and household size (all Japan, Tokyo, Osaka), surveys of housing, rents, apartments, boarding houses and rented rooms in the large and industrial cities, Tokyo's housing survey, indices of building wages, building-material prices and the cost of living, household budget surveys in Japan and Europe, infant mortality, and surveys of substandard housing districts in Tokyo and Osaka.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1276688).",
     "gaps": "Every table is transcribed, with the printed contents; the foreword is not. The scan is a black-and-white microfilm copy with broken strokes and specks; the vertical tables with kanji numerals (pp. 4, 12–15, 58–63) were read by Opus, the rest by Sonnet. Unreadable cells are marked [?] (83 of about 12,400 figures, 0.7%); a plain empty cell is empty in the original. Printed totals that do not add up are kept as printed and noted; where the only doubt was a 3 or 8 (or how a stack of 一/二/三 strokes groups) and exactly one reading made a printed total reconcile, that reading is used and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1276688/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1276688",
     "model": "Sonnet 5.5 and Opus 5.5",
     "blank_marking": True},
    {"slug": "daitoa-koeki-1943", "dir": "Daitoa_Koeki_1943", "group": "other",
     "title": "大東亞交易基本統計表 1943", "subtitle": "Daitōa kōeki kihon tōkeihyō (Basic Trade Statistics of Greater East Asia)",
     "publisher": "日本貿易振興協會 日本貿易研究所東京調査部 編 (Japan Trade Research Institute, Tokyo Research Department), 栗田書店, Tokyo, 昭和18年5月 (May 1943)",
     "blurb": "A wartime compendium of trade and production statistics for the countries of the 'Greater East Asia Co-Prosperity Sphere', compiled largely from League of Nations trade statistics and national returns. Part 1 gives each country's trade (totals, trade by partner country and by commodity, 1935/36–1937/38) for Japan, Manchukuo, China, French Indochina, Thailand, Malaya, Burma, British India, Ceylon, the Philippines, the Netherlands Indies, Australia and New Zealand. Part 2 gives world trade in 29 principal raw materials and foodstuffs by partner country (1936–1938); Part 3 compares production and trade of 128 commodities across the three zones of the sphere (A, B and C), and Part 4 gives world production of 54 foodstuffs and minerals, 1936–1939, with appendices on weights and measures and exchange rates.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1871076).",
     "gaps": "Every table in the four parts and the two appendices is transcribed, with the printed contents; the prefaces and explanatory notes are given as footnotes. The commodity tables of Parts 2 and 3 run over several spreads (row blocks and column groups); each spread is one part of its table, as printed. Read by Sonnet sub-agents from the page images. Unreadable cells are marked [?] (153 of about 57,000 figures, 0.3%); a plain empty cell is empty in the original. Printed totals that do not add up are kept as printed and noted; decimal points too faint to see are either supplied (noted) or the figures kept as printed with a space.",
     "scan": "https://dl.ndl.go.jp/pid/1871076/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1871076",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "manchukuo-minsei-1940", "dir": "Minsei_Nenkan_1940",
     "title": "民生年鑑 1940", "subtitle": "Minsei nenkan (Welfare Yearbook), 第4次 (4th issue), covering 康德7年 (1940)",
     "publisher": "滿洲帝國民生部 (Manchukuo Ministry of People's Welfare), 新京, 康德10年7月 (July 1943); printed by 東亞印書局",
     "blurb": "The Manchukuo Ministry of People's Welfare's yearbook for 1940 (康德7年), covering education, social work, religion, labour, public health and the opium suppression programme. The first part is a narrative of the ministry's administration, printed in parallel Chinese and Japanese, with tables set into it: the ministry's staff and staff movements, documents handled, the laws and ordinances of the year, primary and secondary school statistics by province, normal-school and teacher-certification figures, higher-education institutions, school inspectors by province, textbooks printed, social-work bodies and facilities, granary (義倉) assets, welfare commissioners in each city, prisoner after-care, filial-piety and virtue awards, Catholic dioceses, labour-control agreements, plague outbreaks since 1932, medical examinations, and registered opium and narcotic addicts with the opium-smoking places and rehabilitation centres by province. The second part is the statistics, mostly by province and by city, county (縣) and banner (旗): school-age children and school attendance; national schools, higher national schools, national 學舍 and 義塾 schools (schools, classes, pupils by grade, last year's graduates); primary-school entrants, private schools (私塾), primary-school staff and expenditure; secondary schools (schools, classes, pupils, staff, pupils by nationality, applicants, transfers, graduates, expenditure); universities and training institutes; the Hsingan Academy, students abroad, teacher retraining, special education and kindergartens; the national museum, adult and language schools, youth and farmers' training centres, libraries, people's education halls, lecture halls and reading rooms; religious bodies, clergy and believers by faith and province; historic sites, antiquities, scenic places and natural monuments; and public-physician patients, notifiable infectious diseases and vaccination. An appendix gives the same subjects for the Japanese-administered Kwantung Territory and South Manchuria Railway Zone (1940).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1143221).",
     "gaps": "Every table in both parts and the appendix is transcribed; the narrative prose and organisation charts of the first part are not. The statistics were printed as numbered sheets (第一表ノ一, ノ二 …), often one table across both pages of a spread with the row labels only on the left page; each sheet is given as one part of its table, the right-page figures matched to the left-page row labels by order and row counts. Where a sheet begins in the middle of a province, the province name is supplied from the previous sheet and noted. Each spread was read once by Claude Sonnet 5.5 from full-resolution crops of each page. The scan is a 1940s print on poor paper with worn and broken type: commas and decimal points are hard to tell apart, and 1,146 of about 79,000 filled cells (1.5%) could not be read with confidence and are marked [?]. Printed totals that do not add up are kept as printed and noted in each table (there are many misprints); where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Cells printed as “?” in the original are kept as ?. The scan has page 106 twice (frames 65 and 66; frame 65 is a darker duplicate).",
     "scan": "https://dl.ndl.go.jp/pid/1143221/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1143221",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-manchoukuo-1934", "dir": "Japan_Manchoukuo_1934", "group": "manchuria", "model": "Sonnet 5.5 and Opus 5.5",
     "title": "Japan-Manchoukuo Year Book 1934",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1934",
     "blurb": "The first Japan-Manchoukuo Year Book, a Tokyo English-language annual in two parts. The Japan part covers geography, history, population, the Imperial Court, politics, administration, diplomacy, defence, religion, education, justice, health, the press, the arts, public works, labour, social problems, communications, railways, shipping, national finance, banking, insurance, agriculture, sericulture, forestry, fisheries, mining, industry, domestic and foreign trade, Korea, Taiwan, Karafuto, the South Sea Islands, the six great cities and sports. The Manchoukuo part covers the new state's geography, history, government, industry, agriculture, mining, railways, communications, finance, currency, banking, foreign trade, forestry and fishery, education and principal cities, followed by government bulletins, speeches, the text of treaties, a Who's Who of Japan and Manchoukuo, a business directory and a guide to foreign firms.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Complete scan (two files on the Internet Archive). All statistical tables and columnar lists, the Who's Who, the business directory, the list of foreign firms, the diplomatic and consular lists and the dated chronologies are transcribed; the running text, photographs, maps, advertisements and charts without printed figures are not. Pages with tables were found from contact sheets. Sonnet 5.5 agents read most pages and Opus 5.5 agents the large trade returns and spreads; every printed total was re-added, and totals that did not reconcile were re-read on zoomed crops by Opus 5.5 — where the print itself does not add up, the figures are kept as printed and noted. The book's printed contents, with every chapter and section linked to its page of the scan, are on the contents page.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1934/Japan-Manchoukuo%20Year%20Book%201934%20{part}/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1934",
     "blank_marking": True},
    {"slug": "japan-manchoukuo-1936", "dir": "Japan_Manchoukuo_1936", "group": "manchuria", "model": "Sonnet 5.5 and Opus 5.5",
     "title": "Japan-Manchoukuo Year Book 1936",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1936",
     "blurb": "The 1936 edition of the Tokyo English-language annual on Japan and Manchoukuo. The Japan section covers geography, history, geology, population and emigration, the Imperial Court, administration, politics, diplomacy, defence, justice, education, religion, health, the press, labour, social problems, communications, transport, shipping, public and local finance, banking, insurance, agriculture, sericulture, forestry, fisheries, mining, manufacturing, trade, Korea, Taiwan, Karafuto, the South Sea Islands, the six premier cities and sports. The Manchoukuo section covers geography, history, races and tribes, the founding of the state, population, administration, judicature, diplomacy, defence, education, finance, currency, banking, transport, railways, the purchase of the North Manchuria Railway, agriculture, forestry, fishery, mining, industries, foreign trade, sanitation, the Kwantung Leased Territory, the principal cities, Hsingan, Jehol, the South Manchuria Railway, economic relations with Japan and the customs tariff, followed by government bulletins, treaties, a Who's Who, a business directory with the Konzerns of Japan, a bibliography, learned and social institutions and a map index of place names.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Complete scan, except that pp. iv–v of the printed contents pp. 450–451 (Japan, Manufacturing Industries) and pp. 746–747 (Manchoukuo, Transportation) are missing. All statistical tables and columnar lists, the Who's Who, the business directory, the bibliography, the learned and social institutions, the diplomatic and consular lists, the import and export tariffs, the map index and the dated chronologies are transcribed; the running text, photographs, maps, advertisements and charts without printed figures are not. Pages with tables were found from contact sheets. Sonnet 5.5 agents read most pages and Opus 5.5 agents the large or difficult tables; every printed total was re-added, and totals that did not reconcile were re-read on zoomed crops by Opus 5.5 — where the print itself does not add up, the figures are kept as printed and noted. Figures lost in the binding gutter are marked unreadable. The book's printed contents, with every chapter and section linked to its page of the scan, are on the contents page; Japan chapters IX–XXVI, whose contents page is missing, are listed from their opening pages.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1936/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1936",
     "blank_marking": True},
    {"slug": "japan-manchoukuo-1938", "dir": "Japan_Manchoukuo_1938", "group": "manchuria", "model": "Sonnet 5.5 and Opus 5.5",
     "title": "Japan-Manchoukuo Year Book 1938",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1938",
     "blurb": "The 1938 edition of the Tokyo English-language annual on Japan and Manchoukuo, opening with statistical diagrams and economic barometers. The Japan section covers geography, history, geology, population, the Imperial Court, administration, politics, diplomacy, defence, religion, education, justice, health, the press, the arts, public works, communications, labour, social and industrial problems, transport, shipping, finance, banking, insurance, agriculture, sericulture, forestry, fisheries, mining, manufacturing, trade, Korea, Taiwan, Karafuto, the South Sea Islands, the six premier cities and sports, with supplements on Japan's position in North China, texts of official addresses and statements, and the diplomatic and consular service. The Manchoukuo section covers geography, history, the founding of the state, population, administration, judicature, diplomacy, defence, education, finance, currency, banking, transport and communications, railways, agriculture, forestry, aquatic products, mining, industry, foreign trade, sanitation, principal cities, labour, the South Manchuria Railway, the Kwantung Leased Territory, economic relations with Japan and treaties, followed by a Who's Who, a business directory, the Konzerns of Japan, a bibliography and learned and social institutions.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Complete scan (printed pp. 624–625 are scanned twice; the repeat is skipped). All statistical tables and columnar lists, the economic barometers, the officials' directory, the Who's Who, the business directory, the Konzerns of Japan, the bibliography, the learned and social institutions, the diplomatic and consular lists and the dated chronologies are transcribed; the running text, photographs, maps, advertisements, organisation charts and charts without printed figures are not. Pages with tables were found from contact sheets. Sonnet 5.5 agents read most pages and Opus 5.5 agents the large or difficult tables; every printed total was re-added, and totals that did not reconcile were re-read on zoomed crops by Opus 5.5 — where the print itself does not add up, the figures are kept as printed and noted. The book's printed contents, with every chapter and section linked to its page of the scan, are on the contents page; that contents list swaps the titles of Supplements I and II, and the links follow the pages.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1938/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1938",
     "blank_marking": True},
    {"slug": "japan-manchoukuo-1939", "dir": "Japan_Manchoukuo_1939", "group": "manchuria", "model": "Haiku 5.5, Sonnet 5.5 and Opus 5.5",
     "title": "Japan-Manchoukuo Year Book 1939",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1939",
     "blurb": "The 1939 edition of the Tokyo English-language annual on Japan and Manchoukuo, opening with statistical diagrams and economic barometers. The Japan section covers geography, history, geology, population, the Imperial Court, administration, politics, diplomacy, defence, religion, education, justice, health, the press, the arts, public works, communications, labour, social and industrial problems, transport, shipping, finance, banking, insurance, agriculture, sericulture, forestry, fisheries, mining, manufacturing, trade, Korea, Taiwan, Karafuto, the South Sea Islands, the six premier cities and sports, with a supplement on the diplomatic and consular service. The Manchoukuo section covers geography, history, population, administration, justice, defence, education, finance, banking, communications, transport, agriculture, forestry, fisheries, mining, industry, commerce, foreign trade, labour, the South Manchuria Railway and economic policy, with a supplement on Japan's economic position in China, followed by a Who's Who, a business directory, the Konzerns of Japan, a bibliography and learned and social institutions.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Printed pp. 2–3, 6–7, 760–761, 816–817, 1064–1065, 1082–1083, 1138–1139 and 1142–1143 are missing from the scan, so the tables, entries and lists on them are absent. All statistical tables and columnar lists, the economic barometers, the officials' lists, the Who's Who, the business directory, the Konzerns of Japan, the bibliography, the learned and social institutions, the diplomatic and consular lists and the dated chronologies are transcribed; the running text, photographs, maps, advertisements, organisation charts and charts without printed figures are not. Pages with tables were found from contact sheets. Haiku 5.5 agents read the simpler table pages, Sonnet 5.5 agents most other pages and the directories, and Opus 5.5 agents the large or difficult tables; every printed total was re-added, and totals that did not reconcile, doubtful digits and uncertain kanji were re-read on zoomed crops by Opus 5.5 — where the print itself does not add up, the figures are kept as printed and noted. The book's printed contents, with every chapter and most sections linked to their page of the scan, are on the contents page.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1939/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1939",
     "blank_marking": True},
    {"slug": "japan-manchoukuo-1940", "dir": "Japan_Manchoukuo_1940", "group": "manchuria",
     "title": "Japan-Manchoukuo Year Book 1940", "note": "Incomplete scan: large parts of the book are missing",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1940",
     "blurb": "The 1940 edition of the Tokyo yearbook covering Japan and Manchoukuo. The online scan holds only part of the book: the opening statistical diagrams, Japan's national defence and airways, the colonies (Chosen, Taiwan, Karafuto and the South Sea Islands), and the whole Manchoukuo part — geography, population and immigration, administration, judicature, diplomacy, defence, education, state finance, banking, communications, transport, agriculture, forestry, fisheries, mining, manufacturing, foreign trade, sanitation, labour, the South Manchuria Railway, economic policy and the Kwantung Leased Territory — with the start of the list of learned and social institutions.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Incomplete scan: printed pp. 16–109, 118–207, 210–503 and 878–1185 are not in the online copy, so most of the Japan part, the Who's Who and the business directory are missing, and the scan ends at p. 1203 in the list of learned and social institutions. Two table fragments whose first page is missing are transcribed as fragments. Only tables, lists and that directory page are transcribed; the running text, photographs, maps, advertisements, charts without printed figures, the contents and the bibliography are not. The pages with tables were found from contact sheets and only those pages were read. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1940",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1936", "dir": "Nanyo_Tokei_1936", "group": "south-seas",
     "title": "南洋廳統計年鑑 1936", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第六回 (No. 6), figures mainly for 昭和7–11 (1932–1936), published 昭和13年3月 (March 1938)",
     "publisher": "南洋廳長官官房調査課, パラオ (昭和十三年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its sixth edition: 220 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1932 to 1936 for the whole territory and then 1936 for each branch office (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463314).",
     "gaps": "All 220 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the maps, the statistical charts (統計圖表), the prose survey (概說) and the colophon are not. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Figures are kept exactly as printed, including points or spaces printed where a comma or decimal point is expected. Small figures printed above a cell (foreigners, half-year taxpayers, quantities) are given in the same cell after the figure; in the trade tables many of these small quantities are too blurred to read and are marked [?]. The volume's errata slip (正誤表, 45 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 380 of some 82,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463314/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463314",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1935", "dir": "Nanyo_Tokei_1935", "group": "south-seas",
     "title": "南洋廳統計年鑑 1935", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第五回 (No. 5), figures mainly for 昭和6–10 (1931–1935), published 昭和12年3月 (March 1937)",
     "publisher": "南洋廳長官官房文書課, パラオ (昭和十二年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its fifth edition: 220 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1931 to 1935 for the whole territory and then 1935 for each branch office (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463309).",
     "gaps": "All 220 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the maps, the statistical charts (統計圖表), the prose survey (概說) and the colophon are not. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted; where they looked like a misread digit, the cell was re-read by a reader who had not seen the first reading. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Figures are kept exactly as printed, including points or spaces printed where a comma or decimal point is expected. Small figures printed above a cell (foreigners, half-year taxpayers, quantities) are given in the same cell after the figure. The volume's errata slip (正誤表, 48 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 20 of some 81,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463309/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463309",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1934", "dir": "Nanyo_Tokei_1934", "group": "south-seas",
     "title": "南洋廳統計年鑑 1934", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第四回 (No. 4), figures mainly for 昭和5–9 (1930–1934), published 昭和11年8月 (August 1936)",
     "publisher": "南洋廳長官官房文書課, パラオ (昭和十一年)",
     "note": "Incomplete scan: printed pages 7–16 (tables 6–23) are missing from the copy.",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its fourth edition: 238 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1930 to 1934 for the whole territory and then 1934 for each branch office (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463304).",
     "gaps": "The scanned copy lacks printed pages 7–16 (a printed note on p. 6 reads 7-16缺頁), which held tables 6–23 (climate and the first population tables); the other 220 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表). The contents, the maps, the statistical charts (統計圖表), the prose survey (概說) and the colophon are not transcribed. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted; where they looked like a misread digit, the cell was re-read by a reader who had not seen the first reading. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Figures are kept exactly as printed, including points or spaces printed where a comma is expected (in a few heavy-type trade tables points and commas could not be told apart and are given as commas, as noted). Small figures printed above a cell (foreigners, half-year taxpayers, quantities) are given in the same cell after the figure. No errata slip was found in this copy. About 125 of some 79,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463304/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463304",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1933", "dir": "Nanyo_Tokei_1933", "group": "south-seas",
     "title": "南洋廳統計年鑑 1933", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第三回 (No. 3), figures mainly for 昭和4–8 (1929–1933), published 昭和10年10月 (October 1935)",
     "publisher": "南洋廳, パラオ (昭和十年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its third edition: 237 numbered tables in 14 chapters — land and climate, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1929 to 1933 for the whole territory and then 1933 for each branch office (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463293).",
     "gaps": "All 237 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the maps, the statistical charts (統計圖表), the prose survey (概說) and the colophon are not. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted; a few cells whose totals did not add up were re-read by a reader who had not seen the first reading. Figures are kept exactly as printed, including points or spaces printed where a comma is expected. Small figures printed above a cell (foreigners, half-year taxpayers, quantities) are given in the same cell after the figure; in the trade tables 210–213 a number of these small quantities could not be read and are marked [?]. The volume's errata slip (正誤表, 46 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 65 of some 84,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463293/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463293",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "gyosei-nenpo-1929", "dir": "Gyosei_Nenpo_1929", "group": "south-seas",
     "title": "日本帝國委任統治地域行政年報 1929", "subtitle": "Nihon teikoku inin tōchi chiiki gyōsei nenpō (Annual Report on the Administration of the Territory under Japanese Mandate), 千九百二十九年度 (for 1929)",
     "publisher": "外務省 (Ministry of Foreign Affairs), 東京",
     "blurb": "The Japanese-language edition of Japan's annual report to the League of Nations on the mandated South Sea Islands (Micronesia), for 1929: thirteen chapters (general remarks, administration, finance, education, religion, industry, land, labour, communications, trade, welfare of the islanders, population and the Permanent Mandates Commission's observations), with the 1929 public health report as an appendix. Its tables cover islands and areas, staff, police, arms, liquor and opium control, courts and crime, budgets and taxes, schools and curricula, missions, agriculture, fisheries, coconut planting, trade by commodity, shipping, roads, population, births and deaths, causes of death and hospital patients, including a health survey of the villages of Yap. Tables are printed vertically with kanji numerals; they are given here in rows and columns with Arabic figures and the character forms as printed.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1443814).",
     "gaps": "All tables in the report and its appendix are transcribed; the prose, the organisation chart and the contents are not. The tables are printed vertically in kanji numerals; they are written here horizontally in Arabic figures, with 、 kept as a comma (also where it serves as a decimal mark, as in the 方里 areas). Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where only the grouping of stacked 一/二/三 strokes was in doubt and exactly one grouping made a printed total reconcile, that grouping was used; such cells were re-read by a reader who had not seen the first reading, and cells not confirmed are marked [?]. The crime tables, the trade tables and the table of hospital patients by disease were transcribed a second time independently; where the two readings differed a third blind reading decided, and cells on which no two readings agreed are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1443814/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1443814",
     "model": "Opus 5.5",
     "blank_marking": True},
    {"slug": "gyosei-nenpo-1928", "dir": "Gyosei_Nenpo_1928", "group": "south-seas",
     "title": "日本帝國委任統治地域行政年報 1928", "subtitle": "Nihon teikoku inin tōchi chiiki gyōsei nenpō (Annual Report on the Administration of the Territory under Japanese Mandate), 千九百二十八年度 (for 1928), published 昭和4年12月 (December 1929)",
     "publisher": "外務省 (Ministry of Foreign Affairs), 東京, 昭和四年",
     "blurb": "The Japanese-language edition of Japan's annual report to the League of Nations on the mandated South Sea Islands (Micronesia), for 1928: thirteen chapters (general remarks, administration, finance, education, religion, industry, land, labour, communications, trade, welfare of the islanders, population and the Permanent Mandates Commission's observations), with the 1928 public health report and a supplement of new laws as appendices. Its tables cover islands and areas, staff, police, opium and liquor control, courts and crime, budgets and taxes, schools and curricula, missions, agriculture, fisheries, trade by commodity, shipping, population, births and deaths, causes of death and hospital patients. Tables are printed vertically with kanji numerals; they are given here in rows and columns with Arabic figures and the character forms as printed.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1443806).",
     "gaps": "All tables in the report and its two appendices are transcribed; the prose, the organisation charts, the contents and the texts of the laws are not. The tables are printed vertically in kanji numerals (一五、四七四); they are written here horizontally in Arabic figures, with 、 kept as a comma (also where it serves as a decimal mark, as in the 方里 areas). Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where only the grouping of stacked 一/二/三 strokes was in doubt and exactly one grouping made a printed total reconcile, that grouping was used; every such cell was re-read by a reader who had not seen the first reading, and cells not confirmed are marked [?]. The trade tables, the 1927–28 budget and settled-accounts tables and the deaths-by-cause table were transcribed a second time independently; where the two readings differed a third blind reading decided, and cells on which no two readings agreed are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1443806/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1443806",
     "model": "Opus 5.5",
     "blank_marking": True},
    {"slug": "mandate-report-1925", "dir": "Mandate_Report_1925", "group": "south-seas",
     "title": "Annual Report to the League of Nations on the South Sea Islands 1925",
     "subtitle": "Annual Report to the League of Nations on the Administration of the South Sea Islands under Japanese Mandate for the Year 1925",
     "publisher": "Prepared by the Japanese Government, 1926",
     "blurb": "Japan's English-language annual report to the League of Nations on the mandated South Sea Islands (Micronesia) for 1925: general remarks (islands, area, climate), administration, police, justice and prisons, finance and taxes, education and school curricula, industry (agriculture, marine products, phosphate mining), navigation and trade, population, and answers to the Permanent Mandates Commission, with the 1925 public health report (hospitals, patients and diseases) and a collection of laws and regulations (fee scales and hospital charges) as annexes.",
     "source": "LLM-transcribed from the PDF of the copy in the League of Nations archives (United Nations Geneva, COL22-1-1). Table links give the PDF page number.",
     "gaps": "All tables in the report and its annexes are transcribed, including the fee scales and hospital price lists in the laws annex; the prose, the organisation charts, the photographs, the map and the legal texts are not. The scan is a PDF at 200 dpi; fold-out tables carry no printed page number, so for every table the PDF page number is given (PDF page N). Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted — an independent second reading of the dense health and population fold-outs (about 3,000 figures) agreed with the first on every figure but one, so these differences are in the printed report. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading was used and re-read by a second reader; cells not confirmed are marked [?].",
     "scan": "https://archives.ungeneva.org/gsxx-r5rs-peh2",
     "item": "https://archives.ungeneva.org/gsxx-r5rs-peh2",
     "leaf_label": "PDF page",
     "model": "Haiku 5.5 and Sonnet 5.5"},
    {"slug": "mandate-report-1931", "dir": "Mandate_Report_1931", "group": "south-seas",
     "title": "Annual Report to the League of Nations on the South Sea Islands 1931",
     "subtitle": "Annual Report to the League of Nations on the Administration of the South Sea Islands under Japanese Mandate for the Year 1931",
     "publisher": "Japanese Government, 1932",
     "blurb": "Japan's English-language annual report to the League of Nations Permanent Mandates Commission on the mandated islands of Micronesia (the South Sea Islands: Saipan, Yap, Palau, Truk, Ponape and Jaluit branch bureaus): area and climate, administration, police, justice and prisons, finance and taxation, education, religion, industry, marine products, mining, forestry, land, labour, communications and navigation, trade, the well-being of the islanders and population, followed by the annual report on public health and a collection of laws and regulations.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "All statistical tables in the report and its public health appendix are transcribed; the contents, the prose, the photographs, the maps and the collection of laws and regulations are not. Tables printed sideways were read from page images turned upright. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that looked inconsistent with their totals were re-read by a reader who had not seen the first reading; the printed figure is kept wherever it was confirmed. The settled-account figures on printed p. 117 are faint show-through and could not be confirmed, so they are marked [?].",
     "scan": "https://archive.org/details/LeagueOfNationsReportOnTheJapaneseMandateInMicronesia1931_157/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/LeagueOfNationsReportOnTheJapaneseMandateInMicronesia1931_157",
     "model": "Haiku 5.5 and Sonnet 5.5"},
    {"slug": "mandate-report-1930", "dir": "Mandate_Report_1930", "group": "south-seas",
     "title": "Annual Report to the League of Nations on the South Sea Islands 1930",
     "subtitle": "Annual Report to the League of Nations on the Administration of the South Sea Islands under Japanese Mandate for the Year 1930",
     "publisher": "Japanese Government, 1931",
     "blurb": "Japan's English-language annual report to the League of Nations Permanent Mandates Commission on the mandated islands of Micronesia (the South Sea Islands: Saipan, Yap, Palau, Truk, Ponape and Jaluit branch bureaus): administration, police, justice and prisons, finance, customs and port dues, liquor imports and exports, education, religion, industry, mining, land, labour, communications and navigation, trade, the well-being of the islanders and population, followed by the annual report on public health (hospitals, diseases, causes of death and infant mortality).",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "All statistical tables in the report and its public health appendix are transcribed; the contents, the prose, the photographs and the maps are not. Tables printed sideways were read from page images turned upright. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading was used; such cells and other doubtful figures were re-read by a reader who had not seen the first reading, and those the second reader could not confirm are marked [?]. The scan clips the right edge of some pages: the 1926 column of the table of causes of death of infants (printed pp. 162–163) is lost and marked [?].",
     "scan": "https://archive.org/details/LeagueOfNationsReportOnTheJapaneseMandateInMicronesia1930/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/LeagueOfNationsReportOnTheJapaneseMandateInMicronesia1930",
     "model": "Haiku 5.5 and Sonnet 5.5"},
    {"slug": "nanyo-tokei-1939", "dir": "Nanyo_Tokei_1939", "group": "south-seas",
     "title": "南洋廳統計年鑑 1939", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第九回 (No. 9), figures mainly for 昭和10–14 (1935–1939), published 昭和16年8月 (August 1941)",
     "publisher": "南洋廳內務部企畫課, パラオ (昭和十六年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its ninth and last edition: 179 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1935 to 1939 for the whole territory and then 1939 for each branch office (支廳 and sub-offices: Saipan, Tinian, Rota, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals. The volume is marked 部外秘 (not for outside circulation).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463331).",
     "gaps": "All 179 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the statistical charts (統計圖表), the maps and the colophon are not. The contents list the tables without chapter headings; chapters are assigned from the 總目次 start pages and, where a table shares a chapter's first page, from the running heads. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading was used; every such cell was then re-read by a reader who had not seen the first reading, and cells the second reader could not confirm are marked [?]. Figures are kept exactly as printed, including points, spaces or other marks printed where a comma or decimal point is expected. Small figures printed above a cell (foreigners, quantities) are given in the same cell after the figure; in the trade, agriculture and fisheries tables many of these small quantities and unit marks are too blurred to read and are marked [?]. No errata slip was found in this copy. About 550 of some 74,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463331/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463331",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1938", "dir": "Nanyo_Tokei_1938", "group": "south-seas",
     "title": "南洋廳統計年鑑 1938", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第八回 (No. 8), figures mainly for 昭和9–13 (1934–1938), published 昭和15年3月 (March 1940)",
     "publisher": "南洋廳長官官房調査課, パラオ (昭和十五年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its eighth edition: 183 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1934 to 1938 for the whole territory and then 1938 for each branch office (支廳 and sub-offices: Saipan, Tinian, Rota, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the character forms as printed and Arabic numerals. The volume is marked 部外秘 (not for outside circulation).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463326).",
     "gaps": "All 183 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the statistical charts (統計圖表), the maps and the colophon are not. The contents list the tables without chapter headings; chapters are assigned from the 總目次 start pages, with the liquor-trade tables (160–162) kept under 貿易 and the local-finance tables (179–180) under 財政 where they share a chapter's first page. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Figures are kept exactly as printed, including points, spaces or semicolons printed where a comma or decimal point is expected. Small figures printed above a cell (foreigners, quantities) are given in the same cell after the figure; in the trade and fisheries tables many of these small quantities and unit marks are too blurred to read and are marked [?]. No errata slip was found in this copy. About 470 of some 73,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463326/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463326",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1937", "dir": "Nanyo_Tokei_1937", "group": "south-seas",
     "title": "南洋廳統計年鑑 1937", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第七回 (No. 7), figures mainly for 昭和8–12 (1933–1937), published 昭和14年4月 (April 1939)",
     "publisher": "南洋廳長官官房調査課, パラオ (昭和十四年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its seventh edition: 210 numbered tables in 14 chapters — land, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance, trade by port and commodity, public finance and taxes, and social work — with an appendix table of weights and measures. Most tables give the years 1933 to 1937 for the whole territory and then 1937 for each branch office (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1463319; a second, lower-resolution copy is pid 1454027).",
     "gaps": "All 210 numbered tables are transcribed, with the appendix table of weights and measures (度量衡比較表); the contents, the statistical charts (統計圖表), the prose survey (概說), the maps and the colophon are not. Tables printed across both pages of a spread are joined into one, and long tables run over several spreads are written once. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Small figures printed above a cell (foreigners and similar) are given in the same cell after the figure; the small quantity figures printed above the values in the trade tables 183–186 were too blurred to read and are left out. The volume's errata slip (正誤表, 19 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 50 of some 40,500 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1463319/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1463319",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "nanyo-tokei-1932", "dir": "Nanyo_Tokei_1932", "group": "south-seas",
     "title": "南洋廳統計年鑑 1932", "subtitle": "Nan'yōchō tōkei nenkan (Statistical Yearbook of the South Seas Government), 第二回 (No. 2), figures for 大正11–昭和7 (1922–1932), published 昭和9年12月 (December 1934)",
     "publisher": "南洋廳, パラオ (昭和九年)",
     "blurb": "The statistical yearbook of the South Seas Government (Nan'yōchō), Japan's administration of the mandated islands of Micronesia, in its second edition, which reaches back to the founding of the government in 1922: 257 numbered tables in 14 chapters — land and climate, population (by island, nationality, prefecture of origin, age and occupation), administration, police, public health, justice and prisons, education, religion, industry (agriculture, livestock, forestry, fisheries, manufactures and subsidies), transport and communications, finance and prices, trade by port and commodity, public finance and taxes, and social work — with a short appendix. Most tables give each year from 1922 to 1932 for the whole territory and then for each of the six branch offices (支廳: Saipan, Yap, Palau, Truk, Ponape and Jaluit), often separating Japanese (邦人), islanders (島民: Chamorro and Kanaka) and foreigners. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1280258).",
     "gaps": "All 257 numbered tables are transcribed, with one unnumbered sub-table and the appendix list of offence-name abbreviations; the contents, the maps, the statistical charts (統計圖表), the prose survey (概說) and the colophon are not. One frame of the scan is a repeat of the previous spread and was skipped. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined, by rows or, where later pages add further columns for the same branch offices (tables 30, 166, 183 and 206), by columns. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted; a few tables (notably 81 and 227) have many branch-office cells that do not add up to the printed totals and may contain misreadings. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted; in tables 25 and 26 many final digits that have lost their top stroke at a column rule are read as 6 and listed. Small figures printed above a cell (foreigners, half-year taxpayers, quantities) are given in the same cell after the figure; the quantities in tables 230 (Jaluit) and 231 were too blurred to read and are left out. The volume's errata slip (正誤表, 17 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 550 of some 164,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?.",
     "scan": "https://dl.ndl.go.jp/pid/1280258/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1280258",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-tokei-1935", "dir": "Japan_Tokei_1935",
     "title": "大日本帝國統計年鑑 1935", "subtitle": "Dai Nippon Teikoku tōkei nenkan (Statistical Yearbook of the Empire of Japan), 第五十四回 (No. 54), 昭和十年 (Shōwa 10)",
     "publisher": "內閣統計局, 東京 (昭和十年)",
     "blurb": "The Cabinet Statistics Bureau's statistical yearbook of the Japanese Empire, 54th of the series: a set of summary tables (摘要表) followed by 442 numbered tables in 14 chapters — land and climate, population, agriculture, forestry and fisheries, mining and industry, commerce and banking, trade, transport and communications, social work, labour, education and religion, police, public health and disasters, justice, public finance, and elections, officials, the military and honours — ending with 23 international tables (國際統計表, nos. 420–442) comparing Japan with other countries, and front-matter tables of weights and measures and of currency parities. Most tables give a run of years to 1933 or 1934 for Japan proper (內地), often by prefecture, with the overseas territories (Korea, Taiwan, Karafuto, the Kwantung Leased Territory and the South Seas) shown separately. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the page images published by the Hitotsubashi University Institute of Economic Research, Statistical Yearbook database (一橋大學經濟研究所 日本統計年鑑・帝國統計年鑑データベース, https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1935/); the National Diet Library's own scan of this volume is not open to the public.",
     "gaps": "All 442 numbered tables are transcribed, with the summary tables, two unnumbered sub-tables printed beside numbered ones, and the front-matter tables of weights and measures and of currency parities and exchange rates (from the volume's front-matter scan); the contents, the index, the page of charts, the explanatory notes (略說) and the bureau's list of publications are not. The page images are two-page spreads about 2,000 px wide, so the small type was read from enlarged crops. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined; table 402 (conscription examinations), printed in three sections, is given as parts. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by one or two units of rounding in thousand-yen figures). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Misprints are kept as printed and noted; table 201 is printed with the number 200 and is filed as 201. The volume's errata slip (正誤表, 33 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 210 of some 224,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. Scan links open the page image in the Hitotsubashi database; please credit that database when using these transcriptions.",
     "scan": "https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1935/tab_jpeg/1935_{leaf:03d}.jpg",
     "item": "https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1935/",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-tokei-1938", "dir": "Japan_Tokei_1938",
     "title": "大日本帝國統計年鑑 1938", "subtitle": "Dai Nippon Teikoku tōkei nenkan (Statistical Yearbook of the Empire of Japan), 第五十七回 (No. 57), 昭和十三年版 (Shōwa 13 edition)",
     "publisher": "內閣統計局, 東京 (昭和十三年版)",
     "blurb": "The Cabinet Statistics Bureau's statistical yearbook of the Japanese Empire, 57th of the series, in its full pre-war form: 451 numbered tables in 15 chapters — land, population, agriculture, forestry and fisheries, mining and industry, commerce and banking, trade, transport and communications, social work, labour and employment exchanges, education, shrines and religion, police, public health and disasters, justice, public finance, elections, officials, the military and honours, and industrial associations — followed by 40 international tables (國際統計表) comparing Japan with other countries, and tables of weights and measures and of currency parities. Most tables give a run of years to 1936 or 1937 for Japan proper (內地), often by prefecture, with the overseas territories (Korea, Taiwan, Karafuto, the Kwantung Leased Territory and the South Seas) shown separately. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the page images published by the Hitotsubashi University Institute of Economic Research, Statistical Yearbook database (一橋大學經濟研究所 日本統計年鑑・帝國統計年鑑データベース, https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1938/); the National Diet Library's own scan of this volume is not open to the public.",
     "gaps": "All 451 numbered tables and the 40 international tables are transcribed, with the unnumbered sub-tables printed beside them and the front-matter tables of weights and measures and of currency parities and exchange rates (from the volume's front-matter scan); the contents, the index, the page of charts and the bureau's list of publications are not. The page images are two-page spreads about 2,000 px wide, so the small type was read from enlarged crops. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined; where a table is printed as successive column blocks (tables 13 and 77), each block is a separate part. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by one or two units of rounding in thousand-yen figures). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Where the print uses a full stop or a space for a thousands comma, or drops a decimal point, the reader's reading is noted in the table. The volume's errata slip (正誤表, 21 corrections) is attached as a note to each table it concerns; the figures stay as printed. About 120 of some 248,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. A spot check, in which a second model re-transcribed three tables (1,196 figures) independently, agreed on every figure. Scan links open the page image in the Hitotsubashi database; please credit that database when using these transcriptions.",
     "scan": "https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1938/tab_jpeg/1938_{leaf:03d}.jpg",
     "item": "https://d-infra.ier.hit-u.ac.jp/Japanese/govstat-database/statistical-yb/1938/",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-kanko-1941", "dir": "Kanko_Nenkan_1941",
     "title": "日本觀光年鑑 1941", "subtitle": "Nihon kankō nenkan (Japan Tourism Yearbook), 昭和16年版 (1941 edition)",
     "publisher": "日本觀光事業研究所 (Japan Tourism Research Institute), 東京, 1941",
     "blurb": "A yearbook of the Japanese tourist industry on the eve of the Pacific War. Part one surveys the history of tourism in Japan and the year 1940–41, with tables of foreign visitors and their spending, propaganda budgets, hotel loans, visitors by nationality, port and purpose, arrivals and departures, railway and road traffic, tramways, aviation and shipping; part two describes the tourist organisations of Japan and its empire (prefectural and city tourist associations, with their officers, budgets and work) and lists the hotels and Japanese inns with their owners and numbers of guests; part three surveys tourist resources prefecture by prefecture (scenic spots, hot springs, shrines and temples, historic sites, festivals, folk arts), prints the tourism laws, a bibliography of tourism literature, and a list of tourist films.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1142272).",
     "gaps": "Every table is transcribed, and the directories and lists (tourist organisations, hotels and inns, tourist resources, award and committee lists, the bibliography) are transcribed as directory entries; the prose, the laws and the advertisements are not. Each spread was read once by Claude Sonnet 5.5 (tables and directories) or Claude Haiku 5.5 (prose pages with small tables), with no checking by eye; the bibliography was re-read by Sonnet after a first reading misplaced fields. Unreadable figures and characters are [?] or [illegible]; printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1142272/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1142272",
     "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "dir_label": "Organisations, hotels, resources & lists",
     "blank_marking": True},
    {"slug": "japan-radio-1934", "dir": "Radio_Chosa_1934",
     "title": "全國ラヂオ調査報告 1934", "subtitle": "Zenkoku rajio chōsa hōkoku (National Radio Survey Report), 第1回 (first survey, published 1934)",
     "publisher": "遞信省 (Ministry of Communications) and 日本放送協會 (Broadcasting Corporation of Japan), 東京, 1934",
     "blurb": "The first national survey of radio listeners in Japan, carried out in 1932 among the roughly 1.2 million licensed listeners. The summary chapters and the statistical tables give replies by prefecture, branch, district and occupation; receiver types (crystal sets and valve sets, by number of valves), faults and repairs; listening to news, weather, market and lecture broadcasts; the preferences of men and women of each age group for every kind of programme (lectures, music from nagauta and gidayū to jazz and opera, drama, rakugo and sport) for every prefecture and city; children's hour listening; and listeners' requests for changes to broadcasting, by area and by occupation.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1132172).",
     "gaps": "Every statistical table and the tables in the summary chapters are transcribed, and the request classification is transcribed as directory entries; the prose and the 33 coloured chart plates are not. Each spread was read once by Claude Sonnet 5.5 from full-resolution crops, with no checking by eye; the very long tables (4, 6 and 7) were read in four-frame instalments and joined, so a table may consist of many parts. Unreadable figures are [?]; printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1132172/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1132172",
     "model": "Claude Sonnet 5.5",
     "dir_label": "Request classification",
     "blank_marking": True},
    {"slug": "japan-keishicho-1935", "dir": "Keishicho_Tokei_1935",
     "title": "警視廳統計書 1935", "subtitle": "Keishichō tōkeisho (Statistical Report of the Metropolitan Police Board), 第45回, 昭和10年 (1935)",
     "publisher": "警視總監官房文書課 (Secretariat, Superintendent-General of the Metropolitan Police), 東京, 1936",
     "blurb": "The annual statistical report of the Tokyo Metropolitan Police Board for 1935, covering the whole of Tokyo prefecture station by station. Besides police organisation, staff, pay, discipline and budgets, it is a detailed record of urban life: fires and their causes, population movement and resident foreigners, meetings, labour disputes and associations, pawnshops and second-hand dealers, inns, employment agents, theatres, cinemas and other entertainments with their audiences, geisha, licensed prostitutes, cafés and waitresses, entertainers and teachers of the arts, vehicles and traffic accidents, factories and workers, building permits, infectious diseases, hospitals, doctors and midwives, food inspection and slaughterhouses, suicides by method and motive, accidental deaths, lost property, missing persons, protective custody, crime by type, place, method, month and station, arrests by age, education, occupation and motive, stolen property, and summary convictions for police offences.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1462000).",
     "gaps": "All 353 numbered statistical tables are transcribed; the contents, the chapter dividers and the coloured charts (圖表) are not. Each spread was read once by Claude Sonnet 5.5 from full-resolution crops, with no checking by eye. Columns next to the binding are sometimes clipped or faded, so some tables have runs of [?] in their innermost column; printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1462000/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1462000",
     "model": "Claude Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-gakusei-1938", "dir": "Gakusei_Seikatsu_1938",
     "title": "學生生徒生活調査 1938", "subtitle": "Gakusei seito seikatsu chōsa (Survey of Students' Lives), 昭和13年11月調査 · 上: 專門學校 (vocational colleges) · 下: universities, higher schools, preparatory courses, higher normal schools and women's colleges",
     "publisher": "文部省教學局 (Bureau of Education and Learning, Ministry of Education), 東京, 1939; two volumes (上・下)",
     "blurb": "The Ministry of Education's survey of the lives of 63,028 students in November 1938, in two volumes: 上 covers the men's vocational colleges (專門學校: medicine and pharmacy, foreign languages, fine arts and music, technical, agricultural and commercial colleges, the merchant-marine and fisheries schools, and private colleges); 下 the imperial, public and private universities, the higher schools (高等學校), university preparatory courses, the higher normal schools, women's higher normal schools and women's vocational colleges. Each volume has the same 31 sections, school type by school type and school by school: former schools, ages, home districts and fathers' occupations with how easily the family could pay for their studies; where they lived and ate lunch; their health and illnesses; hours of study and exercise; where their money came from and what side jobs they took; their monthly spending on lodging, food, commuting, books, amusements and sundries, by type of lodging and of school; and ranked lists of the books that had impressed them, the magazines and newspapers they read, their sports, hobbies, tastes, means of self-cultivation, the people they admired, their religion and how they spent the summer vacation. Chapters are marked 上 or 下 by volume.",
     "source": "LLM-transcribed from the National Diet Library scans (上: NDL pid 1710512; 下: NDL pid 1144471).",
     "gaps": "Every table is transcribed, including the errata slip (訂正) in 下. Each spread was read once by Claude Sonnet 5.5 (front matter by Claude Haiku 5.5) from full-resolution crops, with no checking by eye. 上 is a dark microfilm; in 下 the italic ratio (比率) figures are blurred and the column next to the binding is often washed out, so many ratio cells there are [?] (the counts are nearly all read). Printed totals that do not add up, and the frequent misprints in the ratio columns, are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/{partname}/1/{leaf}",
     "scan_parts": {1: "1710512", 2: "1144471"},
     "item": "https://dl.ndl.go.jp/pid/1710512",
     "model": "Claude Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-kaji-1939", "dir": "Kaji_Nenkan_1939",
     "title": "家事年鑑 1939", "subtitle": "Kaji nenkan (Household Management Yearbook), 昭和14年版 (1939 edition)",
     "publisher": "國勢社 (Kokuseisha), 「國勢グラフ」編輯部 ed., 東京・京城, 1939",
     "blurb": "A household-management yearbook for the wartime home. Its sections on nutrition and food, clothing, housing, household hygiene and miscellaneous household economy carry small tables and lists: food composition and vitamin content, standard diets and calorie needs, rice, wheat, soybean, milk and meat supply and consumption, fibres, dyes and washing methods, electrical appliances and running costs, lighting standards, poison gases and air-raid warnings, notifiable diseases, incubation periods and disinfectants, household medicines, savings and substitute goods. A statistical section gives population, births and deaths, causes of death by age, average height and weight, occupations, national income and household income and expenditure by income class; the appendix summarises wartime controls on goods (物資統制一覽) and prices (物價統制一覽).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1072492).",
     "gaps": "Every table and every data list is transcribed (lists as directory entries); the prose, recipes, illustrated plates and charts, the index and the advertisements are not. Each spread was read once by Claude Sonnet 5.5 from full-resolution crops, with no checking by eye. Unreadable figures are [?]; printed totals that do not add up are kept as printed and noted.",
     "scan": "https://dl.ndl.go.jp/pid/1072492/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1072492",
     "model": "Claude Sonnet 5.5",
     "dir_label": "Lists",
     "blank_marking": True},
    {"slug": "japan-jogakko-1937", "dir": "Koto_Jogakko_Chosa_1937",
     "title": "高等女學校諸調査 1937", "subtitle": "全國高等女學校實科高等女學校ニ關スル諸調査 昭和12年度 (Surveys of Girls' High Schools and Practical Girls' High Schools, 1937)",
     "publisher": "文部省普通學務局 (Ministry of Education, General Education Bureau), 東京, 1938 (凡例 dated 昭和13年6月)",
     "blurb": "The Ministry of Education's survey of every public and private girls' high school (高等女學校) and practical girls' high school (實科高等女學校) in Japan on 1 October 1937, school by school. For some 810 girls' high schools and 206 practical girls' high schools it gives each school's founder, principal, location and history; its course length, places, classes and pupils by year; applicants and entrants in 1937 and the previous schooling of first-year entrants; what last year's graduates went on to do (further study, work, home); pupils who left during the year and why; and its teachers (qualified or not, full- or part-time) and the optional subjects it taught — each with prefectural sub-totals, and with summary tables by prefecture for each kind of school, for the advanced (高等科) and specialist (專攻科) courses, and for the girls in the last years of primary school and the applicants to all middle schools.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1710633).",
     "gaps": "Every table is transcribed. The long school-by-school tables were read in four-page pieces by Claude Sonnet 5.5 and joined, each piece once, from tight crops; the 道府縣 and 設立別 of rows at the top of a page are carried from the heading on the page before. The book prints many sub-totals that do not add up (spot checks on the scan confirmed that the printed figures are as transcribed); they are kept as printed and noted in each table. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Ditto marks (同) are kept as printed. 23 of about 112,000 filled cells could not be read and are marked [?]; unreadable characters in school and personal names are marked [illegible] in place.",
     "scan": "https://dl.ndl.go.jp/pid/1710633/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1710633",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-shintai-1934", "dir": "Shintai_Kensa_1934",
     "title": "學生生徒兒童身體檢査統計 1934", "subtitle": "學生生徒兒童身長・體重・胸圍平均累年比較 (明治33～昭和9年度) / 公私立小學校・中學校・高等女學校生徒兒童身體檢査統計 (昭和8・9年度) (Height, Weight and Chest Girth of Pupils and Students, 1900–1934, and School Physical-Examination Statistics for 1933 and 1934)",
     "publisher": "文部大臣官房體育課 (Ministry of Education, Minister's Secretariat, Physical Education Section), 東京, 1937 (昭和12年3月30日發行)",
     "blurb": "The Ministry of Education's figures from the annual physical examination of Japanese schoolchildren and students. The first part gives the average height, weight and chest girth of boys and girls at each age, year by year from 1900 (明治33年度) to 1933 and again to 1934. The second gives, for 1933 and for 1934 and by prefecture, the average height, weight and chest girth at each age of boys and girls in public and private primary schools, of middle-school boys and of girls' high-school pupils, and the percentages rated strong, medium or weak in physical development and nutrition, with spinal curvature, myopia, trachoma, dental caries, anaemia, heart disease, skin disease, enlarged tonsils and other conditions.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1445688).",
     "gaps": "Every table is transcribed; the book has no printed contents, so the contents shown here were made from the table headings (part titles in brackets). Each spread was read once by Claude Sonnet 5.5 from tight crops. Many decimal points did not print (a gap is left in the type); since every figure in a table has the same number of decimals, these are given with the point and listed in each table's notes. No 大正十年 (1921) row is printed in the year-by-year tables. Rows of percentages that do not add up to 100, and figures that look out of line with their neighbours, are kept as printed and noted. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 71 of about 25,200 figures could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1445688/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1445688",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-sotei-1941", "dir": "Sotei_Kyoiku_1941",
     "title": "壯丁教育調査概況 1941", "subtitle": "壯丁教育調査概況 昭和16年度 (Survey of the Education of Conscripts, 1941)",
     "publisher": "文部省國民教育局 (Ministry of Education, National Education Bureau), 東京, 1943 (凡例 dated 昭和18年3月; marked 秘, confidential)",
     "blurb": "The Ministry of Education's confidential report on the schooling and attainment of the 664,680 young men examined for conscription in 1941 (壯丁). It gives their level of schooling — from no schooling and unfinished primary school to university — by prefecture, by city and countryside, and year by year since 1932; why men had not attended or had left the national (primary) school; and the results of the written test set to them at the examination (ethics and civics, Japanese, arithmetic and science): rates of correct answers by question, by level of schooling, by region and by prefecture, compared with schoolchildren's results; and their occupations by prefecture and by city and countryside.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1450977).",
     "gaps": "Every table is transcribed, with the small tables set in the text; the prose, the survey forms and the test papers (pp. 6–7, 55–60) are not. The 正誤表 (errata slip) bound at the back is given as a table, and each correction that falls in a table is noted on that table (the cell stays as printed). Charts that print no figures are not given. The year-by-year prefectural table (第6表, eight spreads) was read spread by spread and joined. Each spread was read once by Claude Sonnet 5.5 from tight crops. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 34 of about 27,600 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1450977/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1450977",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-fujin-sensen-1931", "dir": "Fujin_Shokugyo_Sensen_1931",
     "title": "婦人職業戰線の展望 1931", "subtitle": "Fujin shokugyō sensen no tenbō (The Front of Women's Occupations: a Survey), 東京市, 昭和6年",
     "publisher": "東京市 (Tokyo City Office), 東京, 1931",
     "blurb": "Tokyo City's survey of women in paid work, taken by questionnaire among some 16,000 working women and their employers, with commentary. Part 1 sets out women's work in Japan and Tokyo and the results of the employment exchanges; part 2 describes working women as a whole — purpose of working, family, marital status and children, housing, age, schooling, hobbies, religion, holidays, how they found work, starting pay, length of service, job changes, hours, rest days, commuting, health, wishes and opinions, pay, allowances, bonuses, other income, total income, and spending on clothing, food and lodging, family support, transport, self-improvement, amusements and savings; part 3 does the same occupation by occupation (office clerks, shop assistants, canvassers, typists, telephone operators, draughtswomen, factory women, bus conductresses, theatre usherettes, cleaners, messenger girls, restaurant waitresses, lift girls); part 4 gives the employers' side. A statistical appendix (統計表) prints the full tables by occupation (employees, tables 1–36) and by industry (employers, tables 1–23).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1280892).",
     "gaps": "Every table is transcribed, with the figures printed on charts and the lists of survey items; the prose, essays, quoted opinions and law texts are not. In parts 1–4 the figures are kanji numerals, many printed small and heavy: they were read by Claude Opus 5.5 from tight crops and converted to Arabic figures, but in several of the occupation tables of part 2 (notably pay, allowances, bonuses, income and clothing, pp. 94–130) 三 and 五 print as identical blots at the scan's resolution and many cells could not be read — the same data are given in clear Arabic figures in the statistical appendix, read by Claude Sonnet 5.5. Where stacked strokes could be grouped more than one way (kanji) or a digit was ambiguous only between 3 and 8 (Arabic), and exactly one reading made a printed total reconcile, that reading is used and noted. Printed totals that do not add up are kept as printed and noted. 628 of about 53,500 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1280892/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1280892",
     "model": "Opus 5.5, Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-shokugyo-fujin-1927", "dir": "Shokugyo_Fujin_1927",
     "title": "職業婦人調査 1927", "subtitle": "東京大阪兩市に於ける職業婦人調査 タイピスト・事務員・交換手・店員 (Survey of Working Women in Tokyo and Osaka: Typists, Office Clerks, Telephone Operators, Shop Assistants) and 職業婦人調査 看護婦・産婆 (Nurses and Midwives), 昭和2年3月; two reports bound together",
     "publisher": "中央職業紹介事務局 (Central Employment Exchange Bureau), 東京, 1927 (昭和2年3月; the nurses and midwives volume 昭和2年3月28日發行)",
     "blurb": "Two reports of the Central Employment Exchange Bureau on women's work, bound together in the scanned copy. The first is a questionnaire survey of women typists, office clerks, telephone operators and shop assistants in Tokyo and Osaka, by employer (government offices, banks, companies, shops): their ages, marital status, schooling, years of service, monthly salaries and bonuses, cross-tables of salary by length of service, item-by-item monthly spending (clothing, footwear, cosmetics, hairdressing and baths, correspondence, lodging, contributions to the family budget, savings and more), reasons for working, opinions of the work and its harms, and how they found their jobs, with comparisons by employer and between the two cities and chart plates. The second covers nurses (numbers by prefecture each year from the Meiji era, hospital nurses' pay, nurses' associations with their membership, fees and rules, school nurses, training schools and their fees, examination candidates and passes by prefecture 1915–26) and midwives (numbers by prefecture and year, births per midwife by prefecture and by country, fees, examination results, associations and training institutions), with a fold-out list of the designated nursing schools.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1443096).",
     "gaps": "Every table is transcribed, with the figures printed on the chart plates and the lists of training schools and institutions; the prose, regulations, blank forms and examination questions are not. The scan shows several chart plates and the fold-out tables twice (a dark or partial copy, then a full one); the full copies were read. The figures are kanji numerals, many squeezed two or three to a square; they were read by Claude Opus 5.5 from tight crops and converted to Arabic figures (contents, regulation sections and lists by Claude Sonnet 5.5). Where stacked strokes could be grouped more than one way and exactly one grouping made a printed total reconcile, that grouping is used and noted. The midwives' examination fold-out is printed in very small type: its unreadable cells were read a second time, blind, by Claude Opus 5.5, and only confident readings were filled in. Printed totals and percentages that do not add up are kept as printed and noted. Table numbers restart in each occupation part. 89 of about 22,000 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1443096/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1443096",
     "model": "Opus 5.5, Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-shokugyo-fujin-1926", "dir": "Shokugyo_Fujin_1926",
     "title": "職業婦人調査 女給 1926", "subtitle": "東京大阪兩市に於ける職業婦人調査 女給 (Survey of Working Women in Tokyo and Osaka: Café Waitresses), 大正15年3月",
     "publisher": "中央職業紹介事務局 (Central Employment Exchange Bureau), 東京, 1926 (大正15年3月31日發行)",
     "blurb": "The Central Employment Exchange Bureau's questionnaire survey of 2,785 café waitresses (女給) in Tokyo (1,670) and Osaka (1,115), distributed through the police districts. Its tables give, for each city and police district, the waitresses' ages; whether their parents were living; their brothers and sisters; their prefecture of origin; how long they had lived in the city; their previous jobs and why they took up the work; how long they had been waitresses and in their present café, and how often they had changed; whether they lived in or came in; when they went to bed and got up; their total income, tips and fixed wages; their spending on clothes, savings, remittances home and contributions to the family budget; and their opinions of the work, its harms and their plans for the future. The figures printed on the chart plates are given too.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 976210).",
     "gaps": "Every table is transcribed, with the questionnaire form, the return figures by police district, the lists of answers with counts and the figures printed on the chart plates; the prose, the conclusion and the chapter on cafés, bars and restaurants (no tables) are not. The scan repeats the plate of Figure 5 and shows the fold-out of pp. 78–79 twice (with the flap open and turned back). The figures are kanji numerals, many squeezed two or three to a square; they were read by Claude Opus 5.5 from tight crops and converted to Arabic figures (the questionnaire, the plates and the contents by Claude Sonnet 5.5). Where stacked strokes could be grouped more than one way (一一 or 二, 三 or 二一 or 一二) and exactly one grouping made a printed total reconcile, that grouping is used and noted; readings that went further than that were turned back to [?]. Printed totals and percentages that do not add up are kept as printed and noted; several district tables disagree slightly with the summary tables. Table numbers are as printed: there is no Table 39, and both tip tables by police district are numbered 40. 23 of about 18,000 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/976210/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/976210",
     "model": "Opus 5.5, Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-yomimono-1934", "dir": "Joshi_Seinen_Yomimono_1934",
     "title": "女子青年讀み物に關する調査 1934", "subtitle": "女子青年讀み物に關する調査 附 新刊紹介 (Survey of the Reading of Young Women, with Notices of New Books), 昭和9年",
     "publisher": "大日本聯合女子青年團 (Greater Japan Federation of Young Women's Associations), 東京, 1934 (昭和9年4月1日發行; not for sale)",
     "blurb": "A questionnaire survey of what young women read, taken by the national federation of young women's associations (女子青年團) among 2,950 members in four kinds of district: cities (都市地帶), farming villages (農村地帶), factory districts (工場地帶) and fishing villages (漁村地帶), in 32 prefectures. It gives, by district and prefecture, the books the women found most moving, most useful and harmful; how many books they read and what they spent on them; the kinds of book they wanted; the newspapers and magazines they took monthly or occasionally; whether they had time to read; and their schooling and occupations. An appendix recommends new books (moral education, thought and history, household economy, health, literature, magazines) with prices, publishers and short descriptions, and lists the publishers' addresses. Tables are given in Japanese with the old character forms as printed; the kanji numerals are converted to Arabic figures.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1137687).",
     "gaps": "Every table is transcribed, with the questionnaire form, the figure lists set in the text (questions 2 and 5) and the appendix book lists; the prose is not. The book-by-prefecture grids are printed with one column per book title; they are given turned, one row per book. The figures are kanji numerals, read by Claude Opus 5.5 from tight crops and converted to Arabic figures; the questionnaire and the appendix lists were read by Claude Sonnet 5.5. Where stacked strokes could be grouped more than one way (一一 or 二, 三 or 二一) and exactly one grouping made a printed total reconcile, that grouping is used and noted (56 cells). The farming-village 'harmful books' grid was read twice independently and the readings agree on every figure. Printed totals that do not add up are kept as printed and noted in each table. 11 of about 2,070 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1137687/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1137687",
     "model": "Opus 5.5, Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-kenchiku-1938", "dir": "Kenchiku_Nenkan_1938",
     "title": "建築年鑑 1938", "subtitle": "Kenchiku nenkan (Architectural Yearbook), 昭和13年版 (1938 edition), covering 1937",
     "publisher": "建築學會 (Architectural Institute of Japan), 東京, 1938 (昭和13年7月9日發行); sold by 丸善",
     "blurb": "The Architectural Institute of Japan's yearbook of the Japanese building world in 1937 (昭和12年). Its statistical part (建築統計, tables 1–18) gives building loans of prefectures and public bodies, real-estate sales and mortgages, construction costs by city and month, state and prefectural building budgets, buildings completed in the six great cities under the Urban Building Law by work, structure and use, month by month, completed floor area in 28 prefectures, building-material prices and wage indices for Tokyo and Osaka since 1920, building-cost indices, timber output, imports and exports of building materials, architects and engineers by employment and region, architecture students and teachers, accidents on building sites, and the area, population and households of prefectures and cities. It also has a register of about 740 large buildings completed in 1937 (name, site, owner, architect, contractor, dates, floors, floor area and structure) across Japan, Karafuto, Taipei, Keijō, Dairen and Hsinking; lists of the towns under the Urban Building and City Planning Laws, fire-proof, aesthetic, height and open-space districts and zoning by city; competition results and exhibitions; new books; research grants and prizes; patents, utility models and registered designs; government building offices; architectural societies; schools of architecture; and journals and newspapers — and a day-by-day diary of the architectural world in 1937 (建築界日記). Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1261992).",
     "gaps": "Every table and list is transcribed, with the 1937 diary as a chronology; the review essays of part II, the texts of laws and regulations (only the small tables printed in them are given), the bibliography of journal articles (VII 文獻題目, グラフ索引), the society reports of XI 1, the photo plates and the advertising section are not. Charts that print no figures (tables 3 (2), 6 (5)–(6), 8 (2), 14 and 18) are not given; the figures printed on the pie charts of the map of architects are. The scan lacks the leaf with pp. 76–77 (part II), and pp. 274–291 are bound out of order (the scan links follow the binding). In the register of completed buildings a leading ・ marks a floor area in tsubo, and ditto marks are kept as printed. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 43 of about 28,000 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1261992/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1261992",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-kenchiku-1939", "dir": "Kenchiku_Nenkan_1939",
     "title": "建築年鑑 1939", "subtitle": "Kenchiku nenkan (Architectural Yearbook), 昭和14年版 (1939 edition), covering 1938",
     "publisher": "建築學會 (Architectural Institute of Japan), 東京, 1939 (昭和14年7月1日發行); sold by 丸善",
     "blurb": "The Architectural Institute of Japan's yearbook of the Japanese building world in 1938 (昭和13年), the second year of the war with China, when the controls on steel, timber, cement and copper began. Its review (建築界展望) prints the wartime economic laws affecting building materials, a list of controlled building materials, and small tables of cement, steel, timber and glass supply, substitute materials, material prices and building wages in the six great cities. Its statistical part (建築統計, tables 1–15) gives building loans of prefectures and public bodies by month and region, construction costs by city, structure and month, state and prefectural building budgets, buildings completed in the six great cities under the Urban Building Law by work, structure and use, month by month, completed floor area in 28 prefectures, building-material prices and wage indices for Tokyo and Osaka since 1920, building-cost indices for sample buildings, timber output, exports and imports of building materials, architects and engineers by employment and region, students and staff of architecture schools, and accidents on building sites, 1932–1937. It has a register of 500 large buildings completed in 1938 (name, site, owner, architect, contractor, dates, floors, floor area and structure) across Japan and its empire; the 關係一覽表 of the building laws — the towns under the Urban Building and City Planning Laws (nearly 600, with dates), fire-proof, aesthetic, height and open-space districts, zoning of 92 cities with areas, local ordinances by prefecture, and districts near airfields; competition results, exhibitions and national-treasure buildings designated and repaired; new books; research grants; government building offices; the Institute's membership by region; architectural societies; schools of architecture; and journals and newspapers — and a day-by-day diary of the architectural world in 1938 (建築界日記).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1262001).",
     "gaps": "Every table and list is transcribed, with the 1938 diary as a chronology; the review essays of parts II and III (only the tables and lists printed in them are given), the texts of laws and regulations (only the small tables printed in them are given), the bibliography of journal articles (VII 文獻題目, グラフ索引), the patent lists of IX, the society reports of XI 1 and the advertising section are not. Charts that print no figures (tables 2 (2), 5 (5)–(6), 7 (2), 13 and 15 of part III) are not given; the figures printed on the timber chart (table 9) and the Institute's membership chart are. Each spread was read once by Claude Sonnet 5.5, except the sideways zoning table (關係一覽表 8), read by Claude Opus 5.5 from pages turned upright. Columns lost in the binding gutter (four columns of table 2 (1), one of 5 (4)) are marked [?]. In the register of completed buildings a leading ・ marks a floor area in tsubo, and ditto marks are kept as printed. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 203 of about 25,200 filled cells could not be read and are marked [?]; unreadable characters in names are [?] or [illegible] in place.",
     "scan": "https://dl.ndl.go.jp/pid/1262001/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1262001",
     "model": "Sonnet 5.5 (Opus 5.5 for the sideways zoning table 8)",
     "blank_marking": True},
    {"slug": "japan-kenchiku-1940", "dir": "Kenchiku_Nenkan_1940",
     "title": "建築年鑑 1940", "subtitle": "Kenchiku nenkan (Architectural Yearbook), 昭和15年版 (1940 edition), covering 1939",
     "publisher": "建築學會 (Architectural Institute of Japan), 東京, 1940 (昭和15年7月31日發行); sold by 丸善",
     "blurb": "The Architectural Institute of Japan's yearbook of the Japanese building world in 1939 (昭和14年), the third year of the war with China, when steel, timber and cement were rationed and building was put under control. Its statistical part (建築統計, tables 1–11) gives building loans of prefectures and public bodies by month and region, construction costs and floor area by city, structure and month, state and prefectural building budgets, buildings completed in the six great cities under the Urban Building Law by work, structure and use, month by month, completed floor area in 31 prefectures, building-material prices and wage indices for Tokyo and Osaka since 1920, building-cost indices for sample buildings, and timber output. It has a register of 379 large buildings completed in 1939 (name, site, owner, architect, contractor, dates, floors, floor area and structure) across Japan, Karafuto, Taiwan, Keijō, Dairen, Hsinking and Mukden; the 關係一覽表 of the building laws — the towns under the Urban Building and City Planning Laws (over 600, with dates), air-defence building rules, fire-proof, aesthetic, height, open-space, residential and industrial districts, zoning by city with areas, and local ordinances; the national standards for structural and rivet steel and the timber standards (sizes of boards, scantlings and squares); competition results, exhibitions and national-treasure buildings designated and repaired; new books; research grants; government building offices; architectural societies; schools of architecture; and journals and newspapers — and a day-by-day diary of the architectural world in 1939 (建築界日記).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1262011).",
     "gaps": "Every table and list is transcribed, with the 1939 diary as a chronology; the review essays of part II, the texts of laws and regulations (only the small tables printed in them are given), the articles of the steel and timber standards (only their tables are given), the bibliography of journal articles (VIII 文獻題目, グラフ索引), the patent section X (prose with drawings), the society reports of XII 1 and the advertising section are not. Charts that print no figures (tables 2 (2), 5 (5)–(6), 7 (2), 10 and 11 of part III) are not given; the figures printed on the timber chart (table 9) are. The tables were read by Claude Sonnet 5.5, except the sideways zoning table (關係一覽表 11), read by Claude Opus 5.5 from pages turned upright. On the badly printed budget table 4 of part III, 34 doubtful cells were read a second time, blind, by Opus; where both readers saw a digit that does not make the printed total add up, the digit is kept as printed. In the register of completed buildings a leading ・ marks a floor area in tsubo, and ditto marks are kept as printed. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 14 of about 21,500 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/1262011/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1262011",
     "model": "Sonnet 5.5 (Opus 5.5 for the sideways zoning table 11)",
     "blank_marking": True},
    {"slug": "japan-kenchiku-1941", "dir": "Kenchiku_Nenkan_1941",
     "title": "建築年鑑 1941", "subtitle": "Kenchiku nenkan (Architectural Yearbook), 昭和16年版 (1941 edition), covering 1940",
     "publisher": "建築學會 (Architectural Institute of Japan), 東京, 1941 (昭和16年11月15日發行; 非賣品, not for sale)",
     "blurb": "The Architectural Institute of Japan's yearbook of the Japanese building world in 1940 (昭和15年), printed in November 1941 for members only with a notice asking them to handle it with care for reasons of counter-espionage (防諜). Its review (建築界展望) gives small tables of timber supply, building-material prices and building activity, the results of five design competitions, exhibitions and national-treasure buildings designated and repaired. Its statistical part (建築統計, tables 1–10) gives state and prefectural building budgets, buildings completed in the six great cities under the Urban Building Law by work, structure and use, month by month, completed floor area in 22 prefectures, building-material price and wage indices, building-cost indices for sample buildings, timber output, and the area and population of every prefecture and of 168 cities from the October 1940 census. It has a register of 236 large buildings completed in 1940 (name, site, owner, architect, contractor, dates, floors, floor area and structure) across Japan and its empire; the 關係一覽表 of the building laws — the towns under the Urban Building and City Planning Laws (over 600, with dates), towns under the air-defence building rules, fire-proof, aesthetic, height, open-space, residential and industrial districts, zoning of 101 cities with areas, local ordinances by prefecture, and districts near airfields; the national standards decided in 1940 (plywood, cement, steel bars and sections, hiba timber); new books; research grants; the Institute's members of the Imperial Academy and Academy of Arts; the building staff of ministries, prefectures, cities and the housing and farmland corporations (營團); architectural societies; schools of architecture in Japan and Manchukuo and research institutes; the balance sheets of 19 of 21 large building contractors listed (Ōbayashi, Kajima, Shimizu, Takenaka, Hazama …); and journals and newspapers — and a day-by-day diary of the architectural world in 1940 (建築界日記).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1256689).",
     "gaps": "Every table and list is transcribed, with the 1940 diary as a chronology; the review essays of parts II and III (only the tables and lists printed in them are given), the texts of laws and regulations and of the standards (only their tables are given), the bibliography of journal articles (IX 文獻題目, グラフ索引), the patent section XI, the society reports of XIV 1 and the advertising section are not. The fire chart (table 8) prints no figures and is not given; the figures printed on the timber chart (table 7) are, though many of its small labels could not be read. Each contractor in XVI is one table holding its balance sheet, with the firm's address, officers and accounting date in the caption; where a balance sheet does not add up (e.g. the liabilities of 池田組) the book prints it so. Each spread was read once by Claude Sonnet 5.5, except the sideways zoning table (一覽表 11), read by Claude Opus 5.5 from pages turned upright. In the register of completed buildings a leading ・ marks a floor area in tsubo, and ditto marks are kept as printed. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 49 of about 19,600 filled cells could not be read and are marked [?]; unreadable characters in names are [?] or [illegible] in place.",
     "scan": "https://dl.ndl.go.jp/pid/1256689/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1256689",
     "model": "Sonnet 5.5 (Opus 5.5 for the sideways zoning table 11)",
     "blank_marking": True},
    {"slug": "japan-kenchiku-1942", "dir": "Kenchiku_Nenkan_1942",
     "title": "建築年鑑 1942", "subtitle": "Kenchiku nenkan (Architectural Yearbook), 昭和17年版 (1942 edition), covering 1941",
     "publisher": "建築學會 (Architectural Institute of Japan), 東京, 1943 (昭和18年1月30日發行; 非賣品, not for sale)",
     "blurb": "The Architectural Institute of Japan's yearbook of the Japanese building world in 1941 (昭和16年), the year of the Pacific War's outbreak, a slimmer wartime edition without the statistical part and register of completed buildings of earlier years. Its few statistics give building-material price and building-labour wage indices for 13 cities month by month, and building-cost indices for four sample buildings (an office building, a machine shop, a house and a primary school). Most of the book is lists: a register of 106 cities zoned under the Urban Building Law with the area (tsubo) of residential, commercial and industrial districts, the 630-odd towns and villages under the Urban Building and City Planning Laws with dates, the towns under the air-defence building rules, fire-proof, aesthetic, height, open-space, residential and industrial districts, and local ordinances by prefecture (all as of 1 April 1942); a dated list of the building laws and orders of 1941–42; the national standards for building materials; competition results, exhibitions, new national treasures and important art objects; new books; architectural journals and newspapers; an index of over 200 buildings photographed in the journals in 1941 (building, designer, journal and month); research grants; the building staff of ministries, prefectures, cities and the wartime corporations (營團); architectural societies and the building-trade control associations, with profiles of the main societies; schools of architecture with their students and graduates, in Japan and Manchukuo; research institutes; the building staff of large companies — and a day-by-day diary of the architectural world in 1941 (建築界日記).",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1109442).",
     "gaps": "Every table and list is transcribed, with the 1941 diary as a chronology and the profiles of the main societies (XIII 1) as directory entries; the review essays of part II (only the lists printed in them are given), the texts of laws and regulations and of the standards (only their tables are given), the patent section X and the advertising section are not. Table 3 of part III (fires and fire losses by prefecture) is a bar chart that prints no figures and is not given. This edition has no register of completed buildings; the nearest thing is the index of buildings photographed in the journals (VIII). Pages 122 and 140 were transposed in printing (school rows on p. 122, city building offices on p. 140); each table is given in its proper order and says so. Each spread was read once by Claude Sonnet 5.5 (the short list of control associations, XIII 3, by Haiku 5.5), from full-resolution crops; the sideways zoning table (一覽表 11) from pages turned upright. The small-print 目的 column of the society list (XIII 2) was read at a coarser scale and may have occasional wrong characters. Printed totals that do not add up are kept as printed and noted in each table; where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. 87 of about 12,900 filled cells could not be read and are marked [?]; unreadable characters in names are [?] in place.",
     "scan": "https://dl.ndl.go.jp/pid/1109442/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1109442",
     "model": "Sonnet 5.5 (Haiku 5.5 for one short list)",
     "blank_marking": True},
    {"slug": "japan-hyakkaten-1941", "dir": "Hyakkaten_Nenkan_1941", "kanji_full": True,
     "title": "百貨店年鑑 1941", "subtitle": "Hyakkaten nenkan (Department Store Yearbook), 昭和16・17年版 (1941–42 edition)",
     "publisher": "日本百貨店通信社 (Nihon Hyakkaten Tsūshinsha), 東京, 1941",
     "blurb": "A yearbook of the Japanese department-store trade on the eve of the Pacific War. It prints the 1937 Department Store Law and the rules of the Japan Department Store Association; a survey of every department store in Japan, Korea, Taiwan and Manchuria, region by region, with each company's founding date, capital, shareholders, directors, floor space, staff numbers and profit and loss, followed by its staff list post by post; an address book of department-store people; a directory of the leading suppliers in the Kantō and Kansai regions (trade, firm, telephone, address, proprietor); and, at the end, a digest of the official maximum prices (公定價格) set by the Ministry of Commerce and Industry in 1940–41 for hundreds of everyday goods — furoshiki, ready-made woollen clothing and raincoats, knitwear, shoes, ties, scarves, sports goods, smoking articles, watches, sandals, umbrellas, toys, stationery, cutlery, lacquerware, china, aluminium ware, brooms, carpets, curtains, dried fish, pickles, soy sauce, ham, jam and tsukudani — with producer, wholesale and retail prices.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1071936).",
     "gaps": "The store profiles, staff lists, address book and supplier directory are transcribed as directory entries, and the official price lists as tables; the laws, the prose notes to the price notices, and the advertisements are not. The directories were read by Claude Sonnet 5.5 and the price lists by Claude Opus 5.5 (the prices are printed in tightly packed kanji numerals and were read from enlarged crops), each spread once, with no checking by eye. Figures and characters a reader could not make out with certainty are [?] or [illegible]. Where a store's staff list carries on without its heading, or a block of figures sits apart from its store, the reader's placement is noted in the entry's file. Price lists that run over several spreads were read in pieces and joined. The book prints all its price lists as one part, 公定價格要覽, with no divisions beyond its 41 sections; the seven chapters shown here in square brackets are groupings made for this site, in the printed order, and are not in the book.",
     "scan": "https://dl.ndl.go.jp/pid/1071936/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1071936",
     "model": "Claude Opus 5.5 (price lists) and Sonnet 5.5 (directories)",
     "dir_label": "Stores, staff, addresses & suppliers",
     "blank_marking": True},
    {"slug": "japan-toshi-1941", "dir": "Toshi_Nenkan_1941",
     "title": "日本都市年鑑 1941", "subtitle": "Nihon toshi nenkan (Japan Municipal Yearbook), 第10 (No. 10), 昭和16年用 (for Shōwa 16), with data mostly for 1938–1940",
     "publisher": "東京市政調査會 (Tokyo Institute for Municipal Research), 東京, 1941",
     "blurb": "The tenth edition of the Tokyo Institute for Municipal Research's yearbook of Japanese cities, covering the 160-odd cities of Japan with the cities and large towns of Korea, Taiwan, Karafuto, the Kwantung Leased Territory and Manchukuo, and short accounts of Chinese and foreign cities. Twenty chapters cover a general survey of all cities, city boundaries and their history, population, city assemblies, mayors and municipal staff, city planning, transport (railways, tramways, buses, harbours, aviation), gas, water supply, public health (infectious diseases, hospitals, crematoria, cemeteries, sewerage, refuse, parks), housing, social work, education, police and public safety, amusements, the economy (production, factories, prices, cost of living, wages, interest rates, commerce), economic administration, municipal and colonial finance (revenue, expenditure, property, debt, taxation, new works), Manchukuo cities, Chinese cities and foreign cities.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1271158).",
     "gaps": "Every table is transcribed, including the small tables set into the chapter introductions and the city accounts; the prose, the contents, the city indexes, advertisements and the publisher's lists are not. Each table was read once by Claude Sonnet 5.5 (tables running over several spreads were kept with one reader) or Claude Haiku 5.5 (single-spread tables), from full-resolution crops, with no check by eye; two Haiku batches that stopped partway were redone by Sonnet. Unreadable figures are [?]; printed totals that do not add up are kept as printed and noted. Tables printed in pieces on separate pages (marked 頁へ續く) are joined in the book's reading order.",
     "scan": "https://dl.ndl.go.jp/pid/1271158/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1271158",
     "model": "Claude Sonnet 5.5 and Haiku 5.5",
     "blank_marking": True},
    {"slug": "japan-toshi-1936", "dir": "Toshi_Nenkan_1936",
     "title": "日本都市年鑑 1936", "subtitle": "Nihon toshi nenkan (Japan Municipal Yearbook), 第5 (No. 5), 昭和11年用 (for Shōwa 11), with data mostly for 1933–1935",
     "publisher": "東京市政調査會 (Tokyo Institute for Municipal Research), 東京, 1936",
     "blurb": "The fifth edition of the Tokyo Institute for Municipal Research's yearbook of Japanese cities, covering the 128 cities of Japan with the cities of Korea, Taiwan, the Kwantung Leased Territory, Karafuto and Manchukuo where available. Twenty-five chapters cover a general survey and list of all cities, city boundaries, population (births, deaths, occupations, age groups), city assemblies, mayors and municipal staff, city planning, civil engineering and building, roads and road traffic, rivers and harbours, aviation, posts and telecommunications, tramways and local railways, buses, electricity supply and rates, gas, water supply and water rates, sewerage and refuse disposal, public health (infectious diseases, hospitals, crematoria, cemeteries, parks), social work and relief, markets and slaughterhouses, industrial promotion, education, police and fire services, amusements, the economy (production, factories, prices, wages, commerce, unemployment) and municipal, prefectural and colonial finance.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1446423).",
     "gaps": "Every table is transcribed, including the small tables set into the chapter introductions; the prose, the contents, the city indexes, the bibliography of municipal literature, advertisements and the publisher's lists are not. Each spread was read once by Claude Haiku 5.5 (most tables) or Claude Sonnet 5.5 (the list of all cities, electricity, tramway and water rate schedules, and other text-heavy tables) from full-resolution crops, with no check by eye. Claude Sonnet 5.5 then re-read the tables whose rows did not add up in suspicious numbers or whose names were left unreadable, and redid two batches in full; several misaligned cells were corrected. Unreadable figures are [?]; printed totals that do not add up are kept as printed and noted. Tables printed over several spreads were read in pieces and joined; tables whose title runs across the gutter were joined row by row from their left- and right-page halves.",
     "scan": "https://dl.ndl.go.jp/pid/1446423/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1446423",
     "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-toshi-1931", "dir": "Toshi_Nenkan_1931",
     "title": "日本都市年鑑 1931", "subtitle": "Nihon toshi nenkan (Japan Municipal Yearbook), 第1 (No. 1), 昭和6年用 (for Shōwa 6), with data mostly for 1928–1930",
     "publisher": "東京市政調査會 (Tokyo Institute for Municipal Research), 東京, 1931",
     "blurb": "The first edition of the Tokyo Institute for Municipal Research's yearbook of Japanese cities: a statistical survey of all 109 cities of Japan (the 六大都市 Tokyo, Osaka, Kyoto, Nagoya, Kobe and Yokohama, and the other 市), with the colonial cities of Korea, Taiwan and the Kwantung Leased Territory where available. Twenty chapters cover city summaries (各市要覽), land and boundary extensions, population, births and deaths, city assemblies, mayors and municipal staff, municipal finance (revenue, taxes, expenditure, debt, property and tax rates), city planning, roads, rivers, canals and harbours, electricity supply and rates, tramways and buses, gas, markets and slaughterhouses, water supply and water rates, sewerage, refuse disposal, public health, hospitals, crematoria, cemeteries and parks, education, social work, police and fire services, and industry, banks, trade and wages; a supplement gives the preliminary results of the 1930 census for every city.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1465003).",
     "gaps": "Every table is transcribed, including the small tables set into the chapter introductions (概説); the prose, the contents, the city indexes, advertisements and the publisher's list of publications are not. Each spread was read once by Claude Haiku 5.5 (simple city tables) or Claude Sonnet 5.5 (the city summaries, electricity, tramway, gas and water rate schedules and other text-heavy tables) from full-resolution crops, with no check by eye. Claude Sonnet 5.5 then re-read the italic per-capita and rate columns of the early tables (3 figures corrected), several tables with unreadable names or misplaced rows, and one batch read at too low a resolution. Unreadable figures are [?]; printed totals that do not add up are kept as printed and noted. Tables printed over several spreads were read in pieces and joined; where the left and right pages of a spread carry different columns for the same cities they are joined row by row, or, where the rows do not line up, given as separate parts. Frame p0298 repeats pp. 550–551 (p0300) and is not used.",
     "scan": "https://dl.ndl.go.jp/pid/1465003/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1465003",
     "model": "Claude Haiku 5.5 and Sonnet 5.5",
     "blank_marking": True},
    {"slug": "japan-tokei-1940", "dir": "Japan_Tokei_1940",
     "title": "大日本帝國統計年鑑 1940", "subtitle": "Dai Nippon Teikoku tōkei nenkan (Statistical Yearbook of the Empire of Japan), 第五十九回 (No. 59), 昭和十五年 (Shōwa 15), published 1941",
     "publisher": "內閣統計局, 東京, 1941",
     "blurb": "The Cabinet Statistics Bureau's statistical yearbook of the Japanese Empire, 59th and last of the series, in its shortened wartime form (stamped 防諜上取扱注意, 'handle with care for counter-espionage'): 209 numbered tables in 14 chapters — land, population, agriculture, forestry and fisheries, industry, commerce and banking, trade, transport and communications, welfare, labour, education, shrines and religion, police, public health and disasters, justice, public finance, and pensions — with a table of weights and measures. Most tables give a run of years to 1938 or 1939 for Japan proper (內地), often by prefecture, with the overseas territories (Korea, Taiwan, Karafuto, the Kwantung Leased Territory and the South Seas) shown separately or in their own tables. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1275672; a second copy is pid 1461165). The earlier volumes of the 1930s are digitized by the NDL but not open to the public.",
     "gaps": "All 209 numbered tables are transcribed, with four unnumbered sub-tables printed beside them and the weights-and-measures tables (度量衡比較、合數及略算法); the contents, the index, the page of charts (which print no figures), the bureau's list of publications and the colophon are not. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined; where a table is printed as successive column blocks with different year ranges (table 25), each block is a separate part. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by one or two units of rounding in thousand-yen figures). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. About 320 of some 119,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. A spot check, in which a second model re-transcribed two tables (1,296 figures) independently, agreed on all but one cell, which is marked unreadable.",
     "scan": "https://dl.ndl.go.jp/pid/1275672/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1275672",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1933", "dir": "Taiwan_Tokei_1933",
     "title": "臺灣總督府統計書 1933", "subtitle": "Taiwan Sōtokufu tōkeisho (Statistical Yearbook of the Government-General of Taiwan), 第三十七 (No. 37), 昭和八年 (Shōwa 8), published 1935",
     "publisher": "臺灣總督官房調查課, 臺北, 1935 (昭和十年三月)",
     "blurb": "The Government-General of Taiwan's statistical yearbook for 1933 (昭和8年), the 37th of the series: 536 numbered tables in 23 chapters — land, climate, population, education, shrines, temples and churches, social work, courts and registration, police, prisons, agriculture, forestry, fisheries, mining, manufacturing, electricity, commerce and banking, trade, transport and communications, the government monopolies, public health, public finance, officials, and honours and pensions — with a table of weights and measures. Most tables give 1933 figures by prefecture (州) and district (廳) with a run of earlier years, usually 1928–1932; population tables distinguish Japanese (內地人), Taiwanese (本島人), Koreans, Chinese and other foreigners. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1711175).",
     "gaps": "All 536 numbered tables are transcribed, with the unnumbered sub-tables printed beside them and the table of weights and measures; the contents pages, the map and the four charts are not. Two frames of the scan repeat earlier pages and were skipped. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by a yen or two of rounding). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. The book's errata slip (正誤表, 6 corrections) is attached as a note to each table it concerns; the figures stay as printed. Small figures printed under a main figure with a mark such as ×, △ or ※ (e.g. 兼務, 朝鮮人, 蕃人) are written after it, as in \"209 ×24\". About 270 of some 197,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. A spot check, in which a second model re-transcribed three tables (1,275 figures) independently, agreed on all but one cell, which is marked unreadable.",
     "scan": "https://dl.ndl.go.jp/pid/1711175/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1711175",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1942", "dir": "Taiwan_Tokei_1942",
     "title": "臺灣總督府統計書 1942", "subtitle": "Taiwan Sōtokufu tōkeisho (Statistical Yearbook of the Government-General of Taiwan), 第四十六 (No. 46), 昭和十七年 (Shōwa 17), published 1944",
     "publisher": "臺灣總督府, 臺北, 1944 (昭和十九年三月)",
     "blurb": "The Government-General of Taiwan's statistical yearbook for 1942 (昭和17年), the 46th of the series and one of the last published under Japanese rule: 371 numbered tables in 19 chapters — land, population, shrines, temples and religion, social work, police, courts and registration, prisons, transport and communications, the government monopolies, public health, commerce and banking, agriculture, fisheries, mining, forestry, manufacturing, education, public finance, and officials, honours and pensions — with a table of weights and measures. Most tables give 1942 figures by prefecture (州) and district (廳) with the five years before, 1937–1941; population tables distinguish Japanese (內地人), Taiwanese (本島人), Koreans and Chinese. The wartime edition carries a counter-espionage (防諜) notice, and several pages bear a 軍資秘 (military-resources secret) stamp. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1135464).",
     "gaps": "All 371 numbered tables are transcribed, with one unnumbered block beside table 29 and the table of weights and measures; the contents pages are not. The NDL scan is low-resolution and often blurred, so this volume has far more unreadable cells than the earlier ones: about 2,460 of some 109,000 figure cells could not be read and are marked [?] (in 250 tables), and many column headings and row labels in small type contain [?] for characters that could not be made out. The book prints figures in groups of four digits (8 1897 = 81,897); they are written here with standard thousands commas. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by a yen or two of rounding; on this scan some differences may be misreadings that could not be resolved). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. Small figures printed under a main figure with a mark such as × or △ (e.g. 兼務, 工賃) are written after it, as in \"209 ×24\"; where they were too small to read they are given as ×[?] or, in a few tables, left out, as each table's notes say. A literal ? printed in the book is kept as ?. No independent second reading was made for this volume.",
     "scan": "https://dl.ndl.go.jp/pid/1135464/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1135464",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1938", "dir": "Taiwan_Tokei_1938",
     "title": "臺灣總督府統計書 1938", "subtitle": "Taiwan Sōtokufu tōkeisho (Statistical Yearbook of the Government-General of Taiwan), 第四十二 (No. 42), 昭和十三年 (Shōwa 13), published 1940",
     "publisher": "臺灣總督官房企畫部, 臺北, 1940 (昭和十五年三月)",
     "blurb": "The Government-General of Taiwan's statistical yearbook for 1938 (昭和13年), the 42nd of the series: 499 numbered tables in 21 chapters — land, climate, population, education, shrines, temples and religion, social work, police, courts and registration, prisons, agriculture, forestry, fisheries, mining, manufacturing, commerce and banking, trade, transport and communications, the government monopolies, public health, public finance, and officials, honours and pensions — with a table of weights and measures. Most tables give 1938 figures by prefecture (州) and district (廳) with a run of earlier years, usually 1933–1937; population tables distinguish Japanese (內地人), Taiwanese (本島人), Koreans, Chinese and other foreigners. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1135373).",
     "gaps": "All 499 numbered tables are transcribed, with three unnumbered sub-tables printed beside them and the table of weights and measures; the contents pages, the fold-out map of the island and the prose overview (概說) are not. The NDL scan is low-resolution and often blurred: about 1,710 of some 146,000 figure cells could not be read and are marked [?] (in 278 tables), and some column headings and row labels in small type contain [?] for characters that could not be made out. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by a yen or two of rounding; on this scan some differences may be misreadings that could not be resolved). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. The book's errata slip (正誤表, partly illegible in the scan) is attached as a note to each table it concerns; the figures stay as printed. Small figures printed under a main figure with a mark such as × or △ (e.g. 兼務) are written after it, as in \"209 ×24\"; where they were too small to read they are given as ×[?] or, in a few tables, left out, as each table's notes say. A literal ? printed in the book is kept as ?. A spot check, in which a second model re-transcribed two tables (285 figures) independently, agreed on all but one cell, which is marked unreadable.",
     "scan": "https://dl.ndl.go.jp/pid/1135373/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1135373",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-koko-1905", "dir": "Taiwan_Koko_Chosa_1905",
     "title": "臨時臺灣戶口調査結果表 1905", "subtitle": "Rinji Taiwan kokō chōsa kekkahyō, 明治38年 (Results Tables of the Provisional Census of Taiwan, 1 October 1905)",
     "publisher": "臨時臺灣戶口調査部 (Provisional Census Department, Government-General of Taiwan), 臺北, 1908 (明治41年2月)",
     "blurb": "The results tables of the first census of Taiwan, taken on 1 October 1905 — 123 tables of the island's population by district (廳), sex, age and race (Japanese, Taiwanese of Hokkien and Hakka origin, sinicised and other aborigines, Chinese and other foreigners): area, households and population; age, infants by month of age and marital status; principal and secondary occupations, dependants and occupied persons by occupational class, item and status, for the island and for the three cities; languages spoken; literacy; disabilities and their causes; foot-binding and its abandonment; the birthplace, registered domicile and arrival in Taiwan of Japanese residents; foreigners by nationality; opium smoking; household composition and size; and dwellings and their tenure.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 805872).",
     "gaps": "Every table is transcribed. Most tables run over several spreads — later spreads continuing the columns (more occupations or categories), the next sex, or the percentage and per-mille blocks; each spread is one part of its table, as printed. Every spread was read once by Claude Sonnet 5.5 from tight crops (Arabic figures). The errata slip (誤正表, 21 corrections) is attached as a note to each table it concerns; the figures stay as printed. Some small-print row labels illegible on one spread were completed from another spread of the same table, with a note. Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted; printed totals that do not add up are kept as printed and noted. 66 of about 172,000 filled cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/805872/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/805872",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1897", "dir": "Taiwan_Tokei_1897",
     "title": "臺灣總督府統計書 1897", "subtitle": "Taiwan Sōtokufu tōkeisho, 第一 (No. 1), 明治三十年 (Meiji 30)",
     "publisher": "臺灣總督府民政部文書課, 1899",
     "blurb": "The first statistical annual of the Government-General of Taiwan, giving figures mostly for 1897 (明治30年), two years after the Japanese occupation: 168 numbered tables in 12 chapters — land, population, education, civil and criminal justice, police, prisons, agriculture and manufacturing, foreign trade, transport and communications, public health, public finance, and officials. Tables are mostly broken down by prefecture (縣) and district office (廳), and population tables distinguish Japanese (內地人) from Taiwanese (本島人). Tables are given in Japanese with the old character forms as printed; the kanji numerals of the original are written as Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 805830), in which the first and second annuals are bound together.",
     "gaps": "All 168 numbered tables are transcribed, together with the printed contents. Tables printed across both pages of a spread, or read in sections by different readers, are joined into one. The tables were read by Opus sub-agents from enlarged crops, a few of the last ones by Opus 5.5 through the API and by the orchestrating session; there was no second reading. Printed totals were re-added: totals that do not add up are kept as printed and noted in the table. Where the only doubt was how stacked 一/二/三 strokes group and exactly one reading made a printed total reconcile, that reading is used and noted. Small figures for concurrent post-holders (兼務, marked △ or ×) are written after the main figure, e.g. 372 (△8, ×38). 87 of some 70,000 figure cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/805830/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/805830",
     "model": "Opus 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1898", "dir": "Taiwan_Tokei_1898",
     "title": "臺灣總督府統計書 1898", "subtitle": "Taiwan Sōtokufu tōkeisho, 第二 (No. 2), 明治三十一年 (Meiji 31)",
     "publisher": "臺灣總督府民政部文書課, 1900",
     "blurb": "The second statistical annual of the Government-General of Taiwan, giving figures mostly for 1898 (明治31年), often with 1897 for comparison: 218 numbered tables in 19 chapters — land, population, education, shrines and temples, civil and criminal justice, police, prisons, agriculture, fisheries and salt, mining, manufacturing and commerce, opium, foreign trade, banking and finance, transport and communications, public health, relief, public finance, and officials. Tables are mostly broken down by prefecture (縣) and district office (廳), and population tables distinguish Japanese (內地人) from Taiwanese (本島人). Tables are given in Japanese with the old character forms as printed; the kanji numerals of the original are written as Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 805830), in which the first and second annuals are bound together.",
     "gaps": "All 218 numbered tables are transcribed, together with the printed contents. Tables printed across both pages of a spread, or read in sections by different readers, are joined into one. The tables were read by Opus sub-agents from enlarged crops, a few of the last ones by Opus 5.5 through the API and by the orchestrating session; there was no second reading. Printed totals were re-added: totals that do not add up are kept as printed and noted in the table. Where the only doubt was how stacked 一/二/三 strokes group and exactly one reading made a printed total reconcile, that reading is used and noted. Small figures for concurrent post-holders (兼務, marked △ or ×) are written after the main figure, e.g. 372 (△8, ×38). 154 of some 90,000 figure cells could not be read and are marked [?].",
     "scan": "https://dl.ndl.go.jp/pid/805830/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/805830",
     "model": "Opus 5.5",
     "blank_marking": True},
    {"slug": "taiwan-tokei-1925", "dir": "Taiwan_Tokei_1925",
     "title": "臺灣總督府統計書 1925", "subtitle": "Taiwan Sōtokufu tōkeisho (Statistical Yearbook of the Government-General of Taiwan), 第二十九 (No. 29), 大正十四年 (Taishō 14), published 1927",
     "publisher": "臺灣總督官房調查課, 臺北, 1927",
     "blurb": "The Government-General of Taiwan's statistical yearbook for 1925 (大正14年), the 29th of the series: 512 numbered tables in 23 chapters — land, climate, population, education, shrines and temples, social work, courts and registration, police, prisons, agriculture, forestry, fisheries, mining, manufacturing, electricity, commerce and banking, trade, transport and communications, the government monopolies (camphor, tobacco, alcohol, opium, salt), public health, public finance, officials, and honours and pensions. Most tables give 1925 figures by prefecture (州) and district (廳) with a run of earlier years, usually back to 1920 or 1921; population tables distinguish Japanese (內地人), Taiwanese (本島人), Indigenous people and foreigners. Tables are given in Japanese with the old character forms as printed and Arabic numerals.",
     "source": "LLM-transcribed from the National Diet Library scan (NDL pid 1710988).",
     "gaps": "All 512 numbered tables are transcribed; the contents pages, the fold-out map and the three charts are not. Tables printed across both pages of a spread are joined into one, and long tables read in sections by different readers are joined. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted (many differ by a yen or two of rounding). Where a digit was ambiguous only between 3 and 8 and exactly one reading made a printed total reconcile, that reading is used and noted. The book's own errata slip (正誤, 35 corrections) is attached as a note to each table it concerns; the figures stay as printed. Small figures printed under a main figure with a marker such as (1) (e.g. 兼務, 朝鮮人) are written after it, as in \"30 (1)1\"; in a few tables these small figures were not transcribed, as each table's notes say. About 980 of some 177,000 figure cells could not be read and are marked [?]; a literal ? printed in the book is kept as ?. A spot check, in which a second model re-transcribed four tables (1,693 figures) independently, agreed on every digit.",
     "scan": "https://dl.ndl.go.jp/pid/1710988/1/{leaf}",
     "item": "https://dl.ndl.go.jp/pid/1710988",
     "model": "Sonnet 5.5",
     "blank_marking": True},
    {"slug": "taiwan-1905", "dir": "Taiwan_Progress_1905",
     "title": "The Progress of Taiwan 1905", "subtitle": "台湾十年間之進歩 The Progress of Taiwan",
     "publisher": "Taiwan Nichinichi Shinpōsha, Taihoku, 1905",
     "blurb": "A bilingual (Japanese and English) statistical survey of Taiwan's first ten years under Japanese rule, 1896–1905, in fifteen parts: territory and population, agriculture and industries, foreign commerce, post and telegraph, railways and roads, navigation, banks, education, public sanitation, relief, police, prisons, civil and criminal justice, administration and finance. Titles, headings and row labels keep both the Japanese and the English as printed.",
     "source": "LLM-transcribed from the Internet Archive scan (a Google scan of the Keio University copy).",
     "gaps": "Only tables are transcribed; the preface, contents, map and the bar charts (which print no figures) are not. The print is faint and broken in places: figures that could not be read with certainty are marked [?], and every such cell was read a second time at high zoom. Where a digit could only be 3 or 8 and a printed total reconciles with exactly one reading, that reading is used and noted. Printed totals that do not add up are kept as printed and noted. Wide tables printed across two facing pages are joined into one table.",
     "scan": "https://archive.org/details/the-progress-of-taiwan-1905/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/the-progress-of-taiwan-1905",
     "blank_marking": True},
    {"slug": "taiwan-1912", "dir": "Taiwan_Statistical_Summary_1912",
     "title": "The Statistical Summary of Taiwan 1912", "subtitle": "The Statistical Summary of Taiwan (Formosa)",
     "publisher": "Government of Formosa, Taihoku, 1912",
     "blurb": "An English statistical summary of Taiwan under Japanese rule, mostly 1897–1911, in thirty-three chapters: land, forests, administrative divisions, climate, population, education, religion, justice, police, aborigine affairs, prisons, agriculture, stock farming, marine products, minerals, manufacturing, wages, electricity, the money market and banks, prices, foreign trade and trade with Japan, roads, railways, post, telegraph and telephone, shipping, finance, public health, the government monopolies, charity and the civil service.",
     "source": "LLM-transcribed from the Internet Archive scan (Cornell University Library copy).",
     "gaps": "Only tables are transcribed; the introduction's prose, photographs and maps are not. The pages with tables were found from contact sheets and only those pages were read. Figures that could not be read with certainty are marked [?]. Where a digit could only be 3 or 8 and a printed total reconciles with exactly one reading, that reading is used and noted. Printed totals that do not add up are kept as printed and noted. Tables printed as left and right halves on facing pages are joined into one table.",
     "scan": "https://archive.org/details/cu31924023931680/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/cu31924023931680",
     "blank_marking": True},
    {"slug": "china-peking-1921", "dir": "Peking_Social_Survey_1921", "model": "Sonnet 5.5",
     "title": "Peking: A Social Survey 1921",
     "publisher": "Sidney D. Gamble and John Stewart Burgess",
     "blurb": "A pioneering American social survey of Peking around 1917–1919: geography, government and police, population (the 1917 police census, age and sex, foreigners), health, education, commercial life and the gilds, recreation, prostitution, poverty and philanthropy, prisons, a block-by-block study of the Teng Shih K'ou district, a survey of Christian church families, and religious work. Most figures are in the appendices; each table here carries a one-sentence note on its context in the book.",
     "source": "LLM-transcribed from the Internet Archive scan (JP2 page images).",
     "gaps": "Only tables, columnar lists and charts that print their figures are transcribed; the running text, photographs, maps, numbered regulations and the index are not. Charts that print only axes (e.g. Figs. 7, 8, 29, 33, 34) are skipped. The pages with tables were found from contact sheets; every appendix page was read. Printed pp. 168–169 are missing from the scan. Many printed totals in this book do not add up; every such table was transcribed a second time independently, both readings agreed cell for cell, and the totals are kept as printed and noted. The one-sentence context notes are written by the transcriber from the surrounding text.",
     "scan": "https://archive.org/details/pekingsocialsurv00gambrich/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/pekingsocialsurv00gambrich",
     "blank_marking": True},
    {"slug": "china-handbook-1919-20", "dir": "China_Commercial_Handbook_1919", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Commercial Handbook of China 1919-20",
     "subtitle": "Volumes 1 and 2",
     "publisher": "Julean Arnold and American consular officers; U.S. Department of Commerce, Bureau of Foreign and Domestic Commerce, Miscellaneous Series No. 84, Washington, 1919-1920",
     "blurb": "The U.S. Commerce Department's two-volume survey of China for American business. Volume 1: geography, commercial statistics for China as a whole (imports, exports, trade with the United States, shipping) and a report on each of nineteen consular districts (population, agriculture, mining, communications, finance, industries, the trade of each port). Volume 2: government, history, the treaty, courts and consulates, trade-marks, customs, tariffs, posts, railways, ports and shipping, currency and banking, government finance, concessions, guilds, Chinese products, cotton goods, business practice, education, labour and living conditions, weights and measures, and lists of officials and institutions.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from the Internet Archive scan (Google, from a Harvard copy), in which both volumes are bound together.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, photographs, maps, the glossary and the reading lists are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading), very dense tables and tables continued over pages; a table running over several pages was read in one call with all its pages. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. In this Google scan the figures in some large trade tables are partly blanked out (for example China's trade in Haikwan taels, Vol. 1 p. 47, and cotton imports, Vol. 2 p. 329); those cells are marked unreadable. Volume 2 numbers its pages from 1 again; chapters are labelled Vol. 1 or Vol. 2.",
     "scan": "https://archive.org/details/commercialhandb00arnogoog/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/commercialhandb00arnogoog",
     "blank_marking": True},
    {"slug": "china-handbook-1926", "dir": "China_Commercial_Handbook_1926",
     "title": "China, a Commercial and Industrial Handbook 1926", "subtitle": "China: A Commercial and Industrial Handbook",
     "publisher": "Julean Arnold, U.S. Department of Commerce, Bureau of Foreign and Domestic Commerce (Trade Promotion Series No. 38), Washington, 1926",
     "blurb": "A U.S. government handbook on China's commerce and industries in the early 1920s: geography, the trade of China and its import trade by commodity, currency, exchange and banking, export products, modern industries, the economic structure, government finance, railways and Americans in China, followed by surveys of each American consular district (Canton, Hankow, Hongkong, Mukden, Shanghai, Tientsin, Amoy, Antung, Changsha, Chefoo, Chungking, Dairen, Foochow, Harbin, Kalgan, Nanking, Swatow, Tsinan, Tsingtao and Yunnan) with their trade, industries, banks, transport and living costs. Lists of banks, chambers of commerce, trade organizations, mines, electric plants and newspapers are on the directory page.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Only tables and directory-like lists are transcribed; the running text, photographs, maps, bibliographies and index are not. The pages with tables were found from contact sheets and only those pages were read. Most tables have no printed title, so their titles are given in [brackets]. Where a digit could only be 3 or 8 and a printed total reconciles with exactly one reading, that reading is used and noted. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/chinacommerciali00arno/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinacommerciali00arno",
     "blank_marking": True},
    {"slug": "manchoukuo-1942", "dir": ".", "title": "The Manchoukuo Year Book 1942",
     "publisher": "Manchoukuo Year Book Co., Hsinking, 1942",
     "blurb": "Official English-language yearbook of Manchukuo: geography, population, finance, banking, trade, agriculture, mining, industry, transport, labour, education and more.",
     "source": "LLM-transcribed from 498 photographs of the printed volume (two-page spreads).",
     "gaps": "The online Internet Archive copy is the same set of photographs, cropped and in greyscale, so the scan links open the same spread. Pages 502–503 (Mining) and 966–967 (Index) were not photographed. Gaps in table numbering (e.g. Agriculture Tables 2–3 and 11–17) are in the printed book itself.",
     "scan": "https://archive.org/details/manchoukuo-yearbook-1942/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/manchoukuo-yearbook-1942"},
    {"slug": "far-east-1941", "root": os.environ.get("FAR_EAST_ROOT") or os.path.join(os.path.dirname(ROOT), "The Far East Year Book 1941"),
     "title": "The Far East Year Book 1941",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1941",
     "blurb": "Japan, its colonies (Chosen, Taiwan, Karafuto, the South Sea Islands), Manchoukuo and occupied China, with shorter sections on the Philippines, French Indo-China, Thailand, British Malaya, the Netherlands East Indies and British Borneo.",
     "source": "LLM-transcribed from 581 photographs of the printed volume (two-page spreads).",
     "gaps": "Printed pp. 394–395 (Japan, Chemical and Ceramic Industries; Chemical Tables 11–16) were not photographed. One spread (pp. 1118–1119) was photographed twice; the duplicate is ignored. Numbering gaps are in the printed book: Arts and Crafts cites Tables 6–8 but prints only 1–7, and Japan Labor has no Table 11 and two Tables 15. The National Defence Army Districts table is printed in two places (pp. 101 and 111) and is merged here. Maps, charts without figures and running prose are not transcribed. The China railways descriptions and similar name-and-paragraph lists are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/far-east-year-book-1941/{partname}/page/n{leaf}/mode/1up",
     "scan_parts": {1: "Far%20East%20Year%20Book%201941%20Part%201%20Japan", 2: "Far%20East%20Year%20Book%201941%20Part%202"},
     "item": "https://archive.org/details/far-east-year-book-1941"},
    {"slug": "pacific-survey-1941-42", "dir": "Pacific_Survey_1941_42", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "An Economic Survey of the Pacific Area 1941-42",
     "subtitle": "Part I: Population and Land Utilization (Karl J. Pelzer, 1941) · Part II: Transportation (Katrine R. C. Greene, 1941) · Part III: Industrialization of the Western Pacific (Kate L. Mitchell, 1942)",
     "publisher": "International Secretariat, Institute of Pacific Relations (Frederick V. Field, general editor), 1941-1942; Parts I and II printed in Shanghai by the Willow Pattern Press, Part III in New York by the Haddon Craftsmen",
     "blurb": "The Institute of Pacific Relations' three-part economic survey of the Pacific on the eve of the Pacific War. Part I: population (distribution, growth, age, rural and urban, occupations, migration) and land utilization and tenure. Part II: shipping, railways, highways and motor vehicles, and airways. Part III: industrial and mining development and wartime industry. Countries covered include the Soviet Union, Japan, Korea, Formosa, Manchuria, China, the Philippines, French Indo-China, Thailand, British Malaya, Burma, the Netherlands Indies, India, Australia, New Zealand, Canada and the United States.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from Google scans (via HathiTrust) of copies at the University of Michigan (Part I), the University of California (Part II) and the University of Wisconsin (Part III), each uploaded to the Internet Archive.",
     "gaps": "Only the statistical tables are transcribed; the text, maps, lists of tables, indexes, the publisher's list and the Institute's front matter are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading), very dense tables and tables continued over pages; a table running over several pages was read in one call with all its pages. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. Each part numbers its pages from 1; chapters are labelled Part I, II or III, and tables are filed under the chapter and country section in which they are printed, from each part's contents.",
     "scan": "https://archive.org/details/{partname}/page/n{leaf}/mode/1up",
     "scan_parts": {1: "economic-survey-pacific-area-1941-part-1", 2: "economic-survey-pacific-area-1941-part-2", 3: "economic-survey-pacific-area-1942-part-3"},
     "item": "https://archive.org/details/economic-survey-pacific-area-1941-part-1",
     "blank_marking": True},
    {"slug": "china-1912", "dir": "China_Year_Book_1912", "title": "The China Year Book 1912",
     "publisher": "H. T. Montague Bell and H. G. W. Woodhead (eds.); London: George Routledge & Sons; New York: E. P. Dutton & Co.",
     "blurb": "The first edition of the English-language reference book on China, compiled during the 1911 Revolution.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "Transcribed from a Google scan of the University of Minnesota copy. The scan repeats a run of pages (PDF pages 349–382 duplicate earlier ones); no printed pages are missing. Numbered legal clauses (the Constitution, court and loan regulations, opium agreements) are prose and not transcribed. The mines and companies, the per-railway 'Further Details' and the Government Institutions at Peking are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-year-book-1912/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1912"},
    {"slug": "china-1914", "dir": "China_Year_Book_1914", "model": "Haiku 5.5", "title": "The China Year Book 1914",
     "publisher": "H. T. Montague Bell and H. G. W. Woodhead (eds.); Shanghai: North-China Daily News & Herald, 1914",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/chinayearbook1914shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1914shan",
     "blank_marking": True},
    {"slug": "china-1919", "dir": "China_Year_Book_1919", "model": "Haiku 5.5", "title": "The China Year Book 1919",
     "publisher": "H. G. W. Woodhead (ed.); Shanghai: North-China Daily News & Herald, 1919",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/chinayearbook1919shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1919shan",
     "blank_marking": True},
    {"slug": "china-1913", "dir": "China_Year_Book_1913", "model": "Haiku 5.5", "title": "The China Year Book 1913",
     "publisher": "H. T. Montague Bell and H. G. W. Woodhead (eds.), 1913",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1913/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1913",
     "blank_marking": True},
    {"slug": "china-1916", "dir": "China_Year_Book_1916", "model": "Haiku 5.5", "title": "The China Year Book 1916",
     "publisher": "H. G. W. Woodhead and H. T. Montague Bell (eds.), 1916",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1916/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1916",
     "blank_marking": True},
    {"slug": "china-1922", "dir": "China_Year_Book_1922", "title": "The China Year Book 1921-2",
     "publisher": "H. G. W. Woodhead (ed.), H. T. Montague Bell (assoc. ed.); Tientsin: Tientsin Press",
     "blurb": "The Peking-government-era edition of the English-language reference book on China, covering population, geography, trade, finance, loans, currency, communications, defence, education, Greater China, opium, the customs tariff, the government and a Who's Who.",
     "source": "LLM-transcribed from the Internet Archive scan (University of Toronto copy).",
     "gaps": "No printed pages are missing from the scan. On p. 482 (Postal Statistics, Appendix 2) the Total row runs off the bottom edge of the scan, so its cells are blank. The fold-out on p. 992a (Maritime Customs Revenue of Each Port, 1920) is included. The warship list is printed across facing pages (pp. 542–545) and its two halves were joined line by line. Six tables that run across pages were transcribed with different column layouts on each side and are kept as separate parts (General Loans, pp. 258–263; Treaty Ports, pp. 219–220; Ministry of Foreign Affairs and Legations abroad, pp. 859–863; Salt Revenue staff, pp. 874–875; British Chambers of Commerce, pp. 970–971). Legal texts (the Provisional Criminal Code, treaties, agreements) are transcribed only where they contain tables or lists. The Contents, Index, advertisements and the folding map are not transcribed. The Who's Who, the List of Factories using Foreign Machinery and the Foreign Banks with Branches in China are on the Who's Who & Directories page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where. The tables were read once; they have not been double-checked by a second reading.",
     "scan": "https://archive.org/details/chinayearbook1922shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1922shan"},
    {"slug": "china-1923", "dir": "China_Year_Book_1923", "model": "Haiku 5.5", "title": "The China Year Book 1923",
     "publisher": "H. G. W. Woodhead (ed.), 1923",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1923/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1923",
     "blank_marking": True},
    {"slug": "china-1924-5", "dir": "China_Year_Book_1924", "model": "Haiku 5.5", "title": "The China Year Book 1924-5",
     "publisher": "H. G. W. Woodhead (ed.), 1924",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1924-5/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1924-5",
     "blank_marking": True},
    {"slug": "china-1925-6", "dir": "China_Year_Book_1925", "model": "Haiku 5.5", "title": "The China Year Book 1925-6",
     "publisher": "H. G. W. Woodhead (ed.), 1925",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1925-6/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1925-6",
     "blank_marking": True},
    {"slug": "china-1926-7", "dir": "China_Year_Book_1926", "model": "Haiku 5.5", "title": "The China Year Book 1926-7",
     "publisher": "H. G. W. Woodhead (ed.), 1926",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1926-7/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1926-7",
     "blank_marking": True},
    {"slug": "china-1928", "dir": "China_Year_Book_1928", "model": "Haiku 5.5", "title": "The China Year Book 1928",
     "publisher": "H. G. W. Woodhead (ed.), 1928",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/china-year-book-1928/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1928",
     "blank_marking": True},
    {"slug": "china-1929-30", "dir": "China_Year_Book_1929-30", "title": "The China Year Book 1929-30",
     "publisher": "H. G. W. Woodhead (ed.); Tientsin: The Tientsin Press",
     "blurb": "The Nationalist-era edition of the English-language reference book on China.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "The scan's page order is scrambled in places (parts of the Who's Who and of Chapter III are bound out of sequence); tables are filed under their printed pages. The first sheet of the fold-out on p. 658 (railway-secured foreign loans) is missing from the scan, so that table starts at sheet 658 b. On Who's Who p. 998 a strip near the right margin is missing from the scan, leaving gaps marked [illegible]. Treaty texts, laws and regulations are transcribed only where they contain tables or lists; numbered articles are prose. The Contents, indexes and advertisements are not transcribed. The Chinese Who's Who (pp. 919–1002) is on the Who's Who page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-year-book-1929-30/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-year-book-1929-30"},
    {"slug": "china-1931-2", "dir": "China_Year_Book_1931", "model": "Haiku 5.5", "title": "The China Year Book 1931-2",
     "publisher": "H. G. W. Woodhead (ed.), 1932",
     "blurb": "An edition of the English-language reference annual on China: geography and population, the government and its officials, foreign relations and treaty ports, finance, loans and currency, trade and the Maritime Customs, railways, posts and telegraphs, shipping, mines and industries, the army and navy, education and missions, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/chinayearbook1930000hgww_y9v2/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1930000hgww_y9v2",
     "blank_marking": True},
    {"slug": "china-1944", "dir": "China_Handbook_1944", "model": "Haiku 5.5", "title": "China Handbook 1944",
     "publisher": "Chinese Ministry of Information, 1944",
     "blurb": "The wartime China Handbook compiled by the Chinese Ministry of Information: government and politics, foreign relations, the war of resistance, finance and banking, economy and industry, communications, education and culture, public health and relief, with a Who's Who and directories.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from a scan of the printed volume; the Internet Archive copy (a lending-library item) is linked from each table, but not page by page.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/chinahandbook0000unse",
     "item": "https://archive.org/details/chinahandbook0000unse",
     "blank_marking": True},
    {"slug": "china-provinces-1910", "dir": "China_National_Review_1910", "model": "Haiku 5.5",
     "title": "The Provinces of China 1910",
     "subtitle": "The National Review Annual 1910: The Provinces of China, together with a history of the first year of H.I.M. Hsuan Tung, and an account of the government of China",
     "publisher": "The National Review Office, Shanghai, 1910",
     "blurb": "A Shanghai reference annual describing each of the eighteen provinces of China and the outer territories (Tibet, Sinkiang, Mongolia, Manchuria) on the eve of the 1911 revolution: area, population and density, products, trade of the treaty ports and shipping, with a history of the first year of the Hsuan Tung emperor and an account of the government of China.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Only tables are transcribed; the running text, the maps and the indexes are not. Table pages were found from contact sheets by Claude Sonnet 5.5; each table page was read once by Claude Haiku 5.5 from full-resolution crops, with no second reading and no check by eye. Printed totals are checked automatically and differences noted; figures the model could not read are marked [?]. Chapters follow the printed contents (read by Haiku).",
     "scan": "https://archive.org/details/cu31924023123031/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/cu31924023123031",
     "blank_marking": True},
    {"slug": "china-mission-handbook-1896", "dir": "China_Mission_Handbook_1896", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "The China Mission Hand-book 1896",
     "publisher": "American Presbyterian Mission Press, Shanghai, 1896",
     "blurb": "A reference book on Christian missions in China at the end of the nineteenth century. Part I: essays on Confucianism, Buddhism, Taoism, Islam and the secret sects, the languages and dialects of China, the spread of Christianity and of missions in Asia, and riots. Part II: an account of each Protestant mission society working in China (British, American, Continental and Canadian, the Bible and tract societies, educational associations and mission presses), with its stations and statistics of missionaries, native helpers, communicants, schools and hospitals, and summaries of statistics for all societies.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from the Internet Archive scan of the Princeton Theological Seminary Library copy.",
     "gaps": "Only tables, columnar lists, directory entries and the short chronology are transcribed; prose, maps and the indexes are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (most of the mission statistics; turned upright before reading), very dense tables and tables continued over pages; a table running over several pages was read in one call with all its pages. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. Part II numbers its pages from 1 again; chapters are labelled Part I or Part II.",
     "scan": "https://archive.org/details/chinamissionhand00unse_1/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinamissionhand00unse_1",
     "blank_marking": True},
    {"slug": "china-christian-occupation-1922", "dir": "China_Christian_Occupation_1922", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "The Christian Occupation of China 1922",
     "subtitle": "A general survey of the numerical strength and geographical distribution of the Christian forces in China, made by the Special Committee on Survey and Occupation, China Continuation Committee, 1918-1921",
     "publisher": "China Continuation Committee, Shanghai, 1922",
     "blurb": "The great Protestant missionary survey of China, 1918-1921: the general background (provinces, languages, population, communications, economic change), the Christian occupation of each province (missionaries, Chinese workers, communicants, schools and hospitals by mission society, with density and urgency tables), the unoccupied areas, comparisons of provinces, of the larger missionary societies, of denominations and of the nationality of missionaries, work among special classes, the Chinese church, education, medical work, Christian literature and periodicals, the Roman Catholic and Russian Orthodox churches, and appendices: statistics of Christian occupation by hsien for every province, postal statistics, Catholic residential centres, missionary residential centres arranged chronologically, cities with estimated populations and the statistics of Protestant missions for 1920. Also the list of missionary societies with their initials and Chinese names.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 via the API) from the Internet Archive scan.",
     "gaps": "Tables and columnar lists are transcribed (including the list of missionary societies, the lists of residential centres, institutions and cities, and the corrigenda); the running text, the maps, the graphs and the index are not. Table pages were found from contact sheets by Claude Sonnet 5.5. Pages with dense tables (about ten or more columns or very small type, including the hsien tables of Appendix A) were read once by Claude Sonnet 5.5 from three full-width crops; the others once by Claude Haiku 5.5 from two crops. Tables continued over pages were joined where the column headings match. A few tables were spot-checked against the scan by eye and agreed; the rest were not checked by eye. Printed totals are checked automatically and differences noted; figures the model could not read are marked [?]. The Chinese society names in the list of missionary societies are printed right to left and are given here in reading order.",
     "scan": "https://archive.org/details/christianoccupat00chin/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/christianoccupat00chin",
     "blank_marking": True},
    {"slug": "china-cyb-1937", "dir": "Chinese_Year_Book_1937", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "The Chinese Year Book 1937",
     "subtitle": "1937 Issue (Third Year of Publication)",
     "publisher": "Council of International Affairs, Nanking; printed and distributed by the Commercial Press, Shanghai, 1937",
     "blurb": "The Nationalist government's own English-language yearbook, prepared from official sources by the Council of International Affairs on the eve of the war with Japan, in 53 chapters by officials and scholars: geography, climate, population, languages and religion, the Kuomintang and the five Yuan, home affairs, foreign relations and national defence, public finance and taxation, banking, currency and insurance, domestic and foreign trade, industry, mining, labour, agriculture, co-operatives and fisheries, railways, highways, aviation, shipping, telecommunications and the post, education, the press, public health and opium suppression, the frontier regions and the Chinese overseas, with directories of officials and of the diplomatic and consular services.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from a scan of the printed volume, uploaded to the Internet Archive.",
     "gaps": "Only tables and columnar lists are transcribed; prose, advertisements, maps, graphs and the index are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading), very dense tables and tables continued over pages. A table running over several pages was read in one call with all its pages, up to eight pages (six for dense tables); longer runs were read in parts and joined where the column headings match. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. The contents were read once by Claude Haiku 5.5.",
     "scan": "https://archive.org/details/chinese-year-book-1937/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinese-year-book-1937",
     "blank_marking": True},
    {"slug": "china-cyb-1938-39", "dir": "Chinese_Year_Book_1938", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "The Chinese Year Book 1938-39",
     "subtitle": "1938-39 Issue (Fourth Year of Publication)",
     "publisher": "Council of International Affairs, Chungking; printed and distributed by the Commercial Press, 1939",
     "blurb": "The first wartime issue, compiled after the government's retreat to Chungking: general information (geography, climate, population, languages, religions, history, the frontier regions and the Chinese overseas), the Japanese invasion (the outbreak and course of the war, Japanese war conduct, puppet regimes and economic exploitation, Geneva and Brussels, third-power rights, world sympathy), the wartime government (the Kuomintang and the People's Political Council, war finance, war economy, communications, foreign relations, education, mass mobilization, public health and refugee relief) and the people in the war, with directories of officials and of the diplomatic and consular services.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from a scan of the printed volume, uploaded to the Internet Archive.",
     "gaps": "Only tables and columnar lists are transcribed; prose, advertisements, maps, graphs and the index are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading), very dense tables and tables continued over pages. A table running over several pages was read in one call with all its pages. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. The contents were read once by Claude Haiku 5.5.",
     "scan": "https://archive.org/details/chinese-year-book-1938-39/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinese-year-book-1938-39",
     "blank_marking": True},
    {"slug": "china-cyb-1944-45", "dir": "Chinese_Year_Book_1944", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "The Chinese Year Book 1944-1945",
     "subtitle": "Seventh Issue",
     "publisher": "Council of International Affairs, Chungking; printed and published in Shanghai by the China Daily Tribune Publishing Co., 1946",
     "blurb": "The combined issue for the last two years of the war, compiled from June 1945 and published in Shanghai in January 1946: geography (with Taiwan and the Northeastern provinces), astronomy, climate, population, history, philosophy and literature; the Kuomintang, the People's Political Council and the five Yuan; the Ministry of War, the air force, military campaigns and the Japanese surrender; international conferences (including San Francisco) and foreign relations; public finance, banking and currency, foreign trade, natural resources and industry, agriculture, forestry, water conservancy, land administration, communications, food administration and industrial co-operatives; education, Academia Sinica, the press, public health, social administration, the churches, the Red Cross and war relief and rehabilitation; with a chronology of 1944-45.",
     "source": "LLM-transcribed (Claude Haiku 5.5, and Claude Sonnet 5.5 for very large dense tables, via the API) from a scan of the printed volume, uploaded to the Internet Archive.",
     "gaps": "Only tables, columnar lists, the chronology and the biographical sketches are transcribed; prose, advertisements, maps, graphs and the index are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5, which also flagged pages printed sideways (turned upright before reading), very dense tables and tables continued over pages. A table running over several pages was read in one call with all its pages, up to eight pages (six for dense tables); longer runs were read in parts and joined where the column headings match. Each page was read once and not checked by eye; unreadable figures are marked [?], and printed totals that do not add up are noted and kept as read. The Chronology of Major Events, 1944 and 1945, is on the Chronologies page, each page read once by Claude Haiku 5.5, with dates carried over from date headings written out in full. The biographical sketches of the Chinese delegates to the San Francisco Conference (Appendix I of International Conferences) are on the Who's Who & Directories page. The contents were read once by Claude Haiku 5.5.",
     "scan": "https://archive.org/details/chinese-year-book-1944-45/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinese-year-book-1944-45",
     "blank_marking": True},
    {"slug": "china-farm-economy-1930", "author": "John Lossing Buck", "dir": "Chinese_Farm_Economy_1930", "model": "Gemini 3.8 Flash (agy) and GPT-6.1-Sol (Codex)",
     "title": "Chinese Farm Economy 1930",
     "subtitle": "A Study of 2866 Farms in Seventeen Localities and Seven Provinces in China",
     "publisher": "University of Chicago Press, Chicago, for the University of Nanking and the China Council of the Institute of Pacific Relations, 1930",
     "blurb": "John Lossing Buck's survey of 2,866 farms in seventeen localities of Anhwei, Chihli, Honan, Shansi, Chekiang, Fukien and Kiangsu, 1921–1925, made with his students at the University of Nanking: farm layout and land use, size of farm business, capital, receipts, expenses and profits, ownership and tenancy, crops, livestock, labour, the farm family and population, food consumption and the standard of living, nearly every table set out locality by locality for North and East Central China.",
     "source": "LLM-transcribed (Google Gemini 3.8 Flash via the Antigravity CLI, and OpenAI GPT-6.1-Sol via the Codex CLI) from the Internet Archive scan.",
     "gaps": "Every page was surveyed on contact sheets by Claude Sonnet, and the 295 pages with tables were read once: by GPT-6.1-Sol (low reasoning effort) where the table is printed sideways, by Gemini 3.8 Flash otherwise (two early sideways jobs by Gemini 4 Argon). The 77 sideways pages were turned upright before reading. All 252 tables are transcribed; table numbers restart in each chapter, and Chapter IV has no Table 11 (deleted in the book itself). The blank schedule forms of Appendix IV, the charts, photographs and prose are not transcribed. Unreadable figures are marked [?]; printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/chinesefarmecono0000john_x5u5/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinesefarmecono0000john_x5u5", "blank_marking": True},
    {"slug": "china-tongji-1935", "dir": "China_Tongji_Tiyao_1935", "model": "Sonnet 5.5, Haiku 5.5 and Opus 5.5",
     "title": "中華民國統計提要 1935",
     "subtitle": "Statistical Abstract of the Republic of China, 民國二十四年輯 (1935 compilation)",
     "publisher": "國民政府主計處統計局 (Directorate of Statistics, National Government), Nanking, 1935",
     "blurb": "The National Government's first statistical abstract, compiled from the national statistical report for 1933 (民國二十二年): 330 numbered tables in 36 classes, mostly for 1932–1934 and often by province or county. It covers boundaries, geology and climate; government organisation, laws, courts and crime; officials and examinations; foreign relations and overseas Chinese; population by province and county, with age, marriage, occupation and density; labour, co-operatives and education from universities to primary schools; suicides, homicides and police offences; public health, relief and social organisations; land, agriculture (farm households and holdings, crops, wages, prices, credit), forestry, fisheries, livestock, mining, industry, commerce and trade; prices, money, banking and markets; national and provincial finance, including the monthly receipts and payments of nineteen provinces and municipalities; and posts, telegraphs, telephones, highways, railways, shipping, water conservancy and electric utilities.",
     "source": "Transcribed by Claude sub-agents from the National Library of China scan on Wikimedia Commons.",
     "gaps": "All 330 tables are transcribed except 表16 政權機關, which is an essay rather than a table; the class introductions and reference lists, the organisation charts and the indexes are not transcribed. Every page was surveyed on contact sheets by Claude Sonnet; each table was then read once — by Claude Haiku for plain one-page tables and the monthly provincial accounts, Claude Sonnet for most tables, and Claude Opus for the densest county tables. Wide tables printed across two pages were read as one table, and long tables that run over many pages were read in sections and joined. 表230, the monthly receipts and payments of nineteen provinces and municipalities, is given as one table per province with each month as a part. Printed totals were re-added and a total that does not reconcile is kept as printed with a note. An Opus spot check of three tables (1,649 figures) agreed on all but one figure, a broken digit now marked [?]. In all, 279 of about 388,000 figure cells are marked [?].",
     "scan": "https://commons.wikimedia.org/w/index.php?title=File:NLC511-027032013016022-15763_%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E7%B5%B1%E8%A8%88%E6%8F%90%E8%A6%81.pdf&page={leaf}",
     "item": "https://commons.wikimedia.org/wiki/File:NLC511-027032013016022-15763_%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E7%B5%B1%E8%A8%88%E6%8F%90%E8%A6%81.pdf", "blank_marking": True},
    {"slug": "china-tongji-1947", "dir": "China_Tongji_Tiyao_1947", "model": "Haiku 5.5 and Sonnet 5.5 (Opus 5.5 for doubtful cells)",
     "title": "中華民國統計提要 1947",
     "subtitle": "Statistical Abstract of the Republic of China, 1947 (民國三十六年)",
     "publisher": "國民政府主計處統計局 (Directorate of Statistics, National Government), Nanking, 1947",
     "blurb": "The National Government's bilingual statistical abstract of 1947, in eight sections with 80 numbered tables, most giving series for 1937 to 1946 or early 1947: area and population by province, with the 1942–43 census of nine hsien in Szechwan; agriculture (cultivated land and farmers, crops, livestock, tenancy, farm prices and credit, forests); mining, industry and trade (mineral deposits and output, factories, imports and exports by commodity, wholesale and retail price indices for some twenty-five cities, electricity); public finance and banking (national budgets and accounts, taxes, the grain levy, loans, provincial budgets, banks, deposits and loans, interest and exchange rates); railways, highways, motor vehicles, river shipping, aviation, telegraphs, telephones and the post; education from the universities to adult schools; social organisations, cost-of-living and wage indices, co-operatives, civil and criminal cases, prisons, hospitals and epidemics; and administrative divisions, the pao-chia, representative bodies, civil servants, consulates abroad, courts, civil examinations and the police.",
     "source": "Transcribed by Claude sub-agents from the scan on Wikimedia Commons (SSID 11330959).",
     "gaps": "All 80 tables are transcribed, with their Chinese and English titles, headings and row labels as printed. Every page was surveyed on contact sheets by Claude Sonnet; the 98 pages printed sideways were turned upright before reading. Each table was read once, by Claude Haiku (simple one-page tables) or Claude Sonnet (multi-page tables and tables printed across two facing pages, which were read as one). The scan is a rough 300 dpi black-and-white image with broken and doubled type in places: the 266 cells the first readers could not read were re-read blind (without seeing the rest of the table) by Claude Opus, which settled 122 of them; the remaining 144 (0.8% of 18,319 figure cells) are marked [?]. Printed totals were re-added and a total that does not reconcile is kept as printed with a note. A few figures are printed half a line below their row labels; these were matched to their rows by order, as noted in the tables.",
     "scan": "https://commons.wikimedia.org/w/index.php?title=File:SSID-11330959_%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E7%B5%B1%E8%A8%88%E6%8F%90%E8%A6%81.pdf&page={leaf}",
     "item": "https://commons.wikimedia.org/wiki/File:SSID-11330959_%E4%B8%AD%E8%8F%AF%E6%B0%91%E5%9C%8B%E7%B5%B1%E8%A8%88%E6%8F%90%E8%A6%81.pdf", "blank_marking": True},
    {"slug": "china-education-1934", "dir": "China_Education_Yearbook_1934", "model": "Opus 5.5 and Sonnet 5.5",
     "title": "第一次中國教育年鑑 1934", "note": "(partial extraction)",
     "subtitle": "The First China Education Yearbook (Diyici Zhongguo jiaoyu nianjian), 1934 — reprint volume 2: 丙編 (part), 丁編, 戊編",
     "publisher": "教育部 (Ministry of Education) 編; 開明書店 (Kaiming Bookstore), Shanghai, May 1934; 民國叢書 photo-reprint",
     "blurb": "The Ministry of Education's first yearbook, a survey of Chinese education from the late Qing to 1933. This scan holds the second half of the book: social (popular) education by province — literacy campaigns, people's schools, supplementary and vocational night schools, schools for the blind and deaf, people's education centres, lecture halls, libraries, museums and public sports; study abroad and learned societies; the statistical part (丁編 教育統計) on higher, secondary and primary schools (numbers of schools, classes, pupils, graduates, teachers and staff, revenue and expenditure, by province and since 1912) and on social education; and the miscellany (戊編): a chronology of education from 1862 to 1932, the Boxer-indemnity funds, textbooks, education conferences and research, lists of education officials, donors to schools, the Siku quanshu reprint, commemorative days, biographies of educational pioneers, and surveys of education in Europe, America and Japan.",
     "source": "Transcribed by Claude sub-agents from the CADAL (Fudan University Library) scan of the 民國叢書 reprint on Wikimedia Commons (DjVu, 1,301 pages, 300 dpi black-and-white).",
     "gaps": "PARTIAL EXTRACTION, because of the quality of the scan. Transcribed: all the statistical tables of 丁編 教育統計 (the statistical part, printed horizontally with Arabic figures), the tables and lists of the first part of 丙編 第二 社會教育概況 that had been read before the work was narrowed, the whole chronology 興學以來教育大事記 (1,567 entries, 1862–1932) with its list of sources, and the biographies 教育先進傳略 (102 entries). NOT transcribed: the rest of 丙編 (most of the tables and lists of libraries, museums, sports, study abroad and learned societies, printed vertically with compressed Chinese numerals), and the tables and lists of 戊編 (officials, donors, the surveys of foreign education); 丙編 第一 學校教育概況 is in the other reprint volume, so its contents entries have no scan link. The type of the scan is badly broken in places: in the Arabic tables a 4 often prints like a 1, and 3/5/8 and 0/6/9 lose strokes; in the Chinese tables the digits are compressed two to a character space. Every page was surveyed on contact sheets by Claude Sonnet; tables with Chinese numerals and most statistical tables were read by Claude Opus from enlarged crops, re-adding every printed total to catch misreads; some earlier tables (丁編 pp. 30–47, 54–74 and 94–101, and most 丙編 lists) were read by Claude Sonnet, which an independent check found less reliable (about 94–99% of figures right). A printed total never settled a digit except the 一/二/三 and 3-vs-8 rules; 55 cells that a reader had settled from totals in other ways were turned back into [?]. Totals that do not reconcile are kept as printed with a note. In all 1,440 of about 33,000 figure cells (4.4%) are marked [?].",
     "scan": "https://commons.wikimedia.org/w/index.php?title=File:CADAL07006947_%E4%B8%AD%E5%9C%8B%E6%95%99%E8%82%B2%E5%B9%B4%E9%91%92_1934%E5%B9%B4.djvu&page={leaf}",
     "item": "https://commons.wikimedia.org/wiki/File:CADAL07006947_%E4%B8%AD%E5%9C%8B%E6%95%99%E8%82%B2%E5%B9%B4%E9%91%92_1934%E5%B9%B4.djvu", "blank_marking": True},
    {"slug": "china-smc-1880", "dir": "SMC_Report_1880", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1880",
     "subtitle": "Report for the Year ending 31st December 1880 and Budget for the Year 1881",
     "publisher": "Shanghai Municipal Council, Shanghai, 1881",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1880, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with three returns of arms, accoutrements and ammunition); Finance Matters (appropriations, houses and land assessed, the quarterly General Municipal Rate summaries, the Local Post Office, accounts); the Census of 1880 (foreign and native population, foreign residents by nationality and district, native population 1870–1880); the Police with its returns (foreigners arrested, monthly prisoners, condition and punishments of Chinese prisoners), the Nuisance Branch, the Markets and the Health Officer's report (ages at death, death-rates, deaths and death returns); Works Matters, the Public Garden, the Surveyor's report (cemeteries, drains schedule, roads and road widening); the proposed franchise for the Land Regulations, and the Fire Commission with its Fire Record; then the financial statement for 1880 (revenue and expenditure on facing pages, in taels), deposit accounts and the Sinking Fund, land, buildings and property, the general statement and balance sheet, the comparison of actual and estimated receipts and expenditure, and the budget for 1881 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (4 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1880-and-Budget-for-the-Year-1881/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1880-and-Budget-for-the-Year-1881",
     "blank_marking": True},
    {"slug": "china-smc-1881", "dir": "SMC_Report_1881", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1881",
     "subtitle": "Report for the Year ending 31st December 1881 and Budget for the Year 1882",
     "publisher": "Shanghai Municipal Council, Shanghai, 1882",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1881, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with the return of arms, accoutrements and ammunition); Finance Matters (accounts, appropriations, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Watch Matters (lighting) and the Police with its returns (foreigners arrested, monthly prisoners, condition and punishments of Chinese prisoners), the Nuisance Branch, the Markets and the Health Officer's report (ages at death, death-rates, cholera, phthisis, deaths and death returns); Works Matters, the Public Garden, the Surveyor's report (cemeteries, drains schedule, lamps, roads and road extensions); the Public Band, the Police Gratuity Fund and the Fire Commission with its Fire Record; then the financial statement for 1881 (revenue and expenditure on facing pages, in taels), trust and deposit funds, land, buildings and property, the general statement and balance sheet, the comparison of actual and estimated receipts and expenditure, and the budget for 1882 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (2 cells). The budget has its own page numbers, as printed. The scan lacks budget pages 13–14 and 19–20, so the Public Works estimate, part of the income and expenditure and the first part of the Summary of Expenditure are incomplete; those tables say so.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1881-and-Budget-for-the-Year-1882/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1881-and-Budget-for-the-Year-1882",
     "blank_marking": True},
    {"slug": "china-smc-1882", "dir": "SMC_Report_1882", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1882",
     "subtitle": "Report for the Year ending 31st December 1882 and Budget for the Year 1883",
     "publisher": "Shanghai Municipal Council, Shanghai, 1883",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1882, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with appointments, strength and the return of arms, accoutrements and ammunition); Finance Matters (debentures, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Watch Matters and the Police with its returns (foreigners arrested, monthly prisoners, condition and punishments of Chinese prisoners), the Nuisance Branch, the Markets and the Health Officer's report (ages at death, death-rates, cholera, deaths and death returns); Works Matters, the Recreation Ground, the Surveyor's report (cemeteries, drains schedule, lamps, roads and road extensions); the Public Band, slaughter-house charges and the Fire Commission with its Fire Record; then the financial statement for 1882 (revenue and expenditure on facing pages, in taels), trust and deposit funds, land, buildings and property, the general statement and balance sheet, the comparison of actual and estimated receipts and expenditure, and the budget for 1883 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (8 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1882-and-Budget-for-the-Year-1883/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1882-and-Budget-for-the-Year-1883",
     "blank_marking": True},
    {"slug": "china-smc-1883", "dir": "SMC_Report_1883", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1883",
     "subtitle": "Report for the Year ending 31st December 1883 and Budget for the Year 1884",
     "publisher": "Shanghai Municipal Council, Shanghai, 1884",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1883, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with the return of arms, accoutrements and ammunition); Finance Matters (debentures, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Watch Matters (lighting) and the Police with its returns (foreigners arrested, monthly prisoners, condition and punishments of Chinese prisoners); the Nuisance and Market Branches and the Health Officer's report (ages at death, death-rates, cholera, deaths and death returns); Works Matters, the Recreation Ground, the Surveyor's report (cemeteries, drains schedule, road extensions); the Eurasian School, small-pox at the General Hospital, gas and electric lighting, the Public Band and the Fire Commission with its Fire Record; then the financial statement for 1883 (revenue and expenditure on facing pages, in taels), trust and deposit funds, land, buildings and property, the general statement and balance sheet, outstanding accounts, the comparison of actual and estimated receipts and expenditure, and the budget for 1884 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (2 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1883-and-Budget-for-the-Year-1884/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1883-and-Budget-for-the-Year-1884",
     "blank_marking": True},
    {"slug": "china-smc-1885", "dir": "SMC_Report_1885", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1885",
     "subtitle": "Report for the Year ending 31st December 1885 and Budget for the Year 1886",
     "publisher": "Shanghai Municipal Council, Shanghai, 1886",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1885, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with the field state, strength and the return of arms, accoutrements and ammunition); the Census of 1885 (foreign and native population, foreigners by nationality and occupation, native houses and occupants by road); Watch Matters (lighting, licences) and the Police with returns I–IX (strength, weekly and monthly prisoners, condition and punishments of Chinese prisoners, foreigners charged, arrests, warrants), the Nuisance Branch and the Health Officer's report (cholera, deaths and death returns), the Market Branch; Finance Matters (the loan of 1885, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Works Matters (buildings, roads), the Recreation Ground, the Surveyor's report (cemeteries, drains schedule, roads), the electric-light estimate, the Eurasian School, the Public Band and the Fire Commission with its Fire Record; then the financial statement for 1885 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1886 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (6 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1885-and-Budget-for-the-Year-1886/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1885-and-Budget-for-the-Year-1886",
     "blank_marking": True},
    {"slug": "china-smc-1886", "dir": "SMC_Report_1886", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1886",
     "subtitle": "Report for the Year ending 31st December 1886 and Budget for the Year 1887",
     "publisher": "Shanghai Municipal Council, Shanghai, 1887",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1886, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with strength at inspection, commissions, the Challenge Cup and the return of arms, accoutrements and ammunition); Watch Matters (lighting, licences) and the Police with returns I–IX (strength, weekly and monthly prisoners, condition and punishments of Chinese prisoners, foreigners charged, arrests, warrants), the Nuisance Branch and the Health Officer's report (cholera, deaths and death returns, native death returns); Finance Matters (loans, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Works Matters (new roads in Hongkew, creek dredging), the Recreation Ground, the Surveyor's report (cemeteries, drains schedule, roads), water supply, the Eurasian School, the Public Band and the Fire Commission with its Fire Record; then the financial statement for 1886 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1887 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (3 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1886-and-Budget-for-the-Year-1887/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1886-and-Budget-for-the-Year-1887",
     "blank_marking": True},
    {"slug": "china-smc-1887", "dir": "SMC_Report_1887", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1887",
     "subtitle": "Report for the Year ending 31st December 1887 and Budget for the Year 1888",
     "publisher": "Shanghai Municipal Council, Shanghai, 1888",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1887, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with resignations and commissions, strength, the return of arms, accoutrements and ammunition); Watch Matters (lighting, licences) and the Police with returns I–IX (strength, prisoners, punishments, gaol returns, arrests, foreigners charged, warrants), the Nuisance Branch, the Market Branch and the Health Officer's report (deaths and death-rates, cholera, native death returns); Finance Matters (the year's accounts, the quarterly General Municipal Rate summaries, houses assessed, the Local Post Office); Works Matters (road and bridge works, dredging, the proposed Hongkew road), the Recreation Ground, the Surveyor's report (cemeteries, drains schedule, roads), water supply, the Eurasian School, the Town Band and the Fire Commission with its Fire Record; then the financial statement for 1887 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1888 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (5 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1887-and-Budget-for-the-Year-1888/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1887-and-Budget-for-the-Year-1888",
     "blank_marking": True},
    {"slug": "china-smc-1888", "dir": "SMC_Report_1888", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1888",
     "subtitle": "Report for the Year ending 31st December 1888 and Budget for the Year 1889",
     "publisher": "Shanghai Municipal Council, Shanghai, 1889",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1888, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with new commissions, strength, returns of equipment and ammunition); Watch Matters (lighting, licences) and the Police with returns I–IX (strength, weekly and monthly prisoners, punishments, arrests, foreigners charged, warrants); the Nuisance and Market Branches and the Health Officer's report (deaths and death returns, native death returns); Finance Matters (loan, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Works Matters and the Surveyor's report (roads, road extension, drains schedule, cemeteries), water supply, the Recreation Ground, the Eurasian School, the Town Band and the Fire Commission with its Fire Record; then the financial statement for 1888 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1889 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. No figures were marked unreadable. The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1888-and-Budget-for-the-Year-1889/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1888-and-Budget-for-the-Year-1889",
     "blank_marking": True},
    {"slug": "china-smc-1889", "dir": "SMC_Report_1889", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1889",
     "subtitle": "Report for the Year ending 31st December 1889 and Budget for the Year 1890",
     "publisher": "Shanghai Municipal Council, Shanghai, 1890",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1889, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with strength, returns of arms and equipment and ammunition); Watch Matters (lighting, licences) and the Police with returns I–XI (strength, prisoners, punishments, gaol returns, arrests, foreigners charged, warrants, length of service, larceny); the Nuisance Branch, markets and slaughter-house, and the Health Officer's report (deaths and death-rates, cholera, native death returns); Finance Matters (loan, accounts, the quarterly General Municipal Rate summaries, houses and lots of land assessed, the Local Post Office); Works Matters and the Surveyor's report (roads, pavements, road extension, drains schedule, cemeteries), water supply, the Eurasian School, the Recreation Ground, the Town Band and the Fire Commission with its Fire Record; then the financial statement for 1889 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1890 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (2 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1889-and-Budget-for-the-Year-1890/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1889-and-Budget-for-the-Year-1890",
     "blank_marking": True},
    {"slug": "china-smc-1890", "dir": "SMC_Report_1890", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1890",
     "subtitle": "Report for the Year ending 31st December 1890 and Budget for the Year 1891",
     "publisher": "Shanghai Municipal Council, Shanghai, 1891",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1890, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with strength, returns of arms and equipment and ammunition); Watch Matters with the Census of 1890 (foreign population by nationality, rank and occupation; native population by province of birth, houses and occupants), lighting and licences, and the Police with returns I–XI (prisoners, punishments, arrests, foreigners charged, gaols, strength and length of service); the Nuisance Branch and the Health Officer's report (markets, deaths and death-rates, cholera, native death returns); Finance Matters (accounts, land assessment, the quarterly General Municipal Rate summaries, houses whose assessments were changed, the Local Post Office); Works Matters (roads, pavements, drains schedule, cemeteries, building operations, labour), the Recreation Ground and New Garden, water supply, the Eurasian School, the Public Band and the Fire Commission with its Fire Record; then the financial statement for 1890 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, outstanding contracts and dues, the comparison of actual and estimated receipts and expenditure, and the budget for 1891 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes, and it lacks eight printed pages of the financial statement (pp. 258–259, 262–263, 266–267 and 270–271): the item lines that run on from those pages are given as separate tables noting the gap, and the running totals across them cannot be checked. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (12 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1890-and-Budget-for-the-Year-1891/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1890-and-Budget-for-the-Year-1891",
     "blank_marking": True},
    {"slug": "china-smc-1891", "dir": "SMC_Report_1891", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1891",
     "subtitle": "Report for the Year ending 31st December 1891 and Budget for the Year 1892",
     "publisher": "Shanghai Municipal Council, Shanghai, 1892",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1891, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with strength, parades and the return of arms and ammunition); the Police with returns of prisoners, arrests, punishments, foreigners charged, larceny and strength; the Health Officer's report (deaths and death-rates, native death returns); Finance Matters (the quarterly General Municipal Rate summaries, houses assessed, the Local Post Office); Works Matters (roads and road improvements, sewers and drains schedule, cemeteries, building operations, labour), the markets, the water supply, the Recreation Ground, the Eurasian School, the Public Band and the Fire Commission with its Fire Record; then the financial statement for 1891 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, the outstanding contracts and accounts, the comparison of actual and estimated receipts and expenditure, and the budget for 1892 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The Fire Record (a dated list of fires) is given as a chronology. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes, and the statement comparing actual with estimated expenditure is cut off at the foot of its page in the scan (its last lines and total are missing). Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (36 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1891-and-Budget-for-the-Year-1892/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1891-and-Budget-for-the-Year-1892",
     "blank_marking": True},
    {"slug": "china-smc-1893", "dir": "SMC_Report_1893", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1893",
     "subtitle": "Report for the Year ending 31st December 1893 and Budget for the Year 1894",
     "publisher": "Shanghai Municipal Council, Shanghai, 1894",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1893, the Settlement's Jubilee year, in its older form (sections of correspondence and committee reports rather than numbered departments): Defence Matters (the Shanghai Volunteer Corps with strength, ammunition and the return of arms, accoutrements and ammunition); Watch Matters and licences (lamps, pawn-shops, carriage fees) and the Police with returns I–X (prisoners, arrests, punishments, foreigners, stations, larceny, strength); the Sanitary Board and Health Officer's report (deaths and death-rates, small-pox, cholera and fevers, native death returns, slaughter-house and markets, vaccine station); Finance Matters (résumé of accounts, dues on merchandise, the Local Post Office rates, the quarterly General Municipal Rate summaries and foreign house assessments); Works Matters (roads, footways, bricked and chipped roads, drains and sewers schedule, burials, building operations, labour), the Electric Department's accounts, the Recreation Ground, water supply, the Public School, the Band and the Fire Commission; then the financial statement for 1893 (revenue and expenditure on facing pages, in taels), trust and bank funds, land, buildings and property, the general statement and balance sheet, the comparison of actual and estimated receipts and expenditure, and the budget for 1894 with its summary and comparative statement.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the accounts and the budget (each sub-head of the financial statement and budget is a separate table); the prose and letters are not. The volume prints no table of contents (only an alphabetical index), so the book's contents list here is made of bracketed section headings in the order of the volume. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (48 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1893-and-Budget-for-the-Year-1894/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1893-and-Budget-for-the-Year-1894",
     "blank_marking": True},
    {"slug": "china-smc-1904", "dir": "SMC_Report_1904", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1904",
     "subtitle": "Report for the Year 1904 and Budget for the Year 1905",
     "publisher": "Shanghai Municipal Council, Shanghai, 1905",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1904, arranged by the Council's committees: Watch Matters (the Volunteer Corps with officers, strength, arms and equipment; the Police Force with the nine appendix tables of strength, prisoners, arrests, punishments, foreigners and arms; the Gaol); the Health Officer's report (meteorology, foreign and Chinese deaths and death-rates, hospital cases, infectious disease, milk and dairies, butchers, prosecutions, port health, the Victoria Nursing Home); the Fire Commission's equipment, fires and accounts; Finance Matters (the Overseer of Taxes' report with rate summaries, foreign house assessments amended and new, licence fees, loans and land assessment); Works Matters (bridges, drainage, roads and pavements, scavenging and water, the schedule of municipal properties, amounts receivable and payable, road costs, Land Commission awards, conservancy); the Electricity Department's statistics, accounts and estimate; General matters (water and semaphore, the full Municipal Foreign Staff list); then the financial statement and balance sheet for 1904 (in taels), working accounts of the quarry, convict labour and concreteware, the comparative statement, and the budget for 1905 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the house-assessment lists, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs and the electricity charts are not. Printed pages 321–336 (part of the Works report) are missing from the scan. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (15 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1904-and-Budget-for-the-Year-1905/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1904-and-Budget-for-the-Year-1905",
     "blank_marking": True},
    {"slug": "china-smc-1905", "dir": "SMC_Report_1905", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1905",
     "subtitle": "Report for the Year 1905 and Budget for the Year 1906",
     "publisher": "Shanghai Municipal Council, Shanghai, 1906",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1905, the year of the Settlement census, arranged by the Council's committees: Watch Matters (the Volunteer Corps with officers, strength and arms; the Police Force with the nine appendix tables of strength, apprehensions, arrests, punishments, prisoners and arms, and the Gaol); the Health Officer's report (meteorology, foreign and Chinese deaths and death-rates, hospital cases, infectious disease, mortuary, laundries, sanitary work, water and milk analyses, dairies, butchers, slaughter-house, prosecutions, the Victoria Nursing Home); the Fire Commission's equipment, fires and accounts; Finance Matters (the Overseer of Taxes' report with rate, assessment and licence returns and loans); Works Matters (roads, drainage, new buildings, the schedule of municipal properties, road costs and Land Commission awards); the Electricity Department's statistics, accounts and estimate; General matters (the Semaphore account, the Census of 1905 with foreign population by nationality, district and occupation and native population by district and province of birth, police pay and the full Municipal Foreign Staff list); then the financial statement and balance sheet for 1905 (in taels), working accounts of the quarry, convict labour and concreteware, the comparative statement, and the budget for 1906 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the census tables, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs and the electricity charts are not. The scan is of lower resolution than later volumes. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages (police returns, census) by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (31 cells). The budget has its own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1905-and-Budget-for-the-Year-1906/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1905-and-Budget-for-the-Year-1906",
     "blank_marking": True},
    {"slug": "china-smc-1908", "dir": "SMC_Report_1908", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1908",
     "subtitle": "Report for the Year 1908 and Budget for the Year 1909",
     "publisher": "Shanghai Municipal Council, Shanghai, 1909",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1908, arranged by the Council's committees: Watch Matters (the Volunteer Corps with strength, commissions and arms; the Police Force with branches, traffic, opium, fires, criminal investigation and gaol, and the eight appendix tables of apprehensions, arrests, punishments, prisoners and arms; the Mixed Court); the Health Officer's report (meteorology, foreign and Chinese deaths, infectious disease, vaccination, laboratory analyses, hospitals, refuse, laundries, dairies, butchers, slaughter-house, markets, prices, prosecutions, cemeteries), the Band and the Fire Brigade; Finance Matters (the Overseer of Taxes' report with rate, assessment and licence returns and loans); Works Matters (carriages and carts, roads, water and gas, new buildings, the schedule of municipal properties, road extensions with land and compensation, easements and leases); the Electricity Department's comparative table, accounts and estimate; General matters (opium houses, telephone charges, the Semaphore account, school attendance, police pay scales and the full Municipal Foreign Staff list); then the financial statement and balance sheet for 1908 (in taels), working accounts of the quarry, convict labour and concreteware, the schedules of land, buildings and stores, and the budget for 1909 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague-rat map, the office organisation chart and the electricity charts are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (55 cells). The financial statement and budget have their own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1908-and-Budget-for-the-Year-1909/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1908-and-Budget-for-the-Year-1909",
     "blank_marking": True},
    {"slug": "china-smc-1909", "dir": "SMC_Report_1909", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1909",
     "subtitle": "Report for the Year 1909 and Budget for the Year 1910",
     "publisher": "Shanghai Municipal Council, Shanghai, 1910",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1909, arranged by the Council's committees: Watch Matters (the Volunteer Corps with parades, camps, strength by unit and arms; the Fire Brigade; the Police Force with branches, gaol, traffic and accidents, fires, and the eight appendix tables of apprehensions, arrests, Mixed Court cases, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths, infectious disease and plague rats, vaccination, hospitals, refuse, mosquito work, licensed laundries and dairies, slaughter-house, markets, prices, prosecutions, cemeteries); Works Matters (roads, survey, water and gas, new buildings, the schedule of municipal properties, road extensions with land and compensation by district, easements and leases, parks, public lighting); the Electricity Department's comparative table, accounts and estimate; General matters (school attendance, the Semaphore account and the full Municipal Foreign Staff list); the Overseer of Taxes' report with rate, assessment, licence and loan returns; then the financial statement and balance sheet for 1909 (in taels), the comparative statement, working accounts of the quarry, convict labour and concreteware, the schedules of land, buildings and stores, and the budget for 1910 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague and extension maps, the revenue diagram and the electricity charts are not, nor a few one-line cost calculations inside letters. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (39 cells). The financial statement and budget have their own page numbers, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1909-and-Budget-for-the-Year-1910/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1909-and-Budget-for-the-Year-1910",
     "blank_marking": True},
    {"slug": "china-smc-1911", "dir": "SMC_Report_1911", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1911",
     "subtitle": "Report for the Year 1911 and Budget for the Year 1912",
     "publisher": "Shanghai Municipal Council, Shanghai, 1912",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1911, the year of the Revolution, arranged by the Council's committees: Watch Matters (the Volunteer Corps with monthly strength, unit strengths, inspection and arms; the Fire Brigade's equipment and record of calls; the Police Force with staff, criminal investigation, gaol, traffic and accidents, and the eight appendix tables of apprehensions, arrests, Mixed Court cases, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths and death-rates, infectious disease, plague and rats, vaccination, laboratory, hospitals, refuse, mosquito work, licensed laundries, dairies, bakeries and food shops, slaughter-house, markets, prices, prosecutions, cemeteries); Works Matters (road experiments, bridges, survey, permits and new buildings, materials and concreteware, the schedule of municipal properties, road extensions with land and compensation, easements and leases, parks); the Electricity Department's comparative table, accounts and estimate; General matters (the Public Band, the Council and grant-aided schools, the Semaphore account and the full Municipal Staff list); the Treasurer's and the Overseer of Taxes' reports with rate, assessment, wharfage and licence returns; then the financial statement and balance sheet for 1911 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1912 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the list of calls, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague and road maps, the weather diagram and the electricity charts are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (74 cells, including a percentage column cut off at the binding). Pages are numbered 1–254 and 1A–91A, as printed.",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1911-and-Budget-for-the-Year-1912/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1911-and-Budget-for-the-Year-1912",
     "blank_marking": True},
    {"slug": "china-smc-1912", "dir": "SMC_Report_1912", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1912",
     "subtitle": "Report for the Year 1912 and Budget for the Year 1913",
     "publisher": "Shanghai Municipal Council, Shanghai, 1913",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1912, the first year of the Republic, arranged by the Council's committees: Watch Matters (the Volunteer Corps with monthly strength, unit strengths, the retired list, the efficiency shield and arms; the Fire Brigade's equipment and record of calls; the Police Force with branch strengths, offences, the gaol, traffic and vehicles, finger prints and the eight appendix tables of apprehensions, arrests, Mixed Court cases, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths, infectious disease, plague and rats, vaccination, laboratory, hospitals, refuse, sanitary work, licensed laundries, dairies, bakeries and food shops, slaughter-house, markets, prices, cemeteries); Works Matters (bridges, survey, road experiments and works, permits and drainage, materials and concreteware, the schedule of municipal properties, road extensions with land and compensation, parks); the Electricity Department's comparative table, accounts and estimate; General matters (Tramways, the Public Band, the Council and grant-aided schools with attendance and examinations, the Public Library and Semaphore accounts, and the full Municipal Staff list); the Treasurer's and the Overseer of Taxes' reports with rate, assessment and licence returns; then the financial statement and balance sheet for 1912 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1913 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the list of calls, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague map, the weather diagram and the electricity charts are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (45 cells). Chapters follow the printed contents (three page series, 1A–111A, 1B–172B and 1C–95C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1912-and-Budget-for-the-Year-1913/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1912-and-Budget-for-the-Year-1913",
     "blank_marking": True},
    {"slug": "china-smc-1913", "dir": "SMC_Report_1913", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1913",
     "subtitle": "Report for the Year 1913 and Budget for the Year 1914",
     "publisher": "Shanghai Municipal Council, Shanghai, 1914",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1913, the year of the 'Second Revolution' fighting around Shanghai, arranged by the Council's committees: Watch Matters (the Volunteer Corps with monthly strength, inspection, parade state and nationalities; the Fire Brigade's equipment, additions and record of calls; the Police Force with branch strengths, offences, the gaol, traffic, foreign civil cases and the eight appendix tables of apprehensions, arrests, Mixed Court cases, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths, infectious disease, plague and rats, vaccination, laboratory, hospitals, sanitary work, refuse, slaughter-house, markets, prices, cemeteries; the Paulun Hospital accounts); Works Matters (bridges, survey, roads, traffic census, permits and new buildings, materials and concreteware, the register of municipal properties, road extensions with land and compensation, parks); the Electricity Department's comparative and load-factor tables, accounts and estimate; General matters (Tramways, the Public Band, the Council and grant-aided schools, the Semaphore account and the full Municipal Staff list); the Treasurer's and the Overseer of Taxes' reports with rate, assessment, wharfage and licence returns; then the financial statement and balance sheet for 1913 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1914 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the list of calls, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague and fire-district maps, the weather diagram and the electricity graphs are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (58 cells). Chapters follow the printed contents (three page series, 1A–116A, 1B–144B and 1C–96C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1913-and-Budget-for-the-Year-1914/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1913-and-Budget-for-the-Year-1914",
     "blank_marking": True},
    {"slug": "china-smc-1914", "dir": "SMC_Report_1914", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1914",
     "subtitle": "Report for the Year 1914 and Budget for the Year 1915",
     "publisher": "Shanghai Municipal Council, Shanghai, 1915",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1914, the first year of the war, arranged by the Council's committees: Watch Matters (the Volunteer Corps with monthly strength, nationalities, the annual inspection and arms; the Fire Brigade's officers, equipment, additions and record of calls; the Police Force with branch strengths, offences, the gaol, traffic and accidents, foreign civil cases and the eight appendix tables of apprehensions, arrests, Mixed Court cases, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths and death-rates, infectious disease, plague and rats, vaccination, laboratory, hospitals, sanitary work, refuse, slaughter-house, markets, prices, cemeteries; the Paulun Hospital accounts); Works Matters (bridges, survey, roads, labour, permits and new buildings, materials and concreteware, the schedule of municipal properties, road extensions with land and compensation by district, parks); the Electricity Department's comparative table, accounts, estimate and capital expenditure; General matters (Yangkingpang and Defence Creek, Tramways, the Public Band, the Council and grant-aided schools, the Semaphore account and the full Municipal Staff list); the Treasurer's and the Overseer of Taxes' reports with rate, assessment and licence returns; then the financial statement and balance sheet for 1914 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1915 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the list of calls, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague map, the weather diagram and the graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and wide pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (32 cells). Chapters follow the printed contents (three page series, 1A–111A, 1B–167B and 1C–91C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1914-and-Budget-for-the-Year-1915/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1914-and-Budget-for-the-Year-1915",
     "blank_marking": True},
    {"slug": "china-smc-1915", "dir": "SMC_Report_1915", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1915",
     "subtitle": "Report for the Year 1915 and Budget for the Year 1916",
     "publisher": "Shanghai Municipal Council, Shanghai, 1916",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1915, arranged by the Council's committees: Watch Matters (the Volunteer Corps with strength, changes and arms; the Fire Brigade's motorisation, appliances, calls and monthly return of fires; the Police Force with branch strengths, offences, the gaol, traffic, the Mixed Court and the eight appendix tables of apprehensions, arrests, punishments, prisoners and arms); the Health Officer's report (meteorology, foreign and Chinese deaths, infectious disease, plague and rats, vaccination, laboratory, hospitals, sanitary work, slaughter-house, markets, prices, cemeteries and the mortuary; the General Hospital's indigent patients and the Paulun Hospital accounts); Works Matters (bridges, survey, roads, new building permits, materials, the schedule of municipal properties, road extensions with land and compensation by district, the Land Commission, parks); the Electricity Department's comparative table, tenders, estimate, capital expenditure and accounts; General matters (Tramways, Standing Contracts, the Public Band, the Council and grant-aided schools with rolls, examinations and fees, the Polytechnic, the Semaphore account, the 1915 census of the foreign and Chinese population by nationality, district, occupation and province, and the full Municipal Staff list); the Treasurer's and the Overseer of Taxes' reports with population, rate, assessment, wharfage and licence returns; then the financial statement and balance sheet for 1915 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1916 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan of the University of Illinois copy.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the census, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague map, the weather diagram and the graphs without printed figures are not. Nine sideways tables were turned upright before reading. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and sideways pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (46 cells). Chapters follow the printed contents (three page series, 1A–116A, 1B–179B and 1C–90C, as printed).",
     "scan": "https://archive.org/details/reportshanghaimu1915shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/reportshanghaimu1915shan",
     "blank_marking": True},
    {"slug": "china-smc-1916", "dir": "SMC_Report_1916", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1916",
     "subtitle": "Report for the Year 1916 and Budget for the Year 1917",
     "publisher": "Shanghai Municipal Council, Shanghai, 1917",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1916, arranged by the Council's committees: Watch Matters (the Volunteer Corps with strength, musketry, officers, retired list and arms; the Fire Brigade's jubilee year with motor appliances, calls since 1907 and the list of fires by trade and cause; the Police Force with branch strengths, criminal investigation, gaol and reformatory, traffic and accidents, the Mixed Court, civil cases, apprehensions, punishments, arrests and arms); the Health Officer's report (meteorology, deaths by cause, nationality and age, infectious diseases, plague prevention and rats, vaccination, laboratory, waterworks analyses, hospitals, sanitary work, slaughter-house, markets, prices, cemeteries and the mortuary; the Victoria Nursing Home, Laundry Guild and Paulun Hospital accounts); General matters (the Charity Organisation, water supply, the Council and grant-aided schools with enrolment, attendance, ages, examinations, sports and accounts, the semaphore account and the full Municipal Staff list); Works Matters (bridges, survey, roads, rolling stock, water mains, lighting, permits and new buildings, quarry and concreteware, the schedule of municipal properties, road extensions and compensation, the Land Commission, parks and sports grounds); the Electricity Department's comparative table since 1901, 1917 estimate, accounts and balance sheet; the Treasurer's and the Overseer of Taxes' reports with rate, licence and assessment returns; then the financial statement and balance sheet for 1916 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1917 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan of the University of Illinois copy.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the list of fires, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plague map, the weather diagram and the graphs without printed figures are not. Four sideways tables were turned upright before reading. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense and sideways pages by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (14 cells). Chapters follow the printed contents (three page series, 1A–173A, 1B–74B and 1C–114C, as printed).",
     "scan": "https://archive.org/details/reportshanghaimu1916shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/reportshanghaimu1916shan",
     "blank_marking": True},
    {"slug": "china-smc-1917", "dir": "SMC_Report_1917", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1917",
     "subtitle": "Report for the Year 1917 and Budget for the Year 1918",
     "publisher": "Shanghai Municipal Council, Shanghai, 1918",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1917, arranged by the Council's committees: Watch Matters (the Volunteer Corps with strength, efficiency, officers and arms; the Fire Brigade with motor appliances, calls since 1908 and the fold-out list of fires by trade and cause; the Police Force with strength, traffic, accidents and chauffeurs, gaol, the Mixed Court, civil cases, apprehensions, punishments, arrests and arms); the Health Officer's report (meteorology, deaths by cause, nationality and age, infectious diseases including the history of scarlet fever since 1873, vaccination, laboratory, milk and water, hospitals, sanitary work, slaughter-house, markets, prices, cemeteries and the mortuary; the General and Paulun Hospital accounts); General matters (tramway services and extensions, the Charity Organisation and semaphore accounts, the Council and grant-aided schools with enrolment, attendance, ages, examinations and accounts, and the full Municipal Staff list); Works Matters (bridges, survey, roads, rolling stock, labour, lighting, permits and new buildings, quarry and concreteware, the schedule of municipal properties, road extensions and compensation, the Land Commission, parks); the Electricity Department's comparative table since 1901, 1918 estimate and accounts; the loan-redemption and Treasurer's reports and the Overseer of Taxes' report with rate, licence and assessment returns; then the financial statement and balance sheet for 1917 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1918 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the fold-out list of fires, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the plan of Shanghai, the weather diagram and the graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and fold-outs by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (25 cells). Chapters follow the printed contents (three page series, 1A–234A, 1B–75B and 1C–138C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1917-and-Budget-for-the-Year-1918/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1917-and-Budget-for-the-Year-1918",
     "blank_marking": True},
    {"slug": "china-smc-1918", "dir": "SMC_Report_1918", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1918",
     "subtitle": "Report for the Year 1918 and Budget for the Year 1919",
     "publisher": "Shanghai Municipal Council, Shanghai, 1919",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1918, the last year of the Great War, arranged by the Council's committees: Watch Matters (the Volunteer Corps with strength, efficiency and officers' lists; the Fire Brigade with calls, appliances, losses and the fold-out list of fires; the Police Force with strength, traffic and accidents, gaol, the Mixed Court, civil cases, the registration of enemy subjects, apprehensions, punishments, arrests and arms, and the expenditure on the Armistice celebrations and the local disturbances); Health Matters (meteorology, deaths by cause, nationality and age, infectious diseases, plague prevention, vaccination, laboratory, hospitals, sanitary inspection, markets, slaughter-house and cemeteries, the Paulun Hospital accounts, and the report on sewage disposal and water supply with its appendices on population, water analyses and trade effluents); Educational Matters (enrolment, attendance, ages, examinations, staff and accounts of the Council and grant-aided schools); General Matters (China's war measures, the telephone and tramway companies, water consumption, the Public Band, the Charity Organisation, the semaphore service and the full Municipal Staff list); Works Matters (cadastral survey, roads, water, gas and electric lighting, permits and new buildings, quarry and concreteware, the schedule of municipal properties, road extensions and compensation, the Land Commission, parks and nurseries); the Electricity Department's comparative table since 1901, 1919 estimate and accounts; the Treasurer's and the Superintendent of Revenue's reports with rate, licence and assessment returns; then the financial statement and balance sheet for 1918 (in taels), comparative statements, working accounts of the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1919 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on the fire-loss charts, the fold-out list of fires, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the weather diagram and the graphs without printed figures are not. On the fold-out List of Fires the scan does not show the printed row labels (the trades), so its 76 rows are numbered; and the scan cuts off the right edge of Comparative Statement A, so its 1918 percentage column is unreadable. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and fold-outs by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (43 cells). Chapters follow the printed contents (four page series, A to D, as printed; page 23B is missing from the scan).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1918-and-Budget-for-the-Year-1919/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1918-and-Budget-for-the-Year-1919",
     "blank_marking": True},
    {"slug": "china-smc-1919", "dir": "SMC_Report_1919", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1919",
     "subtitle": "Report for the Year 1919 and Budget for the Year 1920",
     "publisher": "Shanghai Municipal Council, Shanghai, 1920",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1919, the year after the Armistice, arranged by the Council's committees: Watch Matters (the Volunteer Corps with its strength, efficiency, musketry and officers' lists; the Fire Brigade with calls, fires, the fold-out list of fires by trade and cause, appliances and losses; the Police Force with strength, traffic, gaol, the Mixed Court and its assessors, crime, apprehensions and sentences, and the damage in the Hongkew disturbances); Health Matters (meteorology, population, deaths by cause, month, nationality and age, infectious diseases, vaccination, laboratory, hospitals and their accounts, sanitation, food, markets and cemeteries, sewage disposal); Educational Matters (enrolment, attendance, ages, examinations and staff of the Council and grant-aided schools); General Matters (the band, bye-laws, the War Volunteers' Memorial, charity, the semaphore service, the municipal staff who served and died in the Great War); the full Municipal Staff list; Works Matters (bridges, roads, traffic census, permits, quarry, concreteware, municipal properties, road extensions and Land Commission awards, parks); the Electricity Department's report, statistics, 1920 estimate and accounts; the Treasurer's and the Commissioner of Revenue's reports with the rate and licence returns; then the financial statement and balance sheet for 1919 (in taels), the industrial undertakings, the schedules of land, buildings and stores, and the budget for 1920 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on the Fire Brigade charts, the fold-out list of fires, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs of the Riverside Power Station, the weather diagram and the graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and fold-outs by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (40 cells). Chapters follow the printed contents (three page series, 1A–276A, 1B–55B and 1C–122C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1919-and-Budget-for-the-Year-1920/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1919-and-Budget-for-the-Year-1920",
     "blank_marking": True},
    {"slug": "china-smc-1920", "dir": "SMC_Report_1920", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1920",
     "subtitle": "Report for the Year 1920 and Budget for the Year 1921",
     "publisher": "Shanghai Municipal Council, Shanghai, 1921",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1920, arranged by the Council's committees: Watch Matters (the Volunteer Corps with its efficiency return, seniority roll and decorations; the Fire Brigade with calls, losses, motor appliances and the fold-out list of fires by trade and cause; the Police Force with strength, traffic accidents, gaol and reformatory, the Mixed Court, foreign and Chinese civil cases, apprehensions, punishments, arrests and arms; the annual drills of the Expeditionary Forces Emergency Unit); Health Matters (meteorology, deaths by cause, nationality and age, the death-rate since 1880, infectious diseases, plague prevention, vaccination, laboratory, hospitals, sanitary work, markets, slaughter-house, cemeteries and refuse disposal; the Paulun Hospital accounts); Educational Matters (enrolment, attendance, ages, examinations, staff and accounts of the Council and grant-aided schools); General Matters (wharfage dues, tramway fares and road space, water supply, the Public Band's programmes, the 1920 census of the foreign and Chinese population by nationality, district, native place and occupation, the Charity Organisation, the semaphore service, Chinese study, and the full Municipal Staff list); Works Matters (roads, trenches, water, lighting, permits and new buildings, quarry and concreteware, the register of municipal properties, road extensions and compensation, parks and sports grounds); the Electricity Department's statistics, contracts, comparative table since 1901, 1921 estimate and accounts; the Treasurer's and the Commissioner of Revenue's reports with rate, licence and assessment returns; then the financial statement and balance sheet for 1920 (in taels), the comparative statements, industrial undertakings, the schedules of land, buildings and stores, and the budget for 1921 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on the fire-loss chart, the fold-out list of fires and the census fold-out, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, the weather diagram, maps and the graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and fold-outs by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (23 cells). Chapters follow the printed contents (three page series, 1A–302A, 1B–56B and 1C–128C, as printed).",
     "scan": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1920-and-Budget-for-the-Year-1921/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/Shanghai-Municipal-Council-Report-for-the-Year-1920-and-Budget-for-the-Year-1921",
     "blank_marking": True},
    {"slug": "china-smc-1921", "dir": "SMC_Report_1921", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1921",
     "subtitle": "Report for the Year 1921 and Budget for the Year 1922",
     "publisher": "Shanghai Municipal Council, Shanghai, 1922",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1921, arranged by the Council's committees: Watch Matters (the Volunteer Corps with its strength, efficiency, musketry and officers' lists; the Fire Brigade with calls, fires, the fold-out return of fires by trade and cause, appliances and losses; the Police Force with strength, traffic, gaol, the Mixed Court, crime, apprehensions and sentences; the rice crisis with monthly rice prices); Health Matters (meteorology, population, deaths by cause, month, nationality and age, infectious diseases, laboratory, hospitals, sanitation, food, cemeteries and milk); Educational Matters (expenditure, enrolment, attendance, ages, examinations and staff of the Council and grant-aided schools); General Matters (the tramways, water supply, charity, wharfage dues, the semaphore service, the band's programmes, staff salary scales and medical attendance); the full Municipal Staff list; Works Matters (bridges, cadastral work, roads, drainage, lighting, building permits, quarry, concreteware, municipal properties, road extensions and Land Commission awards, parks); the Electricity Department's report, statistics, 1922 estimate and accounts; the Treasurer's and the Commissioner of Revenue's reports with the rate and licence returns; then the financial statement and balance sheet for 1921 (in taels), the schedules of land, buildings, stores and loans, the industrial undertakings, and the budget for 1922 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the fold-out return of fires, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs of the Riverside Power Station and other works, the weather diagram and the graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages, fold-outs and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (18 cells). Chapters follow the printed contents (three page series, 1A–304A, 1B–76B and 1C–130C, as printed).",
     "scan": "https://archive.org/details/reportshanghaimu1921shan/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/reportshanghaimu1921shan",
     "blank_marking": True},
    {"slug": "china-smc-1922", "dir": "SMC_Report_1922", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1922",
     "subtitle": "Report for the Year 1922 and Budget for the Year 1923",
     "publisher": "Shanghai Municipal Council, Shanghai, 1923",
     "note": "(scan ends in the 1923 budget)",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1922, arranged by the Council's committees: Watch Matters (the Volunteer Corps with its strength, efficiency, musketry and officers' lists; the Fire Brigade with calls, fires, the fold-out list of fires by trade and origin, appliances and losses; the Police Force with strength, traffic, gaol, the Mixed Court, crime, apprehensions and sentences, and the gaol dietary); Health Matters (meteorology, population, deaths by cause, month, nationality and age, infectious diseases, plague, vaccination, laboratory, hospitals, tuberculosis dietary, sanitation, food and markets); Educational Matters (enrolment, attendance, ages, examinations, staff and costs of the Council and grant-aided schools); General Matters (the tramways, omnibuses and ricshas, telephone rates, water supply, charity, semaphore service, the orchestra's programmes, the library); the full Municipal Staff list; Works Matters (bridges, roads, drainage and sewers, labour, lighting, permits, quarry, concreteware, municipal properties, road extensions and Land Commission awards, parks); the Electricity Department's report, statistics, 1923 estimate and accounts; the Treasurer's and the Commissioner of Revenue's reports with the revenue returns; then the financial statement and balance sheet for 1922 (in taels), the schedules of land, buildings, stores and loans, the industrial undertakings, and the budget for 1923 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on charts, the fold-out fire and Mixed Court returns, the staff list, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, maps and graphs without printed figures, and the index are not. The scan ends at p. 44D, part-way through the Extraordinary Expenditure of the 1923 budget, so the rest of the budget is missing. An errata slip (two fee corrections, Tls. 2 to Tls. 1.50) is attached as a note where it falls in a table. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages, fold-outs and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (19 cells). Chapters follow the printed contents (four page series, 1A–361A, 1B–86B, 1C–87C and 1D–44D, as printed).",
     "scan": "https://archive.org/details/shanghai-municipal-council-report-for-the-year-1922-and-budget-for-the-year-1923/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/shanghai-municipal-council-report-for-the-year-1922-and-budget-for-the-year-1923",
     "blank_marking": True},
    {"slug": "china-smc-1925", "dir": "SMC_Report_1925", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1925",
     "subtitle": "Report for the Year 1925 and Budget for the Year 1926",
     "publisher": "Shanghai Municipal Council, Shanghai, 1926",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1925, the year of the May 30th Incident and the general strike: the Volunteer Corps (composition, strength, efficiency, seniority lists), the Fire Brigade (calls, fires, damage, appliances), the Police Force (strength, traffic, gaol, the Mixed Court, crime, robberies, finger prints, arrests); the telephone tariff and tramway charges; public health (meteorology, population, deaths by cause, age, month and nationality, communicable diseases, laboratory, hospitals, sanitation, food and milk); the 1925 census of the Settlement (foreign population by nationality, district and occupation; Chinese population by native place and district); charity, the Court of Consuls; education (enrolment, attendance, ages, examinations and accounts of every Council and grant-aided school); public works (bridges, cadastral work, roads, drainage and sewers, refuse, water, labour, lighting, permits, quarry, workshops, concreteware), the schedule of municipal properties, easements, road extensions and Land Commission awards, sewage treatment, parks and the orchestra; the pension list and the full Municipal Staff list; the Electricity Department's report, statistics, 1926 estimate and accounts; the Treasurer's and the Commissioner of Revenue's reports with the revenue returns; then the financial statement and balance sheet for 1925 (in taels), the schedules of land, buildings, stores and loans, the industrial undertakings, and the budget for 1926 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on charts, the census fold-outs, the staff and pension lists, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, maps and graphs without printed figures, and the index are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages, the census fold-outs and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (11 cells). Chapters follow the printed contents; the Electricity and Finance sections are paged 1A–92A and the Estimates 1B–43B, as printed.",
     "scan": "https://archive.org/details/shanghai-municipal-council-report-for-the-year-1925-and-budget-for-the-year-1926/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/shanghai-municipal-council-report-for-the-year-1925-and-budget-for-the-year-1926",
     "blank_marking": True},
    {"slug": "china-smc-1928", "dir": "SMC_Report_1928", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1928",
     "subtitle": "Report for the Year 1928 and Budget for the Year 1929",
     "publisher": "Shanghai Municipal Council, Shanghai, 1929",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for 1928, the year the Council first admitted Chinese members and opened the public parks to Chinese: the Volunteer Corps (strength, inspection, musketry), the Fire Brigade (fires, damage, calls, hydrants, staff), the Police Force (strength, branches, traffic, gaols, the Provisional Court, crime and arrests, finger prints, strikes), the Lester Trust accounts and the waterworks agreement; public health (meteorology, population, deaths by cause, age, month and nationality, communicable diseases, laboratories, hospitals, sanitation, food, markets and cemeteries); education (enrolment, attendance, ages, examinations and staff of every Council school, and the grant-aided schools' accounts); public works (bridges, roads, drainage and sewers, refuse, water supply, labour, lighting, building permits, quarry, workshops), parks, the schedule of municipal properties, easements, road extensions and the Land Commission; the pension list and the full Municipal Staff list; the Electricity Department's report, statistics and accounts; the Commissioner of Revenue's report (rates, assessments, licences, wharfage, markets); then the financial statement and balance sheet for 1928 (in taels), the schedules of land, buildings, stores and loans, the industrial undertakings, and the budget for 1929 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on charts, the staff and pension lists, the accounts and the budget (each department or sub-head of the financial statement and budget is a separate table); the prose, the photographs, maps and graphs without printed figures, and the index are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (13 cells). Chapters follow the printed contents.",
     "scan": "https://archive.org/details/1928-smc-annual-report-and-budget/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/1928-smc-annual-report-and-budget",
     "blank_marking": True},
    {"slug": "china-smc-1932", "dir": "SMC_Report_1932", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1932",
     "subtitle": "Report for the Year 1932 and Budget for the Year 1933",
     "publisher": "Shanghai Municipal Council, Shanghai, 1933",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement, for the year of the Sino-Japanese hostilities around Shanghai: the ratepayers' meeting (with the list of ratepayers present), the public utility companies, the Volunteer Corps, the Fire Brigade (fires, ambulance calls, hydrants, workshops), the Police Force (strength, distribution, crime and arrests, crime charts, film censorship), the gaols and the Municipal Advocate's courts; public health (deaths by cause, age, month and nationality, communicable diseases, laboratories, hospitals, abattoir, markets, milk, sanitation); public works (bridges, cadastral work, roads, sewers, quarry, concreteware, parks, schedule of municipal properties, road expenditure); education (enrolment, attendance, ages and staff of every Council school); then the Treasurer's report, the financial statements and balance sheet for 1932 (in taels), the schedules of land, buildings, stores and pensions, and the budget for 1933 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on charts, the accounts and the budget (each department or sub-head of the financial statements and budget is a separate table); the prose, the photographs, maps and graphs without printed figures, and the index are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (12 cells). Chapters follow the printed contents.",
     "scan": "https://archive.org/details/1932-smc-annual-report-and-budget/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/1932-smc-annual-report-and-budget",
     "blank_marking": True},
    {"slug": "china-smc-1934", "dir": "SMC_Report_1934", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1934",
     "subtitle": "Report for the Year 1934 and Budget for the Year 1935",
     "publisher": "Shanghai Municipal Council; Shanghai: Kelly & Walsh, 1935",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement: the 1934 election and ratepayers' meeting (with the list of ratepayers present), industrial accidents and factory boilers, the public utility companies, the Ricsha Board, the Volunteer Corps, Fire Brigade, Police Force (strength, crime, arrests, traffic, film censorship), the gaols and the Municipal Advocate's courts; public health (population, births, deaths by cause, age and nationality, communicable diseases, laboratories, hospitals, school medical service, abattoir, markets, sanitation, cemeteries); public works (roads, drains, sewers, buildings, lighting, quarry, workshops, parks, municipal properties); education, the orchestra and the public library; then the Treasurer's report, the financial statements and balance sheet for 1934, the schedules of land, buildings, stores and pensions, and the budget for 1935 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including small tables set in the text, the figures printed on charts, the accounts and the budget (each department or sub-head of the financial statements and budget is a separate table); the prose, the photographs and graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (22 cells); a few are at the edge of pages that the scan clips. The scan has no table of contents; the contents shown here are the report's sections.",
     "scan": "https://archive.org/details/1934-shanghai-municipal-council-report-for-the-year-1934-and-budget-for-the-year-1935/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/1934-shanghai-municipal-council-report-for-the-year-1934-and-budget-for-the-year-1935",
     "blank_marking": True},
    {"slug": "china-smc-1936", "dir": "SMC_Report_1936", "model": "Haiku 5.5 and Sonnet 5.5",
     "title": "Shanghai Municipal Council Report 1936",
     "subtitle": "Report for the Year 1936 and Budget for the Year 1937, Part I",
     "publisher": "Shanghai Municipal Council; Shanghai: North-China Daily News & Herald, 1937",
     "blurb": "The annual report of the Shanghai Municipal Council, which governed the International Settlement: the 1936 election and ratepayers' meeting, industrial accidents and factory inspection, the public utility companies, the Ricsha Board, the Volunteer Corps, Fire Brigade, Police Force (strength, crime, arrests, traffic, film censorship), the gaol and the Municipal Advocate's courts; public health (population, births, deaths by cause and nationality, communicable diseases, laboratories, hospitals, school medical service, markets, abattoir, sanitation, licensing, cemeteries); public works (roads, drains, buildings, lighting, quarry, workshops, parks, municipal properties); education; the public library; then the Treasurer's report, the financial statements and balance sheet for 1936, schedules of land, buildings, stores and pensions, and the budget for 1937 with the schedule of rates, taxes, dues and fees.",
     "source": "LLM-transcribed (Claude Haiku 5.5 and Sonnet 5.5 sub-agents) from the Internet Archive scan.",
     "gaps": "All tables and lists are transcribed, including the small tables set in the text, the figures printed on charts, the accounts and the budget (each department or sub-head of the financial statements and budget is a separate table); the prose, the photographs, the posters and graphs without printed figures are not. Table pages were found from contact sheets by Claude Sonnet 5.5; light pages were read once by Claude Haiku 5.5, dense pages and long schedules by Claude Sonnet 5.5. Not checked by eye. Printed totals were re-added by the readers: totals that do not add up are kept as printed and noted. Figures that could not be read are marked [?] (64 cells, 0.1%); some are at the right edge of pages that the scan clips. Part I only: the contents list the report (pp. 1–252); the accounts (Part II) and budget (Part III) follow in the same volume.",
     "scan": "https://archive.org/details/1936-smc-annual-report-and-budget-part-1/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/1936-smc-annual-report-and-budget-part-1",
     "blank_marking": True},
    {"slug": "china-flood-1931", "dir": "China_Flood_1931", "model": "Haiku 5.5", "title": "The 1931 Flood in China: An Economic Survey",
     "publisher": "Department of Agricultural Economics, College of Agriculture and Forestry, University of Nanking, with the National Flood Relief Commission; Nanking, April 1932 (University of Nanking Bulletin No. 1, New Series)",
     "blurb": "A field survey of the great 1931 Yangtze and Huai floods: flood conditions, losses of crops, buildings and livestock, the needs of flooded families, migration, illness and deaths, price changes, relief and refugee camps, with appendix tables by hsien and the survey schedules.",
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from the Giannini Foundation library copy on AgEcon Search.",
     "gaps": "Only tables are transcribed; the text, maps and photographs are not. Pages with tables were found from contact sheets by Claude Sonnet 5.5. Each page was read once by Claude Haiku 5.5; wide tables that Haiku split in two (losing columns) were re-read whole by Claude Sonnet 5.5. Not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Chapters follow the printed contents.",
     "scan": "https://ageconsearch.umn.edu/nanna/record/324563/files/giannini-misc-358.pdf?withWatermark=0&withMetadata=0&registerDownload=1&version=1#page={leaf}",
     "item": "https://ageconsearch.umn.edu/nanna/record/324563/files/giannini-misc-358.pdf?withWatermark=0&withMetadata=0&registerDownload=1&version=1",
     "blank_marking": True},
    {"slug": "china-1938", "dir": "China_Year_Book_1938", "title": "The China Year Book 1938",
     "publisher": "H. G. W. Woodhead (ed.); Shanghai: North-China Daily News & Herald, 1938",
     "blurb": "The wartime edition of the English-language reference book on China, compiled as the Sino-Japanese war began.",
     "source": "LLM-transcribed from a scan of the printed volume.",
     "gaps": "The Internet Archive copy is borrow-only: the scan links open the right page only while you have the book checked out there. No printed pages are missing from the scan. The Calendar for 1938 is transcribed month by month. The Chinese Who's Who (pp. 142–191) is on the Who's Who page; the 1937 summary of Sino-Japanese hostilities and the 1937 fires are on the Chronologies page. Laws, treaties, regulations and diplomatic documents are transcribed only where they contain tables or lists; numbered articles are prose. The Contents, indexes and advertisements are not transcribed. Very long tables (the Import Tariff, the railway obligations) are split into one table per printed page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/chinayearbook1930000hgww/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/chinayearbook1930000hgww"},
    {"slug": "china-1937-43", "dir": "China_Handbook_1937-1943", "title": "China Handbook 1937-1943",
     "publisher": "Chinese Ministry of Information; New York: Macmillan, 1943",
     "blurb": "The Chinese government's wartime reference book on Free China, 1937-1943.",
     "source": "LLM-transcribed from the Internet Archive scan (five parts, two-page spreads).",
     "gaps": "The scan is missing printed pp. 444–445 (so Industry and Labor Table 18 is lost) and pp. lii–liii of the Chinese Who's Who. The legal texts (constitutions, laws, regulations) are transcribed only where they contain tables or lists; numbered articles are prose. The book's Contents, Index and folding map of China are not transcribed. The Associations and Societies chapter and the Chinese Who's Who are on the Who's Who & Directories page; the Kuomintang chronology and the Chronology of Major Events, 1937–1943, are on the Chronologies page. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-handbook-1937-1943/China%20Handbook%201937-1943%20Part%20{part}%20of%205/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-handbook-1937-1943"},
    {"slug": "china-1950", "dir": "China_Handbook_1950",
     "root": os.environ.get("CHINA_1950_ROOT"),
     "title": "China Handbook 1950",
     "publisher": "China Handbook Editorial Board; New York: Rockport Press, 1950",
     "blurb": "The Nationalist government's reference book compiled after its retreat to Taiwan: geography, the provinces, history and a chronology to 1949, government, defence, parties, foreign affairs, the economy, communications, education, health, relief and a Who's Who.",
     "source": "LLM-transcribed from the Internet Archive scan (three parts, two-page spreads).",
     "gaps": "The scan is complete: every printed page from the front matter to p. 786 is present. The contents pages and the index (pp. 787–799) are not transcribed, and neither are running prose, maps and charts without figures. Treaties, agreements, laws, constitutions and statements (much of chapters 6–13, 27 and 31) are prose; only tables and lists printed inside them are transcribed. Each province's summary block (area, population, hsien, capital) in chapter 2 is given as a small table. The Who's Who (chapter 36) is on the Who's Who & Directories page and the Chronology of Major Events, 1911–1949 (chapter 5), on the Chronologies page. Many figures in the tables are printed out of line with their row labels; they were matched by counting, and each table's notes say where. Many printed totals do not add up; the figures are kept as printed and each table's notes say where.",
     "scan": "https://archive.org/details/china-handbook-1950/China%20Handbook%201950%20Part%20{part}%20of%203/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/china-handbook-1950"},
]


# Shown on the About card of every book transcribed before the blank-marking rule of 2026-10-01.
BLANK_NOTE = ('<p class="blanknote"><b>Note:</b> In the early books added to this website, cells that are marked blank '
              'may be blank because the original was blank, or because the large language model extracting the table '
              'had difficulty in reading the cell. Read the transcription notes for each table and check the original '
              'source when in doubt.</p>')

def dl(slug, suffix):
    """Relative path of a download written by build_downloads.py, or None if it hasn't been built."""
    f = f"downloads/{slug}-{suffix}"
    return f if os.path.exists(os.path.join(HERE, f)) else None


def book_dir(book):
    """Books live beside this repo's parent folder, or at an explicit absolute path ("root")."""
    return book.get("root") or os.path.join(ROOT, book["dir"])


def page_key(t):
    m = re.match(r"p(\d)-(\d+)", t["file"]) or re.search(r"(\d+)", t["file"])  # multi-part scans: p{part}-{leaf}
    img = int(m.group(1)) * 10000 + int(m.group(2)) if m and m.lastindex == 2 else (int(m.group(1)) if m else 0)
    n = int(re.search(r"_(\d+)\.json$", t["file"]).group(1))
    return (img, n)


def load(book):
    tables = []
    for f in sorted(glob.glob(os.path.join(book_dir(book), "_work", "tables", "*.json"))):
        try:  # agents may be writing or merging files while we build
            with open(f, encoding="utf-8") as fh:
                t = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        t["file"] = os.path.basename(f)
        t["id"] = t["file"][:-5]
        tables.append(t)
    tables.sort(key=page_key)
    return tables


_LEAFMAPS = {}


def leafmap(book):
    """Optional leafmaps/<slug>.json: {"IMG_5451": 10, ...} or {"IMG_4814": [part, leaf], ...} for books transcribed from photos whose online scan is numbered differently."""
    if book["slug"] not in _LEAFMAPS:
        f = os.path.join(SCRIPTS, "leafmaps", book["slug"] + ".json")
        _LEAFMAPS[book["slug"]] = json.load(open(f, encoding="utf-8")) if os.path.exists(f) else None
    return _LEAFMAPS[book["slug"]]


def scan_links(book, t):
    ims = t.get("images") or [t.get("image")]
    out = []
    for im in ims:
        mp = re.match(r"p(\d)-(\d+)$", im or "")  # multi-part scans: one IA file per part
        if book["scan"] and mp:
            part, leaf = int(mp.group(1)), int(mp.group(2))
            out.append({"label": f"scan part {part}, leaf {leaf}", "url": book["scan"].format(part=part, partname=book.get("scan_parts", {}).get(part, ""), leaf=leaf)})
            continue
        lm = leafmap(book)
        if book["scan"] and lm is not None and im in lm:  # photo names mapped to the online scan's leaves
            if lm[im] is None:
                pp = t.get("printed_pages") or []  # not in the online scan: show only the printed pages
                out.append({"label": ("pp. " if len(pp) > 1 else "p. ") + "–".join([pp[0], pp[-1]] if len(pp) > 1 else pp), "url": None})
            elif isinstance(lm[im], list):  # [part, leaf] for a scan split into several files
                part, leaf = lm[im]
                out.append({"label": f"scan part {part}, leaf {leaf}", "url": book["scan"].format(partname=book["scan_parts"][part], leaf=leaf)})
            else:
                out.append({"label": f"scan leaf {lm[im]}", "url": book["scan"].format(leaf=lm[im])})
            continue
        m = re.match(r"p(\d+)$", im or "")
        if book["scan"] and m:
            out.append({"label": f"{book.get('leaf_label', 'scan leaf')} {int(m.group(1))}", "url": book["scan"].format(leaf=int(m.group(1)))})
        else:
            out.append({"label": "" if book.get("hide_images") else f"photo {im}", "url": None})
    return out


def edition(book):
    m = re.search(r"(\d{4}(?:\s*[-–]\s*\d{1,4})?)", book["title"])
    return re.sub(r"\s*[-–]\s*", "–", m.group(1)) if m else book["title"]


def crosslinks(all_tables):
    """Links between editions of one series: build/crosslinks/chapters.py (hand-made chapter topics) and
    build/crosslinks/families/*.json (recurring tables). Returns {slug: {"ch": ..., "tb": ...}} for the book pages."""
    import importlib.util
    f = os.path.join(SCRIPTS, "crosslinks", "chapters.py")
    out = {b: {"ch": {}, "tb": {}} for b in all_tables}
    if not os.path.exists(f):
        return out
    spec = importlib.util.spec_from_file_location("xl_chapters", f)
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    ed = {b["slug"]: edition(b) for b in BOOKS}
    for series in mod.SERIES.values():
        for topic, members in series["topics"].items():
            present = [b for b in series["books"] if b in members and b in all_tables]
            if len(present) < 2:
                continue
            for b in present:
                for chap in members[b]:
                    others = [{"s": o, "e": ed[o], "c": members[o]} for o in present if o != b]
                    out[b]["ch"].setdefault(chap, []).append({"t": topic, "o": others})
    byid = {(b, t["id"]): t for b, ts in all_tables.items() for t in ts}
    fams = []
    for ff in sorted(glob.glob(os.path.join(SCRIPTS, "crosslinks", "families", "*.json"))):
        with open(ff, encoding="utf-8") as fh:
            for fam in json.load(fh).get("families", []):
                mem = []
                for m in fam.get("members", []):
                    b, _, tid = m.partition("/")
                    if (b, tid) in byid:
                        mem.append((b, tid))
                    else:
                        print(f"crosslinks: {os.path.basename(ff)}: unknown table {m}")
                fams.append({"label": fam.get("label", ""), "note": fam.get("note", ""), "mem": mem})
    # a chapter under two topics can put one table in two families: merge families that share a table
    owner = {}
    for i, fam in enumerate(fams):
        for key in fam["mem"]:
            if key in owner and owner[key] != i:
                j = owner[key]
                while "into" in fams[j]:
                    j = fams[j]["into"]
                if j != i:
                    for k2 in fams[i]["mem"]:
                        if k2 not in fams[j]["mem"]:
                            fams[j]["mem"].append(k2)
                    if fam["note"] and fam["note"] not in fams[j]["note"]:
                        fams[j]["note"] = (fams[j]["note"] + " " + fam["note"]).strip()
                    fam["into"] = j
                    for k2 in fams[j]["mem"]:
                        owner[k2] = j
                break
            owner[key] = i
    order = {s: i for i, s in enumerate(x["slug"] for x in BOOKS)}
    for fam in fams:
        if "into" in fam:
            continue
        mem = fam["mem"]
        if len({b for b, _ in mem}) < 2:
            continue
        mem.sort(key=lambda x: (ed[x[0]], order[x[0]]))
        for b, tid in mem:
            out[b]["tb"][tid] = {"f": fam["label"], "n": fam["note"],
                                 "o": [{"s": o, "e": ed[o], "id": oid, "t": byid[(o, oid)].get("title") or "",
                                  "p": ", ".join(byid[(o, oid)].get("printed_pages") or [])}
                                       for o, oid in mem if o != b]}
    return out


def add_english(book, tables):
    """Optional build/translations/<slug>.json: {id: {"t": English title, "d": one-line description}} shown under the title."""
    f = os.path.join(SCRIPTS, "translations", book["slug"] + ".json")
    if not os.path.exists(f):
        return
    with open(f, encoding="utf-8") as fh:
        tr = json.load(fh)
    for t in tables:
        if t["id"] in tr:
            t["en"] = tr[t["id"]]
    book["_chen"] = tr.get("_chapters", {})


def finder_links(slug):
    """{table id: [[label, href, title]]}: the finder pages (build/finders/registry.py) that carry this table's figures.
    Read from each finder's table_links.json, written by its last build (so a newly specced table gets its link on
    the build after)."""
    if not hasattr(finder_links, "reg"):
        sys.path.insert(0, os.path.join(SCRIPTS, "finders"))
        import registry
        finder_links.reg = registry
    return finder_links.reg.table_links(slug, "../../")


def finder_search_list():
    """The finder pages Full Search shows place cards from: [{name, title, page, index}] (paths from the site root)."""
    finder_links("")   # loads the registry
    return [{"name": c["name"], "title": c["title"], "page": c["page"], "index": c["data"] + "/index.json"}
            for c in finder_links.reg.finders()]


def add_maplinks(book, tables):
    """"Show on map" links for the tables listed in build/maplinks.json (spec: build/MAPLINK_SPEC.md)."""
    import importlib.util
    if not hasattr(add_maplinks, "mod"):
        spec = importlib.util.spec_from_file_location("maplinks", os.path.join(SCRIPTS, "maplinks.py"))
        add_maplinks.mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(add_maplinks.mod)
        add_maplinks.cfg = add_maplinks.mod.load_config()
    M, cfg = add_maplinks.mod, add_maplinks.cfg
    if not any(c.get("book") == book["slug"] for c in cfg.get("tables", [])):
        return
    M.BOOK_TABLES = {x["id"]: x for x in tables}
    book["_year"] = edition(book)
    for t in tables:
        u = M.map_url(book, t, t.get("en"), cfg)
        if u:
            t["map"] = u


def cells(tables):
    return sum(len(r) for t in tables for p in t.get("parts", []) for r in p.get("rows", []))


def qstats(tables):
    """Doubtful cells: unreadable ("[?]", shown with a red hatch) or containing "?"; and tables with more than 20% such cells.
    Returns (doubtful cells, all cells, doubtful-heavy tables, all tables)."""
    q = tot = heavy = 0
    for t in tables:
        tq = tc = 0
        for p in t.get("parts", []):
            for r in p.get("rows", []):
                for c in r:
                    tc += 1
                    tq += isinstance(c, str) and "?" in c
        q += tq; tot += tc; heavy += tc > 0 and tq / tc > 0.2
    return q, tot, heavy, len(tables)


def qstat_html(tables, cls="qstat"):
    q, tot, heavy, nt = qstats(tables)
    if not nt:
        return ""
    pc = lambda a, b: f" ({100 * a / b:.2f}%)" if b and f"{100 * a / b:.2f}" != "0.00" else ""   # no "(0.00%)"
    return (f'<div class="{cls}" title="Cells marked unreadable (red hatch) or containing a printed or doubtful ?">'
            f'Unreadable or “?” cells: <b>{q:,}</b> of {tot:,}{pc(q, tot)} · '
            f'Tables with more than 20% such cells: <b>{heavy:,}</b> of {nt:,}{pc(heavy, nt)}</div>')


# Topic tags (build/topics/<region>.json: {"slug:id": [[topic, subtopic], …]}). Tagged tables get chart views and
# are listed on the topic pages (user, 2026-10-22: Korea first; charts only for the topic tables for now).
TOPIC_TAGS = {}
for _f in sorted((Path(__file__).parent / "topics").glob("*.json")):
    if re.fullmatch(r"[a-z]+\.json", _f.name):   # korea.json, taiwan.json (not the agents' tags_*.json)
        TOPIC_TAGS.update(json.loads(_f.read_text()))
# Every table of these regions gets a chart view (user, 2026-10-22, after the topic tables); elsewhere only tagged tables.
CHART_ALL = ("korea-", "taiwan-", "china-", "japan-", "manchuria-", "manchoukuo-", "manchukuo-", "nanyo-", "far-east-", "pacific-survey-")


def chart_ids(b, tables):
    return [t["id"] for t in tables] if b["slug"].startswith(CHART_ALL) else CHART_IDS.get(b["slug"], [])


CHART_IDS = {}
for _k in TOPIC_TAGS:
    _s, _id = _k.split(":", 1)
    CHART_IDS.setdefault(_s, []).append(_id)


# ---- Topic pages (Korea first; user, 2026-10-22) ---------------------------------------------------------------
TOPICS = [("population", "Population"), ("education", "Education"), ("religion", "Religion"), ("crime", "Crime and justice")]
SUBTOPICS = {
    "population": ["totals and density", "by nationality", "by province or district", "households", "births, deaths and marriages",
                   "migration and foreign residents", "occupations", "age and sex"],
    "education": ["schools and pupils, overview", "elementary and common schools", "secondary and higher schools", "vocational and normal schools",
                  "private schools and sŏdang", "teachers", "finance", "libraries, students abroad and other"],
    "religion": ["overview", "Shinto and shrines", "Buddhism", "Christianity and missions", "other religions and religious bodies"],
    "crime": ["offences and arrests", "prosecutions and courts", "sentences and convictions", "prisons and prisoners", "police",
              "summary punishments", "thought and public-order offences", "juvenile"],
}
TOPIC_REGIONS = {
    "korea": ("Korea", [("ar", "Annual Report (English)", r"^korea-\d{4}-\d{2}$"), ("jj", "朝鮮事情", r"^korea-\d{4}$"),
                        ("nk", "朝鮮年鑑", r"^korea-nenkan-"), ("tk", "統計年報", r"^korea-tokanfu-")]),
    "taiwan": ("Taiwan", [("en", "English reports", r"^taiwan-\d{4}$"), ("tk", "臺灣總督府統計書", r"^taiwan-tokei-")]),
    "china": ("China", [("cy", "China Year Book", r"^china-(19[12]\d|193[18])(-\d+)?$"), ("ch", "China Handbook", r"^china-(1937-43|1944|1950)$"), ("cb", "Chinese Year Book", r"^china-cyb-"),
                        ("ot", "Other surveys", r"^china-(flood|handbook|peking|mission|christian|provinces)-")]),
    "japan": ("Japan", [("jy", "Japan Year Book", r"^japan-\d{4}(-\d+)?$"), ("jm", "Japan-Manchoukuo Year Book", r"^japan-manchoukuo-"),
                        ("tk", "日本帝國統計年鑑", r"^japan-tokei-")]),
    "manchuria": ("Manchuria", [("rp", "Report on Progress in Manchuria", r"^manchuria-\d{4}$"),
                                ("yb", "Manchuria / Manchoukuo Year Book", r"^(manchuria-year-book-|manchoukuo-)"),
                                ("dr", "Manchukuo Directory", r"^manchukuo-directory-")]),
    "south-seas": ("South Seas", [("ny", "南洋廳統計年鑑", r"^nanyo-tokei-")]),
    "other": ("Other", [("fe", "Far East Year Book", r"^far-east-"), ("ps", "Economic Survey of the Pacific Area", r"^pacific-survey-")]),
}


def build_topics(pages):
    """topics/<region>-<topic>.html: every tagged table of a region for a topic, as printed, linked into its book."""
    os.makedirs(os.path.join(HERE, "topics"), exist_ok=True)
    by_slug = {b["slug"]: (b, clean) for b, clean, n, c in pages}
    counts = {}   # (region, topic) -> (tables, volumes)
    have = [r for r, (rn, sr) in TOPIC_REGIONS.items() if any(re.match(rx, k.split(":")[0]) for _, _, rx in sr for k in TOPIC_TAGS)]
    for region, (rname, series) in TOPIC_REGIONS.items():
        vols = {}
        for code, _, rx in series:
            for slug in by_slug:
                if re.match(rx, slug) and any(k.startswith(slug + ":") for k in TOPIC_TAGS):
                    b = by_slug[slug][0]
                    vols[slug] = {"s": slug, "ser": code, "ed": edition(b), "y": years_of(b)[0] or 0, "title": b["title"]}
        if not vols:
            continue
        order = sorted(vols, key=lambda s: (vols[s]["y"], s))
        for key, name in TOPICS:
            items = []
            for slug in order:
                b, clean = by_slug[slug]
                for t in clean:
                    tags = [sub for top, sub in TOPIC_TAGS.get(f"{slug}:{t['id']}", []) if top == key]
                    if not tags:
                        continue
                    n_q = sum(1 for p in t.get("parts", []) for r in p["rows"] for c in r if c == "[?]")
                    label = (f"Table {t['table_no']}. " if t.get("table_no") else "") + (t.get("title") or "")
                    items.append({"s": slug, "id": t["id"], "t": label, "e": (t.get("en") or {}).get("t", ""), "c": t.get("chapter") or "",
                                  "pp": ", ".join(t.get("printed_pages") or []), "sub": [x for x in SUBTOPICS[key] if x in tags], "q": n_q})
            nav = (" · ".join(f'<b>{n}</b>' if k == key else f'<a href="{region}-{k}.html">{n}</a>' for k, n in TOPICS)
                   + '<br><span class="also">' + name + " in: " + " · ".join(f'<b>{TOPIC_REGIONS[r][0]}</b>' if r == region else f'<a href="{r}-{key}.html">{TOPIC_REGIONS[r][0]}</a>' for r in have)
                   + ' · <a href="index.html">All topics</a></span>')
            counts[(region, key)] = (len(items), len({i["s"] for i in items}))
            doc = (TOPIC_PAGE.replace("__TOPIC__", name).replace("__NAV__", nav).replace("__REGION__", rname).replace("__RKEY__", region)
                   .replace("__WHO__", "the colonial administration" if region in ("korea", "taiwan", "south-seas") else "the officials, editors and publishers")
                   .replace("__DATA__", json.dumps({"items": items, "vols": [vols[s] for s in order], "subs": SUBTOPICS[key],
                                                    "series": [[c, n] for c, n, _ in series]}, ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__NTXT__", (lambda n, v: f'{n:,} table{"s" if n != 1 else ""} from {v} {rname} volume{"s" if v != 1 else ""}')(len(items), len({i["s"] for i in items}))))
            with open(os.path.join(HERE, "topics", f"{region}-{key}.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
            print(f"topics/{region}-{key}.html: {len(items)} tables")
    rows = "".join(f'<tr><th>{n}</th>' + "".join(f'<td><a href="{r}-{k}.html"><b>{TOPIC_REGIONS[r][0]}</b><span>{counts[(r, k)][0]:,} table{"s" if counts[(r, k)][0] != 1 else ""} · {counts[(r, k)][1]} volume{"s" if counts[(r, k)][1] != 1 else ""}</span></a></td>' if (r, k) in counts else "<td></td>" for r in have) + "</tr>" for k, n in TOPICS)
    with open(os.path.join(HERE, "topics", "index.html"), "w", encoding="utf-8") as fh:
        fh.write(TOPIC_INDEX.replace("__ROWS__", rows).replace("__HEAD__", "".join(f"<th>{TOPIC_REGIONS[r][0]}</th>" for r in have)))
    return counts, have


def topics_menu(counts, have, prefix=""):
    """The topic menu on the home page: one row per topic, one link per region."""
    if not counts:
        return ""
    rows = "".join(f'<div class="tmrow"><span class="tmt">{n}</span>' + "".join(f'<a href="{prefix}topics/{r}-{k}.html">{TOPIC_REGIONS[r][0]} <small>{counts[(r, k)][0]:,}</small></a>' for r in have if (r, k) in counts) + "</div>" for k, n in TOPICS)
    return f'<section class="tmenu" id="topics"><h2 class="grph">Browse by topic</h2><p class="tmn">Tables on population, education, religion and crime gathered from every volume of a region, each as printed and linked into its book. <a href="{prefix}topics/index.html">All topics →</a></p>{rows}</section>'


TOPIC_INDEX = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>Tables by topic</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Hiragino Mincho ProN","Yu Mincho","Noto Serif CJK JP",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:1040px;margin:0 auto;padding:22px 16px 20px}.band a{color:var(--accent-ink)}.band h1{font-weight:normal;font-size:28px;margin:4px 0 6px}
main{max-width:1040px;margin:0 auto;padding:20px 16px 60px}.lede{color:var(--muted);max-width:760px;font-size:15px}
.tw{overflow-x:auto}table{border-collapse:collapse;width:100%;min-width:560px;background:var(--panel);border:1px solid var(--line)}th,td{border-bottom:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}thead th{font-weight:normal;color:var(--muted);font-size:14px}tbody th{font-weight:normal;font-size:18px;white-space:nowrap}
td a{display:block;color:var(--ink);text-decoration:none}td a b{font-weight:normal;color:var(--accent);text-decoration:underline}td a span{display:block;font-size:12.5px;color:var(--muted)}
@media (max-width:640px){.band h1{font-size:24px}table{min-width:0;border:0;background:transparent}thead{display:none}tbody,tr,th,td{display:block}tr{background:var(--panel);border:1px solid var(--line);margin:0 0 14px;padding:4px 0 8px}tbody th{border:0;padding:10px 14px 4px;font-size:19px}td{display:inline-block;width:calc(50% - 4px);border:0;padding:6px 14px;vertical-align:top}td:empty{display:none}}
</style></head><body>
<div class="band"><div><a href="../index.html">← All books</a><h1>Tables by topic</h1></div></div>
<main><p class="lede">Each page linked below includes a selection (which should not be seen as complete) of tables for a few key topics across one collection of volumes.</p>
<div class="tw"><table><thead><tr><th></th>__HEAD__</tr></thead><tbody>__ROWS__</tbody></table></div></main></body></html>
"""


TOPIC_PAGE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>__REGION__: __TOPIC__ tables</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman","Hiragino Mincho ProN","Yu Mincho","Noto Serif CJK JP","Noto Serif JP",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:1040px;margin:0 auto;padding:22px 16px 20px}.band a{color:var(--accent-ink)}.band h1{font-weight:normal;font-size:28px;margin:4px 0 6px}.crumb{font-size:14px;opacity:.9}.tnav{font-size:15px}.tnav .also{font-size:13.5px;opacity:.9}
main{max-width:1040px;margin:0 auto;padding:20px 16px 60px}.lede{color:var(--muted);max-width:760px;font-size:15px}
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:16px 0 10px}input,select,button{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}#q{flex:1 1 220px;min-width:0}
.ser{display:flex;flex-wrap:wrap;gap:4px 12px;font-size:14px}.ser label{white-space:nowrap}.sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:0}
.cov{overflow-x:auto;border:1px solid var(--line);background:var(--panel);margin:14px 0 6px}.cov table{border-collapse:collapse;font-size:12px}.cov th,.cov td{border-bottom:1px solid var(--line);padding:3px 4px;text-align:center;white-space:nowrap}.cov th.sub{text-align:left;font-weight:normal;position:sticky;left:0;background:var(--panel);padding-right:10px;max-width:200px;white-space:normal;min-width:130px}
.cov thead th{font-weight:normal;color:var(--muted);vertical-align:bottom;writing-mode:vertical-rl;transform:rotate(180deg);height:62px;padding:4px 2px}.cov td.c{cursor:pointer;min-width:20px}.cov td.c b{display:inline-block;min-width:17px;padding:0 3px;border-radius:3px;color:#fff;font-weight:normal}.cov td.c.sel b{outline:2px solid var(--ink)}.cov td.z{color:var(--line)}
.covn{font-size:12.5px;color:var(--muted);margin:0 0 16px}
h2{font-size:19px;font-weight:normal;margin:26px 0 6px;border-bottom:1px solid var(--line);padding-bottom:4px}h2 small{color:var(--muted);font-size:13px}
.it{display:grid;grid-template-columns:118px minmax(0,1fr);gap:2px 14px;padding:8px 2px;border-bottom:1px solid var(--line)}.it .v{font-size:13px;color:var(--muted)}.it .v b{display:block;color:var(--ink);font-weight:normal;font-size:14px}
.it a.tt{color:var(--ink);text-decoration:none;font-size:15.5px}.it a.tt:hover{text-decoration:underline}.it .en{font-size:13.5px;color:var(--muted)}.it .meta{font-size:12.5px;color:var(--muted)}.it .q{color:var(--warn)}
.empty{color:var(--muted);font-style:italic;padding:12px 0}
@media (max-width:600px){.it{grid-template-columns:minmax(0,1fr)}.it .v b{display:inline;margin-right:6px}.band h1{font-size:23px}}
</style></head><body>
<div class="band"><div><div class="crumb"><a href="../index.html#__RKEY__">← All books</a> · __REGION__ · topics</div><h1>__REGION__: __TOPIC__</h1><div class="tnav">__NAV__</div></div></div>
<main>
<p class="lede">__NTXT__ on this site, each as it was printed — with the book's own categories, units, years and gaps — and each opening in its book, where it can be read as a table or a chart. The tables were sorted into these topics by a language model reading their titles and headings, so some may be missing or misplaced; the categories are those of __WHO__ that compiled them, and they change from one volume to the next.</p>
<div class="ctl"><input id="q" type="search" placeholder="Filter titles, translations, chapters…" aria-label="Filter"><select id="sub" aria-label="Subtopic"><option value="">All subtopics</option></select><select id="ord" aria-label="Arrange"><option value="sub">Grouped by subtopic</option><option value="year">Grouped by year</option><option value="vol">Grouped by volume</option></select></div>
<div class="ser" id="ser"></div>
<div class="cov" id="cov"></div><p class="covn">Tables per subtopic in each volume, in edition order; an empty cell means no table on it was found in that volume. Click a number to list those tables.</p>
<div id="out"></div>
</main>
<script>
const D=__DATA__;const COL={};D.series.forEach(([c],i)=>COL[c]=["#4e79a7","#e15759","#59a14f","#b07aa1"][i%4]);
const $=s=>document.querySelector(s),esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const V={};D.vols.forEach(v=>V[v.s]=v);const SER=Object.fromEntries(D.series);let pick=null;
D.subs.forEach(s=>{const o=document.createElement("option");o.value=s;o.textContent=s;$("#sub").appendChild(o)});
$("#ser").innerHTML=D.series.map(([c,n])=>`<label><input type="checkbox" value="${c}" checked> <span class="sw" style="background:${COL[c]}"></span>${esc(n)}</label>`).join("");
const on=()=>new Set([...document.querySelectorAll("#ser input:checked")].map(i=>i.value));
function fold(s){return String(s).normalize("NFKC").toLowerCase()}
function rows(){const q=fold($("#q").value.trim()),sub=$("#sub").value,ser=on();
 return D.items.filter(i=>ser.has(V[i.s].ser)&&(!sub||i.sub.includes(sub))&&(!q||fold(i.t+" "+i.e+" "+i.c).includes(q))&&(!pick||(i.s===pick[0]&&i.sub.includes(pick[1]))))}
function cov(){const ser=on(),vs=D.vols.filter(v=>ser.has(v.ser)&&D.items.some(i=>i.s===v.s));
 let h=`<table><thead><tr><th class="sub"></th>${vs.map(v=>`<th title="${esc(v.title)}">${esc(v.ed)}</th>`).join("")}</tr></thead><tbody>`;
 D.subs.forEach(s=>{h+=`<tr><th class="sub">${esc(s)}</th>`+vs.map(v=>{const n=D.items.filter(i=>i.s===v.s&&i.sub.includes(s)).length;
  return n?`<td class="c${pick&&pick[0]===v.s&&pick[1]===s?" sel":""}" data-s="${v.s}" data-u="${esc(s)}" title="${esc(v.title)} — ${esc(s)}: ${n}"><b style="background:${COL[v.ser]}">${n}</b></td>`:`<td class="z">·</td>`}).join("")+"</tr>"});
 $("#cov").innerHTML=h+"</tbody></table>"}
function item(i){const v=V[i.s];return `<div class="it"><div class="v"><b>${esc(v.ed)}</b><span class="sw" style="background:${COL[v.ser]}"></span>${esc(SER[v.ser])}</div><div><a class="tt" href="../book/${i.s}/#${encodeURIComponent(i.id)}">${esc(i.t)}</a>${i.e&&i.e!==i.t?`<div class="en">${esc(i.e)}</div>`:""}<div class="meta">${esc(v.title)} · ${esc(i.c)}${i.pp?` · p. ${esc(i.pp)}`:""}${i.q?` · <span class="q">${i.q} unreadable cell${i.q>1?"s":""}</span>`:""}</div></div></div>`}
function render(){cov();const R=rows();let h="";
 if(pick)h+=`<p class="covn">Showing ${esc(V[pick[0]].title)} — ${esc(pick[1])}. <a href="#" id="clr">Show all</a></p>`;
 if($("#ord").value==="sub"){D.subs.forEach(s=>{const L=R.filter(i=>i.sub.includes(s));if(L.length)h+=`<h2>${esc(s)} <small>${L.length}</small></h2>`+L.map(item).join("")})}
 else if($("#ord").value==="year"){[...new Set(D.vols.map(v=>v.y))].forEach(y=>{const L=R.filter(i=>V[i.s].y===y);if(L.length)h+=`<h2>${y||"Undated"} <small>${L.length} · edition year</small></h2>`+L.map(item).join("")})}
 else{D.vols.forEach(v=>{const L=R.filter(i=>i.s===v.s);if(L.length)h+=`<h2>${esc(v.title)} <small>${L.length}</small></h2>`+L.map(item).join("")})}
 $("#out").innerHTML=h||'<p class="empty">No tables match.</p>';const c=$("#clr");if(c)c.onclick=e=>{e.preventDefault();pick=null;render()}}
document.addEventListener("input",e=>{if(e.target.closest(".ctl,#ser"))render()});
$("#cov").addEventListener("click",e=>{const td=e.target.closest("td.c");if(!td)return;pick=pick&&pick[0]===td.dataset.s&&pick[1]===td.dataset.u?null:[td.dataset.s,td.dataset.u];render();$("#out").scrollIntoView({behavior:"smooth",block:"start"})});
render();
</script>
</body></html>
"""


def main():
    from build_tags import load_assignments, book_tags, build_tag_pages
    tag_assignments = load_assignments()
    os.makedirs(os.path.join(HERE, "data"), exist_ok=True)
    cards, pages = [], []
    for b in BOOKS:
        b["_dir_n"] = build_directory(b)
        b["_chron_n"] = build_chronology(b)
        for key, kind in (("_dir_n", "directory"), ("_chron_n", "chronology")):
            committed = os.path.join(HERE, "data", f'{b["slug"]}-{kind}.json')
            if not b[key] and os.path.exists(committed):  # folder not on this machine: keep the committed page
                with open(committed, encoding="utf-8") as fh:
                    b[key] = len(json.load(fh))
        tables = load(b)
        if not tables:  # book folder not on this machine: keep the committed data rather than dropping the book
            committed = os.path.join(HERE, "data", b["slug"] + ".json")
            if os.path.exists(committed):
                with open(committed, encoding="utf-8") as fh:
                    tables = json.load(fh)
                for t in tables:
                    t["file"] = t["id"] + ".json"
                print(f"{b['slug']}: no tables in {book_dir(b)}; using committed data/{b['slug']}.json")
        for t in tables:
            t["scans"] = scan_links(b, t)
        add_english(b, tables)
        add_maplinks(b, tables)
        n, c = len(tables), cells(tables)
        chapters = len({t.get("chapter") for t in tables})
        if tables:
            clean = [{k: v for k, v in t.items() if k not in ("file",)} for t in tables]
            with open(os.path.join(HERE, "data", b["slug"] + ".json"), "w", encoding="utf-8") as fh:
                json.dump(clean, fh, ensure_ascii=False, indent=1)
            pages.append((b, clean, n, c))
        b["_qstat"] = qstat_html(tables)
        cards.append((b, n, c, chapters))
        print(f"{b['slug']}: {n} tables, {c:,} cells")
    xl = crosslinks({b["slug"]: clean for b, clean, n, c in pages})
    for b, clean, n, c in pages:
            os.makedirs(os.path.join(HERE, "book", b["slug"]), exist_ok=True)
            data = json.dumps(clean, ensure_ascii=False).replace("</", "<\\/")
            doc = (TEMPLATE.replace("__MODEL__", b.get("model", "Opus 5.5")).replace("__DATA__", data).replace("__DIRCARDS__", dir_cards(b)).replace("__DIRSEC__", dir_section(b, clean)).replace("__PINYIN__", json.dumps(b.get("dir_pinyin", {}), ensure_ascii=False)).replace("__COUNT__", str(n))
                   .replace("__CHEN__", json.dumps(b.get("_chen") or {}, ensure_ascii=False))
                   .replace("__TAGDATA__", json.dumps(book_tags(b["slug"], tag_assignments), ensure_ascii=False).replace("<", "\\u003c"))
                   .replace("__XL__", json.dumps(xl[b["slug"]], ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__FINDERS__", json.dumps(finder_links(b["slug"]), ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__HIDEIMG__", "true" if b.get("hide_images") else "false")
                   .replace("__KANJINUMS__", open(os.path.join(SCRIPTS, "kanji_nums.js"), encoding="utf-8").read().replace("if(typeof module!==\"undefined\")module.exports=KN;\n", ""))
                   .replace("__KNFULL__", json.dumps(b.get("kanji_full") or False))
                   .replace("__ORIG__", json.dumps(orig_link(b), ensure_ascii=False))
                   .replace("__CITE__", json.dumps(citation(b), ensure_ascii=False))
                   .replace("__PTOC__", json.dumps(printed_toc(b, clean), ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__MARKED__", "true" if b.get("blank_marking") else "false")
                   .replace("__CHARTIDS__", json.dumps(chart_ids(b, clean)))
                   .replace("__CHARTJS__", '<script src="../../charts.js" charset="utf-8"></script>\n' if chart_ids(b, clean) else "")
                   .replace("__QSTAT__", json.dumps(b.get("_qstat", ""), ensure_ascii=False))
                   .replace("__XLSX__", f' · <a href="../../{dl(b["slug"], "tables.xlsx")}" style="color:inherit" download>Excel</a>' if dl(b["slug"], "tables.xlsx") else "")
                   .replace("__CELLS__", f"{c:,}").replace("__BOOK__", html.escape(b["title"]))
                   .replace("__SLUG__", b["slug"]).replace("__SOURCE__", "LLM-transcribed")
                   .replace("__DIRLINK__", ('<a class="dirbtn" href="directory.html">Directories</a>' if b.get("_dir_n") else "")
                            + ('<a class="dirbtn" href="chronology.html">Chronologies</a>' if b.get("_chron_n") else "")
                            + (f'<button class="aboutbtn" onclick="document.getElementById(\'about\').showModal()">About</button>'
                               f'<dialog id="about" onclick="if(event.target===this)this.close()"><h3>{html.escape(b["title"])}</h3>{f'<div class="pub">{html.escape(b["subtitle"])}</div>' if b.get("subtitle") else ""}<div class="pub">{html.escape((b["author"] + "; ") if b.get("author") else "")}{html.escape(b["publisher"])}</div>'
                               f'<p>{html.escape(b["gaps"])}</p>{"" if b.get("blank_marking") else BLANK_NOTE}<p class="ver">{html.escape(version_line())}</p><form method="dialog"><button>Close</button></form></dialog>' if b.get("gaps") else "")))
            with open(os.path.join(HERE, "book", b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
    build_tag_pages(pages)
    build_with_maps(pages, tag_assignments)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        nb, nt = sum(1 for b, n, c, ch in cards), sum(n for b, n, c, ch in cards)
        from about_text import INTRO, ABOUT
        allstat = f"{nb} volumes, with a total of {nt:,} tables"
        intro = ('<details class="introbox" id="introbox" open><summary>Introduction</summary>' + INTRO + '</details>'
                 '<script>try{if(localStorage.getItem("homeintro")==="shut")document.getElementById("introbox").open=false}catch(e){}'
                 'document.getElementById("introbox").addEventListener("toggle",e=>{try{localStorage.setItem("homeintro",e.target.open?"open":"shut")}catch(x){}})</script>')
        home = landing(cards).replace("__TOPICMENU__", intro + filter_bar(cards) + f'<p class="allstat" id="allstat" data-txt="{allstat}">{allstat}</p>').replace("__VERSION__", html.escape(version_line()))   # site totals; the topic menu was removed (user, 2026-10-24)
        fh.write(home)
    # about.html: the home page's header and footer around the author's About text (build/about_text.py). The section
    # links of the header point back to the home page; the sort and view tools, which act on the list of books, go.
    head, rest = home.split("<main>", 1)
    head = re.sub(r'<nav class="jump" id="jump">(.*?)</nav>', lambda m: '<nav class="jump" id="jump">' + m.group(1).replace('href="#', 'href="index.html#') + "</nav>", head, flags=re.S)
    head = re.sub(r'<span class="tools">.*?id="viewbtn".*?</span></span>', "", head, flags=re.S)
    head = head.replace("<title>Old Tables of East Asia</title>", "<title>About · Old Tables of East Asia</title>")
    foot = rest[rest.index("<footer>"):]
    with open(os.path.join(HERE, "about.html"), "w", encoding="utf-8") as fh:
        fh.write(head + "<main>" + ABOUT + foot)
    # figures/: the finder pages (build/finders/: Population …) and their hub, from the data/*.json just written, their
    # table specs and the frozen gazetteer; they copy the header and footer of index.html
    sys.path.insert(0, os.path.join(SCRIPTS, "finders"))
    import build_all as finders_build
    finders_build.main()
    books = [{"slug": b["slug"], "title": b["title"], "dir": bool(b.get("_dir_n")), "chron": bool(b.get("_chron_n")),
              "g": group_of(b), "y": years_of(b), "sc": b.get("scan")} for b, n, c, ch in cards if n]
    with open(os.path.join(HERE, "search.html"), "w", encoding="utf-8") as fh:
        fh.write(SEARCH.replace("__BOOKS__", json.dumps(books, ensure_ascii=False))
                 .replace("__FINDERS_IDX__", json.dumps(finder_search_list(), ensure_ascii=False)))


# What a table's map is drawn by, from the payload's `units` (MAPLINK_SPEC): the with-maps page filters on it.
# "admin" = prefectures, provinces and the South Seas island groups; "city" = points; "other" = whole countries
# or the empire's parts. A units value not listed here is "other" and the build says so, so a new kind is seen.
MAP_KINDS = {"prefecture": "admin", "china-province": "admin", "korea-province": "admin", "manchukuo-province": "admin",
             "nanyo-group": "admin", "city": "city", "territory": "other", "country": "other"}


def build_with_maps(pages, assignments):
    """topics/with-maps.html: every table with a View as Map link, searchable by title or tag, filtered by area and by
    what the map draws (provinces, cities, other), sortable.

    The map addresses are NOT in the page. Each carries the table's figures, compressed, so together they were 88% of a
    4.3 MB page (2.9 MB gzipped) that showed nothing until all of it had arrived; the list without them is about 60 KB
    gzipped. They go to topics/maps/<book>.json instead, and the button links to topics/map.html?b=<book>&t=<id>,
    which fetches that one small file and replaces itself with the map. A real link keeps middle-click, open in new
    tab and copy link working, which a fetch-then-window.open on click would not (popup blockers)."""
    import maplinks as M
    voc = json.load(open(os.path.join(HERE, "data", "tags", "vocabulary.json"), encoding="utf-8"))
    lab = {e["id"]: e["label"] for kind in ("topics", "tags") for e in voc[kind]}
    dates = {(c["book"], c["table"]): str(c.get("date") or "")[:4] for c in M.load_config().get("tables", [])}
    items, shards, unknown = [], {}, set()
    for b, clean, n, c in pages:
        for t in clean:
            if not t.get("map"):
                continue
            row = assignments.get(f'{b["slug"]}:{t["id"]}', {})
            d = dates.get((b["slug"], t["id"])) or str(years_of(b)[0] or "")
            units = M.decode(t["map"]).get("units") or "prefecture"
            if units not in MAP_KINDS:
                unknown.add(units)
            items.append({"s": b["slug"], "id": t["id"], "b": b["title"], "g": group_of(b), "d": int(d) if d.isdigit() else 0,
                          "u": MAP_KINDS.get(units, "other"),
                          "t": (f"Table {t['table_no']}. " if t.get("table_no") else "") + (t.get("title") or ""),
                          "e": (t.get("en") or {}).get("t", ""), "tg": [lab[x] for x in row.get("topics", []) + row.get("tags", []) if x in lab]})
            shards.setdefault(b["slug"], {})[t["id"]] = t["map"]
    if unknown:
        print(f"with-maps: map units not in MAP_KINDS, listed as Other: {', '.join(sorted(unknown))}")
    areas = [[g, n] for g, n in (("japan", "Japan"), ("china", "China"), ("korea", "Korea"), ("taiwan", "Taiwan"), ("manchuria", "Manchuria"),
                                 ("south-seas", "South Seas"), ("other", "Other")) if any(i["g"] == g for i in items)]
    kinds = [[k, n] for k, n in (("admin", "By province or prefecture"), ("city", "By city"), ("other", "Other (countries, the empire’s parts)"))
             if any(i["u"] == k for i in items)]
    sd = os.path.join(HERE, "topics", "maps")
    os.makedirs(sd, exist_ok=True)
    for slug, links in shards.items():
        with open(os.path.join(sd, slug + ".json"), "w", encoding="utf-8") as fh:
            json.dump(links, fh, ensure_ascii=False, separators=(",", ":"))
    for f in os.listdir(sd):   # a book that no longer has any map link
        if f.endswith(".json") and f[:-5] not in shards:
            os.remove(os.path.join(sd, f))
    with open(os.path.join(HERE, "topics", "map.html"), "w", encoding="utf-8") as fh:
        fh.write(MAP_REDIRECT)
    data = json.dumps({"items": items, "areas": areas, "kinds": kinds}, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    doc = WITH_MAPS.replace("__DATA__", data).replace("__N__", f"{len(items):,}")
    with open(os.path.join(HERE, "topics", "with-maps.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"topics/with-maps.html: {len(items)} tables, {len(doc.encode()) // 1024} KB; map links in topics/maps/ ({len(shards)} books)")


# topics/map.html?b=<book>&t=<table id>[&map=gh]: fetch that book's map links and go to the table's map. The address
# replaces this page in the history, so Back returns to the list.
MAP_REDIRECT = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Opening the map…</title><meta name="robots" content="noindex"><link rel="stylesheet" href="../tags.css"></head>
<body class="tag-browser"><main><p id="msg" class="lede">Opening the map…</p></main>
<script>
(async()=>{const p=new URLSearchParams(location.search),b=p.get("b")||"",t=p.get("t")||"",msg=document.getElementById("msg");
const L="https://froginawell.net/reference/japanese-empire/",G="https://kmlawson.github.io/japanese-empire-student-map/";
const o=p.get("map"),gh=o?o==="gh":/github\.io$/.test(location.hostname);
try{if(!/^[\w.-]+$/.test(b))throw 0;const r=await fetch("maps/"+b+".json");if(!r.ok)throw 0;const u=(await r.json())[t];
if(typeof u!=="string"||!u.startsWith(L))throw 0;location.replace(gh?u.replace(L,G):u)}
catch(e){msg.textContent="";const a=document.createElement("a");a.href=/^[\w.-]+$/.test(b)?"../book/"+b+"/#"+encodeURIComponent(t):"with-maps.html";
a.textContent="Open the table";msg.append("This map link could not be found. ",a,".")}})();
</script></body></html>
"""


WITH_MAPS = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Tables with Map</title><link rel="stylesheet" href="../tags.css">
<style>
.ctl{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:4px 0 14px}.ctl input,.ctl select{font:14px system-ui,sans-serif;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:5px}
#q{flex:1 1 260px;min-width:0}#n{color:var(--muted);font:13px system-ui,sans-serif;margin:0 0 10px}
.mi{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:10px 14px;margin:0 0 8px;display:flex;gap:14px;align-items:flex-start}
.mi .tx{flex:1;min-width:0}.mi h3{font-size:17px;font-weight:normal;margin:0 0 2px;border:0;padding:0}.mi h3 a{color:var(--ink);text-decoration:none}.mi h3 a:hover{text-decoration:underline}
.mi .en{color:var(--muted);font-size:14px;margin:0 0 3px}.mi .bk{font:13px system-ui,sans-serif;color:var(--muted)}.mi .bk a{color:var(--accent)}
.mi .tags{display:flex;flex-wrap:wrap;gap:4px;margin-top:6px}.mi .tags span{font:12px/1.3 system-ui,sans-serif;border:1px solid var(--line);border-radius:10px;padding:2px 8px;cursor:pointer}.mi .tags span:hover{border-color:var(--accent)}
.mi .go{white-space:nowrap;align-self:center;display:inline-block;padding:6px 11px;border-radius:5px;background:var(--accent);color:var(--accent-ink);text-decoration:none;font:600 13px system-ui,sans-serif}
.mi{content-visibility:auto;contain-intrinsic-size:auto 96px}
#more{color:var(--muted);font:13px system-ui,sans-serif;padding:6px 0 20px}
@media(max-width:600px){.mi{flex-direction:column;gap:6px}.mi .go{align-self:flex-start}}
</style></head><body class="tag-browser">
<header class="band"><div><nav class="navigation"><a href="../index.html">← All books</a> · <a href="index.html">All topics and tags</a></nav><h1>Tables with Map</h1></div></header>
<main><p class="lede">The __N__ tables whose figures can be opened on the Japanese Empire map. Search by title or tag, choose an area or what the map shows, and sort.</p>
<div class="ctl"><input id="q" type="search" placeholder="Search titles and tags…" aria-label="Search titles and tags"><select id="area" aria-label="Area"><option value="">All areas</option></select>
<select id="kind" aria-label="What the map shows"><option value="">Provinces, cities and other</option></select>
<select id="sort" aria-label="Sort"><option value="d">Date, earliest first</option><option value="-d">Date, latest first</option><option value="az">Title A–Z</option></select></div>
<p id="n"></p><div id="out"></div><p id="more" hidden>Loading more tables…</p></main>
<script>
const D=__DATA__;const $=s=>document.querySelector(s);const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let mapQ="";try{const o=new URLSearchParams(location.search).get("map");if(o)mapQ="&map="+encodeURIComponent(o)}catch(e){}
D.areas.forEach(([g,n])=>$("#area").insertAdjacentHTML("beforeend",`<option value="${g}">${esc(n)}</option>`));
D.kinds.forEach(([k,n])=>$("#kind").insertAdjacentHTML("beforeend",`<option value="${k}">${esc(n)}</option>`));
const fold=s=>String(s).toLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g,"");
D.items.forEach(i=>i.k=fold([i.t,i.e,i.b,...i.tg].join(" ")));
const row=i=>`<div class="mi"><div class="tx"><h3><a href="../book/${i.s}/#${i.id}">${esc(i.t)}</a></h3>${i.e?`<p class="en">${esc(i.e)}</p>`:""}<div class="bk"><a href="../book/${i.s}/">${esc(i.b)}</a>${i.d?` · ${i.d}`:""}</div>${i.tg.length?`<div class="tags">${i.tg.map(x=>`<span data-t="${esc(x)}">${esc(x)}</span>`).join("")}</div>`:""}</div><a class="go" href="map.html?b=${encodeURIComponent(i.s)}&amp;t=${encodeURIComponent(i.id)}${esc(mapQ)}" target="_blank" rel="noopener">View as Map ↗</a></div>`;
// The first rows are drawn at once and the rest in batches after, so a long list shows straight away; a new search
// abandons the batches of the old one (gen).
const FIRST=150,BATCH=400;let gen=0;
function drawRest(r,at,g){if(g!==gen)return;if(at>=r.length){$("#more").hidden=true;return}
$("#out").insertAdjacentHTML("beforeend",r.slice(at,at+BATCH).map(row).join(""));setTimeout(()=>drawRest(r,at+BATCH,g),0)}
function render(){const q=fold($("#q").value.trim()).split(/\s+/).filter(Boolean),a=$("#area").value,u=$("#kind").value,so=$("#sort").value;
let r=D.items.filter(i=>(!a||i.g===a)&&(!u||i.u===u)&&q.every(w=>i.k.includes(w)));
const az=(x,y)=>(x.e||x.t).localeCompare(y.e||y.t);
r.sort(so==="az"?az:so==="-d"?(x,y)=>y.d-x.d||az(x,y):(x,y)=>x.d-y.d||az(x,y));
$("#n").textContent=`${r.length.toLocaleString()} of ${D.items.length.toLocaleString()} tables`;
const g=++gen;$("#out").innerHTML=r.slice(0,FIRST).map(row).join("");$("#more").hidden=r.length<=FIRST;
if(r.length>FIRST)setTimeout(()=>drawRest(r,FIRST,g),0);
try{const p=new URLSearchParams();if($("#q").value)p.set("q",$("#q").value);if(a)p.set("a",a);if(u)p.set("u",u);if(so!=="d")p.set("s",so);history.replaceState(null,"","#"+p)}catch(e){}}
try{const p=new URLSearchParams(location.hash.slice(1));$("#q").value=p.get("q")||"";if(p.get("a"))$("#area").value=p.get("a");if(p.get("u"))$("#kind").value=p.get("u");if(p.get("s"))$("#sort").value=p.get("s")}catch(e){}
$("#q").addEventListener("input",render);$("#area").addEventListener("change",render);$("#kind").addEventListener("change",render);$("#sort").addEventListener("change",render);
$("#out").addEventListener("click",e=>{const t=e.target.closest("[data-t]");if(t){$("#q").value=t.dataset.t;render();scrollTo({top:0})}});
render();
</script></body></html>
"""


def group_of(b):
    """Home-page section of a book: japan, china, korea, taiwan, manchuria, south-seas or other."""
    return b.get("group") or next((g for g in ("japan", "china", "korea", "taiwan") if b["slug"].startswith(g)), "manchuria" if b["slug"].startswith("manch") else "other")


def years_of(b):
    """First and last year an edition covers, from the year in its title (1926-7 -> 1926, 1927); None if no year."""
    m = re.search(r"(\d{4})(?:\s*[-–]\s*(\d{1,4}))?", b["title"])
    if not m:
        return None, None
    y1, tail = int(m.group(1)), m.group(2)
    y2 = int(str(y1)[:4 - len(tail)] + tail) if tail else y1
    return y1, max(y1, y2)


def citation(b):
    """The volume's citation for the top of its page: author (books with a personal author, whose site title then
    loses the year the site adds), title, publication line as listed, and the original's address."""
    title = b["title"]
    if b.get("author"):
        title = re.sub(r"\s+(1[89]\d\d)(-\d+)?$", "", title)
    return {"a": b.get("author") or "", "t": title, "p": b["publisher"], "u": b.get("item") or ""}


def orig_link(b):
    """The whole original book online (shown on the book's contents page), with the site's name; None if not online."""
    u = b.get("item")
    if not u:
        return None
    host = re.sub(r"^https?://(www\.)?", "", u).split("/")[0]
    names = {"archive.org": "the Internet Archive", "dl.ndl.go.jp": "the National Diet Library Digital Collections",
             "ageconsearch.umn.edu": "AgEcon Search"}
    return {"u": u, "l": names.get(host, host)}


def page_urls(b, tables):
    """Printed page -> scan URL for a book, from its tables' printed pages and scan images: a page with no table
    of its own is placed by counting on from the nearest earlier page that has one (one scan leaf per page).
    Books whose appendices restart the page numbering are split into runs where the numbers fall back; the
    returned url(page, run) looks only at the given run."""
    lm = leafmap(b) or {}

    def key(im):
        m = re.match(r"p(\d)-(\d+)$", im) or re.match(r"p()(\d+)$", im)
        if m and im not in lm:
            return (int(m.group(1) or 0), int(m.group(2)))
        v = lm.get(im)
        return tuple(v) if isinstance(v, list) else (0, v) if isinstance(v, int) else None

    pts = []
    for t in tables:
        im = (t.get("images") or [t.get("image")])[0]
        m = re.match(r"\s*(\d+)", str((t.get("printed_pages") or [""])[0]))
        if im and m and key(im) is not None:
            pts.append((key(im), int(m.group(1)), im))
    # Group the anchors by offset (scan position minus printed page): the main text drifts slowly as plates are
    # added, an appendix with its own numbering jumps by hundreds, and a stray misread page stands alone.
    def pos(k):
        return k[0] * 100000 + k[1]
    pts.sort(key=lambda x: pos(x[0]) - x[1])
    runs, prev = [], None
    for k, pg, im in pts:
        o = pos(k) - pg
        if prev is None or o - prev > 30:
            runs.append([])
        runs[-1].append((pg, im)); prev = o
    runs = [r for r in runs if len(r) >= 3]
    # printed pages per scan leaf: 1 for a page-by-page scan, 2 where each photo shows an open spread
    spans = sorted((pg2 - pg1) / (pos(k2) - pos(k1)) for (k1, pg1, _), (k2, pg2, _) in zip(sorted(pts, key=lambda x: pos(x[0])), sorted(pts, key=lambda x: pos(x[0]))[1:])
                   if pos(k2) - pos(k1) >= 3 and pg2 > pg1)
    per_leaf = 2 if spans and spans[len(spans) // 2] > 1.5 else 1
    if runs:  # the main text is the biggest group; runs after it are appendices numbered afresh
        main = max(range(len(runs)), key=lambda i: len(runs[i]))
        part = lambda r: (re.match(r"p(\d)-", r[0][1]) or [None, None])[1]
        # a book scanned as several files keeps the earlier files' runs (they are the main text, not front matter)
        # ... or all of them, when no two runs share a printed page: one numbering, scanned out of order
        sp = sorted((min(r)[0], max(r)[0]) for r in runs)
        one_seq = all(a[1] < b[0] for a, b in zip(sp, sp[1:]))
        runs = [r for i, r in enumerate(runs) if i >= main or one_seq or (part(r) is not None and part(r) != part(runs[main]))]

    def url(page, run=0):
        if not b.get("scan") or run >= len(runs):
            return None
        # this run, plus runs whose printed pages do not overlap it (a book split into several scan files)
        lo, hi = min(runs[run])[0], max(runs[run])[0]
        pool = [a for i, r in enumerate(runs) if i == run or not lo <= sorted(r)[len(r) // 2][0] <= hi for a in r]
        below = [a for a in pool if a[0] <= page]
        above = [a for a in pool if a[0] > page]
        if below and page - max(below)[0] <= 250:  # count on from the last page with a table
            pg, im = max(below)
        elif above and min(above)[0] - page <= 40:  # or back from the next one
            pg, im = min(above)
        else:
            return None
        d = round((page - pg) / per_leaf)
        url.last = (key(im)[0], key(im)[1] + d) if key(im) is not None else None  # scan position, for placing tables
        mp = re.match(r"p(\d)-(\d+)$", im)
        if mp:
            return b["scan"].format(part=int(mp.group(1)), partname=b.get("scan_parts", {}).get(int(mp.group(1)), ""), leaf=int(mp.group(2)) + d)
        mp = re.match(r"p(\d+)$", im)
        if mp and im not in lm:
            return b["scan"].format(leaf=int(mp.group(1)) + d)
        v = lm.get(im)
        if isinstance(v, list):
            return b["scan"].format(partname=b["scan_parts"][v[0]], leaf=v[1] + d)
        if isinstance(v, int):
            return b["scan"].format(leaf=v + d)
        return None
    url.key, url.last = key, None
    return url


def kanji_int(t):
    """一〇〇 (digit by digit) or 百二十 (with unit characters) -> int."""
    d = {c: i for i, c in enumerate("〇一二三四五六七八九")}; d["零"] = 0
    if not re.search(r"[十百千]", t):
        return int("".join(str(d[c]) for c in t))
    n = cur = 0
    for c in t:
        if c in d:
            cur = d[c]
        else:
            n += (cur or 1) * {"十": 10, "百": 100, "千": 1000}[c]; cur = 0
    return n + cur


def printed_toc(b, tables=()):
    """The book's printed table of contents, each entry linked to its scan page: [{"l": level, "t": title, "p": page, "u": url}].
    Read from <book>/_work/toc.json, or ../_toc/<slug>/toc.json for books finished before their contents were
    transcribed; an entry's scan page is its "leaf" (added by _pipeline/toc_leaves.py) or else found from its
    printed page via the book's tables (page_urls). Kept in data/<slug>-toc.json, used once the work folder is gone."""
    saved = os.path.join(HERE, "data", b["slug"] + "-toc.json")
    f = next((x for x in (os.path.join(book_dir(b), "_work", "toc.json"), os.path.join(ROOT, "_toc", b["slug"], "toc.json"))
              if os.path.exists(x)), None)
    if not f:
        return json.load(open(saved, encoding="utf-8")) if os.path.exists(saved) else []
    by_page = page_urls(b, tables)
    out, run, top, where = [], 0, 0, []
    for e in json.load(open(f, encoding="utf-8"))["entries"]:
        sl = scan_links(b, {"image": e["leaf"]}) if b.get("scan") and e.get("leaf") else []
        u = sl[0]["url"] if sl else None
        lf = e.get("leaf") or e.get("found_leaf")
        at = by_page.key(lf) if lf else None
        m = re.match(r"\s*(\d+)", str(e.get("page", "")))
        if m and "?" not in str(e.get("page")) and not e.get("no_scan"):  # a half-read page number would send the link astray; no_scan: page missing from the scan
            pg = int(m.group(1))
            if pg < top - 50:  # page numbering starts again (appendices)
                run, top = run + 1, 0
            top = max(top, pg)
            if not u or at is None:
                by_page.last = None
                uu = by_page(pg, run)
                u = u or uu
                at = at if at is not None else by_page.last
        lv = e.get("level", 1)
        parent = next((o for o in reversed(out) if o["l"] < lv), None)
        if not u and not e.get("page") and parent and parent["u"]:  # no page printed: open its chapter's first page
            out.append({"l": lv, "t": e["title"], "p": "", "u": parent["u"], "c": 1}); where.append(None)
            continue
        out.append({"l": lv, "t": e["title"], "p": e.get("page", ""), "u": u}); where.append(at)
    # "Show tables": a numbered table goes under the contents entry with its number ("76 死亡者年齡別"); any other
    # table under the entry that starts nearest before it in the scan
    byno = {}
    for i, o in enumerate(out):
        m = re.match(r"\s*(?:No\.\s*|Table\s+)?([國]?\d+[A-Za-z]?)[\s.、]", o["t"])
        k = m.group(1) if m else None
        mk = re.match(r"\s*第([〇零一二三四五六七八九十百千]+)表", o["t"])  # 第一〇〇表 / 第百二十表
        if mk:
            k = str(kanji_int(mk.group(1)))
        if k and o["l"] >= 2:
            byno.setdefault(k, []).append(i)
    for t in tables:
        im = (t.get("images") or [t.get("image")])[0]
        k = by_page.key(im) if im else None
        hit = byno.get(str(t.get("table_no") or "").strip(), [])
        if len(hit) == 1:
            best = hit[0]
        elif k is None:
            continue
        else:
            best = max((i for i, w in enumerate(where) if w is not None and w <= k), key=lambda i: (where[i], i), default=None)
        if best is not None:
            lab = (f"{t['table_no']}. " if t.get("table_no") else "") + (t.get("title") or "")
            out[best].setdefault("k", []).append([t["id"], lab if len(lab) <= 90 else lab[:89] + "…"])
    with open(saved, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    return out


# Directory entries whose text runs "label: value" items together get them split into fields ("f", one per line under a
# bold label) and any leading text ("h", shown after the name). "t" keeps the whole text for search. Modes: "dot" (items
# separated by " · "), "semi" (by "; "), "prose" (sentences, a label being one to four words without a full stop starting
# a sentence, plus the abbreviated labels in DOT_LABELS). Only entries with two or more labels are split.
DIR_FIELDS = {"japan-kanko-1941": "dot", "japan-hyakkaten-1941": "dot", "china-1923": "semi", "china-1925-6": "semi",
              "china-1924-5": "prose", "manchoukuo-1942": "prose", "japan-manchoukuo-1934": "prose",
              "japan-manchoukuo-1936": "prose", "japan-manchoukuo-1938": "prose", "japan-manchoukuo-1939": "prose",
              "japan-1929": "prose", "china-1944": "prose"}
DOT_LABELS = ["Tel.", "Bank Ref.", "Cable Add."]
PROSE_LABEL = re.compile(r"(?:^|(?<=[.;)] ))(" + "|".join(re.escape(x) for x in DOT_LABELS) +
                         r"|[A-Z][A-Za-z'&/-]*(?: [A-Za-z'&/-]+){0,3})\s?[:：](?:\s|[—–])")


def split_fields(entries, mode):
    """In "prose" a label must recur (3+ times in the book) and must not be followed by "b. …" or nothing, which is an
    occupation printed with a colon ("Lieutenant-General: b. 1885"), not a field."""
    def prose(t, ok):
        ms = [m for m in PROSE_LABEL.finditer(t) if ok is None or m.group(1) in ok]
        out = []
        for i, m in enumerate(ms):
            end = ms[i + 1].start() if i + 1 < len(ms) else len(t)
            v = t[m.end():end].strip().lstrip("—–").strip().rstrip(";").strip()
            out.append((m, v))
        return out
    ok = None
    if mode == "prose":
        from collections import Counter
        cnt = Counter(m.group(1) for e in entries if not e.get("f") for m, v in prose(e.get("t") or "", None)
                      if v and not v.startswith("b. "))
        ok = {k for k, c in cnt.items() if c >= 3}
    n = 0
    for e in entries:
        t = e.get("t") or ""
        if e.get("f") or e.get("nj") is not None or not t:
            continue
        head, f = "", []
        if mode in ("dot", "semi"):
            for seg in t.split(" · " if mode == "dot" else "; "):
                m = re.match(r"^\s*([^:：]{1,24}?)\s*[:：]\s*(.*)$", seg, re.S)
                if m and m.group(2):
                    f.append([m.group(1), m.group(2).strip()])
                elif f:
                    f.append(["", seg.strip()])
                else:
                    head += (" · " if head else "") + seg.strip()
        else:
            ps = [(m, v) for m, v in prose(t, ok) if v and not v.startswith("b. ")]
            ps = prose(t, {m.group(1) for m, v in ps}) if ps else []   # re-cut so a dropped label stays in the text
            head = t[:ps[0][0].start()].strip() if ps else t
            f = [[m.group(1), v] for m, v in ps]
        if sum(1 for k, _ in f if k) >= 2:
            e["f"] = f
            if head:
                e["h"] = head
            n += 1
    return n


def added_dates():
    """build/added_dates.json: {slug: ISO time the book's data first went into git}. A book not yet listed is
    stamped with the current time on its first build, so the record keeps itself up to date."""
    f = os.path.join(SCRIPTS, "added_dates.json")
    d = json.load(open(f)) if os.path.exists(f) else {}
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    new = {b["slug"]: now for b in BOOKS if b["slug"] not in d}
    if new:
        d.update(new); json.dump(dict(sorted(d.items())), open(f, "w"), indent=1)
    return d


# Publication year(s) of a book for the home page's From/To filter: an explicit entry here, else every Western year in
# the publisher line (a range when it names several), else a 明治/大正/昭和 era year there. The filter is by publication,
# not by the year in the title or the year surveyed.
PUB_YEAR = {"gyosei-nenpo-1929": 1930, "china-peking-1921": 1921, "china-1912": 1912, "china-1922": 1921, "china-1929-30": 1929}
ERA = {"明治": 1867, "大正": 1911, "昭和": 1925}


def kanji_int(t):
    if t.isdigit():
        return int(t)
    if t == "元":
        return 1
    d = {c: i for i, c in enumerate("〇一二三四五六七八九")}
    if "十" in t:
        a, _, b = t.partition("十")
        return (d.get(a, 1) if a else 1) * 10 + (d.get(b, 0) if b else 0)
    n = 0
    for c in t:
        if c not in d:
            return None
        n = n * 10 + d[c]
    return n


def pub_years(b):
    if b["slug"] in PUB_YEAR:
        y = PUB_YEAR[b["slug"]]
        return (y, y)
    p = b.get("publisher", "")
    ys = [int(y) for y in re.findall(r"(?<!\d)(1[89]\d\d)(?!\d)", p)]
    if not ys:
        for era, num in re.findall(r"(明治|大正|昭和)\s*([元〇一二三四五六七八九十\d]+)年", p):
            n = kanji_int(num)
            if n:
                ys.append(ERA[era] + n)
    return (min(ys), max(ys)) if ys else None


def filter_bar(cards):
    names = {"japan": "Japan", "china": "China", "korea": "Korea", "taiwan": "Taiwan", "manchuria": "Manchuria", "south-seas": "South Seas Mandate", "other": "Other"}
    have = {group_of(b) for b, n, c, ch in cards}
    opts = "".join(f'<option value="{g}">{n}</option>' for g, n in names.items() if g in have)
    tip = "Years are the year the volume was published, not the year in its title or the year it surveys."
    return ('<div class="fbar" id="fbar"><label>Filter: <input id="fq" type="search" placeholder="title" aria-label="Filter by volume title"></label>'
            '<span class="fyears"><label>From: <input id="fy0" type="text" inputmode="numeric" maxlength="4" placeholder="year" aria-label="Published from (year)"></label>'
            '<label>To: <input id="fy1" type="text" inputmode="numeric" maxlength="4" placeholder="year" aria-label="Published to (year)"></label>'
            f'<button class="itip" id="fyi" type="button" aria-expanded="false" aria-controls="ftip" title="{tip}" aria-label="About the year filter">i</button></span>'
            f'<label>Section: <select id="fsec" aria-label="Section"><option value="">All</option>{opts}</select></label>'
            f'<span class="ftip" id="ftip" hidden>{tip}</span></div>')


def landing(cards):
    added = added_dates()
    items = []
    for b, n, c, ch in cards:
        stat = (f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "" if b.get("dir_only") else "<i>transcription in progress</i>")
        if n and b.get("in_progress"):
            stat += " · <i>transcription in progress</i>"
        link = f'<a class="go dirgo" href="book/{b["slug"]}/">Tables →</a>' if n else ""
        if n and printed_toc(b):  # straight to the book's printed table of contents (opened on its page)
            link += f' <a class="go dirgo" href="book/{b["slug"]}/#toc">ToC →</a>'
        if b.get("_dir_n"):
            stat += (" · " if stat else "") + f'<b>{b["_dir_n"]:,}</b> directory entries' + (" (in progress)" if b.get("dir_in_progress") else "")
            link += f' <a class="go dirgo" href="book/{b["slug"]}/directory.html">Directories →</a>'
        if b.get("_chron_n"):
            stat += f' · <b>{b["_chron_n"]:,}</b> chronology events'
            link += f' <a class="go dirgo" href="book/{b["slug"]}/chronology.html">Chronologies →</a>'
        item = f' · <a href="{b["item"]}">original scan</a>' if b.get("item") else ""
        if b.get("item"):   # list view only (the card has "original scan" under the source line)
            link += f' <a class="go dirgo scango" href="{b["item"]}" target="_blank" rel="noopener">Original ↗</a>'
        grp = group_of(b)
        home = f'book/{b["slug"]}/' if n else f'book/{b["slug"]}/directory.html' if b.get("dir_only") and b.get("_dir_n") else None
        title = f'<a href="{home}" style="color:inherit;text-decoration:none">{html.escape(b["title"])}</a>' if home else html.escape(b["title"])
        py = pub_years(b)
        yattr = f' data-y0="{py[0]}" data-y1="{py[1]}"' if py else ""
        items.append((grp, b["slug"], f"""<article data-t="{html.escape(b["title"])}" data-s="{html.escape(b.get("subtitle", ""))}"{yattr} data-a="{added.get(b["slug"], "")}"><h2>{title}</h2><div class="pub">{html.escape((b["author"] + "; ") if b.get("author") else "")}{html.escape(b["publisher"])}</div>{(f'<div class="pub">{html.escape(b["note"])}</div>' if CJK_RE.search(b["note"]) else f'<div class="pub"><i>{html.escape(b["note"])}</i></div>') if b.get("note") else ""}
<div class="stat">{stat}</div><div class="src">LLM-transcribed{item}</div>{b.get("_qstat", "")}<div class="links">{link}</div></article>"""))
    order = {"far-east": 0, "manchoukuo": 1}
    other = sorted([(sl, h) for g, sl, h in items if g == "other"], key=lambda x: order.get(x[0].rsplit("-", 1)[0], 9))
    names = {"japan": "Japan", "china": "China", "korea": "Korea", "taiwan": "Taiwan", "manchuria": "Manchuria", "south-seas": "South Seas Mandate", "other": "Other"}
    year = {b["slug"]: edition(b) for b in BOOKS}
    body = {"japan": "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "japan"), key=lambda x: (year[x[1]], x[1])))}  # by edition year
    body["china"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "china"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["korea"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "korea"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["taiwan"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "taiwan"), key=lambda x: (year[x[1]], x[1])))
    body["manchuria"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "manchuria"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["south-seas"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "south-seas"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["other"] = "\n".join(h for _, h in other)
    topics = {r: f'<p class="tlinks">{rn} tables by topic: ' + " · ".join(f'<a href="topics/{r}-{k}.html">{n}</a>' for k, n in TOPICS) + "</p>"
              for r, (rn, sr) in TOPIC_REGIONS.items() if any(re.match(rx, k.split(":")[0]) for _, _, rx in sr for k in TOPIC_TAGS)}
    def gstat(g):
        bs = [(b, n) for b, n, c, ch in cards if group_of(b) == g]
        tb, de = sum(n for b, n in bs), sum(b.get("_dir_n") or 0 for b, n in bs)
        return (f'<p class="gstat">{len(bs)} volume{"s" if len(bs) != 1 else ""}, with a total of {tb:,} table{"s" if tb != 1 else ""}'
                + (f', and {de:,} directory entr{"ies" if de != 1 else "y"}' if de else "") + "</p>")
    grids = "".join(f'<section class="grp" id="{g}"><h2 class="grph"><button class="gtog" type="button" aria-expanded="true" title="Collapse or expand this section"><span class="tri" aria-hidden="true">▾</span>{names[g]}</button></h2>{gstat(g)}<div class="grid">{body[g]}</div></section>'
                    for g in ("japan", "china", "korea", "taiwan", "manchuria", "south-seas", "other") if body[g])
    # a floating stack, shown once the reader has scrolled: back to the top, then one letter per section, in the page's
    # order (the China/Japan coin-flip below swaps C and J along with the sections)
    letter = {"japan": "J", "china": "C", "korea": "K", "taiwan": "T", "manchuria": "M", "south-seas": "S", "other": "O"}
    fab = ('<nav id="fab" aria-label="Jump to a section"><a href="#top" class="up" title="Back to the top" aria-label="Back to the top">↑</a>'
           + "".join(f'<a href="#{g}" id="f-{g}" title="{names[g]}">{letter[g]}</a>'
                     for g in ("japan", "china", "korea", "taiwan", "manchuria", "south-seas", "other") if body[g]) + "</nav>")
    return LANDING.replace("__CARDS__", "__TOPICMENU__" + grids + fab)


LANDING = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<title>Old Tables of East Asia</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman","Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:980px;margin:0 auto;padding:34px 16px 30px}.band h1{font-weight:normal;font-size:30px;margin:0 0 8px}.band .lede{color:var(--accent-ink);opacity:.9;margin:0}
main{max-width:980px;margin:0 auto;padding:26px 16px 60px}
.topnav{margin:18px 0 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.jump{display:contents}.jump a{display:inline-block;border:1px solid var(--accent-ink);color:var(--accent-ink);padding:6px 16px;border-radius:5px;text-decoration:none;font-size:15px}.jump a:hover{background:var(--accent-ink);color:var(--accent)}
.grp{scroll-margin-top:12px}.grp{border-top:2px solid var(--line);margin-top:34px;padding-top:6px}.grp:first-child,.allstat+.grp{margin-top:4px;border-top:0}.allstat{margin:0 0 2px;font-size:16px;color:var(--muted)}.allstat+.grp>.grph,#groups .grp.first>.grph{margin-top:2px}#groups .grp.first{margin-top:4px;border-top:0}.introbox>summary{cursor:pointer;color:var(--accent);font-size:14px;letter-spacing:.08em;text-transform:uppercase;font-weight:bold;margin:0 0 8px;width:max-content}.introbox:not([open])>summary{margin-bottom:12px}.fbar{display:flex;flex-wrap:wrap;align-items:center;gap:8px 16px;margin:4px 0 10px;font-size:14px;color:var(--muted)}.fbar label,.fyears{display:inline-flex;align-items:center;gap:6px}.fyears{gap:10px}.fbar input,.fbar select{font:inherit;font-size:14px;color:var(--ink);background:var(--panel);border:1px solid var(--line);border-radius:5px;padding:4px 7px}#fq{width:12ch}#fy0,#fy1{width:6.5ch}.itip{font:italic bold 12px/1 Georgia,serif;width:18px;height:18px;border-radius:50%;border:1px solid var(--muted);background:transparent;color:var(--muted);padding:0;cursor:pointer;margin-left:-4px}.itip[aria-expanded="true"],.itip:hover{background:var(--accent);border-color:var(--accent);color:var(--accent-ink)}.ftip{flex-basis:100%;font-size:13px;margin-top:-4px}#groups article[hidden],#groups .grp[hidden]{display:none!important}.grph{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:18px 0 0;font-weight:bold}.grp .grid{margin-top:14px}.gtog{font:inherit;letter-spacing:inherit;text-transform:inherit;color:inherit;background:none;border:0;padding:0;cursor:pointer;display:inline-flex;align-items:center;gap:7px}.gtog .tri{display:inline-block;font-size:12px;transition:transform .15s}.grp.shut .tri{transform:rotate(-90deg)}.grp.shut>:not(.grph):not(.gstat){display:none}.tmenu{margin:4px 0 8px}.tmn{color:var(--muted);font-size:14.5px;margin:6px 0 10px}.tmn a{color:var(--accent)}.tmrow{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:baseline;padding:7px 0;border-top:1px solid var(--line)}.tmt{min-width:150px;font-size:16px}.tmrow a{color:var(--accent);text-decoration:none;border:1px solid var(--line);background:var(--panel);border-radius:14px;padding:2px 11px;font-size:14.5px}.tmrow a:hover{border-color:var(--accent)}.tmrow small{color:var(--muted)}.gstat{margin:8px 0 0;font-size:15px;color:var(--muted)}.tlinks{margin:4px 0 0;font-size:15px}.tlinks a{color:var(--accent)}
.searchbtn{display:inline-block;background:var(--accent-ink);color:var(--accent);font-weight:bold;padding:9px 16px;border-radius:5px;text-decoration:none;font-size:15px}
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
.links{margin-top:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.links .dirgo{margin:0}
.about{font:inherit;font-size:13px;background:transparent;color:var(--accent);border:1px solid var(--accent);border-radius:5px;padding:5px 10px;cursor:pointer;flex-basis:100%;max-width:max-content}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px}
dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog p{font-size:14.5px}
dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}.qstat{font-size:12.5px;color:var(--muted);margin:-6px 0 12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}.dirgo{display:inline-block;margin:8px 8px 0 0;background:var(--accent);color:var(--accent-ink);padding:6px 12px;border-radius:5px;font-size:14px}
.llmwarn{margin:28px 0 0;padding:12px 14px;border:1px solid #8a5a00;border-left:4px solid #8a5a00;background:var(--panel);font-size:14px}
footer{margin-top:24px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
.tools{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--accent-ink);opacity:.8}.tools:hover{opacity:1}.tools .lbl{font-size:12px;text-transform:uppercase;letter-spacing:.06em}.seg{display:inline-flex;border:1px solid currentColor;border-radius:999px;overflow:hidden}.viewbtn{font:inherit;font-size:13px;background:transparent;color:inherit;border:0;padding:4px 12px;cursor:pointer;white-space:nowrap}.viewbtn+.viewbtn{border-left:1px solid currentColor}.viewbtn:hover{background:rgba(127,127,127,.15)}#sortseg .viewbtn[aria-pressed="true"]{background:var(--accent-ink);color:var(--accent);font-weight:600}.tools{flex-wrap:wrap}
body.list .grid{display:block;margin-top:8px}body.list article{flex-direction:row;align-items:center;gap:12px;padding:5px 10px;border:0;border-bottom:1px solid var(--line);border-left:3px solid var(--accent)}
body.list article+article{margin-top:0}body.list article h2{font-size:16px;margin:0;flex:1;min-width:0}body.list .pub,body.list .stat,body.list .src,body.list .qstat{display:none}
#fab{position:fixed;right:14px;bottom:14px;z-index:20;display:flex;flex-direction:column;gap:3px;opacity:0;pointer-events:none;transition:opacity .2s}#fab.on{opacity:1;pointer-events:auto}#fab a{display:flex;align-items:center;justify-content:center;width:30px;height:26px;border-radius:5px;background:var(--panel);color:var(--accent);border:1px solid var(--line);font:bold 13px/1 system-ui,sans-serif;text-decoration:none;box-shadow:0 1px 3px rgba(0,0,0,.15)}#fab a:hover{background:var(--accent);color:var(--accent-ink)}#fab a.up{height:30px;font-size:16px;margin-bottom:3px;background:var(--accent);color:var(--accent-ink)}@media print{#fab{display:none}}.intro{margin:6px 0 18px;font-size:16px;line-height:1.6}.intro p{margin:0 0 10px}.abouttext{line-height:1.65;font-size:16.5px}.abouttext h2{font-size:26px;font-weight:normal;margin:6px 0 10px}.abouttext h3{font-size:20px;font-weight:normal;margin:30px 0 8px;scroll-margin-top:12px}.abouttext h4{font-size:17px;margin:24px 0 6px}.biblio{list-style:none;padding:0;margin:0}.biblio li{padding-left:2em;text-indent:-2em;margin:0 0 8px}.scango{display:none!important}body.list .scango{display:inline-block!important;background:#cfe6d5;color:#1f4a2c}:root[data-theme="dark"] body.list .scango{background:#2f5a3d;color:#e4ebe6}@media (prefers-color-scheme: dark){:root:not([data-theme="light"]) body.list .scango{background:#2f5a3d;color:#e4ebe6}}body.list .links{margin:0;flex-wrap:nowrap;gap:5px}body.list .dirgo{padding:1px 8px;font-size:12.5px;font-weight:normal;white-space:nowrap}
@media(max-width:560px){body.list article{flex-wrap:wrap;gap:4px}body.list article h2{flex-basis:100%}body.list .links{flex-wrap:wrap}.tools{margin-left:0}}
</style></head><body><div class="band"><div>
<h1><a href="index.html" style="color:inherit;text-decoration:none">Old Tables of East Asia</a></h1>
<div class="topnav"><a class="searchbtn" href="search.html">Search</a><a class="searchbtn" href="topics/index.html">Topics</a><a class="searchbtn" href="about.html">About</a><nav class="jump" id="jump"><a href="#japan" id="j-japan">Japan</a><a href="#china" id="j-china">China</a><a href="#korea">Korea</a><a href="#taiwan">Taiwan</a><a href="#manchuria">Manchuria</a><a href="#south-seas">South Seas</a><a href="#other">Other</a></nav><span class="tools"><span class="lbl">Sort</span><span class="seg" id="sortseg" role="group" aria-label="Sort books"><button class="viewbtn" data-m="date" type="button" aria-pressed="true" title="Sort by edition year">Edition year</button><button class="viewbtn" data-m="az" type="button" aria-pressed="false" title="Sort alphabetically">A–Z</button><button class="viewbtn" data-m="added" type="button" aria-pressed="false" title="Most recently added first">Recently added</button></span><span class="seg"><button class="viewbtn" id="viewbtn" type="button" aria-pressed="false">☰ List</button></span></span></div>
</div></div>
<main>
<div id="groups">
__CARDS__
</div>
<script>(function(){const bs=[...document.querySelectorAll("#sortseg button")];document.querySelectorAll("#groups .grid").forEach(g=>[...g.children].forEach((a,i)=>a.dataset.i=i));
const key=t=>t.replace(/^(The|A|An)\s+/i,"").toLowerCase();
const CMP={date:(x,y)=>x.dataset.i-y.dataset.i,az:(x,y)=>key(x.dataset.t).localeCompare(key(y.dataset.t),"en",{numeric:true}),added:(x,y)=>(y.dataset.a||"").localeCompare(x.dataset.a||"")||x.dataset.i-y.dataset.i};
function set(m){if(!CMP[m])m="date";document.querySelectorAll("#groups .grid").forEach(g=>{const a=[...g.children];a.sort(CMP[m]);a.forEach(e=>g.appendChild(e))});
bs.forEach(b=>b.setAttribute("aria-pressed",b.dataset.m===m?"true":"false"));try{localStorage.setItem("homesort",m)}catch(e){}}
let m="date";try{m=localStorage.getItem("homesort")||"date"}catch(e){}set(m);bs.forEach(b=>b.onclick=()=>set(b.dataset.m))})();</script>
<script>(function(){const b=document.getElementById("viewbtn");function set(l){document.body.classList.toggle("list",l);b.textContent=l?"▦ Cards":"☰ List";b.setAttribute("aria-pressed",l);try{localStorage.setItem("homeview",l?"list":"cards")}catch(e){}}
let l=false;try{l=localStorage.getItem("homeview")==="list"}catch(e){}set(l);b.onclick=()=>set(!document.body.classList.contains("list"))})();</script>
<script>(function(){let s={};try{s=JSON.parse(localStorage.getItem("homeshut")||"{}")}catch(e){}
function set(g,shut){g.classList.toggle("shut",shut);g.querySelector(".gtog").setAttribute("aria-expanded",!shut);if(shut)s[g.id]=1;else delete s[g.id];try{localStorage.setItem("homeshut",JSON.stringify(s))}catch(e){}}
document.querySelectorAll("#groups .grp").forEach(g=>{if(s[g.id])set(g,true);g.querySelector(".gtog").onclick=()=>set(g,!g.classList.contains("shut"))});
function open(){const g=location.hash&&document.getElementById(location.hash.slice(1));if(g&&g.classList.contains("shut"))set(g,false)}
["jump","fab"].forEach(id=>document.getElementById(id)&&document.getElementById(id).addEventListener("click",e=>{const a=e.target.closest("a");if(a){const g=document.getElementById(a.getAttribute("href").slice(1));if(g&&g.classList.contains("shut"))set(g,false)}}));open()})();</script>
<script>(function(){const q=document.getElementById("fq"),y0=document.getElementById("fy0"),y1=document.getElementById("fy1"),sec=document.getElementById("fsec"),st=document.getElementById("allstat");if(!q)return;
// Home filter: title (and subtitle) text, publication years From/To (a book with no known year is hidden while a year
// is set), and one section. Sections left with no book are hidden; the total line counts what is shown.
const norm=x=>(x||"").normalize("NFKC").toLowerCase();
function run(){const t=norm(q.value.trim()),a=parseInt(y0.value,10),b=parseInt(y1.value,10),g=sec.value;let n=0,tot=0;
 document.querySelectorAll("#groups .grp").forEach(G=>{let k=0;G.querySelectorAll("article").forEach(A=>{tot++;
  let ok=(!t||norm(A.dataset.t+" "+(A.dataset.s||"")).includes(t))&&(!g||G.id===g);
  if(ok&&(a||b)){const p=+A.dataset.y0,r=+A.dataset.y1;ok=!!p&&(!a||r>=a)&&(!b||p<=b)}
  A.hidden=!ok;if(ok)k++});G.hidden=!k;n+=k;
  const gs=G.querySelector(".gstat");if(gs){if(!gs.dataset.txt)gs.dataset.txt=gs.textContent;const m=G.querySelectorAll("article").length;gs.textContent=(t||a||b)?`${k} of ${m} volume${m===1?"":"s"} shown`:gs.dataset.txt}});
 st.textContent=(t||a||b||g)?`${n} of ${tot} volumes shown`:st.dataset.txt;first()}
// the first section shown sits close under the total line (with hidden sections before it, :first-child cannot tell)
function first(){let f=false;document.querySelectorAll("#groups .grp").forEach(G=>{G.classList.toggle("first",!f&&!G.hidden);if(!G.hidden)f=true})}
setTimeout(first,0);
[q,y0,y1].forEach(e=>e.addEventListener("input",run));sec.addEventListener("change",run);
const i=document.getElementById("fyi"),tp=document.getElementById("ftip");i.addEventListener("click",()=>{tp.hidden=!tp.hidden;i.setAttribute("aria-expanded",!tp.hidden)});
if(q.value||y0.value||y1.value||sec.value)run()})();</script>
<script>if(Math.random()<.5){const g=document.getElementById("groups");g.insertBefore(document.getElementById("china"),document.getElementById("japan"));
const n=document.getElementById("jump");n.insertBefore(document.getElementById("j-china"),document.getElementById("j-japan"));
const f=document.getElementById("fab");if(f)f.insertBefore(document.getElementById("f-china"),document.getElementById("f-japan"))}</script>
<script>(function(){const f=document.getElementById("fab");if(!f)return;const t=()=>f.classList.toggle("on",scrollY>window.innerHeight*.6);addEventListener("scroll",t,{passive:true});t();
f.querySelector(".up").addEventListener("click",e=>{e.preventDefault();scrollTo({top:0,behavior:"smooth"});history.replaceState(null,"",location.pathname+location.search)})})();</script>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision models of Opus 5.5, Sonnet 5.5, or Haiku 5.5 (named on each book's page). Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<script>document.addEventListener("click",e=>{const b=e.target.closest("[data-about]");if(b){document.getElementById(b.dataset.about).showModal();return}
if(e.target.tagName==="DIALOG")e.target.close()});</script>
<footer>Each table can be downloaded as CSV from its page. Each book can be downloaded whole as an Excel workbook (one sheet per table, with a linked contents sheet) or as JSON; directories are available as Markdown.<br><br>The website was created by Claude Opus 5.5 with <a href="https://muninn.net/">Konrad M. Lawson</a> at the prompt. See: <a href="https://froginawell.net/frog/sources/">Other Resources at Frog in a Well</a><br><span class="ver">__VERSION__</span></footer>
</main></body></html>
"""


# Private notes layer (annotate.js), shared by the table and directory pages. Each page defines anView(), anGo(view),
# AN_NOTE and AN_AREA before this block, calls anSync() after every view change, and then
# try{if(localStorage.getItem("stat-notes")==="1")anSet(true)}catch(e){} once its first view is drawn.
ANNOT_JS = r"""// Private notes (annotate.js v1.4.0, MIT, ../../annotate.js): loaded only after the reader turns Notes on.
// Notes stay in this browser's localStorage, under one key per view (anView(), defined by each page); anGo(view) opens a view.
let AN_ON=false,AN_LOAD=null,AN_FOCUS=null;const AN_PROJ="stat-tables";
function anDark(){const r=document.documentElement;return r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches}
function anCfg(open){const d=anDark();return {project:AN_PROJ,page:location.pathname+"#"+anView(),theme:d?"dark":"light",accent:d?"#8cc49e":"#1f4a2c",startOpen:open,
 note:AN_NOTE}}
function anOpen(){let off=false;try{off=localStorage.getItem("an-off")==="1"}catch(e){}return !off}
function anSync(force){const A=window.Annotate;if(!AN_ON||!A||!A.config)return;if(!force&&A.config.page===location.pathname+"#"+anView())return;
 const l=document.getElementById("__an_launch");A.init(anCfg(!(l&&l.classList.contains("an-show"))))}
function anLoad(){if(window.Annotate){window.Annotate.init(anCfg(anOpen()));return Promise.resolve()}
 return AN_LOAD||(AN_LOAD=new Promise((ok,no)=>{window.AnnotateConfig=anCfg(anOpen());const s=document.createElement("script");s.src="../../annotate.js";s.onload=()=>{anSync(true);if(AN_FOCUS){const f=AN_FOCUS;AN_FOCUS=null;setTimeout(()=>window.Annotate.focus(f),400)}ok()};s.onerror=()=>{AN_LOAD=null;no()};document.head.appendChild(s)}))}
function anSet(on,user){AN_ON=on;try{if(on)localStorage.setItem("stat-notes","1");else localStorage.removeItem("stat-notes");if(user&&on)localStorage.removeItem("an-off")}catch(e){}
 document.body.classList.toggle("notes-on",on);const b=$("#annot");b.setAttribute("aria-pressed",String(on));b.textContent=on?"Notes ✓":"Notes";
 if(on)anLoad().catch(()=>{AN_ON=false;b.setAttribute("aria-pressed","false");b.textContent="Notes"});else if(window.Annotate)window.Annotate.destroy()}
function anLink(id){let v=null;try{const d=JSON.parse(localStorage.getItem("annotate:"+AN_PROJ)||"{}");const c=(d.comments||[]).find(x=>x&&x.id===id);
  if(c&&typeof c.page==="string"&&c.page.includes("#"))v=c.page.slice(c.page.indexOf("#")+1)}catch(e){}
 anGo(v);if(v===null)return;
 if(window.Annotate&&AN_ON)setTimeout(()=>window.Annotate.focus(id),400);else AN_FOCUS=id}
$("#annot").onclick=()=>anSet(!AN_ON,true);
// annotate.js 1.4.0 cancels an open comment on any pointerdown outside it, including the "your name" dialog it shows
// before the first comment is saved; keep that pointerdown from reaching its handler so the first comment is not lost.
document.addEventListener("pointerdown",e=>{if(e.target.closest&&e.target.closest("#__an_namewrap"))e.stopPropagation()},true);
// annotate.js finds a highlight's surrounding text only when the selection starts in a text node; a selection that starts
// or ends on an element (a whole cell, a triple-click) would be anchored to the first matching text on the page, often
// in the table list. Move such ends into the first/last selected text node before annotate.js reads the selection.
document.addEventListener("pointerup",()=>{if(!AN_ON)return;const g=getSelection();if(!g||g.isCollapsed||!g.rangeCount)return;
 const r=g.getRangeAt(0);if(r.startContainer.nodeType===3&&r.endContainer.nodeType===3)return;
 const root=r.commonAncestorContainer,w=document.createTreeWalker(root.nodeType===3?root.parentNode:root,NodeFilter.SHOW_TEXT,{acceptNode:n=>r.intersectsNode(n)&&n.nodeValue.trim()?1:3});
 let a=null,b=null,n;while((n=w.nextNode())){if(!a)a=n;b=n}if(!a)return;
 const r2=r.cloneRange();if(r.startContainer.nodeType!==3)r2.setStart(a,0);if(r.endContainer.nodeType!==3)r2.setEnd(b,b.nodeValue.length);
 g.removeAllRanges();g.addRange(r2)},true);
// Touch screens: a long-press selection usually ends in pointercancel, not the pointerup annotate.js waits for,
// so with the Highlight tool on, open the comment box once the selection has settled.
let anSelT=0;document.addEventListener("selectionchange",()=>{clearTimeout(anSelT);if(!AN_ON||!matchMedia("(pointer:coarse)").matches)return;
 anSelT=setTimeout(()=>{const s=getSelection();if(!s||s.isCollapsed||!document.querySelector('#__an_bar .an-btn[data-tool="highlight"].an-on'))return;
  const n=s.anchorNode&&(s.anchorNode.nodeType===1?s.anchorNode:s.anchorNode.parentElement);if(!n||!n.closest(AN_AREA)||document.querySelector("#__an_compose.an-show"))return;
  n.dispatchEvent(new PointerEvent("pointerup",{bubbles:true,pointerType:"touch"}))},700)});
"""


TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<script src="../../fold.js"></script>
<title>__BOOK__ · Tables</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.45 Georgia,"Times New Roman","Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a,header .meta{color:var(--accent-ink)!important;opacity:.88}
header button{background:transparent;color:var(--accent-ink);border-color:currentColor}
header h1{font-size:20px;margin:0;font-weight:normal}
header .meta{color:var(--muted);font-size:13px}
#wrap{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 56px);position:relative}
.keyrow{display:flex;align-items:center;justify-content:space-between;gap:8px}
#sidetog,#sideopen{width:18px;height:16px;padding:0;border:1.5px solid var(--muted);border-radius:3px;background:transparent;box-shadow:none;cursor:pointer;position:relative;opacity:.7;flex:none}
#sidetog::before,#sideopen::before{content:"";position:absolute;left:4px;top:0;bottom:0;border-left:1.5px solid var(--muted)}
#sidetog:hover,#sideopen:hover{opacity:1}
#sideopen{display:none;position:absolute;z-index:3;top:20px;left:12px}
body.noside #sideopen{display:block}body.noside #side{display:none}body.noside #wrap{grid-template-columns:minmax(0,1fr)}body.noside.cmp #wrap{grid-template-columns:minmax(0,1fr) minmax(0,1fr)}body.noside #main{padding-left:44px}
#side{border-right:1px solid var(--line);display:flex;flex-direction:column;min-height:0}
#side .ctl{padding:10px;border-bottom:1px solid var(--line);display:flex;flex-direction:column;gap:6px}
input,select,button{font:inherit;font-size:14px;padding:6px 8px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#list{overflow:auto;flex:1}
#list .ch{position:sticky;top:0;background:var(--bg);cursor:pointer;padding:8px 10px 4px;font-size:12px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);border-bottom:1px solid var(--line)}
#list a{display:block;padding:6px 10px;border-bottom:1px solid var(--line);color:inherit;text-decoration:none;font-size:14px}
#list a:hover{background:var(--hi)}
#list a.on,#list a.on:hover{background:var(--accent);color:var(--accent-ink);border-left:3px solid var(--accent)}
#list a.on small{color:var(--accent-ink);opacity:.85}
body.kbd #list a:not(.on):hover{background:transparent}
#list a small{color:var(--muted);display:block;font-size:12px}
#main{overflow:auto;padding:18px 22px;min-width:0}
h2{margin:0 0 4px;font-weight:normal;font-size:22px}
.sub{color:var(--muted);font-size:14px;margin-bottom:10px}.scanlink,.scanlink:visited{display:inline-block;margin:1px 2px;padding:1px 9px;border:1px solid var(--accent);border-radius:4px;background:var(--accent);color:var(--accent-ink);font:600 13px/1.5 system-ui,sans-serif;text-decoration:none;white-space:nowrap}.scanlink:hover{filter:brightness(1.18);text-decoration:none}
.tw{overflow:auto;border:1px solid var(--line);background:var(--panel);margin:8px 0 16px;max-height:70vh;width:fit-content;max-width:100%}.tw:focus{outline:none}.tw:focus-visible{outline:2px solid var(--line)}
table{border-collapse:collapse;font-size:13.5px;font-family:"Iowan Old Style",Georgia,"Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
th,td{border:1px solid var(--line);padding:3px 7px;vertical-align:top}
th{position:sticky;top:0;background:var(--panel);text-align:left;font-weight:bold;font-size:12.5px}
th.sortable{cursor:pointer;user-select:none;padding-right:18px;position:sticky}
th.sortable::after{content:"\2195";position:absolute;right:5px;opacity:.3;font-weight:normal}
th.sortable[aria-sort="ascending"]::after{content:"\25B2";opacity:.9}
th.sortable[aria-sort="descending"]::after{content:"\25BC";opacity:.9}
th.sortable:hover{background:var(--hi)}
thead.ml{position:sticky;top:0;z-index:1}thead.ml th{position:relative;vertical-align:bottom}thead.ml th.grp{text-align:center;vertical-align:middle;font-weight:bold}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{background:repeating-linear-gradient(45deg,transparent 0 4px,var(--hi) 4px 8px)}
td.illeg{background:repeating-linear-gradient(45deg,transparent 0 4px,rgba(200,60,40,.32) 4px 8px)}tr.hlrow td{background:rgba(183,121,31,.13)}td.hlcell{outline:2px solid #b7791f;outline-offset:-2px;background:rgba(183,121,31,.3)!important}
tr:hover td{background:var(--hi)}
td.nw,th.nw{white-space:nowrap}.ver{color:var(--muted);font-size:12px}.vrow{display:flex;align-items:stretch;gap:8px;flex-wrap:wrap}.vrow .vsw{margin:4px 0 2px}.mapbtn,.mapbtn:visited{display:inline-flex;align-items:center;box-sizing:border-box;margin:4px 0 2px;font-size:13px;font-weight:400;line-height:inherit;padding:0 11px;border:1px solid var(--accent);border-radius:5px;background:var(--accent);color:var(--accent-ink);text-decoration:none}.mapbtn:hover{filter:brightness(1.15);text-decoration:none}td.w6,th.w6{min-width:6.3em}tr.sec td:first-child{font-weight:bold;font-style:italic}tr.sec.cjk td:first-child{font-style:normal}
.part{font-weight:bold;margin-top:12px}
.tbl{padding-bottom:22px;margin-bottom:26px;border-bottom:2px solid var(--line)}
.chhead{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:0 0 4px}
.chsum{color:var(--muted);font-size:14px;margin-bottom:18px}
.chgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,calc(var(--chfs,17px)*12)),1fr));gap:calc(var(--chfs,17px)*.6)}
.chbtn{display:block;padding:.65em .8em;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);text-decoration:none;font-weight:bold;font-size:var(--chfs,clamp(16px,.9vw + 9px,21px));line-height:1.25;overflow-wrap:anywhere}
.chbtn:hover{border-color:var(--accent);background:var(--hi)}
.chbtn small{display:block;color:var(--muted);font-weight:normal;font-size:max(11px,.62em);margin-top:.2em}
.chhead a{color:inherit}
.xl{font-size:13.5px;margin:4px 0 12px;color:var(--muted);line-height:1.9}
.xl a{color:var(--accent)}
.xlc a{margin-right:12px;white-space:nowrap}
.xlo{display:inline-flex;align-items:stretch;margin:2px 8px 2px 0;border:1px solid var(--line);border-radius:5px;background:var(--panel);white-space:nowrap;line-height:1.7;overflow:hidden;vertical-align:middle}
.xlo a{padding:1px 9px;display:flex;align-items:center}
.cmpb{font-size:12px;padding:1px 9px;border:0;border-left:1px solid var(--line);border-radius:0;background:var(--hi);color:var(--ink)}
.cmpb:hover{background:var(--accent);color:var(--accent-ink)}
.xln{font-style:italic;line-height:1.4;margin-top:2px}
#cmp{overflow:auto;padding:18px 22px;border-left:1px solid var(--line);min-width:0;background:var(--panel)}
#cmp .cmphead{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:12px}
#cmp .cmphead select{flex:1;min-width:0}
body.cmp #wrap{grid-template-columns:280px minmax(0,1fr) minmax(0,1fr)}
.tbl h2 a{color:inherit;text-decoration:none}
.keys{font-size:12px;color:var(--muted)}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);color:var(--ink);font-size:14px}
.notes{font-size:13.5px;color:var(--muted)}
details.notes{margin:6px 0}details.notes>summary{cursor:pointer;font-weight:bold;padding:3px 0;list-style:revert}details.notes>summary.warn{color:var(--warn)}details.notes>ul{margin:4px 0 8px}
.notes li.warn{color:var(--warn)}
.row{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin:8px 0}
.scan{display:flex;gap:10px;flex-wrap:wrap;margin-top:10px}
.scan a img{height:160px;border:1px solid var(--line)}
mark{background:var(--hi);color:inherit}
#toggle{margin-left:auto}
.dirbtn{margin-left:auto;background:var(--accent-ink);color:var(--accent)!important;opacity:1!important;font-weight:bold;font-size:14px;padding:6px 14px;border-radius:5px;text-decoration:none;align-self:center}.homebtn~.dirbtn,.homebtn~.aboutbtn,.homebtn~.anbtn{margin-left:0}.dirbtn:hover{filter:brightness(.93)}.dirbtn+#toggle,.dirbtn+.dirbtn,.dirbtn+.aboutbtn{margin-left:0}
.en{margin:2px 0 6px;font-size:15px}
.che{display:block;text-transform:none;letter-spacing:0;font-size:11.5px;color:var(--muted);margin-top:1px}
.che2{display:block;font-size:15px;color:var(--muted);margin-top:2px}
.che3{display:block;font-weight:normal;font-size:max(12px,.54em);color:var(--muted);margin-top:.15em}
.enn{color:var(--muted);font-size:13px;white-space:nowrap}
.ptoc{margin:0 0 18px;border:1px solid var(--line,#ccc);border-radius:6px;background:var(--panel);padding:6px 12px}.ptoc summary{cursor:pointer;font-weight:bold;padding:4px 0}.ptoc ul{list-style:none;margin:6px 0;padding:0;columns:2 420px;column-gap:28px}.ptoc li{display:flex;gap:8px;break-inside:avoid;padding:1px 0;line-height:1.35}.ptoc li a{color:inherit}.ptoc li a:hover{color:var(--accent)}.ptoc .pp{margin-left:auto;color:var(--muted,#777);font-variant-numeric:tabular-nums;white-space:nowrap}.ptoc .pl0{font-weight:bold;text-transform:none;margin-top:10px;break-after:avoid}.ptoc .pl1{font-weight:bold;margin-top:4px}.ptoc .pl2{padding-left:16px;font-size:14px}.ptoc .pl3{padding-left:32px;font-size:13px}.ptoc .ptk{display:block;font-size:14px;margin:2px 0 6px;cursor:pointer}.ptoc .ptkh{color:var(--muted);font-size:13px}.ptoc li.ptt{display:none;font-size:13px;font-weight:normal}.ptoc ul.showt li.ptt{display:flex}.ptoc a.ptti{display:none;color:color-mix(in srgb,var(--accent) 60%,var(--ink));text-decoration:none;padding:0 6px}.ptoc .tbadge{display:inline-flex;align-items:center;justify-content:center;box-sizing:border-box;width:15px;height:15px;padding:0;border:1.5px solid currentColor;border-radius:3px;font:700 10px/1 system-ui,-apple-system,"Segoe UI",Arial,sans-serif;margin-right:5px;vertical-align:-2px;flex:none}.ptoc a.ptti .tbadge{margin:0}.ptoc ul.showt a.ptti{display:inline}.ptoc li.ptt a{color:color-mix(in srgb,var(--accent) 60%,var(--ink))}
.qstat{font-size:13.5px;color:var(--muted);margin:0 0 16px}.cite{font-size:13.5px;color:var(--muted);margin:0 0 16px;overflow-wrap:anywhere}.cite b{color:var(--ink);font-weight:600}.origbtn{display:inline-block;margin:4px 0 16px;padding:8px 14px;border:1px solid var(--accent);border-radius:6px;background:var(--panel);color:var(--accent);text-decoration:none;font-size:15px;font-weight:bold}.origbtn:hover{background:var(--hi)}
.ctx{max-width:760px;font-size:14.5px;line-height:1.55;margin:8px 0 12px;padding:9px 12px;border-left:3px solid var(--accent);background:var(--panel)}
.aboutbtn{margin-left:auto;font:inherit;font-size:14px;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:5px;padding:5px 12px;cursor:pointer;align-self:center}.aboutbtn+#toggle{margin-left:0}
.anbtn{margin-left:auto;font:inherit;font-size:14px;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:5px;padding:5px 12px;cursor:pointer;align-self:center}.anbtn[aria-pressed="true"]{background:var(--accent-ink);color:var(--accent)}.dirbtn+.anbtn,.aboutbtn+.anbtn,.anbtn+#toggle{margin-left:0}
@media (max-width:640px){html body #__an_bar.an-right,html body #__an_bar.an-left{flex-direction:row;left:0;right:0;margin:0 auto;width:max-content;max-width:calc(100vw - 12px);transform:none;bottom:10px;gap:2px;padding:5px}html body #__an_bar .an-btn,html body #__an_colorbtn{width:min(36px,calc((100vw - 44px)/9.5));height:36px}html body #__an_bar .an-sep{width:1px;height:24px;margin:0 2px}html body #__an_bar #__an_colorpop{right:auto;left:50%;transform:translateX(-50%);bottom:52px;top:auto;width:max-content}body.notes-on{padding-bottom:70px}}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px;font-size:14.5px}dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog .pub{color:var(--muted);font-size:13px}dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}
.vsw{display:inline-flex;border:1px solid var(--line);border-radius:5px;overflow:hidden;margin:4px 0 2px;vertical-align:middle}.vsw button{border:0;border-radius:0;padding:4px 11px;font-size:13px;background:var(--panel);color:var(--muted)}.vsw button+button{border-left:1px solid var(--line)}.vsw button.on{background:var(--accent);color:var(--accent-ink)}
body.vw-chart .tbl.hasch .tw{display:none}body.vw-table .tchart{display:none}
.tchart button,.vsw button{box-shadow:none;-webkit-appearance:none;appearance:none}.tchart select{box-shadow:none}.tc-tabs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}.tc-tabs:empty{display:none}.tc-tabs button{font-size:13px;padding:3px 11px;border-radius:14px;max-width:100%;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.tc-tabs button.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
.tchart{position:relative;border:1px solid var(--line);background:var(--panel);margin:8px 0 16px;padding:10px 12px}.tchart.tc-none{display:none}.tc-bar{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}.tc-bar:empty{display:none}.tc-bar button,.tc-bar select{font-size:13px;padding:3px 9px}.tc-bar button.on{background:var(--hi);border-color:var(--accent);color:var(--ink)}
.tc-leg{display:flex;flex-wrap:wrap;gap:4px 6px;margin-bottom:8px;max-height:10em;overflow:auto}.tc-chip{font-size:12.5px;padding:2px 9px;border-radius:12px;opacity:.5;display:inline-flex;align-items:center;gap:5px;max-width:100%;text-align:left}.tc-chip.on{opacity:1;border-color:var(--muted)}.tc-chip i,.tc-tip i,.tc-mt i{display:inline-block;width:10px;height:10px;border-radius:2px;flex:none}.tc-grp{font-size:12px;color:var(--muted);width:100%;margin-top:2px}.tc-all{font-size:12px;padding:2px 9px}
.tc-svg{display:block;overflow:visible}.tc-ax{font-size:10.5px;fill:var(--muted)}.tc-lab{font-size:12px;fill:var(--ink)}.tc-tot{font-weight:600}.tc-gl{font-size:12px;font-weight:600;fill:var(--ink)}.tc-grid{stroke:var(--line);stroke-width:1}.tc-zero{stroke:var(--muted);stroke-width:1}.tc-guide{stroke:var(--muted);stroke-dasharray:3 3}.tc-q{font-size:12px;font-weight:700;fill:#c0392b}.tc-neq{font-size:14px;font-weight:700;fill:var(--warn)}.tc-totmark{stroke:var(--ink);stroke-width:2}.tc-in{font-size:11px;font-weight:600;pointer-events:none}.tc-parts{font-size:12.5px;color:var(--muted);margin:2px 0 0;line-height:1.5}.tc-parts b{color:var(--ink)}.tc-parts span{white-space:nowrap}.tc-parts i{display:inline-block;width:9px;height:9px;border-radius:2px;margin:0 4px 0 2px;vertical-align:0}span.tc-chip{cursor:default}.tc-val{font-size:11px;fill:var(--muted)}.tc-big{font-size:12.5px;font-weight:700;fill:var(--ink)}.tc-totp{border-bottom:1px solid var(--line);padding-bottom:6px;margin-bottom:10px}.tc-totp::before{content:"Printed total";display:block;font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:var(--muted);margin:2px 0 2px}
.tc-tip{position:absolute;z-index:5;background:var(--panel);color:var(--ink);border:1px solid var(--line);box-shadow:0 2px 8px rgba(0,0,0,.2);padding:6px 9px;font-size:12.5px;max-width:min(360px,92%);pointer-events:none;line-height:1.45}.tc-tip div{display:flex;gap:5px;align-items:baseline}.tc-tip i{position:relative;top:1px}.tc-sum{margin-top:4px;color:var(--muted)}.tc-sum.warn{color:var(--warn)}
.tc-note{font-size:12px;color:var(--muted);margin:8px 0 0}.tc-msg{font-size:13px;color:var(--muted)}.tc-multi{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:14px}.tc-mt{font-size:12.5px;display:flex;gap:6px;align-items:center;margin-bottom:2px}tr.tc-hl td{background:var(--hi)}
@media (max-width:760px){#sidetog,body.noside #sideopen{display:none}body.noside #side{display:flex}body.noside #main{padding-left:16px}#wrap,body.cmp #wrap{grid-template-columns:minmax(0,1fr);height:auto}#cmp{border-left:0;border-top:2px solid var(--accent);padding:14px 16px}#side,#main{min-width:0;max-width:100vw}#list a{overflow-wrap:anywhere}.tw{max-height:none}header{padding:12px 16px}header h1{font-size:18px}.dirbtn{margin-left:0}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}.chgrid{gap:8px}.chbtn{padding:11px 13px}.chbtn small{font-size:12px}}
#tfab{position:fixed;right:12px;bottom:14px;z-index:30;display:flex;flex-direction:column;gap:4px;opacity:0;pointer-events:none;transition:opacity .2s}#tfab.on{opacity:.92;pointer-events:auto}#tfab button{width:44px;height:40px;border-radius:7px;background:var(--panel);color:var(--accent);border:1px solid var(--line);font:bold 19px/1 system-ui,sans-serif;padding:0;box-shadow:0 1px 3px rgba(0,0,0,.18);cursor:pointer;touch-action:manipulation}#tfab button:hover{background:var(--accent);color:var(--accent-ink)}#tfab button.up{background:var(--accent);color:var(--accent-ink);margin-bottom:2px}@media (min-width:761px){#tfab{right:20px;bottom:18px}}@media print{#tfab{display:none!important}}
</style>
<link rel="stylesheet" href="../../tags.css"><script src="../../data/tags/vocabulary.js"></script><script src="../../tags.js"></script></head>
<body>
<header><a href="../../" style="text-decoration:none;font-size:14px">← All books</a><h1><a href="./" onclick="goHome();return false" style="color:inherit;text-decoration:none" title="Back to this book's contents">__BOOK__</a></h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../../data/__SLUG__.json" style="color:inherit">JSON</a>__XLSX__</span>
<a class="dirbtn homebtn" href="./" onclick="goHome();return false" title="Back to this book's contents (chapters and the printed table of contents)">☰ Contents</a>__DIRLINK__<button id="annot" class="anbtn" aria-pressed="false" title="Private notes: highlight and comment on tables. Saved only in this browser.">Notes</button><button id="toggle" title="Toggle light/dark">◐</button></header>
<div id="wrap">
<button id="sideopen" type="button" title="Show the table list" aria-label="Show the table list"></button>
<nav id="side"><div class="ctl">
<input id="q" type="search" placeholder="Search titles, headings, cells…">
<select id="ch"><option value="">All chapters</option></select>
<input type="checkbox" id="flag" hidden>
<div class="keyrow"><span class="keys">↑ ↓ ← → keys: previous / next table · 1 2 3: table / chart / both</span><button id="sidetog" type="button" title="Hide the table list" aria-label="Hide the table list" aria-expanded="true"></button></div>
</div><div id="list"></div></nav>
<main id="main"></main>
<aside id="cmp" hidden></aside>
</div>
<nav id="tfab" aria-label="Scroll the page"><button type="button" class="up" data-go="top" title="Back to the top" aria-label="Back to the top">⤒</button><button type="button" data-go="prev" title="Previous table" aria-label="Previous table">↑</button><button type="button" data-go="next" title="Next table" aria-label="Next table">↓</button></nav>
<script>(function(){const f=document.getElementById("tfab");if(!f)return;
// Narrow screens scroll the window; wider ones scroll #main (the table pane beside the list).
const narrow=()=>matchMedia("(max-width:760px)").matches,M=()=>document.getElementById("main");
const pos=()=>narrow()?scrollY:(M()?M().scrollTop:0);
const t=()=>f.classList.toggle("on",pos()>innerHeight*.6);addEventListener("scroll",t,{passive:true});
document.addEventListener("scroll",e=>{if(e.target&&e.target.id==="main")t()},{passive:true,capture:true});addEventListener("resize",t);t();
// Floating buttons: top / previous table / next table. In a chapter they scroll between its tables (showing
// any not yet loaded) and at either end open the next chapter at its first table or the previous one at its last; with
// one table shown they step through the table list as the arrow keys do, into the next/previous chapter at the ends.
// Scroll el to the top of the scroller and hold it there for 1.5 s while charts and lazy parts above it lay out. Safari
// has no scroll anchoring, so a chart mounting just above the target pushed it down until a late re-align (a visible
// jump, mobile 2026-11-12). Corrections run in requestAnimationFrame and a ResizeObserver, before paint; any touch,
// wheel, mouse or key input lets go.
window.pinTop=el=>{const sc=narrow()?window:M(),off=()=>narrow()||!M()?0:M().getBoundingClientRect().top,ev=["touchstart","wheel","mousedown","keydown"];
 if(window.__pin)window.__pin();let raf=0,ro=null;
 const end=()=>{cancelAnimationFrame(raf);if(ro)ro.disconnect();ev.forEach(n=>removeEventListener(n,end,true));if(window.__pin===end)window.__pin=null};
 const fix=()=>{if(!el.isConnected)return end();const d=el.getBoundingClientRect().top-off();if(Math.abs(d)>1)sc.scrollBy(0,d)};
 el.scrollIntoView({block:"start"});window.__pin=end;
 if(window.ResizeObserver){ro=new ResizeObserver(fix);const b=document.getElementById("chbody");ro.observe(b||M()||document.body)}
 const t0=performance.now(),loop=()=>{fix();if(window.__pin===end)raf=performance.now()-t0<1500?requestAnimationFrame(loop):(end(),0)};raf=requestAnimationFrame(loop);
 ev.forEach(n=>addEventListener(n,end,{capture:true,passive:true}))};
f.addEventListener("click",e=>{const b=e.target.closest("button");if(!b)return;const g=b.dataset.go;
 const sc=narrow()?window:M(),off=()=>narrow()||!M()?0:M().getBoundingClientRect().top;
 if(g==="top"){sc.scrollTo({top:0,behavior:"smooth"});return}
 const down=g==="next";
 if(typeof mode!=="undefined"&&mode==="one"&&typeof stepList==="function"){stepList(down,true);return}
 const all=()=>[...document.querySelectorAll("#main section.tbl")];const ss=all();let c=-1;ss.forEach((x,k)=>{if(x.getBoundingClientRect().top-off()<=8)c=k});
 const atEnd=narrow()?innerHeight+scrollY>=document.documentElement.scrollHeight-4:M().scrollTop+M().clientHeight>=M().scrollHeight-4;
 // tables above may still be laying out (charts, lazy parts), so re-align on the target a few times
 const go=x=>pinTop(x);
 const k=down?(atEnd?ss.length:c+1):c-1;
 if(k>=0&&k<ss.length){go(ss[k]);return}
 // more tables of this chapter not loaded yet: load the next batch and go to its first table
 const mb=down&&document.querySelector("#chmore button");if(mb){const n=ss.length;mb.click();const x=all()[n];if(x){go(x);return}}
 // past either end of a chapter: the next chapter at its first table, or the previous chapter at its last
 const sel=document.getElementById("ch"),opts=sel?[...sel.options].map(o=>o.value).filter(Boolean):[],n=opts.indexOf(sel?sel.value:"")+(down?1:-1);
 if(sel&&sel.value&&n>=0&&n<opts.length){if(typeof enterAt!=="undefined")enterAt=down?"first":"last";location.hash="ch="+encodeURIComponent(opts[n]);
  if(down)setTimeout(()=>{const m=document.getElementById("main");if(m)m.scrollIntoView({block:"start"})},250);return}
 if(!down)sc.scrollTo({top:0,behavior:"smooth"})})})();</script>
__CHARTJS__<script>
const TABLE_TAG_DATA=__TAGDATA__;
const T=__DATA__;
(function(){const set=off=>{document.body.classList.toggle("noside",off);try{localStorage.setItem("sideoff",off?"1":"0")}catch(e){}};
 let off=false;try{off=localStorage.getItem("sideoff")==="1"}catch(e){}set(off);
 document.getElementById("sidetog").onclick=()=>set(true);document.getElementById("sideopen").onclick=()=>set(false)})();
const CHARTIDS=new Set(__CHARTIDS__);let VW="both";try{VW=localStorage.getItem("tview")||"both"}catch(e){}document.body.classList.add("vw-"+VW);
const DIRCARDS=__DIRCARDS__;const DIRSEC=__DIRSEC__;const PY=__PINYIN__;let ALTR=false;try{ALTR=localStorage.getItem("altrom")==="1"}catch(e){}
const pyd=a=>{if(ALTR||!a)return a;const w=a.split(" ")[0];return PY[w]?PY[w]+a.slice(w.length):a};
const pyl=l=>ALTR?l:pyd(l).replace(/\(([^() ]+)\)$/,(m,w)=>PY[w]?`(${PY[w]})`:m);
const HIDEIMG=__HIDEIMG__;
__KANJINUMS__
const KNFULL=__KNFULL__;let NF="a";try{NF=localStorage.getItem("numform")||"a"}catch(e){}
const kn=(s,q)=>NF==="a"?KN(s,KNFULL):s;
const ORIG=__ORIG__;const CITE=__CITE__;
const PTOC=__PTOC__;
const PTK=PTOC.some(e=>e.k);let ptkOn=true;try{ptkOn=localStorage.getItem("ptocTables")!=="0"}catch(e){}
const ptoc=()=>PTOC.length?`<details class="ptoc"><summary>Contents of the printed book (${PTOC.length} entries)${ORIG?` · each links to its page on ${esc(ORIG.l)}`:""}</summary>${PTK?`<label class="ptk"><input type="checkbox" id="ptocT"${ptkOn?" checked":""} onchange="ptocTables(this.checked)"> Include table links <span class="tbadge" style="margin:0 0 0 3px">T</span></label>`:""}<ul${ptkOn?' class="showt"':""}>`+PTOC.map(e=>{const ks=e.k||[],same=ks.length===1?ks.filter(k=>ptLike(k[1],e.t)):ks.filter(k=>ptNorm(k[1])===ptNorm(e.t)),rest=ks.filter(k=>!same.includes(k));
  return `<li class="pl${e.l}">${e.u?`<a href="${esc(e.u)}" target="_blank" rel="noopener"${e.c?` title="No page printed for this section: opens the first page of its chapter"`:""}>${esc(e.t)}</a>`:esc(e.t)}${same.map(k=>`<a class="ptti" href="#${esc(k[0])}" title="Open this table on this site: ${esc(k[1])}"><span class="tbadge">T</span></a>`).join("")}${e.p?`<span class="pp">${esc(e.p)}</span>`:""}</li>`+rest.map(k=>`<li class="ptt pl${Math.min(e.l+1,3)}"><a href="#${esc(k[0])}" title="Open this table on this site"><span class="tbadge">T</span>${esc(k[1])}</a></li>`).join("")}).join("")+`</ul></details>`:"";
// a table whose title is the entry's own title gets only a marker beside the entry (user, 2026-10-22)
// an entry's only table counts as the entry itself unless the titles are radically different
function ptLike(a,b){const x=ptNorm(a),y=ptNorm(b);if(!x||!y||x.includes(y)||y.includes(x))return true;
 // Chinese/Japanese: share half the characters; other scripts: share half the words (3+ letters)
 const cjk=CJK.test(x+y),tok=t=>cjk?[...new Set(ptNorm(t))]:[...new Set(String(t).normalize("NFKC").toLowerCase().match(/[a-z\u00c0-\u024f]{3,}/g)||[])];
 const A=tok(a),B=new Set(tok(b));if(!A.length||!B.size)return false;return A.filter(c=>B.has(c)).length/Math.min(A.length,B.size)>=0.5}
function ptNorm(t){return String(t).normalize("NFKC").replace(/^\s*第[〇零一二三四五六七八九十百千]+表\s*/,"").replace(/^\s*(?:No\.\s*|Table\s+)?[國]?\d+[A-Za-z]?[\s.、:]*/i,"").replace(/[\s、，,.．・:：;；()（）\[\]［］「」『』〔〕\-—–]/g,"").toLowerCase()}
function ptocTables(on){ptkOn=on;document.querySelectorAll(".ptoc ul").forEach(u=>u.classList.toggle("showt",on));try{localStorage.setItem("ptocTables",on?"1":"0")}catch(e){}}
// link to the whole original book (Internet Archive, NDL, …) shown at the top of the contents
const origLink=()=>(ORIG?`<a class="origbtn" href="${esc(ORIG.u)}" target="_blank" rel="noopener">View Original</a>`:"")+(CITE?`<p class="cite"><b>Citation:</b> ${CITE.a?esc(CITE.a)+", ":""}${/[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]/.test(CITE.t)?esc(CITE.t):`<i>${esc(CITE.t)}</i>`} (${esc(CITE.p)})${CITE.u?`. ${esc(CITE.u)}`:""}</p>`:"");
const MARKED=__MARKED__;
const CJK=/[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]/;  // never italicise Asian text (user, 2026-10-22)
const QSTAT=__QSTAT__;
const XL=__XL__;
const FL=__FINDERS__;   // tables whose figures are on a finder page (build/finders/): [[label, href, title]]
const CHEN=__CHEN__;
const chE=(c,cls)=>CHEN[c]?`<span class="${cls||"che"}">${esc(CHEN[c])}</span>`:"";
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const isNum=s=>/^[\s(]*[-—–]?[\d.,]+[)*%]*\s*$/.test(s)||/^[—–-]$/.test(s.trim())||s.trim()==="...";
const warnRe=/not reconcile|unreadable|illegible|uncertain|could not|does not/i;
T.forEach(t=>{t._text=fold([t.title,t.en&&t.en.t,t.en&&t.en.d,t.table_no,t.caption_extra,t.context,t.chapter,...(t.parts||[]).flatMap(p=>[p.label,...p.columns,...p.rows.flat()]),...(t.parts||[]).flatMap(p=>[...p.columns,...p.rows.flat()]).filter(c=>typeof c==="string"&&KN(c,KNFULL)!==c).map(c=>KN(c,KNFULL)),...(t.footnotes||[])].join(" ").toLowerCase());
 t._warn=(t.transcriber_notes||[]).some(n=>warnRe.test(n));});
const chapters=[...new Set(T.map(t=>t.chapter||"(no chapter)"))];
chapters.forEach(c=>$("#ch").insertAdjacentHTML("beforeend",`<option value="${esc(c)}">${esc(c)}${CHEN[c]?" — "+esc(CHEN[c]):""}</option>`));
function label(t){return (t.table_no?`Table ${t.table_no}. `:"")+(t.title||"")+(t.continued?" (continued)":"")}
function renderList(){const q=fold($("#q").value.trim().toLowerCase()),ch=$("#ch").value,fl=$("#flag").checked;let h="",last=null,n=0;
 T.forEach((t,i)=>{if(ch&&(t.chapter||"(no chapter)")!==ch)return;if(fl&&!t._warn)return;if(q&&!q.split(/\s+/).every(w=>t._text.includes(w)))return;
  const c=t.chapter||"(no chapter)";if(c!==last){h+=`<div class="ch" data-ch="${esc(c)}">${esc(c)}${chE(c)}</div>`;last=c}
  h+=`<a href="#${t.id}" data-i="${i}">${esc(label(t))}<small>p. ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":" · "+esc(t.image)}${t._warn?" · ⚠":""}</small></a>`;n++});
 $("#list").innerHTML=h||"<p style='padding:10px'>No matches.</p>";mark()}
function hl(s,q){s=esc(s);if(!q)return s;q.split(/\s+/).filter(Boolean).forEach(w=>{s=s.replace(new RegExp("("+foldRe(w)+")","ig"),"<mark>$1</mark>")});return s}
function csv(t){const L=[];(t.parts||[]).forEach(p=>{if(p.label)L.push([p.label]);L.push(p.columns);p.rows.forEach(r=>L.push(r));L.push([])});
 return L.map(r=>r.map(c=>/[",\n]/.test(c??"")?'"'+String(c).replace(/"/g,'""')+'"':(c??"")).join(",")).join("\n")}
function hasChart(t){return CHARTIDS.has(t.id)&&window.TableCharts&&TableCharts.chartable(t)}
function vsw(){return `<div class="vsw" role="group" aria-label="Show table, chart or both">${[["table","Table"],["chart","Chart"],["both","Both"]].map(([v,l])=>`<button type="button" data-vw="${v}" class="${VW===v?"on":""}">${l}</button>`).join("")}</div>`}
function knHas(t){if(t._kn===undefined)t._kn=(t.parts||[]).some(p=>[...p.columns,...p.rows.flat()].some(c=>typeof c==="string"&&KN(c,KNFULL)!==c));return t._kn}
function nsw(){return `<div class="vsw nsw" role="group" aria-label="Numerals" title="Kanji numerals are shown as Arabic numerals for reading; the data, the downloads and the CSV keep them as printed">${[["a","Arabic"],["p","As printed"]].map(([v,l])=>`<button type="button" data-nf="${v}" class="${NF===v?"on":""}">${l}</button>`).join("")}</div>`}
function setVW(v){VW=v;try{localStorage.setItem("tview",v)}catch(e){}document.body.classList.remove("vw-table","vw-chart","vw-both");document.body.classList.add("vw-"+v);document.querySelectorAll(".vsw button").forEach(b=>b.classList.toggle("on",b.dataset.vw===v));chartsGo()}
function chartsGo(){if(window.TableCharts)TableCharts.mountAll(document.getElementById("main"),id=>T.find(x=>x.id===id),{marked:MARKED})}
// 1, 2, 3: Table, Chart, Both, on views that offer the choice (ignored while typing in a field)
document.addEventListener("keydown",e=>{const v={"1":"table","2":"chart","3":"both"}[e.key];if(!v||e.altKey||e.ctrlKey||e.metaKey||e.repeat)return;
 const ae=document.activeElement;if(ae&&(/INPUT|SELECT|TEXTAREA/.test(ae.tagName)||ae.isContentEditable))return;
 if(document.querySelector(".vsw button[data-vw]"))setVW(v)});
document.addEventListener("click",e=>{const n=e.target.closest(".nsw button");if(n){NF=n.dataset.nf;try{localStorage.setItem("numform",NF)}catch(x){}const m=$("#main"),y=m.scrollTop,w=scrollY;route();m.scrollTop=y;scrollTo(0,w);return}const b=e.target.closest(".vsw button");if(b)setVW(b.dataset.vw)});
// Column headings flattened as "Upper — Lower" are drawn as a multi-row header: neighbouring columns with the same
// upper heading share one cell spanning them, as printed. Display only: the column names themselves are unchanged.
function wcls(c,n,w){return shortLab(c,n,w)?" nw":CJK.test(String(c??""))?" w6":""}
function mapHref(u){const L="https://froginawell.net/reference/japanese-empire/",G="https://kmlawson.github.io/japanese-empire-student-map/";let o=null;try{o=new URLSearchParams(location.search).get("map")}catch(e){}const gh=o?o==="gh":/github\.io$/.test(location.hostname);return gh?u.replace(L,G):u}
function shortLab(c,n,w){const s=String(c??"").trim();if(!s)return false;return CJK.test(s)?s.replace(/\s/g,"").length<=n:s.split(/\s+/).length<=w}
function headHTML(cols,q){const L=cols.map(c=>{const x=String(c??"").split(" — ").filter(y=>y.trim());return x.length?x:[""]}),D=Math.max(1,...L.map(x=>x.length));
 const leaf=(c,j,rs)=>`<th class="sortable${wcls(L[j][L[j].length-1],6,2)}" data-col="${j}"${rs>1?` rowspan="${rs}"`:""} title="${esc(c)} — click to sort">${hl(kn(L[j][L[j].length-1]),q)}</th>`;
 if(D===1)return `<thead><tr>${cols.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(kn(c),q)}</th>`).join("")}</tr></thead>`;
 let h=`<thead class="ml">`;
 for(let r=0;r<D;r++){h+="<tr>";let j=0;
  while(j<L.length){const n=L[j].length;
   if(r===n-1){h+=leaf(cols[j],j,D-n+1);j++;continue}
   if(r>n-1){j++;continue}
   const key=L[j].slice(0,r+1).join(" — ");let k=j+1;
   while(k<L.length&&L[k].length-1>r&&L[k].slice(0,r+1).join(" — ")===key)k++;
   h+=`<th class="grp${wcls(L[j][r],6,2)}"${k-j>1?` colspan="${k-j}"`:""}>${hl(kn(L[j][r]),q)}</th>`;j=k}
  h+="</tr>"}
 return h+"</thead>"}
// links to the scan leaves of a table (top line and foot of every table)
const scanLinks=t=>(t.scans||[]).map(s=>s.url?`<a class="scanlink" href="${s.url}" target="_blank" rel="noopener" title="Open this page of the original scan">${esc(s.label)} ↗</a>`:esc(s.label)).join(" ");
function tableHTML(t,q,other){const ch=!other&&hasChart(t);let h=`<section class="tbl${ch?" hasch":""}" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2>${!other?TableTags.render(TABLE_TAG_DATA[t.id],"../../"):""}${t.en?`<p class="en"><b>${hl(t.en.t,q)}</b>: ${hl(t.en.d,q)} <span class="enn">(Note: LLM translation)</span></p>`:""}<div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":(t.scans||[]).some(s=>s.url)?` · ${scanLinks(t)}`:` · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}`}</div>`+((ch||t.map||knHas(t)||(!other&&FL[t.id]))?`<div class="vrow">${ch?vsw():""}${knHas(t)?nsw():""}${t.map?`<a class="mapbtn" href="${esc(mapHref(t.map))}" target="_blank" rel="noopener" title="Opens the Japanese Empire map in a new tab, with this table's figures by prefecture">View as Map ↗</a>`:""}${(!other&&FL[t.id]||[]).map(f=>`<a class="mapbtn" href="${esc(f[1])}" title="${esc(f[2])}">${esc(f[0])} →</a>`).join("")}</div>`:"");
 if(!other)h+=xlTable(t);
 if(t.caption_extra)h+=CJK.test(t.caption_extra)?`<div class="sub">${hl(t.caption_extra,q)}</div>`:`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 if(t.context)h+=`<p class="ctx"><b>Context.</b> ${hl(t.context,q)}</p>`;
 (t.parts||[]).forEach((p,pi)=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw" data-p="${pi}" tabindex="0"><table>${headHTML(p.columns,q)}<tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?(CJK.test(r[0])?' class="sec cjk"':' class="sec"'):""}>`+r.map((c,j)=>c==="[?]"?`<td class="illeg" title="Unreadable in the scan" aria-label="unreadable"></td>`:`<td class="${j&&isNum(kn(c))?"num":""}${!j?wcls(c,12,3):""}${j&&c===""&&!sec&&!MARKED?" blank":""}"${j&&c===""&&!sec&&MARKED?' title="Blank in the original"':""}>${/^https:\/\/archive\.org\/details\/\S+$/.test(c)?`<a href="${esc(c)}" target="_blank" rel="noopener">scan ↗</a>`:hl(kn(c),q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>";if(ch)h+=`<div class="tchart" data-id="${esc(t.id)}" data-p="${pi}"></div>`});
 if((t.footnotes||[]).length){const fn=t.footnotes.map(n=>hl(n,q)),hit=fn.some(x=>x.includes("<mark>"));h+=`<details class="notes"${hit?" open":""}><summary>Printed notes (${fn.length})</summary><ul>${fn.map(x=>`<li>${x}</li>`).join("")}</ul></details>`;}
 if((t.transcriber_notes||[]).length)h+=`<details class="notes"><summary${t._warn?' class="warn"':""}>Transcriber's notes (${t.transcriber_notes.length})${t._warn?" — includes unreadable or doubtful cells":""}</summary><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></details>`;
 h+=`<div class="row"><button data-act="dl" data-id="${t.id}">Download CSV</button><button data-act="cp" data-id="${t.id}">Copy as TSV</button></div>`;
 if(!HIDEIMG)h+=`<div class="sub">${(t.scans||[]).some(s=>s.url)?"View original source scan:":"Source:"} ${scanLinks(t)}</div>`;
 h+=`</section>`;
 return h}
// Links to the same chapter / the same recurring table in other editions of the series
function xlChapter(ch){const L=XL.ch[ch];if(!L)return "";
 return `<div class="xl xlc">`+L.map(x=>`<div>${L.length>1?esc(x.t)+" in other editions":"This chapter in other editions"}: `+
  x.o.map(o=>o.c.map(c=>`<a href="../${o.s}/#ch=${encodeURIComponent(c)}">${esc(o.e)}${o.c.length>1?" · "+esc(c):""}</a>`).join("")).join("")+`</div>`).join("")+`</div>`}
function xlTable(t){const x=XL.tb[t.id];if(!x||!x.o.length)return "";const g=[];x.o.forEach(o=>{const l=g.find(z=>z.s===o.s);if(l)l.n++;else g.push({...o,n:1})});
 return `<div class="xl">Similar table in other editions: `+g.map(o=>{const lab=o.e+(o.n>1?` (${o.n} parts)`:"");
  return `<span class="xlo"><a href="../${o.s}/#${encodeURIComponent(o.id)}" title="${esc(o.t)}">${esc(lab)}</a><button class="cmpb" data-cmp="${o.s}/${esc(o.id)}" data-for="${esc(t.id)}" title="Show the ${esc(o.e)} table side by side">Compare</button></span>`}).join("")+
  (x.n?`<div class="xln">${esc(x.n)}</div>`:"")+`</div>`}
// Side-by-side comparison with a table from another edition (loaded from ../../data/<slug>.json)
const BOOKDATA={};let cmpS=null,cmpId=null,cmpT=null,cmpE="",cmpJump=false;
function loadBook(s){return BOOKDATA[s]||(BOOKDATA[s]=fetch("../../data/"+s+".json").then(r=>{if(!r.ok)throw r.status;return r.json()}))}
function closeCmp(){cmpS=cmpId=cmpT=null;document.body.classList.remove("cmp");$("#cmp").hidden=true;$("#cmp").innerHTML=""}
async function showCmp(){if(!cmpS||mode!=="one"){closeCmp();return}
 const pane=$("#cmp"),x=XL.tb[cur];document.body.classList.add("cmp");pane.hidden=false;
 const opts=x?x.o:[];const ms=opts.filter(o=>o.s===cmpS);const pick=ms.find(o=>o.id===cmpId)||ms[0];
 const head=`<div class="cmphead"><select id="cmpsel" aria-label="Compare with">${opts.map(o=>`<option value="${o.s}/${esc(o.id)}"${pick&&o.s===pick.s&&o.id===pick.id?" selected":""}>${esc(o.e)} — ${esc(o.t)}${o.p?` (p. ${esc(o.p.split(", ")[0])})`:""}</option>`).join("")}${pick?"":`<option selected>—</option>`}</select><button id="cmpx">Close ✕</button></div>`;
 if(!pick){pane.innerHTML=head+`<p class="sub">${opts.length?`This table has no counterpart in the ${esc(cmpE)} edition; choose another edition above.`:"This table has no counterpart in other editions."}</p>`;return}
 cmpId=pick.id;cmpE=pick.e;pane.innerHTML=head+`<p class="sub">Loading…</p>`;
 try{const T2=await loadBook(pick.s);const t2=T2.find(z=>z.id===pick.id);if(!t2)throw 0;cmpT=t2;
  if(cmpS!==pick.s||cmpId!==pick.id)return;
  pane.innerHTML=head+`<div class="chhead">${esc(pick.e)} edition · <a href="../${pick.s}/#${encodeURIComponent(pick.id)}">open in that book</a></div>`+tableHTML(t2,"",true).replace(' id="t-',' data-x="');
  pane.scrollTop=0;pane.querySelectorAll("table").forEach(initSort);if(innerWidth<=760&&cmpJump){cmpJump=false;pane.scrollIntoView({block:"start"})}}
 catch(e){pane.innerHTML=head+`<p class="sub">Could not load that table (the page must be served from a web server).</p>`}}
$("#cmp").addEventListener("change",e=>{if(e.target.id!=="cmpsel")return;const v=e.target.value,i=v.indexOf("/");cmpS=v.slice(0,i);cmpId=v.slice(i+1);showCmp()});
$("#cmp").addEventListener("click",e=>{if(e.target.id==="cmpx"){closeCmp();return}const b=e.target.closest("button[data-act]");if(b&&cmpT)act(b,cmpT)});
const LLMWARN=`<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of __MODEL__. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>`;
function filtered(){const q=fold($("#q").value.trim().toLowerCase()),ch=$("#ch").value,fl=$("#flag").checked;
 return T.filter(t=>(!ch||(t.chapter||"(no chapter)")===ch)&&(!fl||t._warn)&&(!q||q.split(/\s+/).every(w=>t._text.includes(w))))}
let mode="one",cur=null;
function dirCards(){if(!DIRCARDS)return "";const card=c=>`<a class="chbtn" href="directory.html#s=${encodeURIComponent(c.s)}">${esc(c.l)}<small>${c.n.toLocaleString()} entr${c.n===1?"y":"ies"}</small></a>`;
 const pl=DIRCARDS.places.map(x=>({...x,l:pyd(x.l)})),bg=DIRCARDS.big||0;
 return `<h2 style="margin:0 0 6px">Directory</h2><div class="chsum">${DIRCARDS.total.toLocaleString()} directory entries. Choose a place or a list. Place names are in pinyin; the directory page has a toggle for the book's own romanization.</div><h3 style="margin:14px 0 8px">Places</h3><div class="chgrid" style="--chfs:15px">`+pl.slice(0,bg).concat(pl.slice(bg).sort((x,y)=>x.l.localeCompare(y.l))).map(card).join("")+`</div>`+(DIRCARDS.other.length?`<h3 style="margin:20px 0 8px">Other lists</h3><div class="chgrid" style="--chfs:15px">`+DIRCARDS.other.map(x=>card({...x,l:pyl(x.l)})).join("")+`</div>`:"")}
function dirSec(top){if(!DIRSEC)return "";const g=DIRSEC.groups;
 return `<h2 style="margin:${top?0:28}px 0 6px">Directory</h2><div class="chsum">${DIRSEC.total.toLocaleString()} directory entr${DIRSEC.total===1?"y":"ies"}${g.length>1?` in ${g.length} sections`:""}. Choose a section to open the directory.</div><div class="chgrid" style="--chfs:15px">`+
  g.map(c=>`<a class="chbtn" href="directory.html${c.s?"#s="+encodeURIComponent(c.s):""}">${esc(c.l)}<small>${c.n.toLocaleString()} entr${c.n===1?"y":"ies"}</small></a>`).join("")+`</div>`}
function showHome(){mode="home";cur=null;closeCmp();const n={};T.forEach(t=>{const c=t.chapter||"(no chapter)";n[c]=(n[c]||0)+1});
 if(DIRCARDS){$("#main").innerHTML=`<div class="chhead">Contents</div>`+origLink()+QSTAT+ptoc()+dirCards()+`<h2 style="margin:28px 0 6px">Tables</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} section${chapters.length===1?"":"s"}. Choose a section, or pick a single table from the list.</div><div class="chgrid" style="--chfs:15px">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+LLMWARN;$("#main").scrollTop=0;mark();anSync();return}
 $("#main").innerHTML=`<div class="chhead">Contents</div>`+origLink()+QSTAT+ptoc()+(DIRSEC&&DIRSEC.first?dirSec(true):"")+`<h2 style="margin:${DIRSEC&&DIRSEC.first?28:0}px 0 6px">Chapters</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} chapter${chapters.length===1?"":"s"}. Choose a chapter, or pick a single table from the list.</div><div class="chgrid" id="chgrid">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+dirCards()+(DIRSEC&&!DIRSEC.first?dirSec(false):"")+LLMWARN;
 $("#main").scrollTop=0;fitGrid();mark();anSync()}
// Desktop: pick the largest button font (12-28px) at which every chapter button fits in the pane without scrolling
function fitGrid(){const g=$("#chgrid");if(!g)return;g.style.removeProperty("--chfs");if(innerWidth<=760)return;
 const m=$("#main"),limit=()=>m.getBoundingClientRect().bottom-parseFloat(getComputedStyle(m).paddingBottom);
 const fits=x=>{g.style.setProperty("--chfs",x+"px");return g.getBoundingClientRect().bottom<=limit()};
 let lo=12,hi=28;if(fits(hi))return;if(!fits(lo))return;
 for(let k=0;k<9;k++){const mid=(lo+hi)/2;if(fits(mid))lo=mid;else hi=mid}
 g.style.setProperty("--chfs",lo.toFixed(2)+"px")}
let fitRaf=0;addEventListener("resize",()=>{if(mode!=="home"||DIRCARDS)return;cancelAnimationFrame(fitRaf);fitRaf=requestAnimationFrame(fitGrid)});
// On narrow screens (single-column layout, <=760px) the window scrolls, not #main: bring the top of #main into view.
function mainTop(){const m=$("#main");m.scrollTop=0;if(matchMedia("(max-width:760px)").matches){const y=m.getBoundingClientRect().top+scrollY;if(scrollY>y||scrollY<y-innerHeight/2)scrollTo(0,y)}}
function showOne(id){const t=T.find(x=>x.id===id)||T[0];if(!t){$("#main").innerHTML="<p>No tables yet.</p>";return}
 mode="one";cur=t.id;$("#main").innerHTML=tableHTML(t,$("#q").value.trim())+LLMWARN;mainTop();
 document.querySelectorAll("#main table").forEach(initSort);chartsGo();mark();if(cmpS)showCmp();anSync()}
const CH_BUDGET=30000;function tCells(t){return (t.parts||[]).reduce((a,p)=>a+(p.rows||[]).length*Math.max(1,(p.columns||[]).length),0)}
function showChapter(ch){const q=$("#q").value.trim();const ts=filtered();mode="chapter";cur=null;closeCmp();
 let h=`<div class="chhead"><a href="#">All chapters</a> · Chapter</div><h2 style="margin-bottom:6px">${esc(ch)}${chE(ch,"che2")}</h2><div class="chsum">${ts.length} table${ts.length===1?"":"s"}${$("#flag").checked||q?" matching the current filters":""}</div>`+xlChapter(ch);
 let ci=0;const batch=()=>{let s="",c=0;while(ci<ts.length&&(c===0||c+tCells(ts[ci])<=CH_BUDGET)){c+=tCells(ts[ci]);s+=tableHTML(ts[ci],q);ci++}return s};
 const more=()=>ci<ts.length?`<p id="chmore"><button type="button">Show more tables (${ts.length-ci} of ${ts.length} not shown yet)</button></p>`:"";
 h+=(ts.length?`<div id="chbody">${enterAt==="last"?(()=>{let s="";while(ci<ts.length)s+=batch();return s})():batch()}</div>${more()}`:"<p>No tables match.</p>")+LLMWARN;
 $("#main").innerHTML=h;mainTop();document.querySelectorAll("#main table").forEach(initSort);chartsGo();
 const wire=()=>{const b=document.querySelector("#chmore button");if(!b)return;b.onclick=()=>{const tmp=document.createElement("div");tmp.innerHTML=batch();const nodes=[...tmp.children];document.getElementById("chbody").append(...nodes);nodes.forEach(n=>n.querySelectorAll("table").forEach(initSort));document.getElementById("chmore").outerHTML=more();chartsGo();mark();wire()}};wire();
 if(enterAt&&ts.length){const t=enterAt==="first"?ts[0]:ts[ts.length-1];cur=t.id;const el=document.getElementById("t-"+t.id);if(el&&enterAt==="last")pinTop(el)
  listShow(document.querySelector(`#list a[href="#${CSS.escape(t.id)}"]`))}
 enterAt=null;mark();anSync()}
let enterAt=null;
// #<table id>~<part>.<row>.<col> (links from the Population page): open the table and mark that cell
function hlCell(p,r,c){const tw=document.querySelector(`#main .tw[data-p="${p}"]`);const tr=tw&&tw.querySelector(`tr[data-i="${r}"]`);if(!tr)return;
 tr.classList.add("hlrow");const td=tr.children[c];if(td)td.classList.add("hlcell");setTimeout(()=>(td||tr).scrollIntoView({block:"center",inline:"center"}),30)}
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h.startsWith("an=")){anLink(h.slice(3));return}
 const hc=h.match(/^(.+)~(\d+)\.(\d+)\.(\d+)$/);if(hc&&T.some(x=>x.id===hc[1])){showOne(hc[1]);hlCell(+hc[2],+hc[3],+hc[4]);return}
 // a cell address that cannot be read still opens its table, never the book's first one
 const hx=h.indexOf("~");if(hx>0&&T.some(x=>x.id===h.slice(0,hx))){showOne(h.slice(0,hx));return}
 if(h.startsWith("ch=")){const ch=h.slice(3);if($("#ch").value!==ch){$("#ch").value=ch;renderList()}showChapter(ch);return}
 if(mode==="chapter"&&h&&document.getElementById("t-"+h)){cur=h;pinTop(document.getElementById("t-"+h));mark();return}
 if(h==="toc"){if($("#ch").value){$("#ch").value="";renderList()}showHome();const d=document.querySelector("#main details.ptoc");if(d){d.open=true;[0,80,400].forEach(ms=>setTimeout(()=>d.scrollIntoView({block:"start"}),ms))}return}
 if(!h){if($("#ch").value){$("#ch").value="";renderList()}if(T.length){showHome();return}}
 showOne(h)}
$("#main").addEventListener("click",e=>{const c=e.target.closest("button.cmpb");
 if(c){const v=c.dataset.cmp,i=v.indexOf("/");cmpS=v.slice(0,i);cmpId=v.slice(i+1);cmpJump=true;
  // open the single-table view directly: in chapter view a hash change would only scroll to the table
  if(mode==="one"&&cur===c.dataset.for)showCmp();else{if(decodeURIComponent(location.hash.slice(1))!==c.dataset.for)history.pushState(null,"","#"+c.dataset.for);showOne(c.dataset.for)}return}
 const b=e.target.closest("button[data-act]");if(!b)return;const t=T.find(x=>x.id===b.dataset.id);if(t)act(b,t)});
function act(b,t){
 if(b.dataset.act==="dl"){const bl=new Blob(["﻿"+csv(t)],{type:"text/csv"});const a=document.createElement("a");a.href=URL.createObjectURL(bl);a.download=t.id+".csv";a.click()}
 else navigator.clipboard.writeText((t.parts||[]).map(p=>[p.columns,...p.rows].map(r=>r.join("\t")).join("\n")).join("\n\n"))}
$("#list").addEventListener("click",e=>{const c=e.target.closest(".ch");if(!c)return;location.hash="ch="+encodeURIComponent(c.dataset.ch||c.textContent)});
// Arrow keys: previous/next table in the sidebar list (ignored while typing in a field). With the focus in a table that
// scrolls on that key's axis, the key scrolls the table instead; a table that fits has nothing to scroll, so it browses.
document.addEventListener("keydown",e=>{if(!["ArrowDown","ArrowUp","ArrowLeft","ArrowRight"].includes(e.key))return;if(e.altKey||e.ctrlKey||e.metaKey)return;
 const ae=document.activeElement,tag=(ae&&ae.tagName)||"";if(/INPUT|SELECT|TEXTAREA/.test(tag))return;
 const tw=ae&&ae.closest&&ae.closest(".tw");if(tw&&(/Left|Right/.test(e.key)?tw.scrollWidth>tw.clientWidth:tw.scrollHeight>tw.clientHeight))return;
 document.body.classList.add("kbd");
 if(stepList(e.key==="ArrowDown"||e.key==="ArrowRight"))e.preventDefault()});
// Previous/next table in the sidebar list; at either end of a chapter's list, step into the next/previous chapter
// (entering it at its first or last table). Returns true when it moved. fab: called from the mobile buttons.
function stepList(down,fab){const links=[...document.querySelectorAll("#list a[href^='#']")];if(!links.length)return false;
 let i=links.findIndex(a=>a.classList.contains("on"));const ch=$("#ch").value;
 if(ch&&i>-1&&((down&&i===links.length-1)||(!down&&i===0))){
  const opts=[...$("#ch").options].map(o=>o.value).filter(Boolean);const k=opts.indexOf(ch)+(down?1:-1);
  if(k>=0&&k<opts.length){enterAt=down?"first":"last";location.hash="ch="+encodeURIComponent(opts[k]);return true}
  return false}
 i=i<0?(down?0:links.length-1):Math.min(links.length-1,Math.max(0,i+(down?1:-1)));
 location.hash=links[i].getAttribute("href").slice(1);if(!fab)listShow(links[i]);return true}
// Bring a sidebar link into view by scrolling the list only: scrollIntoView also scrolls the window, which on phones
// (list stacked above the tables) jumped the page up to the list and back (2026-11-12).
function listShow(a){const L=$("#list");if(!a||!L)return;const lr=L.getBoundingClientRect(),r=a.getBoundingClientRect();
 if(r.top<lr.top)L.scrollTop+=r.top-lr.top;else if(r.bottom>lr.bottom)L.scrollTop+=r.bottom-lr.bottom}
document.addEventListener("mousemove",()=>document.body.classList.remove("kbd"));
// Click-to-sort: asc -> desc -> original. Numeric-aware; blanks/dashes last; total rows pinned;
// sorting happens within blocks delimited by section-heading rows.
const pinRe=/^\s*(grand\s+)?(total|totals|sum|average|mean)\b/i;
function sortVal(s){s=(s||"").trim();if(s===""||/^[—–\-.…]+$/.test(s))return null;
 const neg=/^\(.*\)$/.test(s)||/^[-−–]\s*\d/.test(s);const n=s.replace(/[,\s¥$£%*†‡()]/g,"").replace(/^[-−–]/,"");
 if(/^\d+(\.\d+)?$/.test(n))return (neg?-1:1)*parseFloat(n);return s.toLowerCase()}
function cmp(a,b){if(a===null&&b===null)return 0;if(a===null)return 1;if(b===null)return -1;
 if(typeof a==="number"&&typeof b==="number")return a-b;return String(a).localeCompare(String(b),undefined,{numeric:true})}
function initSort(tbl){const ths=[...tbl.querySelectorAll("th.sortable")];
 ths.forEach(th=>th.addEventListener("click",()=>{const col=+th.dataset.col;const cur=th.getAttribute("aria-sort");
  const next=cur==="ascending"?"descending":cur==="descending"?null:"ascending";
  ths.forEach(x=>x.removeAttribute("aria-sort"));if(next)th.setAttribute("aria-sort",next);
  const tb=tbl.tBodies[0];const rows=[...tb.rows];const blocks=[[]];
  rows.sort((a,b)=>a.dataset.i-b.dataset.i).forEach(r=>{if(r.classList.contains("sec")){blocks.push([r]);blocks.push([])}else blocks[blocks.length-1].push(r)});
  const out=[];blocks.forEach(bl=>{if(bl.length&&bl[0].classList.contains("sec")){out.push(...bl);return}
   if(!next){out.push(...bl);return}
   const pinned=bl.filter(r=>pinRe.test(r.cells[0].textContent)),body=bl.filter(r=>!pinRe.test(r.cells[0].textContent));
   body.sort((a,b)=>{const va=sortVal(a.cells[col].textContent),vb=sortVal(b.cells[col].textContent);
    if(va===null||vb===null)return cmp(va,vb);const c=cmp(va,vb);return next==="ascending"?c:-c});
   out.push(...body,...pinned)});
  out.forEach(r=>tb.appendChild(r))}))}
function mark(){const id=cur||decodeURIComponent(location.hash.slice(1));document.querySelectorAll("#list a").forEach(a=>a.classList.toggle("on",a.getAttribute("href")==="#"+id))}
$("#ch").addEventListener("input",()=>{renderList();const ch=$("#ch").value;
 if(ch)location.hash="ch="+encodeURIComponent(ch);else{history.replaceState(null,"",location.pathname);showHome()}});
["q","flag"].forEach(k=>$("#"+k).addEventListener("input",()=>{renderList();if(mode==="chapter")showChapter($("#ch").value)}));
window.addEventListener("hashchange",route);
function goHome(){if(location.hash)history.pushState(null,"",location.pathname+location.search);route();scrollTo(0,0);const m=$("#main");if(m)m.scrollTop=0}
$("#toggle").onclick=()=>{const r=document.documentElement,d=r.dataset.theme==="dark"||(!r.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);r.dataset.theme=d?"light":"dark";anSync(true)};
function anView(){return mode==="one"?cur||"":mode==="chapter"?"ch="+$("#ch").value:""}
function anGo(v){history.replaceState(null,"",location.pathname+(v?"#"+v:""));route()}
const AN_AREA="#main",AN_NOTE="anything you want to check or remember. Select text to highlight it, or drop a pin, and add a comment. Notes belong to the view you make them in (one table, or a whole chapter) and are kept only in this browser; Download saves a copy you can keep or send.";
/*__ANNOT_JS__*/
renderList();route();
try{if(localStorage.getItem("stat-notes")==="1")anSet(true)}catch(e){}
</script>
</body>
</html>
"""


# Notes (annotate.js) is switched off for now (user, 2026-10-10): no button, no loader; set True to bring it back.
NOTES_ENABLED = False
ANNOT_OFF_JS = "function anSync(){}function anSet(){}function anLink(){anGo(null)}"


def notes_layer(tpl):
    if NOTES_ENABLED:
        return tpl.replace("/*__ANNOT_JS__*/", ANNOT_JS)
    return re.sub(r'<button id="annot"[^>]*>Notes</button>', "", tpl).replace("/*__ANNOT_JS__*/", ANNOT_OFF_JS)


TEMPLATE = notes_layer(TEMPLATE)

def dir_key(f):
    mp = re.match(r"p(\d)-(\d+)", os.path.basename(f))
    if mp:
        return int(mp.group(1)) * 10000 + int(mp.group(2))
    m = re.search(r"(\d+)", os.path.basename(f))
    return int(m.group(1)) if m else 0


def section_summary(names, last=False):
    """': A, B, C.' from appendix/chapter names, shortened to their top-level part, at most four."""
    parts = []
    for a in names:
        a = re.sub(r"^(Appendix|App\.|Chapter|Ch\.|Table)\s*[A-Z0-9]+\s*[:.—-]\s*", "", a or "").strip()
        if not last:
            a = re.split(r" — |: ", a)[0]
        a = a.strip("[] .")
        if a and a not in parts:
            parts.append(a)
    if not parts:
        return "."
    return ": " + ", ".join(parts[:4]) + (", etc." if len(parts) > 4 else ".")


BIG_PLACES = ["Hsinking", "Harbin", "Dairen", "Mukden", "Kirin"]


def dir_section(book, tables):
    """JSON for the "Directory" section on a book's home page (books without "dir_cards"): one chapter-style card
    per directory section, and whether the section goes before the chapters. It goes first when the directory
    covers more scan pages than the tables do, or when the book sets "dir_first" (user, 2026-11-06)."""
    f = os.path.join(HERE, "data", book["slug"] + "-directory.json")
    if book.get("dir_cards") or not os.path.exists(f):
        return "null"
    es = json.load(open(f, encoding="utf-8"))
    if not es:
        return "null"
    from collections import Counter
    groups = Counter(e.get("a") or "" for e in es)
    dir_leaves = {e.get("u") for e in es if e.get("u")}
    table_leaves = {i for t in tables for i in (t.get("images") or [t.get("image")]) if i}
    out = {"total": len(es), "first": bool(book.get("dir_first")) or len(dir_leaves) > len(table_leaves),
           "groups": [{"l": a or "Directory", "s": "A:" + a if a else "", "n": n} for a, n in groups.items()]}
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")


def dir_cards(book):
    """JSON for the 'Directory' cards on a book's home page (books with "dir_cards": True): places first
    (largest cities first, then A–Z), then other lists (non-place groups and sub-headings within places)."""
    f = os.path.join(HERE, "data", book["slug"] + "-directory.json")
    if not book.get("dir_cards") or not os.path.exists(f):
        return "null"
    es = json.load(open(f, encoding="utf-8"))
    from collections import Counter
    groups, subs = Counter(e["a"] for e in es), Counter((e["a"], e["s"]) for e in es if e["s"])
    places = [a for a in groups if a.split(" ")[0] in book.get("dir_places", [])]
    rank = lambda a: (BIG_PLACES.index(a.split(" ")[0]) if a.split(" ")[0] in BIG_PLACES else 99, a)
    out = {"total": len(es), "big": sum(1 for a in places if a.split(" ")[0] in BIG_PLACES), "places": [{"l": a, "s": "A:" + a, "n": groups[a]} for a in sorted(places, key=rank)], "other": []}
    for a in sorted(set(groups) - set(places)):
        out["other"].append({"l": a, "s": "A:" + a, "n": groups[a]})
    for (a, s2), k in sorted(subs.items(), key=lambda x: (rank(x[0][0]), x[0][1])):
        if a in places:
            out["other"].append({"l": f"{s2} ({a.split(' ')[0]})", "s": f"G:{a} — {s2}", "n": k})
    return json.dumps(out, ensure_ascii=False).replace("</", "<\\/")


def build_directory(book):
    """Write <slug>/directory.html from <dir>/_work/directory/*.json; return the entry count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "directory", "*.json")), key=dir_key)
    entries = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                d = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            print("skipped", f)
            continue
        leaf = d.get("leaf") or os.path.basename(f)[:-5]
        scan = scan_links(book, {"images": [leaf]})[0]
        city = d.get("city") or {}
        city = city if isinstance(city, dict) else {"en": city}
        for e in d.get("entries", []):
            if e.get("en") or e.get("ja"):  # bilingual directory entry: English and Japanese blocks of one firm
                en, ja = e.get("en") or {}, e.get("ja") or {}
                flat = lambda v: "; ".join(map(str, v)) if isinstance(v, list) else str(v)
                side = lambda x: " · ".join(flat(x[k]) for k in ("business", "tel", "address", "person", "other") if x.get(k))
                names = " / ".join(flat(x["name"]) for x in (en, ja) if x.get("name")) or "[continued]"
                if e.get("no"):  # numbered firms (indexes refer to the number)
                    names = f'{e["no"]}. {names}'
                txt = " ‖ ".join(t for t in (side(en), side(ja)) if t)
                if e.get("note"):
                    txt += f" [note: {e['note']}]"
                ec = e.get("city") or city
                ec = ec if isinstance(ec, dict) else {"en": ec}
                place = " ".join(v for v in (ec.get("en"), ec.get("ja")) if v) or d.get("appendix") or ""
                sec = e.get("section") or ""
                if sec.isupper():
                    sec = re.sub(r"\b(Of|And|The|In|For|To|At|On)\b", lambda m: m.group(1).lower(), sec.title())
                    sec = sec[:1].upper() + sec[1:]
                if sec.startswith("German Firms"):  # a list of its own, grouped by city
                    place, sec = sec, place
                entries.append({"a": place, "s": sec, "n": names, "t": txt, **({"no": str(e["no"])} if e.get("no") else {}),
                                "ne": flat(en.get("name") or ""), "te": side(en), "nj": flat(ja.get("name") or ""), "tj": side(ja),
                                "p": e.get("page") or ", ".join(d.get("printed_pages") or []), "l": scan["label"], "u": scan["url"]})
                continue
            sec = e.get("section") or ""
            if sec.isupper():
                sec = sec.title()
            app = e.get("appendix") or d.get("appendix") or ""
            entries.append({"a": app, "s": sec, **({"k": "i"} if book.get("dir_index") and app.startswith(book["dir_index"]) else {}), "n": (e.get("name") or "").rstrip(" ,.") + (" " + e["mark"] if e.get("mark") else "") + (f' ({e["rank"]})' if e.get("rank") else ""),
                            "t": e.get("text") or "", "p": e.get("page") or ", ".join(d.get("printed_pages") or []),
                            "l": scan["label"], "u": scan["url"],
                            # optional: the entry's printed fields as [label, value] pairs and its descriptive text,
                            # shown one field per line under bold labels ("t" keeps everything, for search)
                            **({"f": e["fields"]} if e.get("fields") else {}), **({"d": e["description"]} if e.get("description") else {})})
    committed = os.path.join(HERE, "data", book["slug"] + "-directory.json")
    if not files and os.path.exists(committed):  # book folder not on this machine: rebuild the page from the committed data
        with open(committed, encoding="utf-8") as fh:
            entries = json.load(fh)
    if not entries:
        return 0
    if DIR_FIELDS.get(book["slug"]):
        n = split_fields(entries, DIR_FIELDS[book["slug"]])
        print(f"  {book['slug']}: {n:,} directory entries shown as labelled fields")
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(committed, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    desc = f"{len(entries):,} entries" + section_summary(e["a"] for e in entries)
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__PLACES__", json.dumps(book.get("dir_places", []))).replace("__DIRCARDS__", dir_cards(book)).replace("__PINYIN__", json.dumps(book.get("dir_pinyin", {}), ensure_ascii=False)).replace("__COUNT__", f"{len(entries):,}").replace("__DESC__", html.escape(desc))
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"]).replace("__MODEL__", book.get("model", "Opus 5.5"))
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("dir_in_progress") else "")
           .replace("__MD__", f' · <a href="../../{dl(book["slug"], "directory.md")}" download>Markdown</a>' if dl(book["slug"], "directory.md") else ""))
    if book.get("dir_only"):  # no tables page: drop the link to it and give the book's description here instead
        doc = doc.replace('<a href="./" style="text-decoration:none;font-size:14px">← Tables</a><a href="../../" style="text-decoration:none;font-size:14px">All books</a>',
                          '<a href="../../" style="text-decoration:none;font-size:14px">← All books</a>', 1)
        about = "".join(f"<p>{html.escape(book[k])}</p>" for k in ("blurb", "gaps") if book.get(k))
        sub = f'<p>{html.escape(book["subtitle"])} · {html.escape(book["publisher"])}</p>' if book.get("subtitle") else ""
        ptoc = printed_toc(book)
        # one block per top-level entry (with its sub-entries), so a column break never separates a heading from its items
        groups = []
        for o in ptoc:
            line = (f'<div style="padding-left:{(o["l"]-1)*1.3+1.2}em;text-indent:-1.2em">' + (f'<a href="{o["u"]}" target="_blank" rel="noopener">{html.escape(o["t"])}</a>' if o.get("u") else html.escape(o["t"]))
                    + (f' <span style="color:var(--muted)">{html.escape(str(o["p"]))}</span>' if o.get("p") else "") + "</div>")
            if o["l"] <= 1 or not groups: groups.append([])
            groups[-1].append(line)
        tl = "".join('<li style="break-inside:avoid;margin:0 0 6px">' + "".join(g) + "</li>" for g in groups)
        ctoc = f'<details class="ctoc" style="margin:0 0 14px;font-size:15px"><style>.ctoc a{{color:var(--accent);text-decoration:none}}.ctoc a:hover{{text-decoration:underline}}</style><summary>Contents of the printed book</summary><ul style="list-style:none;padding-left:0;columns:18em;column-gap:28px;margin:8px 0">{tl}</ul></details>' if ptoc else ""
        ci = citation(book)
        ol = orig_link(book)
        cite = ((f'<a class="origbtn" href="{html.escape(ol["u"])}" target="_blank" rel="noopener" style="display:inline-block;margin:4px 0 8px;padding:6px 12px;border:1px solid var(--accent);border-radius:6px;color:var(--accent);text-decoration:none">View Original</a>' if ol else "")
                + f'<p style="font-size:13.5px;color:var(--muted);margin:0 0 12px;overflow-wrap:anywhere"><b style="color:var(--ink);font-weight:600">Citation:</b> '
                + (html.escape(ci["a"]) + ", " if ci["a"] else "") + (html.escape(ci["t"]) if CJK_RE.search(ci["t"]) else f'<i>{html.escape(ci["t"])}</i>') + f' ({html.escape(ci["p"])})'
                + (f'. {html.escape(ci["u"])}' if ci["u"] else "") + "</p>")
        doc = doc.replace('<main><div id="toc">', f'<main>{cite}<details style="margin:0 0 8px;font-size:15px"><summary>About this book</summary>{sub}{about}</details>{ctoc}<div id="toc">', 1)
    with open(os.path.join(HERE, "book", book["slug"], "directory.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(entries)} directory entries")
    return len(entries)


def build_chronology(book):
    """Write <slug>/chronology.html from <dir>/_work/chronology/*.json (events lists); return the event count."""
    files = sorted(glob.glob(os.path.join(book_dir(book), "_work", "chronology", "*.json")), key=dir_key)
    events = []
    for f in files:
        try:
            with open(f, encoding="utf-8") as fh:
                c = json.load(fh)
        except (FileNotFoundError, json.JSONDecodeError):
            continue
        scan = scan_links(book, {"images": [c.get("image") or os.path.basename(f)[:-5].split("_")[0]]})[0]
        head = " — ".join(x for x in (c.get("chapter"), c.get("title")) if x)
        for e in c.get("events", []):
            events.append({"a": head, "s": "", "n": e.get("date") or "", "t": e.get("text") or "",
                           "p": e.get("page") or ", ".join(c.get("printed_pages") or []), "l": scan["label"], "u": scan["url"]})
    committed = os.path.join(HERE, "data", book["slug"] + "-chronology.json")
    if not files and os.path.exists(committed):  # book folder not on this machine: rebuild the page from the committed data
        with open(committed, encoding="utf-8") as fh:
            events = json.load(fh)
    if not events:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(committed, "w", encoding="utf-8") as fh:
        json.dump(events, fh, ensure_ascii=False, indent=1)
    data = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__PLACES__", "[]").replace("__DIRCARDS__", "null").replace("__PINYIN__", "{}").replace("__COUNT__", f"{len(events):,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"]).replace("__MODEL__", book.get("model", "Opus 5.5"))
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("in_progress") else "")
           .replace("· Directories", "· Chronologies").replace("-directory.json", "-chronology.json")
           .replace(" entries", " events").replace("Filter names, places, firms, words…", "Filter dates, names, places, words…")
           .replace("> names only<", "> dates only<").replace("These entries were", "These events were")
           .replace("__MD__", f' · <a href="../../{dl(book["slug"], "chronology.md")}" download>Markdown</a>' if dl(book["slug"], "chronology.md") else "")
           .replace("__DESC__", html.escape(f"{len(events):,} events" + section_summary((e["a"].split(" — ")[-1] for e in events), last=True))))
    if book["slug"].startswith("japan-"):
        doc = doc.replace('<main><div id="out">', '<main><p style="margin:0 0 14px;font-size:15px">See also <a style="color:var(--accent)" href="https://froginawell.net/reference/empire-chronicle/">Chronicles of the Japanese Empire</a>.</p><div id="out">', 1)
    with open(os.path.join(HERE, "book", book["slug"], "chronology.html"), "w", encoding="utf-8") as fh:
        fh.write(doc)
    print(f"{book['slug']}: {len(events)} chronology events")
    return len(events)


DIRTEMPLATE = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<script src="../../fold.js"></script>
<title>__BOOK__ · Directories</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman","Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a,header .meta{color:var(--accent-ink)!important;opacity:.88}
header h1{font-size:20px;margin:0;font-weight:normal}
header .meta{font-size:13px}
header button{margin-left:auto;background:transparent;color:var(--accent-ink);border-color:currentColor}
.bar{position:sticky;top:0;z-index:2;background:var(--bg);border-bottom:1px solid var(--line)}
.bar>div{max-width:900px;margin:0 auto;padding:12px 16px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.bar select{max-width:100%}
input,select,button{font:inherit;font-size:14px;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#q{flex:1 1 260px;font-size:16px}
#cnt{color:var(--muted);font-size:13px;width:100%}
main{max-width:900px;margin:0 auto;padding:10px 16px 60px}
.sec{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:22px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.e{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:9px 12px;margin:0 0 8px}
.e b{font-size:15.5px}
.e .t{font-size:14.5px}
.e .fl{font-size:14px;margin:4px 0 0;line-height:1.4}.e .fl>div{padding-left:1.2em;text-indent:-1.2em}.e .dsc{font-size:14.5px;margin:6px 0 0}
#toc h2{margin:4px 0 6px;font-size:20px}#toc h3{margin:14px 0 8px;font-size:16px}
.tocgrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,190px),1fr));gap:8px;margin-bottom:6px}
.tocbtn{display:block;padding:8px 10px;border:1px solid var(--line);border-radius:6px;background:var(--panel);color:var(--ink);text-decoration:none;font-weight:bold;font-size:15px;line-height:1.25}
.tocbtn:hover{border-color:var(--accent)}.tocbtn small{display:block;color:var(--muted);font-weight:normal;font-size:12px;margin-top:2px}
.e .l2{margin-top:2px}
.e .m{font-size:12.5px;color:var(--muted);margin-top:3px}
.e .m a{color:var(--accent)}
mark{background:#f3e3a0;color:inherit}
:root[data-theme="dark"] mark{background:#5a4d1c}
#more{display:block;margin:14px auto}#more[hidden]{display:none}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);font-size:14px}
.anbtn{margin-left:auto;font:inherit;font-size:14px;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:5px;padding:5px 12px;cursor:pointer;align-self:center}.anbtn[aria-pressed="true"]{background:var(--accent-ink);color:var(--accent)}.anbtn+#toggle{margin-left:0}
.an-unanchored-pill{display:none!important}
@media (max-width:640px){html body #__an_bar.an-right,html body #__an_bar.an-left{flex-direction:row;left:0;right:0;margin:0 auto;width:max-content;max-width:calc(100vw - 12px);transform:none;bottom:10px;gap:2px;padding:5px}html body #__an_bar .an-btn,html body #__an_colorbtn{width:min(36px,calc((100vw - 44px)/9.5));height:36px}html body #__an_bar .an-sep{width:1px;height:24px;margin:0 2px}html body #__an_bar #__an_colorpop{right:auto;left:50%;transform:translateX(-50%);bottom:52px;top:auto;width:max-content}body.notes-on{padding-bottom:70px}}
</style></head><body>
<header><a href="./" style="text-decoration:none;font-size:14px">← Tables</a><a href="../../" style="text-decoration:none;font-size:14px">All books</a><h1>__BOOK__ · Directories</h1>
<span class="meta">__DESC____PROG__ · LLM-transcribed · <a href="../../data/__SLUG__-directory.json">JSON</a>__MD__</span>
<button id="annot" class="anbtn" aria-pressed="false" title="Private notes: highlight and comment on entries. Saved only in this browser.">Notes</button><button id="toggle" title="Toggle light/dark">◐</button></header>
<div class="bar"><div>
<input id="q" type="search" placeholder="Filter names, places, firms, words…" autofocus>
<select id="ap"><option value="">All sections</option></select>
<label style="font-size:13px" title="Show only the names, and search only in names"><input type="checkbox" id="nameonly"> names only</label>
<label style="font-size:13px" id="jflab" hidden><input type="checkbox" id="jafirst"> 日本語 first</label>
<label style="font-size:13px" id="arlab" hidden><input type="checkbox" id="altrom"> alt. romanization</label>
<div id="cnt"></div></div></div>
<style>.ixb{column-width:15em;column-gap:22px;margin:4px 0 6px;font-size:14.5px;line-height:1.35}.ix{break-inside:avoid;padding:1px 0}.ix a{color:var(--accent)}.ixp{font-size:13px;color:var(--muted);margin:0 0 18px}.ixp a{color:var(--accent)}.e.hit{outline:2px solid var(--accent)}.fno{font-weight:bold;color:var(--muted)}#out.nonly .e .t{display:none}#out.nonly .e{padding-top:4px;padding-bottom:4px}</style>
<main><div id="toc"></div><div id="out"></div><button id="more" hidden>Show more</button>
<div class="llmwarn" role="note"><b>Warning:</b> These entries were transcribed by the vision model of __MODEL__. Before using any of them, you must verify specific details with the original source which is linked to whenever possible.</div></main>
<script>
const E=__DATA__;
const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>fold(s.normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase());
E.forEach(e=>{e._n=norm(e.n);e._all=norm(e.n+" "+e.t+" "+e.s)});
const groups=[...new Set(E.map(e=>e.a+(e.s?" — "+e.s:"")))];
const PLACES=__PLACES__;const DC=__DIRCARDS__;const PY=__PINYIN__;
let ALT=false;try{ALT=localStorage.getItem("altrom")==="1"}catch(e){}
const disp=a=>{if(ALT||!a)return a;const w=a.split(" ")[0];return PY[w]?PY[w]+a.slice(w.length):a};
const dispLab=l=>{if(ALT)return l;return disp(l).replace(/\(([^() ]+)\)$/,(m,w)=>PY[w]?`(${PY[w]})`:m)};
let apps=[...new Set(E.map(e=>e.a))];
const sel=$("#ap");
const addApp=a=>{const o=document.createElement("option");o.value="A:"+a;o.textContent=a;sel.appendChild(o);
 groups.filter(g=>g.startsWith(a+" — ")).forEach(g=>{const o=document.createElement("option");o.value="G:"+g;o.textContent="   "+g.slice(a.length+3);sel.appendChild(o)})};
function buildSel(){if(!PLACES.length){apps.forEach(addApp);return}const keep=sel.value;while(sel.options.length>1)sel.remove(1);
 const isP=a=>PLACES.includes(a.split(" ")[0]),cmp=(x,y)=>x.localeCompare(y);
 const opt=(v,t)=>{const o=document.createElement("option");o.value=v;o.textContent=t;sel.appendChild(o)};
 apps.filter(isP).map(a=>[a,disp(a)]).sort((x,y)=>cmp(x[1],y[1])).forEach(([a,t])=>opt("A:"+a,t));const sp=document.createElement("option");sp.disabled=true;sp.textContent="──────────";sel.appendChild(sp);
 const rest=apps.filter(a=>!isP(a)).map(a=>["A:"+a,a]).concat(groups.filter(g=>g.includes(" — ")).map(g=>{const i=g.indexOf(" — "),a=g.slice(0,i),sub=g.slice(i+3);return["G:"+g,isP(a)?`${sub} (${a.split(" ")[0]})`:`${a}: ${sub}`]}));
 rest.map(([v,t])=>[v,dispLab(t)]).sort((x,y)=>cmp(x[1],y[1])).forEach(([v,t])=>opt(v,t));sel.value=keep}
buildSel();
if(Object.keys(PY).length){$("#arlab").hidden=false;$("#altrom").checked=ALT;$("#altrom").addEventListener("change",()=>{ALT=$("#altrom").checked;try{localStorage.setItem("altrom",ALT?"1":"0")}catch(e){};buildSel();run()})}
function hl(s,terms){s=esc(s);if(!terms.length)return s;
 // highlight accent-insensitively by matching on normalised text
 const src=s,n=norm(src);let marks=[];terms.forEach(t=>{let i=0;const et=norm(esc(t));while(et&&(i=n.indexOf(et,i))>-1){marks.push([i,i+et.length]);i+=et.length}});
 if(!marks.length)return s;marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;
 marks.forEach(([a,b])=>{if(a<pos)return;out+=src.slice(pos,a)+"<mark>"+src.slice(a,b)+"</mark>";pos=b});return out+src.slice(pos)}
let JF=false;try{JF=localStorage.getItem("jafirst")==="1"}catch(e){}
if(E.some(e=>e.nj!==undefined)){$("#jflab").hidden=false;$("#jafirst").checked=JF;$("#jafirst").addEventListener("change",()=>{JF=$("#jafirst").checked;try{localStorage.setItem("jafirst",JF?"1":"0")}catch(e){};run()})}
let res=[],shown=0;const STEP=300;
function run(){const q=norm($("#q").value.trim());const terms=q.split(/\s+/).filter(Boolean);const v=sel.value;const no=$("#nameonly").checked;
 if(DC){const c=x=>`<a class="tocbtn" href="#" data-s="${esc(x.s)}">${esc(x.l)}<small>${x.n.toLocaleString()} entr${x.n===1?"y":"ies"}</small></a>`;
  const pl=DC.places.map(x=>({...x,l:disp(x.l)})),big=pl.slice(0,DC.big||0),restP=pl.slice(DC.big||0).sort((x,y)=>x.l.localeCompare(y.l));
  $("#toc").innerHTML=(q||v)?"":`<h2>Contents</h2><h3>Places</h3><div class="tocgrid">${big.concat(restP).map(c).join("")}</div>`+(DC.other.length?`<h3>Other lists</h3><div class="tocgrid">${DC.other.map(x=>c({...x,l:dispLab(x.l)})).join("")}</div>`:"")+`<h3>All entries</h3>`}
 res=E.filter(e=>{if(v.startsWith("A:")&&e.a!==v.slice(2))return false;if(v.startsWith("G:")&&e.a+(e.s?" — "+e.s:"")!==v.slice(2))return false;
  const hay=no?e._n:e._all;return terms.every(t=>hay.includes(t))});
 $("#cnt").textContent=`${res.length.toLocaleString()} of ${E.length.toLocaleString()} entries`;
 $("#out").innerHTML="";$("#out").classList.toggle("nonly",no);shown=0;more(terms);
 try{history.replaceState(null,"",(q||v)?"#"+new URLSearchParams({q:$("#q").value.trim(),s:v}).toString():location.pathname)}catch(e){}anSync()}
const FIRM=new Set(E.filter(e=>e.no).map(e=>e.no));
const ixLinks=(t,terms)=>esc(t).replace(/\d+/g,d=>FIRM.has(d)?`<a href="#" data-f="${d}">${d}</a>`:d);
function more(terms){terms=terms||norm($("#q").value.trim()).split(/\s+/).filter(Boolean);
 let h="",last=shown?groupOf(res[shown-1]):null,i=shown,end=Math.min(res.length,shown+STEP);
 while(i<end){const e=res[i];const g=groupOf(e);if(g!==last){h+=`<div class="sec">${esc(g)}</div>`;last=g}
  if(e.k==="i"){let j=i,pg=[],seen=new Set();h+=`<div class="ixb">`;
   while(j<res.length&&res[j].k==="i"&&groupOf(res[j])===g){const x=res[j];h+=`<div class="ix"><b>${hl(x.n,terms)}</b> ${ixLinks(x.t,terms)}</div>`;
    if(!seen.has(x.p)){seen.add(x.p);pg.push(x)}j++}
   h+=`</div><div class="ixp">Pages: ${pg.map(x=>x.u?`<a href="${x.u}" target="_blank" rel="noopener">p. ${esc(x.p)}</a>`:"p. "+esc(x.p)).join(" · ")}</div>`;
   i=j;end=Math.max(end,i);continue}
  i++;
  const ln=(n,t)=>(n?`<b>${hl(n,terms)}</b> `:"")+`<span class="t">${hl(t||"",terms)}</span>`;
  const body=(e.nj!==undefined)?(JF?[[e.nj,e.tj],[e.ne,e.te]]:[[e.ne,e.te],[e.nj,e.tj]]).filter(x=>x[0]||x[1]).map((x,i)=>`<div class="l${i+1}">${i===0&&e.no?`<span class="fno">${esc(e.no)}.</span> `:""}${ln(x[0],x[1])}</div>`).join(""):(e.f?`<b>${hl(e.n,terms)}</b>${e.h?` <span class="t">${hl(e.h,terms)}</span>`:""}<div class="fl">${e.f.map(([k,v])=>`<div>${k?`<b>${esc(k)}:</b> `:""}${hl(v,terms)}</div>`).join("")}</div>${e.d?`<div class="dsc">${hl(e.d,terms)}</div>`:""}`:`<b>${hl(e.n,terms)}</b> <span class="t">${hl(e.t,terms)}</span>`);
  h+=`<div class="e"${e.no?` id="f-${esc(e.no)}"`:""}>${body}<div class="m">p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`}
 $("#out").insertAdjacentHTML("beforeend",h);shown=Math.min(res.length,i);$("#more").hidden=shown>=res.length}
function goFirm(no){const f=E.find(e=>e.no===no);if(!f)return;$("#q").value="";sel.value="A:"+f.a;run();
 while(!document.getElementById("f-"+no)&&shown<res.length)more();const el=document.getElementById("f-"+no);
 if(el){document.querySelectorAll(".e.hit").forEach(x=>x.classList.remove("hit"));el.classList.add("hit");el.scrollIntoView({block:"center"})}}
$("#out").addEventListener("click",ev=>{const a=ev.target.closest("[data-f]");if(!a)return;ev.preventDefault();goFirm(a.dataset.f)});
const groupOf=e=>disp(e.a)+(e.s?" — "+e.s:"");
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,120)});
sel.addEventListener("change",run);$("#toc").addEventListener("click",ev=>{const a=ev.target.closest("[data-s]");if(!a)return;ev.preventDefault();sel.value=a.dataset.s;run();scrollTo(0,0)});$("#nameonly").addEventListener("change",run);$("#more").addEventListener("click",()=>more());
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark";anSync(true)});
// Notes are keyed by section (the search box only filters; notes on entries it hides stay listed in the panel)
function anView(){return sel.value?"s="+sel.value:""}
function anGo(v){$("#q").value="";sel.value=v&&v.startsWith("s=")?v.slice(2):"";run()}
const AN_AREA="#out",AN_NOTE="anything you want to check or remember. Select text to highlight it, or drop a pin, and add a comment. Notes belong to the section you make them in and are kept only in this browser; Download saves a copy you can keep or send.";
/*__ANNOT_JS__*/
let anFirst=null;try{const h=decodeURIComponent(location.hash.slice(1));if(h.startsWith("an="))anFirst=h.slice(3);else{const p=new URLSearchParams(location.hash.slice(1));if(p.get("q"))$("#q").value=p.get("q");if(p.get("s"))sel.value=p.get("s")}}catch(e){}
run();
try{if(localStorage.getItem("stat-notes")==="1")anSet(true)}catch(e){}
if(anFirst)anLink(anFirst);
addEventListener("hashchange",()=>{const h=decodeURIComponent(location.hash.slice(1));if(h.startsWith("an="))anLink(h.slice(3))});
</script></body></html>
"""


DIRTEMPLATE = notes_layer(DIRTEMPLATE)


SEARCH = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<script src="fold.js"></script>
<title>Search · Old Tables of East Asia</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff;--hi:#e2ece4;--warn:#8a5a00;--mark:#f3e3a0}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13;--hi:#1f3527;--warn:#e0a54a;--mark:#5a4d1c}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.5 Georgia,"Times New Roman","Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
header{padding:14px 18px;background:var(--accent);color:var(--accent-ink);display:flex;gap:14px;align-items:baseline;flex-wrap:wrap}
header a{color:var(--accent-ink);opacity:.88;font-size:14px;text-decoration:none}header h1{font-size:20px;margin:0;font-weight:normal}
header button{margin-left:auto;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:4px;font:inherit;padding:4px 8px;cursor:pointer}
main{max-width:1000px;margin:0 auto;padding:18px 16px 60px}
.box{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:14px;display:flex;gap:10px;flex-wrap:wrap}
input,select{font:inherit;font-size:16px;padding:8px 10px;border:1px solid var(--line);background:var(--bg);color:var(--ink);border-radius:4px}
#q{flex:1 1 320px}#scope{flex:0 0 auto}
.filters{display:flex;gap:10px 16px;flex-wrap:wrap;align-items:center;width:100%;font-size:14px;color:var(--muted);border-top:1px solid var(--line);padding-top:10px}
.filters select,.filters input{font-size:14px;padding:5px 8px}
.filters input[type=number]{width:6.2em}
.filters label{display:inline-flex;gap:6px;align-items:center}
.filters .yrs{display:inline-flex;gap:6px;align-items:center}
#reset{font:inherit;font-size:13px;background:none;border:0;color:var(--accent);text-decoration:underline;cursor:pointer;padding:0}
.pager{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:10px 0;font-size:13.5px;color:var(--muted)}
.pager button{font:inherit;font-size:13.5px;padding:4px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px;cursor:pointer}
.pager button[disabled]{opacity:.4;cursor:default}
.pager button.on{background:var(--accent);color:var(--accent-ink);border-color:var(--accent)}
#status{color:var(--muted);font-size:13px;margin:12px 0 10px}
.kind{font-size:17px;margin:26px 0 4px;color:var(--accent);border-bottom:2px solid var(--accent);padding-bottom:3px}
.bk{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:18px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.bk a{color:inherit}
.r{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:8px 12px;margin:0 0 7px}
.r a.t{font-size:15.5px;color:var(--ink);text-decoration:none;font-weight:bold}.r a.t:hover{text-decoration:underline}
.r .m{font-size:12.5px;color:var(--muted)}.r .m a{color:var(--accent)}
.r .snip{font-size:13px;margin-top:4px;font-family:"Iowan Old Style",Georgia,"Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
.r .snip div{white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
mark{background:var(--mark);color:inherit}
.llmwarn{margin:24px 0 8px;padding:12px 14px;border:1px solid var(--warn);border-left:4px solid var(--warn);background:var(--panel);font-size:14px}
#fcards{display:flex;flex-direction:column;gap:6px;margin:0 0 10px}#fcards .fcard{display:block;border:1px solid var(--line);border-left:4px solid var(--accent);background:var(--panel);padding:8px 12px;color:var(--ink);text-decoration:none;font-size:15px}#fcards .fcard:hover{border-color:var(--accent)}#fcards .fcard b{font-weight:600;color:var(--accent)}#fcards .fcard span{display:block;font-size:13px;color:var(--muted)}
</style></head><body>
<header><a href="./">← All books</a><h1>Search</h1><button id="toggle" title="Toggle light/dark">◐</button></header>
<main>
<div class="box"><input id="q" type="search" placeholder="e.g. rice, Dairen, cotton exports, Mitsui, Kato…" autofocus>
<select id="scope" aria-label="Search in">
<option value="all">Everything</option><option value="t">Tables only</option><option value="w">Who's Who only</option>
<option value="d">All directories</option><option value="c">Chronologies only</option></select>
<div class="filters">
<label>Region <select id="reg" aria-label="Region"><option value="">All</option><option value="japan">Japan</option><option value="china">China</option><option value="korea">Korea</option><option value="taiwan">Taiwan</option><option value="manchuria">Manchuria</option><option value="south-seas">South Seas Mandate</option><option value="other">Other</option></select></label>
<span class="yrs">Years <input id="y1" type="number" inputmode="numeric" min="1890" max="1960" placeholder="from" aria-label="From year"> – <input id="y2" type="number" inputmode="numeric" min="1890" max="1960" placeholder="to" aria-label="To year"></span>
<label><input type="checkbox" id="titles"> Titles and names only</label>
<button id="reset" type="button" hidden>Clear filters</button>
</div></div>
<div id="fcards"></div><div id="status"></div><div id="out"></div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision models of Opus 5.5, Sonnet 5.5, or Haiku 5.5 (named on each book's page). Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
</main>
<script>
const BOOKS=__BOOKS__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>fold(String(s??"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase());
function hl(s,terms){s=String(s??"");const n=norm(s);let marks=[];terms.forEach(t=>{let i=0;while(t&&(i=n.indexOf(t,i))>-1){marks.push([i,i+t.length]);i+=t.length}});
 if(!marks.length)return esc(s);marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;marks.forEach(([a,b])=>{if(a<pos)return;out+=esc(s.slice(pos,a))+"<mark>"+esc(s.slice(a,b))+"</mark>";pos=b});return out+esc(s.slice(pos))}
// Search runs on the Pagefind indexes written by build/build_search.py: pagefind/ (everything) and
// pagefind-titles/ (table titles, entry names and chronology headings only). Only the index pieces a query
// needs are downloaded, and only the results on the page shown.
const PF={};
function pagefind(ti){const d=ti?"pagefind-titles":"pagefind";return PF[d]||(PF[d]=import("./"+d+"/pagefind.js").then(async m=>{await m.options({excerptLength:40});await m.init();return m}))}
const CJKC="[々〆぀-ヿ㐀-䶿一-鿿豈-﫿\u{20000}-\u{2fa1f}]",CJK=new RegExp(CJKC,"u"),CJKG=new RegExp(CJKC,"gu");
// the query is prepared like the indexed text: folded, and Chinese/Japanese characters spaced and searched as a phrase
// very common English words match most of the collection and make a search take many seconds; they are left out
// of the query unless nothing else is left
const STOP=new Set("a an and are as at be by for from in is it of on or that the this to was were with".split(" "));
function pfQuery(q){let ws=norm(q).replace(/"/g," ").split(/\s+/).filter(Boolean);const kept=ws.filter(w=>!STOP.has(w));if(kept.length)ws=kept;
 return ws.map(w=>{if(!CJK.test(w))return w;const sp=w.replace(CJKG," $& ").trim().replace(/\s+/g," ");return sp.includes(" ")?`"${sp}"`:sp}).join(" ")}
// a single Latin letter matches a large part of the index; wait for a second letter (one CJK character is enough)
const tooShort=q=>{const t=norm(q).replace(/"/g," ").trim();return !t||(!CJK.test(t)&&t.replace(/\s/g,"").length<2)}
const unspace=h=>String(h||"").replace(new RegExp(`(${CJKC})((?:</?mark>)*) +(?=(?:</?mark>)*${CJKC})`,"gu"),"$1$2");
const BK=Object.fromEntries(BOOKS.map(b=>[b.slug,b]));
const PAGE=100;
let RES={},PG={t:0,d:0,c:0},LAST={},RTOK=0;
function yearRange(){const a=parseInt($("#y1").value),z=parseInt($("#y2").value);const lo=isNaN(a)?(isNaN(z)?null:z):a,hi=isNaN(z)?(isNaN(a)?null:a):z;return lo===null?[null,null]:[Math.min(lo,hi),Math.max(lo,hi)]}
function bookFilter(){const g=$("#reg").value,[lo,hi]=yearRange();return b=>(!g||b.g===g)&&(lo===null||(b.y&&b.y[0]!==null&&b.y[1]>=lo&&b.y[0]<=hi))}
function pfFilters(kind){const f={kind};const g=$("#reg").value;if(g)f.region=g;const [lo,hi]=yearRange();
 if(lo!==null){const ys=[];for(let y=Math.max(lo,1850);y<=Math.min(hi,1970);y++)ys.push(String(y));f.year={any:ys.length?ys:["none"]}}return f}
function pager(kind,n){const pages=Math.ceil(n/PAGE);if(pages<=1)return "";const p=PG[kind];
 const nums=[...new Set([0,1,p-1,p,p+1,pages-2,pages-1].filter(x=>x>=0&&x<pages))].sort((a,b)=>a-b);let h="",last=-1;
 nums.forEach(x=>{if(x-last>1)h+="<span>…</span>";h+=`<button data-k="${kind}" data-p="${x}" class="${x===p?"on":""}"${x===p?' aria-current="page"':""}>${x+1}</button>`;last=x});
 return `<div class="pager"><button data-k="${kind}" data-p="${p-1}"${p?"":" disabled"}>‹ Previous</button>${h}<button data-k="${kind}" data-p="${p+1}"${p<pages-1?"":" disabled"}>Next ›</button><span>${(p*PAGE+1).toLocaleString()}–${Math.min(n,(p+1)*PAGE).toLocaleString()} of ${n.toLocaleString()}</span></div>`}
const href=d=>{const u=String(d.url||"");const i=u.indexOf("book/");return i>=0?u.slice(i):u.replace(/^\/+/,"")};   // Pagefind prefixes the folder the site is served from (e.g. /reference/old-tables/); links are relative to search.html
const slugOf=d=>(href(d).match(/^book\/([^/]+)\//)||[])[1]||"";
// printed pages and scan leaves are stored shifted into the Private Use Area so that searches do not match them
const unhide=s=>[...String(s||"")].map(c=>String.fromCodePoint(c.codePointAt(0)-0xF0000)).join("");
function scanUrl(d){const b=BK[slugOf(d)];if(!b||!b.sc||d.meta.n===undefined)return "";const n=unhide(d.meta.n);return b.sc.includes("{leaf}")?b.sc.replace("{leaf}",n):b.sc}
function groupBy(ds){const by=new Map();ds.forEach(d=>{const s=slugOf(d);if(!d._shown){d._shown=1;d.meta.p=unhide(d.meta.p);d.meta.u=scanUrl(d)}if(!by.has(s))by.set(s,[]);by.get(s).push(d)});return by}
function tablesHTML(ds,terms){let h="";groupBy(ds).forEach((xs,s)=>{const b=BK[s]||{title:s};h+=`<div class="bk">${esc(b.title)} · ${xs.length}</div>`;
  xs.forEach(d=>{const m=d.meta;h+=`<div class="r"><a class="t" href="${esc(href(d))}">${hl(m.title,terms)}</a>${m.e?`<div class="m">${hl(m.e,terms)}</div>`:""}<div class="m">${esc(m.c||"")}${m.p?(m.c?" · ":"")+"p. "+esc(m.p):""}${m.u?` · <a href="${esc(m.u)}" target="_blank" rel="noopener">scan</a>`:""}</div>`+
   snip(d,terms)+`</div>`})});return h}
// snippet: up to three original lines (table rows, headings) that contain a search term; the index text holds
// the lines joined with " ¶ " and, after " ¶¶ ", folded copies, which are skipped here
function snip(d,terms){const lines=String(d.content||"").split(" ¶¶ ")[0].split(" ¶ ").map(unspace);
 const hits=lines.filter(l=>{const n=norm(l);return terms.some(w=>n.includes(w))}).slice(0,3);
 return hits.length?`<div class="snip">${hits.map(l=>`<div>${hl(l,terms)}</div>`).join("")}</div>`:""}
function entriesHTML(ds,terms,page,q){let h="";groupBy(ds).forEach((xs,s)=>{const b=BK[s]||{title:s};h+=`<div class="bk">${esc(b.title)} · ${xs.length} · <a href="book/${s}/${page}#${new URLSearchParams({q}).toString()}">open in book</a></div>`;
  xs.forEach(d=>{const m=d.meta;h+=`<div class="r"><b>${hl(m.title,terms)}</b> <span class="snip">${hl(m.t,terms)}</span><div class="m">${esc(m.a||"")}${m.x?" — "+esc(m.x):""}${m.p?(m.a?" · ":"")+"p. "+esc(m.p):""}${m.u?` · <a href="${esc(m.u)}" target="_blank" rel="noopener">scan</a>`:""}</div></div>`})});return h}
const count=(n,one,many)=>`${n.toLocaleString()} ${n===1?one:many}`;
const KINDS={t:["Tables",""],d:["Who's Who &amp; directories","directory.html"],c:["Chronologies","chronology.html"]};
async function render(){const tok=++RTOK;const {terms,q,sc}=LAST;
 const secs=await Promise.all(["t","d","c"].map(async k=>{const r=RES[k];if(!r||!r.length)return "";
  const ds=await Promise.all(r.slice(PG[k]*PAGE,(PG[k]+1)*PAGE).map(x=>x.data()));
  const body=k==="t"?tablesHTML(ds,terms):entriesHTML(ds,terms,KINDS[k][1],q);
  return `<section id="sec-${k}">`+(sc==="all"?`<div class="kind">${KINDS[k][0]}</div>`:"")+pager(k,r.length)+body+pager(k,r.length)+`</section>`}));
 if(tok!==RTOK)return false;$("#out").innerHTML=secs.join("")||"<p>No matches.</p>";return true}
function state(){const o={q:$("#q").value.trim(),s:$("#scope").value};if($("#reg").value)o.r=$("#reg").value;if($("#y1").value)o.y1=$("#y1").value;if($("#y2").value)o.y2=$("#y2").value;if($("#titles").checked)o.ti="1";return o}
// one search at a time: Pagefind works through queries one by one, so a search started while another runs waits for it;
// while one runs, only the latest request is kept and it starts when the current one ends
let BUSY=false,AGAIN=false;
async function run(){if(BUSY){AGAIN=true;return}BUSY=true;try{do{AGAIN=false;await run1()}while(AGAIN)}finally{BUSY=false}}
// finder pages (build/finders/): a card for each place whose name matches the query, above the results
const FINDERS=__FINDERS_IDX__;const FIDX={};
function ffold(s){return String(s||"").normalize("NFKD").replace(/[\u0300-\u036f]/g,"").toLowerCase().replace(/[-'’ʻ`.\s]+/g,"")}
async function finderCards(q){const box=$("#fcards");if(!box)return;const v=ffold(q);if(v.length<2||(v.length<3&&!/[\u3400-\u9fff]/.test(v))){box.innerHTML="";return}
 let h="";for(const f of FINDERS){try{if(!FIDX[f.name])FIDX[f.name]=fetch(f.index).then(r=>r.json());const d=await FIDX[f.name];
  const hits=[];for(const [id,a] of Object.entries(d.places)){if(!a[10])continue;const names=[a[0],a[1],...(a[11]||[])].map(ffold);
   const sc=names.includes(v)?2:names.some(n=>n.startsWith(v)&&v.length>=4)?1:0;if(sc)hits.push([sc,a[10],id,a])}
  hits.sort((x,y)=>y[0]-x[0]||y[1]-x[1]);
  for(const [sc,n,id,a] of hits.slice(0,3))h+=`<a class="fcard" href="${f.page}#p=${encodeURIComponent(id)}"><b>${esc(f.title)}: ${esc(a[0])}</b> ${esc(a[1])}<span>${n.toLocaleString("en-US")} figure${n===1?"":"s"}${a[4]?`, ${a[5]}–${a[6]}`:""} from the site's tables →</span></a>`}catch(e){}}
 if(ffold($("#q").value.trim())===v)box.innerHTML=h}
async function run1(){const q=$("#q").value.trim(),sc=$("#scope").value,ti=$("#titles").checked;finderCards(q);const terms=norm(q).replace(/"/g," ").split(/\s+/).filter(Boolean);
 const st=state();const filt=!!(st.r||st.y1||st.y2||st.ti),narrow=!!(st.r||st.y1||st.y2);$("#reset").hidden=!filt;
 try{history.replaceState(null,"",q||sc!=="all"||filt?"#"+new URLSearchParams(st).toString():location.pathname)}catch(e){}
 const nb=BOOKS.filter(bookFilter()).length,inb=narrow?` in ${nb} book${nb===1?"":"s"}`:"";
 if(!terms.length||tooShort(q)){RES={};RTOK++;$("#status").textContent=terms.length?"Keep typing…":narrow?`Type to search ${nb} book${nb===1?"":"s"}.`:"Type to search.";$("#out").innerHTML="";return}
 $("#status").textContent="Searching…";
 let P;try{P=await pagefind(ti)}catch(e){$("#status").textContent="The search index is not installed on this copy of the site (it is built separately: see build/README.md), or the page is not being served from a web server.";return}
 const query=pfQuery(q),dirs={any:["d","w"]};
 const kinds=sc==="all"?[["t","t"],["d",dirs],["c","c"]]:sc==="t"?[["t","t"]]:sc==="w"?[["d","w"]]:sc==="d"?[["d",dirs]]:[["c","c"]];
 // sections are searched one after another and shown as each finishes, so tables appear while directories are still searched;
 // a newer search (AGAIN) stops this one between sections
 const lab={t:["table","tables"],d:sc==="w"?["Who's Who entry","Who's Who entries"]:["directory entry","directory entries"],c:["chronology event","chronology events"]};
 const names={t:"tables",d:"directories",c:"chronologies"};RES={};PG={t:0,d:0,c:0};LAST={terms,q,sc};const done=[];
 for(const [i,[k,f]] of kinds.entries()){const r=await P.search(query,{filters:pfFilters(f)});
  if(AGAIN||JSON.stringify(state())!==JSON.stringify(st))return;
  RES[k]=r&&r.results?r.results:[];done.push(count(RES[k].length,...lab[k]));
  const more=i<kinds.length-1?` · searching ${names[kinds[i+1][0]]}…`:inb;
  if(await render())$("#status").textContent=done.join(" · ")+more}}
$("#out").addEventListener("click",e=>{const b=e.target.closest(".pager button[data-p]");if(!b||b.disabled)return;const k=b.dataset.k;PG[k]=+b.dataset.p;render().then(ok=>{const sec=ok&&document.getElementById("sec-"+k);if(sec)sec.scrollIntoView({block:"start"})})});
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,300)});$("#scope").addEventListener("change",run);
$("#reg").addEventListener("change",run);$("#titles").addEventListener("change",run);["y1","y2"].forEach(k=>$("#"+k).addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,300)}));
$("#reset").addEventListener("click",()=>{$("#reg").value="";$("#y1").value="";$("#y2").value="";$("#titles").checked=false;run()});
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
function fromHash(){try{const p=new URLSearchParams(location.hash.slice(1));$("#q").value=p.get("q")||p.get("t")||p.get("d")||"";const sc=p.get("s")||(p.get("tab")==="d"?"d":"all");if([...$("#scope").options].some(o=>o.value===sc))$("#scope").value=sc;
 if([...$("#reg").options].some(o=>o.value===p.get("r")))$("#reg").value=p.get("r");if(/^\d{4}$/.test(p.get("y1")||""))$("#y1").value=p.get("y1");if(/^\d{4}$/.test(p.get("y2")||""))$("#y2").value=p.get("y2");$("#titles").checked=p.get("ti")==="1"}catch(e){}}
fromHash();addEventListener("hashchange",()=>{fromHash();run()});
run();
</script></body></html>
"""

if __name__ == "__main__":
    main()
