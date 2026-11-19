#!/usr/bin/env python3
"""Read complete pilot inputs in bounded, consecutive character chunks."""
import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent / "pilot"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--batch", required=True)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--chars", type=int, default=16000)
    parser.add_argument("--index", action="store_true")
    args = parser.parse_args()
    batch = json.loads((HERE / "batches" / (args.batch + ".json")).read_text())
    chunks, index, position = [], [], 0
    for item in batch["items"]:
        wrapper = json.loads((HERE / item["input"]).read_text())
        text = json.dumps(wrapper, ensure_ascii=False, separators=(",", ":")) + "\n"
        index.append({"key": item["key"], "start": position, "end": position + len(text),
                      "title": wrapper["table"].get("title", "")})
        chunks.append(text)
        position += len(text)
    stream = "".join(chunks)
    if args.index:
        print(json.dumps({"batch_id": args.batch, "total_chars": len(stream), "tables": index}, ensure_ascii=False, indent=1))
        return
    stop = min(len(stream), args.offset + args.chars)
    print(json.dumps({"batch_id": args.batch, "start": args.offset, "end": stop,
                      "total_chars": len(stream), "next_offset": stop if stop < len(stream) else None}))
    print(stream[args.offset:stop])


if __name__ == "__main__":
    main()
