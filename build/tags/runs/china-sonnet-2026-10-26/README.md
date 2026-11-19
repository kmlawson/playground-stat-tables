# China tagging run

8,866 tables / 20 volumes / 887 sequential batches, using
`anthropic/claude-sonnet-5-5`. No OCR. No published data or Topics-page changes.

The user permits zero detailed tags when no existing tag fits. High-level topics
remain mandatory. `vocabulary.json`, `rules.md`, `system.txt` and all complete
batch inputs are frozen by `manifest.json`.

`progress.json` and `PROGRESS.md` show the latest checkpoint. Completed batches
save the provider response and validated labels under `batches/batch-NNNN/`.
`assignments.json` collects saved labels; `no-detailed-tags.json` collects records
with `tags: []`; `review-queue.json` preserves model questions. These files update
after every completed batch. All labels remain unreviewed model output.

Resume with `python3 -B build/tags/run_china_sonnet.py run` from the site directory.
A process lock prevents concurrent workers, and validated batches are skipped.
`validate` checks saved results without making API calls. `runner.log` contains
progress events. A transient failure is retried sequentially; no attempt is made
after the 899-CLI-attempt ceiling. The provider SDK may retry transport failures
internally; CLI attempts and completed batches are reported separately.
