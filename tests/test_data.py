import json
from pathlib import Path

import pytest

from checks import unsupported_items
from schema import FIELDS, PatientRecord

NOTES = sorted((Path(__file__).parent.parent / "data").glob("*/*.txt"))


def test_notes_exist():
    assert NOTES


@pytest.mark.parametrize("path", NOTES, ids=lambda p: p.stem)
def test_answer_is_valid_and_comes_from_the_note(path):
    answer = json.loads(path.with_suffix(".json").read_text(encoding="utf-8"))
    assert set(answer) == set(FIELDS)  # every field marked by hand, even when empty
    record = PatientRecord.model_validate(answer)
    assert unsupported_items(record, path.read_text(encoding="utf-8")) == []
