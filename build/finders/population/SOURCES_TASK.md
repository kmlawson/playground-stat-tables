# Population page — where to find the real historical statistics (agent brief)

The site *Old Tables of East Asia* has a Population page (`figures/population.html`) that gathers population figures
transcribed from old yearbooks for each place. At the top of each region's page we will add a short caution: these
figures are for comparison and study; for serious work, consult the historical statistics published by national
statistical agencies and in recent scholarship. Your job is to find **the best online sources** of historical
population statistics **up to about 1950** for your regions, so the page can link to them.

## What to find, per region

1. **National / official agencies** that host historical (pre-1950) population data: e.g. a statistics bureau's
   historical statistics series, a national archive or library's digitised statistical yearbooks and census reports.
   For each: the agency's **home page** and a **deep link** that takes a reader as close as possible to the pre-1950
   population data (the historical-statistics section, the census series page, the specific table or collection).
2. **Scholarship and research databases** of recognised standing: university or research-institute projects that
   publish long-run historical population series (e.g. compiled long-term statistics, historical census databases,
   digitised colonial census series). Prefer free, stable, well-maintained sites; name the institution and the
   reference work they are based on.

Aim for 2–5 sources per region, best first. Quality beats quantity: a source must actually hold pre-1950 population
figures for that place. For colonial territories, look both at the former colonial power's records (e.g. Japanese
Government-General statistics digitised by Japanese, Korean or Taiwanese institutions) and at the present-day
country's agencies.

## Verify every link

Open every URL you give (WebFetch, or `curl -sL -A "old-tables-research/1.0 (link check)" -o /dev/null -w "%{http_code}"`)
and confirm it loads and says what you claim. Never put any personal name, e-mail address or contact detail in a
User-Agent, header or request. Record whether the page is in English, Japanese, Korean or Chinese, and whether the
data need a login (avoid those unless nothing else exists; say so).

## Output

Write `build/finders/population/work/sources/<AGENT>.json`, a JSON object keyed by region id:

```json
{"japan": [{"name": "Historical Statistics of Japan", "by": "Statistics Bureau of Japan", "kind": "agency",
            "home": "https://...", "deep": "https://...", "lang": "en, ja",
            "what": "one sentence: what pre-1950 population data is there and how to reach it",
            "checked": "200, 2026-11-09"}], …}
```

`kind`: `agency` or `scholarship`. Write the file early and add to it as you go; check it parses
(`python3 -c "import json,sys;json.load(open(sys.argv[1]))" FILE`). Do not change any other file. No git commands.
Scratch files only in `build/finders/population/work/sources/<AGENT>-scratch/`, never `/tmp`.

Reply with only: regions covered, number of sources per region, and anything you could not find.
