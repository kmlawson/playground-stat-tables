"""mkprompts.py <pre> <series> <nbins> <about> [--new slugs]: write prompts/<pre>N.txt for matching agents (new series:
from S01.txt; update: from JU1.txt), splitting the series' listings into nbins by size."""
import glob, os, re, sys
pre, ser, nb, about = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4]
new = sys.argv[sys.argv.index('--new') + 1] if '--new' in sys.argv else None
L = sorted(((sum(1 for l in open(f) if '|' in l), os.path.basename(f)[:-4]) for f in glob.glob(f'listings/{ser}--*.txt')), reverse=True)
bins = [[0, []] for _ in range(nb)]
for n, x in L:
    b = min(bins, key=lambda b: b[0]); b[0] += n; b[1].append(x)
tpl = open('prompts/JU1.txt' if new else 'prompts/S01.txt').read(); src = 'JU1' if new else 'S01'
for i, (n, xs) in enumerate(bins, 1):
    p = tpl.replace(src, f'{pre}{i}')
    p = re.sub(r'covers these listing files \(in listings/\): .*', 'covers these listing files (in listings/): ' + ', '.join(x + '.txt' for x in xs), p)
    p = re.sub(r'These are (five|editions)[^\n]*', about, p)
    if new: p = re.sub(r'The NEW editions are [^:]*:', f'The NEW editions are {new}:', p)
    open(f'prompts/{pre}{i}.txt', 'w').write(p); print(f'{pre}{i}', n, xs)
