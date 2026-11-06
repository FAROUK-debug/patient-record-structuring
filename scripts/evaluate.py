"""
evaluate.py — Score the extractor against the hand-marked answers.
Run: python -m scripts.evaluate            (build notes)
     python -m scripts.evaluate --split test

An item counts as found if it equals the answer or one contains the other as whole
words ("increased thirst" and "increased thirst for two months"). The exact line
counts only identical text, so it shows what that leniency adds.
"""

import argparse
import re
import time
from pathlib import Path

from checks import unsupported_items
from rules import extract
from schema import FIELDS, PatientRecord

DATA = Path(__file__).parent.parent / "data"


def _norm(text: str) -> str:
    return " ".join(text.casefold().split())


def _same(a: str, b: str) -> bool:
    short, long = sorted((_norm(a), _norm(b)), key=len)
    return re.search(rf"(?<!\w){re.escape(short)}(?!\w)", long) is not None


def _exact(a: str, b: str) -> bool:
    return _norm(a) == _norm(b)


def count(predicted: list[str], expected: list[str], same=_same) -> tuple[int, int, int]:
    """Return (true positives, false positives, false negatives). Each answer matches once."""
    left = list(expected)
    hits = 0
    for value in predicted:
        match = next((e for e in left if same(value, e)), None)
        if match is not None:
            left.remove(match)
            hits += 1
    return hits, len(predicted) - hits, len(left)


def f1(tp: int, fp: int, fn: int) -> float:
    return 2 * tp / (2 * tp + fp + fn) if tp else 0.0


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", default="build", choices=["build", "test"])
    args = parser.parse_args()

    totals = {field: [0, 0, 0] for field in FIELDS}
    exact = [0, 0, 0]
    invented = items = 0
    paths = sorted((DATA / args.split).glob("*.txt"))
    started = time.perf_counter()
    for path in paths:
        note = path.read_text(encoding="utf-8")
        answer = PatientRecord.model_validate_json(path.with_suffix(".json").read_text(encoding="utf-8"))
        record = extract(note)
        invented += len(unsupported_items(record, note))
        for field in FIELDS:
            predicted = [item.value for item in getattr(record, field)]
            items += len(predicted)
            expected = [item.value for item in getattr(answer, field)]
            result = count(predicted, expected)
            totals[field] = [t + r for t, r in zip(totals[field], result)]
            exact = [t + r for t, r in zip(exact, count(predicted, expected, _exact))]
    ms = (time.perf_counter() - started) * 1000 / len(paths)

    print(f"{args.split}: {len(paths)} notes")
    for field, result in totals.items():
        print(f"  {field:16} F1 {f1(*result):6.1%}   found {result[0]}, wrong {result[1]}, missed {result[2]}")
    overall = [sum(r[i] for r in totals.values()) for i in range(3)]
    print(f"  {'overall':16} F1 {f1(*overall):6.1%}   found {overall[0]}, wrong {overall[1]}, missed {overall[2]}")
    print(f"  {'overall exact':16} F1 {f1(*exact):6.1%}   found {exact[0]}, wrong {exact[1]}, missed {exact[2]}")
    print(f"  invented: {invented}/{items} items, {ms:.1f} ms per note")


if __name__ == "__main__":
    main()
