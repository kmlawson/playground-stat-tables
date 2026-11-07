"""What the finder pages are missing since their last batch (CLAUDE.md, "Finder pages").

    python3 build/finders/status.py              report, per finder: tables with no spec, specs whose table changed,
                                                 new unmatched place names, new suspicious figures
    python3 build/finders/status.py --batches    also write the pending tables' previews for the spec agents to
                                                 build/finders/<name>/work/batches/pending-<date>/bNN.txt (specs then
                                                 go to build/finders/<name>/specs/pending-<date>/bNN.json)
    python3 build/finders/status.py --baseline   after a batch has been reviewed: record the current unmatched names and
                                                 suspicious figures as seen (build/finders/<name>/baseline/), so the
                                                 next report shows only what is new

Run it after a build (it reads data/*.json and each finder's work/unplaced.txt, which the build writes).
"""
import datetime, importlib.util, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import registry  # noqa: E402


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def read_lines(p):
    return set(open(p, encoding="utf-8").read().split("\n")) - {""} if os.path.exists(p) else set()


def main():
    batches, baseline = "--batches" in sys.argv, "--baseline" in sys.argv
    for c in registry.finders():
        d = c["dir"]
        sys.path.insert(0, d)
        MP = load(os.path.join(d, "make_previews.py"), c["name"] + "_previews")
        X = load(os.path.join(d, "extract.py"), c["name"] + "_extract")
        CK = load(os.path.join(d, "check.py"), c["name"] + "_check")
        specs = X.load_specs()
        stale = list(X.L.STALE)
        cands = MP.candidates()
        pending = [(k, p) for s, k, p in cands if k not in specs]
        print(f"== {c['name']}: {len(cands):,} candidate tables, {len(specs):,} with a spec")
        print(f"   {len(pending) - len([k for k, _ in pending if k in stale]):,} tables with no spec yet; {len(stale)} specs left out because their table changed")
        # unmatched names (count >= 3) and suspicious figures not seen before
        bdir = os.path.join(d, "baseline")
        up = os.path.join(d, "work", "unplaced.txt")
        names = set()
        if os.path.exists(up):
            for line in open(up, encoding="utf-8"):
                n, rk, lab = (line.rstrip("\n").split("\t") + ["", "", ""])[:3]
                if n.isdigit() and int(n) >= 3:
                    names.add(f"{rk}|{lab}")
        else:
            print("   (no work/unplaced.txt: build first)")
        outs = {CK.key(cl) for _, cl, _ in CK.outliers()}
        new_names = names - read_lines(os.path.join(bdir, "unplaced.txt"))
        new_outs = outs - read_lines(os.path.join(bdir, "outliers.txt"))
        print(f"   {len(new_names):,} new unmatched place names (seen 3+ times); {len(new_outs):,} new suspicious figures"
              f" in {len({k.split('|')[0] for k in new_outs}):,} tables")
        if batches:
            tag = "pending-" + datetime.date.today().isoformat()
            n = MP.write_batches(os.path.join(d, "work", "batches", tag), [p for _, p in pending])
            with open(os.path.join(d, "work", "new_names.txt"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(sorted(new_names)) + "\n")
            with open(os.path.join(d, "work", "new_outliers.txt"), "w", encoding="utf-8") as fh:
                fh.write("\n".join(sorted(new_outs)) + "\n")
            print(f"   wrote {n} batch file(s) to work/batches/{tag}/ (specs go to specs/{tag}/), work/new_names.txt, work/new_outliers.txt")
        if baseline:
            os.makedirs(bdir, exist_ok=True)
            open(os.path.join(bdir, "unplaced.txt"), "w", encoding="utf-8").write("\n".join(sorted(names)) + "\n")
            open(os.path.join(bdir, "outliers.txt"), "w", encoding="utf-8").write("\n".join(sorted(outs)) + "\n")
            print(f"   baseline recorded: {len(names):,} names, {len(outs):,} figures")


if __name__ == "__main__":
    main()
