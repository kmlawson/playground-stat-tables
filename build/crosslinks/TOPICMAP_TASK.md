# Chapter-to-topic mapping for a series (one agent per series)

Working folder: /Users/kml/shell/projects/yearbooks/japanyearbooks/stat-tables-site/build/crosslinks
Input: topicmap_input/<series>.md — the series' existing topics (if any) and every chapter of the new editions.
Output: topicmaps/<series>.json:
{"name": "<series name>", "books": ["<new edition slugs>"], "topics": {"<topic>": {"<slug>": ["<chapter name exactly as listed>", ...]}}}
- For an EXISTING series: map each new edition's chapters onto the existing topic names (copy them exactly). A chapter may
  go under two topics if it clearly covers both (e.g. "Justice, Police and Sanitation"). Add a new topic only for a subject
  that recurs in at least two editions (new or existing) and has no existing topic.
- For a NEW series: define about 8–20 short English topics that recur across the editions (e.g. "Population", "Finance",
  "Foreign trade", "Education") and map every edition's chapters onto them.
- Chapter names must be copied exactly as listed (they are matched as strings). Leave out chapters with no recurring
  counterpart (front matter, one-off sections) unless they hold tables that recur elsewhere.
Write valid JSON (python3 json.dump, ensure_ascii=False, indent=1) and check that every chapter name you used is in the
input. No git, nothing in /tmp. Reply in ≤3 lines: topics, chapters mapped, chapters left out.
