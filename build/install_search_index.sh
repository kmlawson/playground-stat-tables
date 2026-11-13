#!/bin/sh
# Install a new Pagefind search index on the live site.
#
# Usage, from the site folder (the one with search.html), after uploading the tarball there:
#   sh install_search_index.sh [search-index-upload.tar.gz] [site folder]
# (kept in the repository as build/install_search_index.sh; upload a copy next to the tarball)
#
# Unpacks the tarball into a temporary folder next to the site, checks it has both indexes,
# then swaps them in for the old pagefind/ and pagefind-titles/ and deletes the old ones.
# Search keeps working until the swap, which takes a moment. The tarball is left in place.
set -eu

TARBALL=${1:-search-index-upload.tar.gz}
SITE=${2:-.}

[ -f "$TARBALL" ] || { echo "No tarball at $TARBALL" >&2; exit 1; }
[ -f "$SITE/search.html" ] || { echo "$SITE does not look like the site folder (no search.html)" >&2; exit 1; }

NEW=$(mktemp -d "$SITE/.pagefind-new.XXXXXX")
OLD=$(mktemp -d "$SITE/.pagefind-old.XXXXXX")
trap 'rm -rf "$NEW"' EXIT

echo "Unpacking $TARBALL ..."
tar -xzf "$TARBALL" -C "$NEW"

for d in pagefind pagefind-titles; do
  [ -f "$NEW/$d/pagefind.js" ] || { echo "The tarball has no $d/pagefind.js; nothing changed." >&2; rmdir "$OLD"; exit 1; }
done
find "$NEW" -name .DS_Store -delete

# swap: move the old folders aside, the new ones in
for d in pagefind pagefind-titles; do
  if [ -e "$SITE/$d" ] || [ -L "$SITE/$d" ]; then mv "$SITE/$d" "$OLD/$d"; fi
  mv "$NEW/$d" "$SITE/$d"
done
chmod -R a+rX "$SITE/pagefind" "$SITE/pagefind-titles"

echo "Deleting the old index ..."
rm -rf "$OLD"

echo "Done: $(find "$SITE/pagefind" -type f | wc -l | tr -d ' ') files in pagefind/, $(find "$SITE/pagefind-titles" -type f | wc -l | tr -d ' ') in pagefind-titles/."
echo "You can now delete $TARBALL."
