#!/usr/bin/env python3
"""Build the stat-tables site: a landing page plus one table browser per book.

For each book in BOOKS, reads <book dir>/_work/tables/*.json and writes
<slug>/index.html (self-contained) and data/<slug>.json. Books without tables yet are listed
as "in progress" on the landing page. Scan links point to the online scan where one exists.
"""
import json, glob, os, re, html
from pathlib import Path

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
    pc = lambda a, b: f"{100 * a / b:.2f}%" if b else "0%"
    return (f'<div class="{cls}" title="Cells marked unreadable (red hatch) or containing a printed or doubtful ?">'
            f'Unreadable or “?” cells: <b>{q:,}</b> of {tot:,} ({pc(q, tot)}) · '
            f'Tables with more than 20% such cells: <b>{heavy:,}</b> of {nt:,} ({pc(heavy, nt)})</div>')


# Topic tags (build/topics/<region>.json: {"slug:id": [[topic, subtopic], …]}). Tagged tables get chart views and
# are listed on the topic pages (user, 2026-10-22: Korea first; charts only for the topic tables for now).
TOPIC_TAGS = {}
for _f in sorted((Path(__file__).parent / "topics").glob("*.json")):
    if re.fullmatch(r"[a-z]+\.json", _f.name):   # korea.json, taiwan.json (not the agents' tags_*.json)
        TOPIC_TAGS.update(json.loads(_f.read_text()))
