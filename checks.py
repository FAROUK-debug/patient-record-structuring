"""
checks.py — The anti-invention check.

An item is kept only if its source sentence is in the note and its value is in that
sentence. Case and spacing are ignored; the words themselves must match.
"""

import re

from schema import FIELDS, PatientRecord


def _norm(text: str) -> str:
    return " ".join(text.split()).casefold()


def unsupported_items(record: PatientRecord, note: str) -> list[str]:
    """Describe every item the note doesn't back up. Empty means the record is clean."""
    note = _norm(note)
    problems = []
    for field in FIELDS:
        for item in getattr(record, field):
            source = _norm(item.source)
            if source not in note:
                problems.append(f"{field}: source not in note: {item.source!r}")
            # Whole words only, so "ill" doesn't match inside "pills".
            elif not re.search(rf"(?<!\w){re.escape(_norm(item.value))}(?!\w)", source):
                problems.append(f"{field}: value not in source: {item.value!r}")
    return problems
