#!/bin/bash
# Rebuild the Pagefind search indexes without making the computer unusable (user, 2026-11-13: a full-speed run
# made the machine unusable; an hour or three is fine):
#  - macOS background QoS (taskpolicy -b: efficiency cores only, throttled disk I/O), nice 19, 2 index threads;
#  - written into _search.noindex/ (Spotlight skips folders named *.noindex, so the ~330,000 index files are not
#    indexed by Spotlight as they are written); the site's pagefind/ and pagefind-titles/ are symlinks to it;
#  - a watchdog pauses the whole job (SIGSTOP) while free memory is under 25% and resumes it above 35%,
#    and logs memory every minute to _search.noindex/build.log;
#  - then packs ../search-index-upload.tar.gz for the live site.
# Run:  bash build/search_gently.sh      (from the repo; uses uv with pagefind[extended])
set -u
cd "$(dirname "$0")/.."
SITE=$PWD; OUT=$SITE/_search.noindex; mkdir -p "$OUT"; LOG=$OUT/build.log
T=${SEARCH_THREADS:-2}
export SEARCH_OUT=$OUT SEARCH_THREADS=$T RAYON_NUM_THREADS=$T
: >| "$LOG"
set -m   # the job gets its own process group, so the watchdog can pause and resume all of it at once
taskpolicy -b nice -n 19 uv run --with "pagefind[extended]" build/build_search.py >> "$LOG" 2>&1 &
PID=$!
set +m
free_pct() { memory_pressure 2>/dev/null | awk -F': ' '/free percentage/{gsub("%","",$2);print $2}'; }
paused=0; tick=0; start=$(date +%s)
while kill -0 $PID 2>/dev/null; do
  sleep 20; tick=$((tick+1))
  f=$(free_pct); f=${f:-50}
  if [ $paused = 0 ] && [ "$f" -lt 25 ]; then kill -STOP -- -$PID 2>/dev/null; paused=1; echo "[watchdog $(date +%H:%M)] free memory ${f}% — paused" >> "$LOG"; fi
  if [ $paused = 1 ] && [ "$f" -gt 35 ]; then kill -CONT -- -$PID 2>/dev/null; paused=0; echo "[watchdog $(date +%H:%M)] free memory ${f}% — resumed" >> "$LOG"; fi
  if [ $((tick % 3)) = 0 ]; then
    rss=$(ps -o rss= -g $PID 2>/dev/null | awk '{s+=$1}END{printf "%.1f", s/1048576}')
    echo "[watchdog $(date +%H:%M)] $(( ($(date +%s)-start)/60 )) min, job memory ${rss} GB, system free ${f}%" >> "$LOG"
  fi
done
wait $PID; rc=$?
[ $rc = 0 ] || { echo "build_search.py failed (exit $rc); the old indexes are untouched"; tail -5 "$LOG"; exit $rc; }
for n in pagefind pagefind-titles; do
  if [ -d "$SITE/$n" ] && [ ! -L "$SITE/$n" ]; then
    \mv -f "$SITE/$n" "$OUT/old-$n" && taskpolicy -b find "$OUT/old-$n" -delete
  fi
  [ -L "$SITE/$n" ] || ln -s "_search.noindex/$n" "$SITE/$n"
done
taskpolicy -b nice -n 19 tar -czf "$SITE/../search-index-upload.tar.gz" -C "$OUT" pagefind pagefind-titles
grep -E '^pagefind' "$LOG"
echo "packed $(du -h "$SITE/../search-index-upload.tar.gz" | cut -f1) → $(cd "$SITE/.." && pwd)/search-index-upload.tar.gz; took $(( ($(date +%s)-start)/60 )) min"