# Every table of these regions gets a chart view (user, 2026-10-22, after the topic tables); elsewhere only tagged tables.
CHART_ALL = ("korea-", "taiwan-", "china-", "japan-")


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
    "china": ("China", [("cy", "China Year Book", r"^china-(19[12]\d|193[18])(-\d+)?$"), ("ch", "China Handbook", r"^china-(1937-43|1944|1950)$"),
                        ("ot", "Other surveys", r"^china-(flood|handbook|peking)-")]),
    "japan": ("Japan", [("jy", "Japan Year Book", r"^japan-\d{4}(-\d+)?$"), ("jm", "Japan-Manchoukuo Year Book", r"^japan-manchoukuo-"),
                        ("tk", "日本帝國統計年鑑", r"^japan-tokei-")]),
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
                   .replace("__WHO__", "the colonial administration" if region in ("korea", "taiwan") else "the officials, editors and publishers")
                   .replace("__DATA__", json.dumps({"items": items, "vols": [vols[s] for s in order], "subs": SUBTOPICS[key],
                                                    "series": [[c, n] for c, n, _ in series]}, ensure_ascii=False).replace("</", "<\\/"))
                   .replace("__N__", str(len(items))).replace("__NV__", str(len({i["s"] for i in items}))))
            with open(os.path.join(HERE, "topics", f"{region}-{key}.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
            print(f"topics/{region}-{key}.html: {len(items)} tables")
    rows = "".join(f'<tr><th>{n}</th>' + "".join(f'<td><a href="{r}-{k}.html"><b>{TOPIC_REGIONS[r][0]}</b><span>{counts[(r, k)][0]:,} tables · {counts[(r, k)][1]} volumes</span></a></td>' if (r, k) in counts else "<td></td>" for r in have) + "</tr>" for k, n in TOPICS)
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
</style></head><body>
<div class="band"><div><a href="../index.html">← All books</a><h1>Tables by topic</h1></div></div>
<main><p class="lede">Each page gathers the tables on one topic from every volume of one region, as printed — with their own categories, units, years and gaps — in edition order, with a grid showing which volumes have tables on what. The tables were sorted into topics by a language model reading their titles and headings, so some may be missing or misplaced.</p>
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
<p class="lede">__N__ tables from __NV__ __REGION__ volumes on this site, each as it was printed — with the book's own categories, units, years and gaps — and each opening in its book, where it can be read as a table or a chart. The tables were sorted into these topics by a language model reading their titles and headings, so some may be missing or misplaced; the categories are those of __WHO__ that compiled them, and they change from one volume to the next.</p>
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
        b["_qstat"] = qstat_html(tables)
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
                   .replace("__ORIG__", json.dumps(orig_link(b), ensure_ascii=False))
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
                               f'<dialog id="about" onclick="if(event.target===this)this.close()"><h3>{html.escape(b["title"])}</h3>{f'<div class="pub">{html.escape(b["subtitle"])}</div>' if b.get("subtitle") else ""}<div class="pub">{html.escape(b["publisher"])}</div>'
                               f'<p>{html.escape(b["gaps"])}</p>{"" if b.get("blank_marking") else BLANK_NOTE}<form method="dialog"><button>Close</button></form></dialog>' if b.get("gaps") else "")))
            with open(os.path.join(HERE, "book", b["slug"], "index.html"), "w", encoding="utf-8") as fh:
                fh.write(doc)
    tcounts, thave = build_topics(pages)
    with open(os.path.join(HERE, "index.html"), "w", encoding="utf-8") as fh:
        fh.write(landing(cards).replace("__TOPICMENU__", topics_menu(tcounts, thave)))
    books = [{"slug": b["slug"], "title": b["title"], "dir": bool(b.get("_dir_n")), "chron": bool(b.get("_chron_n")),
              "g": group_of(b), "y": years_of(b), "sc": b.get("scan")} for b, n, c, ch in cards if n]
    with open(os.path.join(HERE, "search.html"), "w", encoding="utf-8") as fh:
        fh.write(SEARCH.replace("__BOOKS__", json.dumps(books, ensure_ascii=False)))


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
            return b["scan"].format(part=int(mp.group(1)), leaf=int(mp.group(2)) + d)
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
        if m and "?" not in str(e.get("page")):  # a half-read page number would send the link astray
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
        grp = group_of(b)
        title = f'<a href="book/{b["slug"]}/" style="color:inherit;text-decoration:none">{html.escape(b["title"])}</a>' if n else html.escape(b["title"])
        items.append((grp, b["slug"], f"""<article data-t="{html.escape(b["title"])}"><h2>{title}</h2><div class="pub">{html.escape(b["publisher"])}</div>{f'<div class="pub"><i>{html.escape(b["note"])}</i></div>' if b.get("note") else ""}
<div class="stat">{stat}</div><div class="src">LLM-transcribed{item}</div>{b.get("_qstat", "")}<div class="links">{link}</div></article>"""))
    order = {"far-east": 0, "manchoukuo": 1}
    other = sorted([(sl, h) for g, sl, h in items if g == "other"], key=lambda x: order.get(x[0].rsplit("-", 1)[0], 9))
    names = {"japan": "Japan", "china": "China", "korea": "Korea", "taiwan": "Taiwan", "manchuria": "Manchuria", "south-seas": "South Seas Mandate", "other": "Other"}
    body = {g: "\n".join(h for gg, sl, h in items if gg == g) for g in ("japan",)}
    year = {b["slug"]: edition(b) for b in BOOKS}
    body["china"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "china"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["korea"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "korea"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["taiwan"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "taiwan"), key=lambda x: (year[x[1]], x[1])))
    body["manchuria"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "manchuria"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["south-seas"] = "\n".join(h for g, sl, h in sorted((x for x in items if x[0] == "south-seas"), key=lambda x: (year[x[1]], x[1])))  # by edition year
    body["other"] = "\n".join(h for _, h in other)
    topics = {r: f'<p class="tlinks">{rn} tables by topic: ' + " · ".join(f'<a href="topics/{r}-{k}.html">{n}</a>' for k, n in TOPICS) + "</p>"
              for r, (rn, _) in TOPIC_REGIONS.items() if any(k.startswith(r + "-") for k in TOPIC_TAGS)}
    grids = "".join(f'<section class="grp" id="{g}"><h2 class="grph">{names[g]}</h2>{topics.get(g, "")}<div class="grid">{body[g]}</div></section>'
                    for g in ("japan", "china", "korea", "taiwan", "manchuria", "south-seas", "other") if body[g])
    return LANDING.replace("__CARDS__", "__TOPICMENU__" + grids)


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
.grp{scroll-margin-top:12px}.grp{border-top:2px solid var(--line);margin-top:34px;padding-top:6px}.grp:first-child{margin-top:4px}.grph{font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);margin:18px 0 0;font-weight:bold}.grp .grid{margin-top:14px}.tmenu{margin:4px 0 8px}.tmn{color:var(--muted);font-size:14.5px;margin:6px 0 10px}.tmn a{color:var(--accent)}.tmrow{display:flex;flex-wrap:wrap;gap:6px 8px;align-items:baseline;padding:7px 0;border-top:1px solid var(--line)}.tmt{min-width:150px;font-size:16px}.tmrow a{color:var(--accent);text-decoration:none;border:1px solid var(--line);background:var(--panel);border-radius:14px;padding:2px 11px;font-size:14.5px}.tmrow a:hover{border-color:var(--accent)}.tmrow small{color:var(--muted)}.tlinks{margin:8px 0 0;font-size:15px}.tlinks a{color:var(--accent)}
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
.tools{margin-left:auto;display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--accent-ink);opacity:.8}.tools:hover{opacity:1}.tools .lbl{font-size:12px;text-transform:uppercase;letter-spacing:.06em}.seg{display:inline-flex;border:1px solid currentColor;border-radius:999px;overflow:hidden}.viewbtn{font:inherit;font-size:13px;background:transparent;color:inherit;border:0;padding:4px 12px;cursor:pointer;white-space:nowrap}.viewbtn+.viewbtn{border-left:1px solid currentColor}.viewbtn:hover{background:rgba(127,127,127,.15)}
body.list .grid{display:block;margin-top:8px}body.list article{flex-direction:row;align-items:center;gap:12px;padding:5px 10px;border:0;border-bottom:1px solid var(--line);border-left:3px solid var(--accent)}
body.list article+article{margin-top:0}body.list article h2{font-size:16px;margin:0;flex:1;min-width:0}body.list .pub,body.list .stat,body.list .src,body.list .qstat{display:none}
body.list .links{margin:0;flex-wrap:nowrap;gap:5px}body.list .dirgo{padding:1px 8px;font-size:12.5px;font-weight:normal;white-space:nowrap}
@media(max-width:560px){body.list article{flex-wrap:wrap;gap:4px}body.list article h2{flex-basis:100%}body.list .links{flex-wrap:wrap}.tools{margin-left:0}}
</style></head><body><div class="band"><div>
<h1>Old Year Book Tables of East Asia</h1>
<div class="topnav"><a class="searchbtn" href="search.html">Full Search</a><a class="searchbtn" href="topics/index.html">Topics</a><nav class="jump" id="jump"><a href="#japan" id="j-japan">Japan</a><a href="#china" id="j-china">China</a><a href="#korea">Korea</a><a href="#taiwan">Taiwan</a><a href="#manchuria">Manchuria</a><a href="#south-seas">South Seas</a><a href="#other">Other</a></nav><span class="tools"><span class="lbl">View</span><span class="seg"><button class="viewbtn" id="sortbtn" type="button">⇅ A–Z</button><button class="viewbtn" id="viewbtn" type="button" aria-pressed="false">☰ List</button></span></span></div>
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
<div class="llmwarn" role="note"><b>Warning:</b> These tables were transcribed by the vision models of Opus 5.5, Sonnet 5.5, or Haiku 5.5 (named on each book's page). Before using any of these figures, you must verify specific statistics with the original source which is linked to whenever possible.</div>
<script>document.addEventListener("click",e=>{const b=e.target.closest("[data-about]");if(b){document.getElementById(b.dataset.about).showModal();return}
if(e.target.tagName==="DIALOG")e.target.close()});</script>
<footer>Each table can be downloaded as CSV from its page. Each book can be downloaded whole as an Excel workbook (one sheet per table, with a linked contents sheet) or as JSON; directories are available as Markdown.<br><br>The website was created by Claude Opus 5.5 with <a href="https://muninn.net/">Konrad M. Lawson</a> at the prompt. See: <a href="https://froginawell.net/frog/sources/">Other Resources at Frog in a Well</a></footer>
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
tr.sec td:first-child{font-weight:bold;font-style:italic}tr.sec.cjk td:first-child{font-style:normal}
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
.qstat{font-size:13.5px;color:var(--muted);margin:0 0 16px}.origbtn{display:inline-block;margin:4px 0 16px;padding:8px 14px;border:1px solid var(--accent);border-radius:6px;background:var(--panel);color:var(--accent);text-decoration:none;font-size:15px;font-weight:bold}.origbtn:hover{background:var(--hi)}
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
.tc-svg{display:block;overflow:visible}.tc-ax{font-size:10.5px;fill:var(--muted)}.tc-lab{font-size:12px;fill:var(--ink)}.tc-tot{font-weight:600}.tc-gl{font-size:12px;font-weight:600;fill:var(--ink)}.tc-grid{stroke:var(--line);stroke-width:1}.tc-zero{stroke:var(--muted);stroke-width:1}.tc-guide{stroke:var(--muted);stroke-dasharray:3 3}.tc-q{font-size:12px;font-weight:700;fill:#c0392b}.tc-neq{font-size:14px;font-weight:700;fill:var(--warn)}.tc-totmark{stroke:var(--ink);stroke-width:2}
.tc-tip{position:absolute;z-index:5;background:var(--panel);color:var(--ink);border:1px solid var(--line);box-shadow:0 2px 8px rgba(0,0,0,.2);padding:6px 9px;font-size:12.5px;max-width:min(360px,92%);pointer-events:none;line-height:1.45}.tc-tip div{display:flex;gap:5px;align-items:baseline}.tc-tip i{position:relative;top:1px}.tc-sum{margin-top:4px;color:var(--muted)}.tc-sum.warn{color:var(--warn)}
.tc-note{font-size:12px;color:var(--muted);margin:8px 0 0}.tc-msg{font-size:13px;color:var(--muted)}.tc-multi{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:14px}.tc-mt{font-size:12.5px;display:flex;gap:6px;align-items:center;margin-bottom:2px}tr.tc-hl td{background:var(--hi)}
@media (max-width:760px){#wrap,body.cmp #wrap{grid-template-columns:minmax(0,1fr);height:auto}#cmp{border-left:0;border-top:2px solid var(--accent);padding:14px 16px}#side,#main{min-width:0;max-width:100vw}#list a{overflow-wrap:anywhere}.tw{max-height:none}header{padding:12px 16px}header h1{font-size:18px}.dirbtn{margin-left:0}#side{border-right:0;border-bottom:1px solid var(--line)}#list{max-height:40vh}#main{padding:14px 16px}.chgrid{gap:8px}.chbtn{padding:11px 13px}.chbtn small{font-size:12px}}
</style>
</head>
<body>
<header><a href="../../" style="text-decoration:none;font-size:14px">← All books</a><h1><a href="./" onclick="goHome();return false" style="color:inherit;text-decoration:none" title="Back to this book's contents">__BOOK__</a></h1>
<span class="meta">__COUNT__ tables · __CELLS__ cells · __SOURCE__ · <a href="../../data/__SLUG__.json" style="color:inherit">JSON</a>__XLSX__</span>
<a class="dirbtn homebtn" href="./" onclick="goHome();return false" title="Back to this book's contents (chapters and the printed table of contents)">☰ Contents</a>__DIRLINK__<button id="annot" class="anbtn" aria-pressed="false" title="Private notes: highlight and comment on tables. Saved only in this browser.">Notes</button><button id="toggle" title="Toggle light/dark">◐</button></header>
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
__CHARTJS__<script>
const T=__DATA__;
const CHARTIDS=new Set(__CHARTIDS__);let VW="both";try{VW=localStorage.getItem("tview")||"both"}catch(e){}document.body.classList.add("vw-"+VW);
const DIRCARDS=__DIRCARDS__;const PY=__PINYIN__;let ALTR=false;try{ALTR=localStorage.getItem("altrom")==="1"}catch(e){}
const pyd=a=>{if(ALTR||!a)return a;const w=a.split(" ")[0];return PY[w]?PY[w]+a.slice(w.length):a};
const pyl=l=>ALTR?l:pyd(l).replace(/\(([^() ]+)\)$/,(m,w)=>PY[w]?`(${PY[w]})`:m);
const HIDEIMG=__HIDEIMG__;
const ORIG=__ORIG__;
const PTOC=__PTOC__;
const PTK=PTOC.some(e=>e.k);let ptkOn=false;try{ptkOn=localStorage.getItem("ptocTables")==="1"}catch(e){}
const ptoc=()=>PTOC.length?`<details class="ptoc"><summary>Contents of the printed book (${PTOC.length} entries)${ORIG?` · each links to its page on ${esc(ORIG.l)}`:""}</summary>${PTK?`<label class="ptk"><input type="checkbox" id="ptocT"${ptkOn?" checked":""} onchange="ptocTables(this.checked)"> Show tables <span class="ptkh">(links to the tables transcribed on this site)</span></label>`:""}<ul${ptkOn?' class="showt"':""}>`+PTOC.map(e=>{const ks=e.k||[],same=ks.length===1?ks.filter(k=>ptLike(k[1],e.t)):ks.filter(k=>ptNorm(k[1])===ptNorm(e.t)),rest=ks.filter(k=>!same.includes(k));
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
const origLink=()=>ORIG?`<a class="origbtn" href="${esc(ORIG.u)}" target="_blank" rel="noopener">Read the full original book on ${esc(ORIG.l)} ↗</a>`:"";
const MARKED=__MARKED__;
const CJK=/[\u3040-\u30ff\u3400-\u9fff\uf900-\ufaff]/;  // never italicise Asian text (user, 2026-10-22)
const QSTAT=__QSTAT__;
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
function hasChart(t){return CHARTIDS.has(t.id)&&window.TableCharts&&TableCharts.chartable(t)}
function vsw(){return `<div class="vsw" role="group" aria-label="Show table, chart or both">${[["table","Table"],["chart","Chart"],["both","Both"]].map(([v,l])=>`<button type="button" data-vw="${v}" class="${VW===v?"on":""}">${l}</button>`).join("")}</div>`}
function setVW(v){VW=v;try{localStorage.setItem("tview",v)}catch(e){}document.body.classList.remove("vw-table","vw-chart","vw-both");document.body.classList.add("vw-"+v);document.querySelectorAll(".vsw button").forEach(b=>b.classList.toggle("on",b.dataset.vw===v));chartsGo()}
function chartsGo(){if(window.TableCharts)TableCharts.mountAll(document.getElementById("main"),id=>T.find(x=>x.id===id),{marked:MARKED})}
document.addEventListener("click",e=>{const b=e.target.closest(".vsw button");if(b)setVW(b.dataset.vw)});
function tableHTML(t,q,other){const ch=!other&&hasChart(t);let h=`<section class="tbl${ch?" hasch":""}" id="t-${t.id}"><h2><a href="#${t.id}">${hl(label(t),q)}</a></h2>${t.en?`<p class="en"><b>${hl(t.en.t,q)}</b>: ${hl(t.en.d,q)} <span class="enn">(Note: LLM translation)</span></p>`:""}<div class="sub">${esc(t.chapter||"")} · printed page${(t.printed_pages||[]).length>1?"s":""} ${esc((t.printed_pages||[]).join(", "))}${HIDEIMG?"":` · ${/^p\d/.test(t.image||"")?"scan leaf":"photo"} ${esc((t.images||[t.image]).join(", "))}`}</div>`+(ch?vsw():"");
 if(!other)h+=xlTable(t);
 if(t.caption_extra)h+=CJK.test(t.caption_extra)?`<div class="sub">${hl(t.caption_extra,q)}</div>`:`<div class="sub"><i>${hl(t.caption_extra,q)}</i></div>`;
 if(t.context)h+=`<p class="ctx"><b>Context.</b> ${hl(t.context,q)}</p>`;
 (t.parts||[]).forEach((p,pi)=>{if(p.label)h+=`<div class="part">${hl(p.label,q)}</div>`;
  h+=`<div class="tw" data-p="${pi}"><table><thead><tr>${p.columns.map((c,j)=>`<th class="sortable" data-col="${j}" title="Click to sort">${hl(c,q)}</th>`).join("")}</tr></thead><tbody>`;
  p.rows.forEach((r,ri)=>{const sec=r.length>1&&r.slice(1).every(c=>c==="");h+=`<tr data-i="${ri}"${sec?(CJK.test(r[0])?' class="sec cjk"':' class="sec"'):""}>`+r.map((c,j)=>c==="[?]"?`<td class="illeg" title="Unreadable in the scan" aria-label="unreadable"></td>`:`<td class="${j&&isNum(c)?"num":""}${j&&c===""&&!sec&&!MARKED?" blank":""}"${j&&c===""&&!sec&&MARKED?' title="Blank in the original"':""}>${hl(c,q)}</td>`).join("")+"</tr>"});
  h+="</tbody></table></div>";if(ch)h+=`<div class="tchart" data-id="${esc(t.id)}" data-p="${pi}"></div>`});
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
 if(DIRCARDS){$("#main").innerHTML=`<div class="chhead">Contents</div>`+origLink()+QSTAT+ptoc()+dirCards()+`<h2 style="margin:28px 0 6px">Tables</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} section${chapters.length===1?"":"s"}. Choose a section, or pick a single table from the list.</div><div class="chgrid" style="--chfs:15px">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+LLMWARN;$("#main").scrollTop=0;mark();anSync();return}
 $("#main").innerHTML=`<div class="chhead">Contents</div>`+origLink()+QSTAT+ptoc()+`<h2 style="margin-bottom:6px">Chapters</h2><div class="chsum">${T.length} table${T.length===1?"":"s"} in ${chapters.length} chapter${chapters.length===1?"":"s"}. Choose a chapter, or pick a single table from the list.</div><div class="chgrid">`+
  chapters.map(c=>`<a class="chbtn" href="#ch=${encodeURIComponent(c)}">${esc(c)}${chE(c,"che3")}<small>${n[c]} table${n[c]===1?"":"s"}</small></a>`).join("")+`</div>`+dirCards()+LLMWARN;
 $("#main").scrollTop=0;fitGrid();mark();anSync()}
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
 document.querySelectorAll("#main table").forEach(initSort);chartsGo();mark();if(cmpS)showCmp();anSync()}
function showChapter(ch){const q=$("#q").value.trim();const ts=filtered();mode="chapter";cur=null;closeCmp();
 let h=`<div class="chhead"><a href="#">All chapters</a> · Chapter</div><h2 style="margin-bottom:6px">${esc(ch)}${chE(ch,"che2")}</h2><div class="chsum">${ts.length} table${ts.length===1?"":"s"}${$("#flag").checked||q?" matching the current filters":""}</div>`+xlChapter(ch);
 h+=(ts.map(t=>tableHTML(t,q)).join("")||"<p>No tables match.</p>")+LLMWARN;
 $("#main").innerHTML=h;$("#main").scrollTop=0;document.querySelectorAll("#main table").forEach(initSort);chartsGo();
 if(enterAt&&ts.length){const t=enterAt==="first"?ts[0]:ts[ts.length-1];cur=t.id;const el=document.getElementById("t-"+t.id);if(el&&enterAt==="last")el.scrollIntoView({block:"start"});
  const a=document.querySelector(`#list a[href="#${CSS.escape(t.id)}"]`);if(a)a.scrollIntoView({block:"nearest"})}
 enterAt=null;mark();anSync()}
let enterAt=null;
function route(){const h=decodeURIComponent(location.hash.slice(1));
 if(h.startsWith("an=")){anLink(h.slice(3));return}
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
    committed = os.path.join(HERE, "data", book["slug"] + "-directory.json")
    if not files and os.path.exists(committed):  # book folder not on this machine: rebuild the page from the committed data
        with open(committed, encoding="utf-8") as fh:
            entries = json.load(fh)
    if not entries:
        return 0
    os.makedirs(os.path.join(HERE, "book", book["slug"]), exist_ok=True)
    with open(committed, "w", encoding="utf-8") as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=1)
    data = json.dumps(entries, ensure_ascii=False).replace("</", "<\\/")
    desc = f"{len(entries):,} entries" + section_summary(e["a"] for e in entries)
    doc = (DIRTEMPLATE.replace("__DATA__", data).replace("__PLACES__", json.dumps(book.get("dir_places", []))).replace("__DIRCARDS__", dir_cards(book)).replace("__PINYIN__", json.dumps(book.get("dir_pinyin", {}), ensure_ascii=False)).replace("__COUNT__", f"{len(entries):,}").replace("__DESC__", html.escape(desc))
           .replace("__BOOK__", html.escape(book["title"])).replace("__SLUG__", book["slug"]).replace("__MODEL__", book.get("model", "Opus 5.5"))
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
<label style="font-size:13px"><input type="checkbox" id="nameonly"> names only</label>
<label style="font-size:13px" id="jflab" hidden><input type="checkbox" id="jafirst"> 日本語 first</label>
<label style="font-size:13px" id="arlab" hidden><input type="checkbox" id="altrom"> alt. romanization</label>
<div id="cnt"></div></div></div>
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
 $("#out").innerHTML="";shown=0;more(terms);
 try{history.replaceState(null,"",(q||v)?"#"+new URLSearchParams({q:$("#q").value.trim(),s:v}).toString():location.pathname)}catch(e){}anSync()}
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
</style></head><body>
<header><a href="./">← All books</a><h1>Full Search</h1><button id="toggle" title="Toggle light/dark">◐</button></header>
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
<div id="status"></div><div id="out"></div>
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
const href=d=>String(d.url||"").replace(/^\/+/,"");
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
async function run1(){const q=$("#q").value.trim(),sc=$("#scope").value,ti=$("#titles").checked;const terms=norm(q).replace(/"/g," ").split(/\s+/).filter(Boolean);
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
