#!/usr/bin/env python3
"""Build the stat-tables site: a landing page plus one table browser per book.

For each book in BOOKS, reads <book dir>/_work/tables/*.json and writes
<slug>/index.html (self-contained) and data/<slug>.json. Books without tables yet are listed
as "in progress" on the landing page. Scan links point to the online scan where one exists.
"""
import json, glob, os, re, html

SCRIPTS = os.path.dirname(os.path.abspath(__file__))  # build/: scripts, leaf maps, docs (not deployed)
HERE = os.path.dirname(SCRIPTS)  # site root: everything here except build/, CLAUDE.md and .git is deployed
# Folder holding the book folders. A worktree placed elsewhere (e.g. the far-east-1941 branch)
# must set STAT_TABLES_ROOT to the Manchoukuo folder, or relative book dirs resolve wrongly.
ROOT = os.environ.get("STAT_TABLES_ROOT") or os.path.dirname(HERE)

BOOKS = [
    {"slug": "japan-1905", "dir": "Japan_Year_Book_1905", "title": "The Japan Year Book 1905",
     "publisher": "The \"Japan Year Book\" Office, Tokyo, 1905",
     "blurb": "The first edition of The Japan Year Book, compiled during the Russo-Japanese War: geography, population, the Imperial Court, politics, finance, banking, industry, trade, education, the army and navy, communications, a Who's Who (\"Contemporary Worthies\"), diplomacy, the press, Formosa, Korea, and an appended import tariff.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of a New York Public Library copy).",
     "gaps": "The dated narrative of the \"Progress of the War\" chapter (pp. 315-347) was transcribed separately and is not included; the statistical tables printed in that chapter (spoils, prisoners, warships lost) are. Advertisements, the contents and the Index were skipped, as were law and treaty texts. The Import Tariff List in the Appendix is given one table per page. The \"Contemporary Worthies\" Who's Who, the Imperial family and the steamship-company sketches are on the Who's Who & Directories page.",
     "scan": "https://archive.org/details/japan-year-book-1905/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1905"},
    {"slug": "japan-1910", "dir": "Japan_Year_Book_1910", "title": "The Japan Year Book 1910",
     "publisher": "The Japan Year Book Office, Tokyo, 1910",
     "blurb": "The fifth annual edition, compiled by Y. Takenob and K. Kawakami: geography, population, the Imperial Court, a Who's Who, arts and crafts, education, religion, justice, agriculture, mining, industry, finance, diplomacy, politics, trade, banking, the army and navy, communications, shipping, railways, the press, Formosa, Karafuto, South Manchuria and Korea.",
     "source": "LLM-transcribed from the Internet Archive scan (Google scan of the 2013 Edition Synapse facsimile, University of Minnesota copy).",
     "gaps": "The scan is low resolution, so more figures are left blank than in later volumes; each blank is explained in a transcriber's note. Advertisements, the contents and the Index were skipped. The Who's Who, the Imperial family and the art and pottery sketches are on the Who's Who & Directories page; the Diary of 1908-9 is on the Chronologies page. Treaty texts and law articles are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1910/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1910"},
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
    {"slug": "japan-1939-40", "dir": "Japan_Year_Book_1939-40", "title": "The Japan Year Book 1939-40",
     "publisher": "The Foreign Affairs Association of Japan, Tokyo, 1939",
     "blurb": "The wartime edition of the standard English-language reference on the Japanese Empire.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The Internet Archive scan often repeats a leaf in place of the next one, so about 90 printed pages are missing, among them pp. 273–274, 277–278, 283–284 (part of the 1937-38 budget and Banking Tables 1–3), 380–381 (Balance of International Payments), 778–779, 784, 787–788, 793, 796–797, 802–803, 808, 811, 814, 817, 820–821, 825, 830–832, 843–844, 847, 850, 853–854, 861, 866, 869, 873, 876, 879, 886, 888, 893, 896–897, 901, 904, 908–909, 912, 918–919, 928–929, 934, 937, 940–941, 947–948, 951–952 (including the opening of the Karafuto chapter), 956, 959, 962–963, 967, 970–971, 1023, 1026–1027, 1033–1034, 1039, 1123, 1130, 1135–1137 and 1142. Tables that run onto a missing page are incomplete and say so. Page 363 is heavily over-inked, leaving about 90 blank cells in the census table there. Lists are included as well as tables; the Clubs & Societies list is on the directory page. The bibliography, index and advertisements are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1939-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1939-1940", "dir_label": "Clubs & Societies Directory"},
    {"slug": "japan-1946-48", "dir": "Japan_Year_Book_1946-48", "title": "The Japan Year Book 1946-48",
     "publisher": "The Foreign Affairs Association of Japan (no place or date on the title page)",
     "blurb": "The first post-war edition, covering occupied Japan.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "The scan is complete: no printed pages are missing and no leaves repeat. Part I runs to p. 614; the Appendix (SCAP directives, the new Constitution and post-war laws, documents of 1945–47, the war-crimes indictment and a List of Emperors) is paged again from 1. The Appendix is almost all legal text, so only its lists are transcribed. A few cells on folding inserts are lost in the fold and are left blank. The index, advertisements and a short run of church-group entries (printed pp. 489–490) are not transcribed.",
     "scan": "https://archive.org/details/japan-year-book-1946-1948/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-year-book-1946-1948"},
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
     "title": "Annual Report on Reforms and Progress in Chosen 1926-27",
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
    {"slug": "japan-manchoukuo-1940", "dir": "Japan_Manchoukuo_1940", "group": "manchuria",
     "title": "Japan-Manchoukuo Year Book 1940 (incomplete scan)", "subtitle": "Japan-Manchoukuo Year Book 1940",
     "publisher": "Japan-Manchoukuo Year Book Co., Tokyo, 1940",
     "blurb": "The 1940 edition of the Tokyo yearbook covering Japan and Manchoukuo. The online scan holds only part of the book: the opening statistical diagrams, Japan's national defence and airways, the colonies (Chosen, Taiwan, Karafuto and the South Sea Islands), and the whole Manchoukuo part — geography, population and immigration, administration, judicature, diplomacy, defence, education, state finance, banking, communications, transport, agriculture, forestry, fisheries, mining, manufacturing, foreign trade, sanitation, labour, the South Manchuria Railway, economic policy and the Kwantung Leased Territory — with the start of the list of learned and social institutions.",
     "source": "LLM-transcribed from the Internet Archive scan.",
     "gaps": "Incomplete scan: printed pp. 16–109, 118–207, 210–503 and 878–1185 are not in the online copy, so most of the Japan part, the Who's Who and the business directory are missing, and the scan ends at p. 1203 in the list of learned and social institutions. Two table fragments whose first page is missing are transcribed as fragments. Only tables, lists and that directory page are transcribed; the running text, photographs, maps, advertisements, charts without printed figures, the contents and the bibliography are not. The pages with tables were found from contact sheets and only those pages were read. Printed totals that do not add up are kept as printed and noted.",
     "scan": "https://archive.org/details/japan-manchoukuo-year-book-1940/page/n{leaf}/mode/1up",
     "item": "https://archive.org/details/japan-manchoukuo-year-book-1940",
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
     "source": "LLM-transcribed (Claude Haiku 5.5 via the API) from a scan of the printed volume.",
     "gaps": "Only tables, columnar lists and directory entries are transcribed; prose, chronologies, treaty and law texts, advertisements, the contents and the index are not. Pages with tables and directories were found from contact sheets by Claude Sonnet 5.5, so small tables set into the prose may be missing. Each page was read once by Claude Haiku 5.5 from full-resolution crops and not checked by eye; unreadable figures are marked, and printed totals that do not add up are noted and kept as read. Tables continued over pages were joined where the column headings match. The Who's Who and directories are on the Who's Who & Directories page.",
     "scan": None,
     "item": None,
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
            out.append({"label": f"scan part {part}, leaf {leaf}", "url": book["scan"].format(part=part, leaf=leaf)})
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
            out.append({"label": f"scan leaf {int(m.group(1))}", "url": book["scan"].format(leaf=int(m.group(1)))})
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


def cells(tables):
    return sum(len(r) for t in tables for p in t.get("parts", []) for r in p.get("rows", []))


def main():
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
        n, c = len(tables), cells(tables)
        chapters = len({t.get("chapter") for t in tables})
        if tables:
            clean = [{k: v for k, v in t.items() if k not in ("file",)} for t in tables]
            with open(os.path.join(HERE, "data", b["slug"] + ".json"), "w", encoding="utf-8") as fh:
                json.dump(clean, fh, ensure_ascii=False, indent=1)
            pages.append((b, clean, n, c))
        cards.append((b, n, c, chapters))
        print(f"{b['slug']}: {n} tables, {c:,} cells")
    xl = crosslinks({b["slug"]: clean for b, clean, n, c in pages})
    for b, clean, n, c in pages:
            os.makedirs(os.path.join(HERE, "book", b["slug"]), exist_ok=True)
            data = json.dumps(clean, ensure_ascii=False).replace("</", "<\\/")
            doc = (TEMPLATE.replace("__MODEL__", b.get("model", "Opus 5.5")).replace("__DATA__", data).replace("__DIRCARDS__", dir_cards(b)).replace("__PINYIN__", json.dumps(b.get("dir_pinyin", {}), ensure_ascii=False)).replace("__COUNT__", str(n))
                   .replace("__CHEN__", json.dumps(b.get("_chen") or {}, ensure_ascii=False))
                   .replace("__XL__", json.dumps(xl[b["slug"]], ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__HIDEIMG__", "true" if b.get("hide_images") else "false")
                   .replace("__MARKED__", "true" if b.get("blank_marking") else "false")
                   .replace("__XLSX__", f' · <a href="../../{dl(b["slug"], "tables.xlsx")}" style="color:inherit" download>Excel</a>' if dl(b["slug"], "tables.xlsx") else "")
                   .replace("__CELLS__", f"{c:,}").replace("__BOOK__", html.escape(b["title"]))
                   .replace("__SLUG__", b["slug"]).replace("__SOURCE__", "LLM-transcribed")
                   .replace("__DIRLINK__", ('<a class="dirbtn" href="directory.html">Directories</a>' if b.get("_dir_n") else "")
                            + ('<a class="dirbtn" href="chronology.html">Chronologies</a>' if b.get("_chron_n") else "")
                            + (f'<button class="aboutbtn" onclick="document.getElementById(\'about\').showModal()">About</button>'
                               f'<dialog id="about" onclick="if(event.target===this)this.close()"><h3>{html.escape(b["title"])}</h3>{f'<div class="pub">{html.escape(b["subtitle"])}</div>' if b.get("subtitle") else ""}<div class="pub">{html.escape(b["publisher"])}</div>'
                               f'<p>{html.escape(b["gaps"])}</p>{"" if b.get("blank_marking") else BLANK_NOTE}<form method="dialog"><button>Close</button></form></dialog>' if b.get("gaps") else "")))
            with open(os.path.join(HERE, "book", b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(landing(cards))
    books = [{"slug": b["slug"], "title": b["title"], "dir": bool(b.get("_dir_n")), "chron": bool(b.get("_chron_n"))} for b, n, c, ch in cards if n]
    with open(os.path.join(HERE, "search.html"), "w", encoding="utf-8") as fh:
        fh.write(SEARCH.replace("__BOOKS__", json.dumps(books, ensure_ascii=False)))


def landing(cards):
    items = []
    for b, n, c, ch in cards:
        stat = (f"<b>{n}</b> tables · <b>{c:,}</b> cells · {ch} chapters" if n else "<i>transcription in progress</i>")
        if n and b.get("in_progress"):
            stat += " · <i>transcription in progress</i>"
        link = f'<a class="go dirgo" href="book/{b["slug"]}/">Tables →</a>' if n else ""
        if b.get("_dir_n"):
            stat += f' · <b>{b["_dir_n"]:,}</b> directory entries' + (" (in progress)" if b.get("dir_in_progress") else "")
            link += f' <a class="go dirgo" href="book/{b["slug"]}/directory.html">Directories →</a>'
        if b.get("_chron_n"):
            stat += f' · <b>{b["_chron_n"]:,}</b> chronology events'
            link += f' <a class="go dirgo" href="book/{b["slug"]}/chronology.html">Chronologies →</a>'
        item = f' · <a href="{b["item"]}">original scan</a>' if b.get("item") else ""
        grp = b.get("group") or next((g for g in ("japan", "china", "korea", "taiwan") if b["slug"].startswith(g)), "manchuria" if b["slug"].startswith("manch") else "other")
        title = f'<a href="book/{b["slug"]}/" style="color:inherit;text-decoration:none">{html.escape(b["title"])}</a>' if n else html.escape(b["title"])
        items.append((grp, b["slug"], f"""<article data-t="{html.escape(b["title"])}"><h2>{title}</h2><div class="pub">{html.escape(b["publisher"])}</div>
<div class="stat">{stat}</div><div class="src">LLM-transcribed{item}</div><div class="links">{link}</div></article>"""))
    order = {"far-east": 0, "manchoukuo": 1}
    other = sorted([(sl, h) for g, sl, h in items if g == "other"], key=lambda x: order.get(x[0].rsplit("-", 1)[0], 9))
    names = {"japan": "Japan", "china": "China", "korea": "Korea", "taiwan": "Taiwan", "manchuria": "Manchuria", "other": "Other"}
    body = {g: "\n".join(h for gg, sl, h in items if gg == g) for g in ("japan",)}
    year = {b["slug"]: edition(b) for b in BOOKS}
    body["china"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "china"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["korea"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "korea"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["taiwan"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "taiwan"), key=lambda x: (year[x[1]], x[1])))
    body["manchuria"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "manchuria"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["other"] = "\n".join(h for _, h in other)
    grids = "".join(f'<section class="grp" id="{g}"><h2 class="grph">{names[g]}</h2><div class="grid">{body[g]}</div></section>'
                    for g in ("japan", "china", "korea", "taiwan", "manchuria", "other") if body[g])
    return LANDING.replace("__CARDS__", grids)


LANDING = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<title>Old Year Book Tables of East Asia</title>
<style>
:root{--bg:#f4f5f3;--panel:#ffffff;--ink:#1b2420;--muted:#5d6a62;--line:#d8ded9;--accent:#1f4a2c;--accent-ink:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}}
:root[data-theme="dark"]{--bg:#111814;--panel:#17211b;--ink:#e4ebe6;--muted:#9aa89f;--line:#2c3a31;--accent:#8cc49e;--accent-ink:#0f1a13}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.55 Georgia,"Times New Roman","Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
.band{background:var(--accent);color:var(--accent-ink)}.band>div{max-width:980px;margin:0 auto;padding:34px 16px 30px}.band h1{font-weight:normal;font-size:30px;margin:0 0 8px}.band .lede{color:var(--accent-ink);opacity:.9;margin:0}
main{max-width:980px;margin:0 auto;padding:26px 16px 60px}
.topnav{margin:18px 0 0;display:flex;gap:8px;flex-wrap:wrap;align-items:center}.jump{display:contents}.jump a{display:inline-block;border:1px solid var(--accent-ink);color:var(--accent-ink);padding:6px 16px;border-radius:5px;text-decoration:none;font-size:15px}.jump a:hover{background:var(--accent-ink);color:var(--accent)}
.grp{scroll-margin-top:12px}.grp{border-top:2px solid var(--line);margin-top:34px;padding-top:6px}.grp:first-child{margin-top:4px}.grph{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:18px 0 0;font-weight:bold}.grp .grid{margin-top:14px}
.searchbtn{display:inline-block;background:var(--accent-ink);color:var(--accent);font-weight:bold;padding:9px 16px;border-radius:5px;text-decoration:none;font-size:15px}
.lede{color:var(--muted);max-width:720px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(280px,1fr));gap:18px;margin-top:28px}
article{background:var(--panel);border:1px solid var(--line);border-top:3px solid var(--accent);padding:18px 18px 16px;display:flex;flex-direction:column}
h2{font-size:20px;font-weight:normal;margin:0 0 4px}.pub{color:var(--muted);font-size:13px;margin-bottom:8px}
.links{margin-top:auto;display:flex;flex-wrap:wrap;gap:8px;align-items:center}.links .dirgo{margin:0}
.about{font:inherit;font-size:13px;background:transparent;color:var(--accent);border:1px solid var(--accent);border-radius:5px;padding:5px 10px;cursor:pointer;flex-basis:100%;max-width:max-content}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px}
dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog p{font-size:14.5px}
dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}.stat{font-size:14px;margin-bottom:6px}.src{font-size:12.5px;color:var(--muted);margin-bottom:12px}
a{color:var(--accent)}.go{font-size:15px;text-decoration:none;font-weight:bold}.dirgo{display:inline-block;margin:8px 8px 0 0;background:var(--accent);color:var(--accent-ink);padding:6px 12px;border-radius:5px;font-size:14px}
.llmwarn{margin:28px 0 0;padding:12px 14px;border:1px solid #8a5a00;border-left:4px solid #8a5a00;background:var(--panel);font-size:14px}
footer{margin-top:24px;font-size:13px;color:var(--muted);border-top:1px solid var(--line);padding-top:14px}
.tools{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--accent-ink);opacity:.8}.tools:hover{opacity:1}.tools .lbl{font-size:12px;text-transform:uppercase;letter-spacing:.06em}.seg{display:inline-flex;border:1px solid currentColor;border-radius:999px;overflow:hidden}.viewbtn{font:inherit;font-size:13px;background:transparent;color:inherit;border:0;padding:4px 12px;cursor:pointer;white-space:nowrap}.viewbtn+.viewbtn{border-left:1px solid currentColor}.viewbtn:hover{background:rgba(127,127,127,.15)}
body.list .grid{display:block;margin-top:8px}body.list article{flex-direction:row;align-items:center;gap:12px;padding:5px 10px;border:0;border-bottom:1px solid var(--line);border-left:3px solid var(--accent)}
body.list article+article{margin-top:0}body.list article h2{font-size:16px;margin:0;flex:1;min-width:0}body.list .pub,body.list .stat,body.list .src{display:none}
body.list .links{margin:0;flex-wrap:nowrap;gap:5px}body.list .dirgo{padding:1px 8px;font-size:12.5px;font-weight:normal;white-space:nowrap}
@media(max-width:560px){body.list article{flex-wrap:wrap;gap:4px}body.list article h2{flex-basis:100%}body.list .links{flex-wrap:wrap}.tools{margin-left:0}}
</style></head><body><div class="band"><div>
<h1>Old Year Book Tables of East Asia</h1>
<div class="topnav"><a class="searchbtn" href="search.html">Full Search</a><nav class="jump" id="jump"><a href="#japan" id="j-japan">Japan</a><a href="#china" id="j-china">China</a><a href="#korea">Korea</a><a href="#taiwan">Taiwan</a><a href="#manchuria">Manchuria</a><a href="#other">Other</a></nav><span class="tools"><span class="lbl">View</span><span class="seg"><button class="viewbtn" id="sortbtn" type="button">⇅ A–Z</button><button class="viewbtn" id="viewbtn" type="button" aria-pressed="false">☰ List</button></span></span></div>
</div></div>
<main>
<div id="groups">
__CARDS__
</div>
<script>(function(){const b=document.getElementById("sortbtn");document.querySelectorAll("#groups .grid").forEach(g=>[...g.children].forEach((a,i)=>a.dataset.i=i));
const key=t=>t.replace(/^(The|A|An)\s+/i,"").toLowerCase();function set(az){document.querySelectorAll("#groups .grid").forEach(g=>{const a=[...g.children];a.sort(az?(x,y)=>key(x.dataset.t).localeCompare(key(y.dataset.t),"en",{numeric:true}):(x,y)=>x.dataset.i-y.dataset.i);a.forEach(e=>g.appendChild(e))});
b.textContent=az?"⇅ By date":"⇅ A–Z";b.title=az?"Showing A–Z; click to sort by date":"Showing by date; click to sort A–Z";try{localStorage.setItem("homesort",az?"az":"date")}catch(e){}b.dataset.az=az?"1":""}
let az=false;try{az=localStorage.getItem("homesort")==="az"}catch(e){}set(az);b.onclick=()=>set(!b.dataset.az)})();</script>
<script>(function(){const b=document.getElementById("viewbtn");function set(l){document.body.classList.toggle("list",l);b.textContent=l?"▦ Cards":"☰ List";b.setAttribute("aria-pressed",l);try{localStorage.setItem("homeview",l?"list":"cards")}catch(e){}}
let l=false;try{l=localStorage.getItem("homeview")==="list"}catch(e){}set(l);b.onclick=()=>set(!document.body.classList.contains("list"))})();</script>
<script>if(Math.random()<.5){const g=document.getElementById("groups");g.insertBefore(document.getElementById("china"),document.getElementById("japan"));
const n=document.getElementById("jump");n.insertBefore(document.getElementById("j-china"),document.getElementById("j-japan"))}</script>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision models of Opus 5.5 or Sonnet 5.5 (named on each book's page). Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<script>document.addEventListener("click",e=>{const b=e.target.closest("[data-about]");if(b){document.getElementById(b.dataset.about).showModal();return}
if(e.target.tagName==="DIALOG")e.target.close()});</script>
<footer>Each table can be downloaded as CSV from its page. Each book can be downloaded whole as an Excel workbook (one sheet per table, with a linked contents sheet) or as JSON; directories are available as Markdown.<br><br>The website was created by Claude Opus 5.5 with <a href="https://muninn.net/">Konrad M. Lawson</a> at the prompt. See: <a href="https://froginawell.net/frog/sources/">Other Resources at Frog in a Well</a></footer>
</main></body></html>
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
#wrap{display:grid;grid-template-columns:340px 1fr;height:calc(100vh - 56px)}
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
.sub{color:var(--muted);font-size:14px;margin-bottom:10px}
.tw{overflow:auto;border:1px solid var(--line);background:var(--panel);margin:8px 0 16px;max-height:70vh}
table{border-collapse:collapse;font-size:13.5px;font-family:"Iowan Old Style",Georgia,"Noto Serif JP","Hiragino Mincho ProN","Hiragino Mincho Pro","Yu Mincho","YuMincho","Noto Serif CJK JP","Source Han Serif JP","MS PMincho",serif}
th,td{border:1px solid var(--line);padding:3px 7px;vertical-align:top}
th{position:sticky;top:0;background:var(--panel);text-align:left;font-weight:bold;font-size:12.5px}
th.sortable{cursor:pointer;user-select:none;padding-right:18px;position:sticky}
th.sortable::after{content:"\2195";position:absolute;right:5px;opacity:.3;font-weight:normal}
th.sortable[aria-sort="ascending"]::after{content:"\25B2";opacity:.9}
th.sortable[aria-sort="descending"]::after{content:"\25BC";opacity:.9}
th.sortable:hover{background:var(--hi)}
td.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
td.blank{background:repeating-linear-gradient(45deg,transparent 0 4px,var(--hi) 4px 8px)}
td.illeg{background:repeating-linear-gradient(45deg,transparent 0 4px,rgba(200,60,40,.32) 4px 8px)}
tr:hover td{background:var(--hi)}
tr.sec td:first-child{font-weight:bold;font-style:italic}
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
.dirbtn{margin-left:auto;background:var(--accent-ink);color:var(--accent)!important;opacity:1!important;font-weight:bold;font-size:14px;padding:6px 14px;border-radius:5px;text-decoration:none;align-self:center}.dirbtn:hover{filter:brightness(.93)}.dirbtn+#toggle,.dirbtn+.dirbtn,.dirbtn+.aboutbtn{margin-left:0}
.en{margin:2px 0 6px;font-size:15px}
.che{display:block;text-transform:none;letter-spacing:0;font-size:11.5px;color:var(--muted);margin-top:1px}
.che2{display:block;font-size:15px;color:var(--muted);margin-top:2px}
.che3{display:block;font-weight:normal;font-size:max(12px,.54em);color:var(--muted);margin-top:.15em}
.enn{color:var(--muted);font-size:13px;white-space:nowrap}
.ctx{max-width:760px;font-size:14.5px;line-height:1.55;margin:8px 0 12px;padding:9px 12px;border-left:3px solid var(--accent);background:var(--panel)}
.aboutbtn{margin-left:auto;font:inherit;font-size:14px;background:transparent;color:var(--accent-ink);border:1px solid currentColor;border-radius:5px;padding:5px 12px;cursor:pointer;align-self:center}.aboutbtn+#toggle{margin-left:0}
dialog{max-width:min(560px,calc(100vw - 32px));border:1px solid var(--line);border-top:4px solid var(--accent);background:var(--panel);color:var(--ink);padding:18px 20px;border-radius:6px;font-size:14.5px}dialog::backdrop{background:rgba(0,0,0,.45)}dialog h3{margin:0 0 2px;font-weight:normal;font-size:19px}dialog .pub{color:var(--muted);font-size:13px}dialog form button{font:inherit;font-size:14px;background:var(--accent);color:var(--accent-ink);border:0;border-radius:5px;padding:6px 14px;cursor:pointer}
@media (max-width:760px){#wrap,body.cmp #wrap{grid-template-columns:minmax(0,1fr);height:auto}#cmp{border-left:0;border-top:2px solid var(--accent);padding:14px 16px}#side,#main{min-width:0;max-width:100vw}#list a{overflow-wrap:anywhere}.tw{max-height:none}header{padding:12px 16px}header h1{font-size:18px}.dirbtn{margin-left:0}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}.chgrid{gap:8px}.chbtn{padding:11px 13px}.chbtn small{font-size:12px}}
</style>
</head>
<body>
<header><a href="../../" style="text-decoration:none;font-size:14px">← All books</a><h1>__BOOK__</h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../../data/__SLUG__.json" style="color:inherit">JSON</a>__XLSX__</span>
__DIRLINK__<button id="toggle" title="Toggle light/dark">◐</button></header>
<div id="wrap">
<nav id="side"><div class="ctl">
<input id="q" type="search" placeholder="Search titles, headings, cells…">
<select id="ch"><option value="">All chapters</option></select>
<label style="font-size:13px;color:var(--muted)"><input type="checkbox" id="flag"> only tables with transcriber warnings</label>
<span class="keys">↑ / ↓ keys: previous / next table</span>
</div><div id="list"></div></nav>
<main id="main"></main>
<aside id="cmp" hidden></aside>
</div>
<script>
const T=__DATA__;
const DIRCARDS=__DIRCARDS__;const PY=__PINYIN__;let ALTR=false;try{ALTR=localStorage.getItem("altrom")==="1"}catch(e){}
const pyd=a=>{if(ALTR||!a)return a;const w=a.split(" ")[0];return PY[w]?PY[w]+a.slice(w.length):a};
const pyl=l=>ALTR?l:pyd(l).replace(/\(([^() ]+)\)$/,(m,w)=>PY[w]?`(${PY[w]})`:m);
const HIDEIMG=__HIDEIMG__;
const MARKED=__MARKED__;
const XL=__XL__;
const CHEN=__CHEN__;
const chE=(c,cls)=>CHEN[c]?`<span class="${cls||"che"}">${esc(CHEN[c])}</span>`:"";
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const isNum=s=>/^[\s(]*[-—–]?[\d.,]+[)*%]*\s*$/.test(s)||/^[—–-]$/.test(s.trim())||s.trim()==="...";
const warnRe=/not reconcile|unreadable|illegible|uncertain|could not|does not/i;
T.forEach(t=>{t._text=fold([t.title,t.en&&t.en.t,t.en&&t.en.d,t.table_no,t.caption_extra,t.context,t.chapter,...(t.parts||[]).flatMap(p=>[p.label,...p.columns,...p.rows.flat()]),...(t.footnotes||[])].join(" ").toLowerCase());
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
function tableHTML(t,q,other){let h=`<section class="tbl" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2>${t.en?`<p class="en"><b>${hl(t.en.t,q)}</b>: ${hl(t.en.d,q)} <span class="enn">(Note: LLM translation)</span></p>`:""}<div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":` · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}`}</div>`;
 if(!other)h+=xlTable(t);
 if(t.caption_extra)h+=`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 if(t.context)h+=`<p class="ctx"><b>Context.</b> ${hl(t.context,q)}</p>`;
 (t.parts||[]).forEach(p=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw"><table><thead><tr>${p.columns.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?' class="sec"':""}>`+r.map((c,j)=>c==="[?]"?`<td class="illeg" title="Unreadable in the scan" aria-label="unreadable"></td>`:`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec&&!MARKED?" blank":""}"${j&&c===""&&!sec&&MARKED?' title="Blank in the original"':""}>${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>"});
 if((t.footnotes||[]).length){const fn=t.footnotes.map(n=>hl(n,q)),hit=fn.some(x=>x.includes("<mark>"));h+=`<details class="notes"${hit?" open":""}><summary>Printed notes (${fn.length})</summary><ul>${fn.map(x=>`<li>${x}</li>`).join("")}</ul></details>`;}
 if((t.transcriber_notes||[]).length)h+=`<details class="notes"><summary${t._warn?' class="warn"':""}>Transcriber's notes (${t.transcriber_notes.length})${t._warn?" — includes unreadable or doubtful cells":""}</summary><ul>${t.transcriber_notes.map(n=>`<li class="${warnRe.test(n)?"warn":""}">${esc(n)}</li>`).join("")}</ul></details>`;
 h+=`<div class="row"><button data-act="dl" data-id="${t.id}">Download CSV</button><button data-act="cp" data-id="${t.id}">Copy as TSV</button></div>`;
 if(!HIDEIMG)h+=`<div class="sub">Source: ${(t.scans||[]).map(s=>s.url?`<a href="${s.url}" target="_blank" rel="noopener">${esc(s.label)}</a>`:esc(s.label)).join(", ")}</div>`;
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
function showHome(){mode="home";cur=null;closeCmp();const n={};T.forEach(t=>{const c=t.chapter||"(no chapter)";n[c]=(n[c]||0)+1});
 if(DIRCARDS){$("#main").innerHTML=`<div class="chhead">Contents</div>`+dirCards()+`<h2 style="margin:28px 0 6px">Tables</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} section${chapters.length===1?"":"s"}. Choose a section, or pick a single table from the list.</div><div class="chgrid" style="--chfs:15px">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+LLMWARN;$("#main").scrollTop=0;mark();return}
 $("#main").innerHTML=`<div class="chhead">Contents</div><h2 style="margin-bottom:6px">Chapters</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} chapter${chapters.length===1?"":"s"}. Choose a chapter, or pick a single table from the list.</div><div class="chgrid">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+dirCards()+LLMWARN;
 $("#main").scrollTop=0;fitGrid();mark()}
// Desktop: pick the largest button font (12-28px) at which every chapter button fits in the pane without scrolling
function fitGrid(){const g=$(".chgrid");if(!g)return;g.style.removeProperty("--chfs");if(innerWidth<=760)return;
 const m=$("#main"),limit=()=>m.getBoundingClientRect().bottom-parseFloat(getComputedStyle(m).paddingBottom);
 const fits=x=>{g.style.setProperty("--chfs",x+"px");return g.getBoundingClientRect().bottom<=limit()};
 let lo=12,hi=28;if(fits(hi))return;if(!fits(lo))return;
 for(let k=0;k<9;k++){const mid=(lo+hi)/2;if(fits(mid))lo=mid;else hi=mid}
 g.style.setProperty("--chfs",lo.toFixed(2)+"px")}
let fitRaf=0;addEventListener("resize",()=>{if(mode!=="home"||DIRCARDS)return;cancelAnimationFrame(fitRaf);fitRaf=requestAnimationFrame(fitGrid)});
function showOne(id){const t=T.find(x=>x.id===id)||T[0];if(!t){$("#main").innerHTML="<p>No tables yet.</p>";return}
 mode="one";cur=t.id;$("#main").innerHTML=tableHTML(t,$("#q").value.trim())+LLMWARN;$("#main").scrollTop=0;
 document.querySelectorAll("#main table").forEach(initSort);mark();if(cmpS)showCmp()}
function showChapter(ch){const q=$("#q").value.trim();const ts=filtered();mode="chapter";cur=null;closeCmp();
 let h=`<div class="chhead"><a href="#">All chapters</a> · Chapter</div><h2 style="margin-bottom:6px">${esc(ch)}${chE(ch,"che2")}</h2><div class="chsum">${ts.length} table${ts.length===1?"":"s"}${$("#flag").checked||q?" matching the current filters":""}</div>`+xlChapter(ch);
 h+=(ts.map(t=>tableHTML(t,q)).join("")||"<p>No tables match.</p>")+LLMWARN;
 $("#main").innerHTML=h;$("#main").scrollTop=0;document.querySelectorAll("#main table").forEach(initSort);
 if(enterAt&&ts.length){const t=enterAt==="first"?ts[0]:ts[ts.length-1];cur=t.id;const el=document.getElementById("t-"+t.id);if(el&&enterAt==="last")el.scrollIntoView({block:"start"});
  const a=document.querySelector(`#list a[href="#${CSS.escape(t.id)}"]`);if(a)a.scrollIntoView({block:"nearest"})}
 enterAt=null;mark()}
let enterAt=null;
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h.startsWith("ch=")){const ch=h.slice(3);if($("#ch").value!==ch){$("#ch").value=ch;renderList()}showChapter(ch);return}
 if(mode==="chapter"&&h&&document.getElementById("t-"+h)){cur=h;document.getElementById("t-"+h).scrollIntoView({block:"start"});mark();return}
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
// Up/Down arrows: previous/next table in the sidebar list (ignored while typing in a field)
document.addEventListener("keydown",e=>{if(e.key!=="ArrowDown"&&e.key!=="ArrowUp")return;if(e.altKey||e.ctrlKey||e.metaKey)return;
 const tag=(document.activeElement&&document.activeElement.tagName)||"";if(/INPUT|SELECT|TEXTAREA/.test(tag))return;
 const links=[...document.querySelectorAll("#list a[href^='#']")];if(!links.length)return;
 document.body.classList.add("kbd");
 let i=links.findIndex(a=>a.classList.contains("on"));const down=e.key==="ArrowDown";
 const ch=$("#ch").value;
 // at either end of a chapter's list, step into the next/previous chapter
 if(ch&&i>-1&&((down&&i===links.length-1)||(!down&&i===0))){
  const opts=[...$("#ch").options].map(o=>o.value).filter(Boolean);const k=opts.indexOf(ch)+(down?1:-1);
  if(k>=0&&k<opts.length){e.preventDefault();enterAt=down?"first":"last";location.hash="ch="+encodeURIComponent(opts[k])}
  return}
 i=i<0?(down?0:links.length-1):Math.min(links.length-1,Math.max(0,i+(down?1:-1)));
 e.preventDefault();location.hash=links[i].getAttribute("href").slice(1);links[i].scrollIntoView({block:"nearest"})});
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
$("#toggle").onclick=()=>{const r=document.documentElement,d=r.dataset.theme==="dark"||(!r.dataset.theme&&matchMedia("(prefers-color-scheme: dark)").matches);r.dataset.theme=d?"light":"dark"};
renderList();route();
</script>
</body>
</html>
"""


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
                entries.append({"a": place, "s": sec, "n": names, "t": txt,
                                "ne": flat(en.get("name") or ""), "te": side(en), "nj": flat(ja.get("name") or ""), "tj": side(ja),
                                "p": e.get("page") or ", ".join(d.get("printed_pages") or []), "l": scan["label"], "u": scan["url"]})
                continue
            sec = e.get("section") or ""
            if sec.isupper():
                sec = sec.title()
            entries.append({"a": d.get("appendix") or "", "s": sec, "n": (e.get("name") or "").rstrip(" ,.") + (" " + e["mark"] if e.get("mark") else "") + (f' ({e["rank"]})' if e.get("rank") else ""),
                            "t": e.get("text") or "", "p": e.get("page") or ", ".join(d.get("printed_pages") or []),
                            "l": scan["label"], "u": scan["url"]})
    if not entries:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-directory.json"), "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    desc = f"{len(entries):,} entries" + section_summary(e["a"] for e in entries)
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__PLACES__", json.dumps(book.get("dir_places", []))).replace("__DIRCARDS__", dir_cards(book)).replace("__PINYIN__", json.dumps(book.get("dir_pinyin", {}), ensure_ascii=False)).replace("__COUNT__", f"{len(entries):,}").replace("__DESC__", html.escape(desc))
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
           .replace("__PROG__", " · <i>transcription in progress</i>" if book.get("dir_in_progress") else "")
           .replace("__MD__", f' · <a href="../../{dl(book["slug"], "directory.md")}" download>Markdown</a>' if dl(book["slug"], "directory.md") else ""))
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
    if not events:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(os.path.join(HERE, "data", book["slug"] + "-chronology.json"), "w", encoding="utf-8") as fh:
        json.dump(events, fh, ensure_ascii=False, indent=1)
    data = json.dumps(events, ensure_ascii=False).replace("</", "<\\/")
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__PLACES__", "[]").replace("__DIRCARDS__", "null").replace("__PINYIN__", "{}").replace("__COUNT__", f"{len(events):,}")
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"])
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
input,select,button{font:inherit;font-size:14px;padding:7px 9px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:4px}
button{cursor:pointer}
#q{flex:1 1 260px;font-size:16px}
#cnt{color:var(--muted);font-size:13px;width:100%}
main{max-width:900px;margin:0 auto;padding:10px 16px 60px}
.sec{font-size:13px;letter-spacing:.06em;text-transform:uppercase;color:var(--accent);margin:22px 0 6px;border-bottom:1px solid var(--line);padding-bottom:3px}
.e{background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--accent);padding:9px 12px;margin:0 0 8px}
.e b{font-size:15.5px}
.e .t{font-size:14.5px}
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
</style></head><body>
<header><a href="./" style="text-decoration:none;font-size:14px">← Tables</a><a href="../../" style="text-decoration:none;font-size:14px">All books</a><h1>__BOOK__ · Directories</h1>
<span class="meta">__DESC____PROG__ · LLM-transcribed · <a href="../../data/__SLUG__-directory.json">JSON</a>__MD__</span>
<button id="toggle" title="Toggle light/dark">◐</button></header>
<div class="bar"><div>
<input id="q" type="search" placeholder="Filter names, places, firms, words…" autofocus>
<select id="ap"><option value="">All sections</option></select>
<label style="font-size:13px"><input type="checkbox" id="nameonly"> names only</label>
<label style="font-size:13px" id="jflab" hidden><input type="checkbox" id="jafirst"> 日本語 first</label>
<label style="font-size:13px" id="arlab" hidden><input type="checkbox" id="altrom"> alt. romanization</label>
<div id="cnt"></div></div></div>
<main><div id="toc"></div><div id="out"></div><button id="more" hidden>Show more</button>
<div class="llmwarn" role="note"><b>Warning:</b> These entries were transcribed by the vision model of Opus 5.5. Before using any of them, you must verify specific details with the original source which is linked to whenever possible.</div></main>
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
 $("#out").innerHTML="";shown=0;more(terms);
 try{history.replaceState(null,"",(q||v)?"#"+new URLSearchParams({q:$("#q").value.trim(),s:v}).toString():location.pathname)}catch(e){}}
function more(terms){terms=terms||norm($("#q").value.trim()).split(/\s+/).filter(Boolean);
 let h="",last=shown?groupOf(res[shown-1]):null;
 res.slice(shown,shown+STEP).forEach(e=>{const g=groupOf(e);if(g!==last){h+=`<div class="sec">${esc(g)}</div>`;last=g}
  const ln=(n,t)=>(n?`<b>${hl(n,terms)}</b> `:"")+`<span class="t">${hl(t||"",terms)}</span>`;
  const body=(e.nj!==undefined)?(JF?[[e.nj,e.tj],[e.ne,e.te]]:[[e.ne,e.te],[e.nj,e.tj]]).filter(x=>x[0]||x[1]).map((x,i)=>`<div class="l${i+1}">${ln(x[0],x[1])}</div>`).join(""):`<b>${hl(e.n,terms)}</b> <span class="t">${hl(e.t,terms)}</span>`;
  h+=`<div class="e">${body}<div class="m">p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`});
 $("#out").insertAdjacentHTML("beforeend",h);shown=Math.min(res.length,shown+STEP);$("#more").hidden=shown>=res.length}
const groupOf=e=>disp(e.a)+(e.s?" — "+e.s:"");
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,120)});
sel.addEventListener("change",run);$("#toc").addEventListener("click",ev=>{const a=ev.target.closest("[data-s]");if(!a)return;ev.preventDefault();sel.value=a.dataset.s;run();scrollTo(0,0)});$("#nameonly").addEventListener("change",run);$("#more").addEventListener("click",()=>more());
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));if(p.get("q"))$("#q").value=p.get("q");if(p.get("s"))sel.value=p.get("s")}catch(e){}
run();
</script></body></html>
"""


SEARCH = r"""<!DOCTYPE html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Noto+Serif+JP:wght@400;700&display=swap">
<script src="fold.js"></script>
<title>Full Search · Old Year Book Tables of East Asia</title>
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
</style></head><body>
<header><a href="./">← All books</a><h1>Full Search</h1><button id="toggle" title="Toggle light/dark">◐</button></header>
<main>
<div class="box"><input id="q" type="search" placeholder="e.g. rice, Dairen, cotton exports, Mitsui, Kato…" autofocus>
<select id="scope" aria-label="Search in">
<option value="all">Everything</option><option value="t">Tables only</option><option value="w">Who's Who only</option>
<option value="d">All directories</option><option value="c">Chronologies only</option></select></div>
<div id="status"></div><div id="out"></div>
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision model of Opus 5.5. Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
</main>
<script>
const BOOKS=__BOOKS__;
const $=s=>document.querySelector(s);
const esc=s=>String(s??"").replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
const norm=s=>fold(String(s??"").normalize("NFD").replace(/[̀-ͯ]/g,"").toLowerCase());
function hl(s,terms){s=String(s??"");const n=norm(s);let marks=[];terms.forEach(t=>{let i=0;while(t&&(i=n.indexOf(t,i))>-1){marks.push([i,i+t.length]);i+=t.length}});
 if(!marks.length)return esc(s);marks.sort((a,b)=>a[0]-b[0]);let out="",pos=0;marks.forEach(([a,b])=>{if(a<pos)return;out+=esc(s.slice(pos,a))+"<mark>"+esc(s.slice(a,b))+"</mark>";pos=b});return out+esc(s.slice(pos))}
const WHO=/who.?s who|contemporary worthies/i;
let TB=null,DR=null,CH=null;
async function loadTables(){if(TB)return TB;$("#status").textContent="Loading tables…";
 TB=(await Promise.all(BOOKS.map(b=>fetch("data/"+b.slug+".json").then(r=>r.json()).then(ts=>ts.map(t=>{
  const rows=(t.parts||[]).flatMap(p=>p.rows||[]);
  return {b,t,rows,head:norm([t.title,t.table_no,t.chapter,t.caption_extra].join(" ")),all:norm([t.title,t.table_no,t.chapter,t.caption_extra,t.context,...(t.parts||[]).flatMap(p=>[p.label,...(p.columns||[])]),...rows.map(r=>r.join(" ")),...(t.footnotes||[])].join(" \n "))}}))))).flat();return TB}
async function loadList(kind,flag){$("#status").textContent="Loading "+(kind==="directory"?"directories":"chronologies")+"…";
 return (await Promise.all(BOOKS.filter(b=>b[flag]).map(b=>fetch("data/"+b.slug+"-"+kind+".json").then(r=>r.json()).then(es=>es.map(e=>({b,e,n:norm(e.n),all:norm(e.n+" "+e.t+" "+e.s+" "+e.a)}))).catch(()=>[])))).flat()}
async function loadDirs(){return DR||(DR=await loadList("directory","dir"))}
async function loadChron(){return CH||(CH=await loadList("chronology","chron"))}
const LIMIT=400;
function tablesHTML(res,terms){const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));let h="";
 BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length}</div>`;
  xs.forEach(x=>{const t=x.t;const lab=(t.table_no?`Table ${t.table_no}. `:"")+(t.title||"");
   const hits=x.rows.filter(r=>terms.some(w=>norm(r.join(" ")).includes(w))).slice(0,3);
   h+=`<div class="r"><a class="t" href="book/${b.slug}/#${encodeURIComponent(t.id)}">${hl(lab,terms)}</a><div class="m">${esc(t.chapter||"")} · p. ${esc((t.printed_pages||[]).join(", "))}${(t.scans||[])[0]&&t.scans[0].url?` · <a href="${t.scans[0].url}" target="_blank" rel="noopener">scan</a>`:""}</div>`+
    (hits.length?`<div class="snip">${hits.map(r=>`<div>${r.map(c=>hl(c,terms)).join(" · ")}</div>`).join("")}</div>`:"")+`</div>`})});return h}
function entriesHTML(res,terms,page,q){const by={};res.slice(0,LIMIT).forEach(x=>(by[x.b.slug]=by[x.b.slug]||[]).push(x));let h="";
 BOOKS.forEach(b=>{const xs=by[b.slug];if(!xs)return;h+=`<div class="bk">${esc(b.title)} · ${xs.length} · <a href="book/${b.slug}/${page}#${new URLSearchParams({q}).toString()}">open in book</a></div>`;
  xs.forEach(({e})=>{h+=`<div class="r"><b>${hl(e.n,terms)}</b> <span class="snip">${hl(e.t,terms)}</span><div class="m">${esc(e.a)}${e.s?" — "+esc(e.s):""} · p. ${esc(e.p)}${e.u?` · <a href="${e.u}" target="_blank" rel="noopener">${esc(e.l)}</a>`:e.l?" · "+esc(e.l):""}</div></div>`})});return h}
const match=(xs,terms)=>xs.filter(x=>terms.every(w=>x.all.includes(w)));
const count=(n,one,many)=>`${n.toLocaleString()} ${n===1?one:many}${n>LIMIT?` (showing ${LIMIT})`:""}`;
async function run(){const q=$("#q").value.trim(),sc=$("#scope").value;const terms=norm(q).split(/\s+/).filter(Boolean);
 try{history.replaceState(null,"",q||sc!=="all"?"#"+new URLSearchParams({q,s:sc}).toString():location.pathname)}catch(e){}
 if(!terms.length){$("#status").textContent="Type to search.";$("#out").innerHTML="";return}
 const parts=[],stat=[];
 if(sc==="all"||sc==="t"){const res=match(await loadTables(),terms);res.sort((a,b)=>terms.filter(w=>b.head.includes(w)).length-terms.filter(w=>a.head.includes(w)).length);
  stat.push(count(res.length,"table","tables"));if(res.length)parts.push((sc==="all"?`<div class="kind">Tables</div>`:"")+tablesHTML(res,terms))}
 if(sc==="all"||sc==="d"||sc==="w"){let res=match(await loadDirs(),terms);if(sc==="w")res=res.filter(x=>WHO.test(x.e.a));
  res.sort((a,b)=>terms.filter(w=>b.n.includes(w)).length-terms.filter(w=>a.n.includes(w)).length);
  stat.push(count(res.length,sc==="w"?"Who's Who entry":"directory entry",sc==="w"?"Who's Who entries":"directory entries"));
  if(res.length)parts.push((sc==="all"?`<div class="kind">Who's Who &amp; directories</div>`:"")+entriesHTML(res,terms,"directory.html",q))}
 if(sc==="all"||sc==="c"){const res=match(await loadChron(),terms);stat.push(count(res.length,"chronology event","chronology events"));
  if(res.length)parts.push((sc==="all"?`<div class="kind">Chronologies</div>`:"")+entriesHTML(res,terms,"chronology.html",q))}
 if(norm($("#q").value.trim())!==norm(q)||$("#scope").value!==sc)return;
 $("#status").textContent=stat.join(" · ");$("#out").innerHTML=parts.join("")||"<p>No matches.</p>"}
let tm;$("#q").addEventListener("input",()=>{clearTimeout(tm);tm=setTimeout(run,200)});$("#scope").addEventListener("change",run);
$("#toggle").addEventListener("click",()=>{const r=document.documentElement;const d=r.dataset.theme?r.dataset.theme==="dark":matchMedia("(prefers-color-scheme: dark)").matches;r.dataset.theme=d?"light":"dark"});
try{const p=new URLSearchParams(location.hash.slice(1));$("#q").value=p.get("q")||p.get("t")||p.get("d")||"";const sc=p.get("s")||(p.get("tab")==="d"?"d":"all");if([...$("#scope").options].some(o=>o.value===sc))$("#scope").value=sc}catch(e){}
run();
</script></body></html>
"""

if __name__ == "__main__":
    main()
