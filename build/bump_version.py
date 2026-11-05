"""bump_version.py: increment the site version (build/VERSION.json) and stamp it with the current local time.

Version numbers are 1.<update>: 1.100, 1.101, … 1.999, 1.1000, 1.1001 (no decimal arithmetic; the update count just
grows). Bump it whenever a commit changes more than a very minor fix (new books, features, data corrections).
The site shows "Version 1 update N · last updated DD Month YYYY, HH:MM" in the home page footer and book About panels.
Usage: python3 build/bump_version.py        (prints the new version)
"""
import json, os, datetime
f = os.path.join(os.path.dirname(os.path.abspath(__file__)), "VERSION.json")
v = json.load(open(f)) if os.path.exists(f) else {"major": 1, "update": 99}
v["update"] += 1
v["updated"] = datetime.datetime.now().astimezone().strftime("%Y-%m-%dT%H:%M%z")
json.dump(v, open(f, "w"), indent=1)
print(f"{v['major']}.{v['update']}  ({v['updated']})")
