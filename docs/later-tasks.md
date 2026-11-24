# Later tasks

Tasks agreed with the user but not yet done. Remove an entry once it is done.

---

## Move the git database off the external drive (Oma) to the local disk

**Why.** The site checkouts are git *worktrees* of one older clone whose `.git` (≈ 2.9 GB) lives on the external drive
Oma. Every `git status` / `add` / `commit` therefore reads and writes over that drive: slow (a commit of ~1,000 rebuilt
pages sat in `git add` for over 5 minutes on 2026-11-24), and git fails outright when Oma is not mounted.

**Who depends on it.** List the worktrees first — all of them must be repaired after the move:

    cd ~/shell/projects/yearbooks/japanyearbooks/stat-tables-site
    git rev-parse --git-common-dir      # the main clone's .git on Oma (the thing to move)
    git worktree list                   # the main clone + every worktree (japanyearbooks, fareast, chinahandbook1950, …)

**When.** Only while no session is committing in any of the worktrees, and after any running build/deploy/clean-up has
finished. Ask the user to confirm first (it touches every checkout).

**Steps.**

1. Note the main clone's folder (the parent of the `--git-common-dir` path above), and check free space (`df -h ~`).
2. Copy the whole main clone (working tree + `.git`) to the local disk, preserving everything:

       rsync -a "<main clone folder on Oma>/" ~/shell/projects/yearbooks/stat-tables-main/

   Check the copy: `cd ~/shell/projects/yearbooks/stat-tables-main && git status && git log --oneline -1`.
3. Point every worktree at the local copy (run inside the NEW main clone, naming each worktree folder):

       cd ~/shell/projects/yearbooks/stat-tables-main
       git worktree repair ~/shell/projects/yearbooks/japanyearbooks/stat-tables-site \
                           ~/shell/projects/yearbooks/fareast/stat-tables-site \
                           ~/shell/projects/yearbooks/chinahandbook1950/stat-tables-site
       git worktree prune          # drops stale entries such as a removed /tmp review worktree

4. Verify in each worktree: `git rev-parse --git-common-dir` now shows the local path; `git status` and
   `git log --oneline -1` work; branches are unchanged. Then unmount Oma briefly and confirm git still works.
5. Keep the Oma copy as a backup until the user is satisfied; delete it only when the user says so.
6. Update the docs that mention it: the "Git" line under "Where things are" in `CLAUDE.md` ("git fails if Oma is not
   mounted") and the "Oma must be mounted" note in `../human-handoff.md`.

Nothing is lost by this move: all branches, history, stashes and uncommitted work travel with the copy.
