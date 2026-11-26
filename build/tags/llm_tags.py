"""llm_tags.py build|write <slug> — the controlled-tag batches of a new book through the llm CLI instead of agents
(for books the user puts on the llm CLI; first used for japan-tokei-1930, 2026-11-26).
build: one job per batches/bNN.json; the system prompt carries NEW_BOOK_TASK.md's rules with README.md,
CLASSIFICATION.md and VOCABULARY.md inline (cached), the batch goes in the prompt. Replies → results/bNN.json.
Run: python3 ../_pipeline/run.py build/tags/runs/new-<slug>/llm_jobs.json 4   (from the site folder's parent's view: any cwd)
Then: python3 build/tags/new_book_tags.py apply <slug>."""
import glob, json, os, re, sys
H = os.path.dirname(os.path.abspath(__file__))
slug = sys.argv[2]; R = f'{H}/runs/new-{slug}'
sys.path.insert(0, H + '/../../../_pipeline'); from common import load
SYS = ("You classify existing table transcriptions with a controlled vocabulary; you do not transcribe or correct anything.\n\n"
       "RULES (README.md):\n" + open(H + '/README.md').read() + "\n\nLATER DECISIONS, which take precedence (CLASSIFICATION.md):\n"
       + open(H + '/CLASSIFICATION.md').read() + "\n\nVOCABULARY (VOCABULARY.md):\n" + open(H + '/VOCABULARY.md').read())
TASK = """Classify every record below (one complete table each: original title, English title/description "en", chapter, caption, parts with columns and row labels, footnotes). "prior", when present, is the saved assignment of a table with the same title in an earlier edition of the same series: a hint, not an answer — keep it when it fits, improve it when the content supports more or different terms.

For each record give:
- "topics": 1–2 high-level topic IDs (principal subject first); [] only if no topic can be decided.
- "tags": 0–3 detailed tag IDs, most useful first, ONLY where a vocabulary term genuinely fits the subject of the table; [] rather than forcing a term. Do not tag incidental rows, units or places.
- "flags": ["text-tables"] only for textual tables (rosters, lists of offices, reference lists); otherwise [].
- Use only IDs that exist in the vocabulary. Never invent IDs. If a useful term is missing, say so in "why".
- "why": a few words of evidence.

Return ONLY a JSON list (no markdown fences), one object per record in the same order, with the record's "key":
[{"key": "...", "topics": [...], "tags": [...], "flags": [], "why": "..."}]

RECORDS:
"""
if sys.argv[1] == 'build':
    os.makedirs(R + '/results', exist_ok=True); os.makedirs(R + '/llm', exist_ok=True)
    jobs = [{'imgs': [], 'model': 'claude-sonnet-5.5', 'system': R + '/llm/system.txt', 'options': {'max_tokens': 64000, 'cache': True},
             'stream': True, 'timeout': 2400, 'prompt': TASK + open(b).read(), 'out': f'{R}/llm/{os.path.basename(b)}'}
            for b in sorted(glob.glob(R + '/batches/b*.json'))]
    open(R + '/llm/system.txt', 'w').write(SYS)
    json.dump(jobs, open(R + '/llm_jobs.json', 'w'), ensure_ascii=False); print(len(jobs), 'jobs')
if sys.argv[1] == 'write':
    for b in sorted(glob.glob(R + '/batches/b*.json')):
        keys = [x['key'] for x in json.load(open(b))]; f = f'{R}/llm/{os.path.basename(b)}'
        s = open(f).read().strip() if os.path.exists(f) else ''; s = re.sub(r'^```(json)?\s*|\s*```$', '', s)
        try: d = json.loads(s[s.find('['):])
        except Exception: print(os.path.basename(b), 'unreadable reply'); continue
        if [x.get('key') for x in d] != keys: print(os.path.basename(b), 'keys differ', len(d), len(keys)); continue
        json.dump(d, open(f'{R}/results/{os.path.basename(b)}', 'w'), ensure_ascii=False, indent=1)
        print(os.path.basename(b), len(d), 'records,', sum(1 for x in d if x.get('tags')), 'with tags')
