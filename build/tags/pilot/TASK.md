# Pilot worker task

No OCR, ever. No Git operations. Classify existing JSON; do not edit source data,
definitions, live tags, or pages. Write only your assigned result file.

Read `../README.md` and `../vocabulary.json` relative to this directory. The
vocabulary version is recorded in your batch file. Definitions include completion
review and calibration terms centrally approved for this pilot. Every topic and
detailed tag in that version is available; associations do not constrain valid use.

Your batch file is `batches/<batch-id>.json`. Its input files contain the full
records. Inspect all parts, rows and notes of each one. Do not rely on titles,
selection hints, book collection, old tags or nearby contents headings. Use the
English layer together with original content. Preserve source terminology and
figures; tag reported categories without endorsing them.

`../read_pilot.py --batch <batch-id> --index` lists record offsets. Then read the
complete stream using consecutive offsets, for example:

    python3 -B build/tags/read_pilot.py --batch pilot-a --offset 0 --chars 16000

Continue at each returned `next_offset` through the end. Use sufficient tool-output
budget for each chunk; reread a shorter range if any output is truncated. You may
instead read individual complete files in bounded parts. Never drop body rows to
make the batch fit a single tool response. Save intermediate results if needed.

Write `results/<batch-id>.json` with this schema:

```json
{
  "schema_version": 1,
  "vocabulary_version": "1.0.0-pilot",
  "batch_id": "pilot-a",
  "assignments": {
    "<book-slug>:<table-id>": {
      "topics": ["trade"],
      "tags": ["exports", "silk"],
      "flags": [],
      "rationale": "Brief evidence from this record that supports the classification.",
      "review_questions": []
    }
  },
  "batch_notes": []
}
```

One or two distinct topics; one to three distinct detailed tags; flags either `[]`
or `["text-tables"]`. Use only vocabulary IDs. Every assigned key appears exactly
once. Review questions identify actual unresolved choices; keep routine rationale
out of that queue. If a required concept is missing, give the best supported
approved labels and explain the proposed addition in `review_questions` without
inventing an ID. These are provisional pilot classifications, not publication.

Finish by validating your JSON and exact key set against the batch. Report the
number of classified/text tables, genuine unresolved cases, and recurring rule
problems. Do not spend a second full pass on the batch; central review targets the
questions and boundary cases.
