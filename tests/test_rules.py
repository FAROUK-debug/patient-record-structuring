from pathlib import Path

import pytest

from checks import unsupported_items
from rules import extract
from schema import NOT_MENTIONED
from scripts.evaluate import count, f1

NOTES = sorted((Path(__file__).parent.parent / "data" / "build").glob("*.txt"))


def values(record, field):
    return [item.value for item in getattr(record, field)]


def test_labelled_note():
    record = extract("Allergies: latex.\nOrders: ferritin, full blood count.\n")
    assert values(record, "allergies") == ["latex"]
    assert values(record, "exams_ordered") == ["ferritin", "full blood count"]


def test_label_alone_on_its_line():
    record = extract("Investigations\nHelicobacter stool test requested.\n\nFollow-up\nPhone call in 10 days.\n")
    assert values(record, "exams_ordered") == ["Helicobacter stool test"]
    assert values(record, "follow_up") == ["Phone call in 10 days"]


def test_prose_note():
    record = extract("Seen for a cough for five days. He takes amlodipine 5 mg once daily. Allergic to penicillin.")
    assert values(record, "main_complaint") == ["cough"]
    assert values(record, "medications") == ["amlodipine 5 mg once daily"]
    assert values(record, "allergies") == ["penicillin"]


def test_missing_stays_not_mentioned():
    assert extract("Patient came in for a repeat prescription.").display("allergies") == NOT_MENTIONED


def test_stated_absence_is_kept():
    assert values(extract("Allergies: none."), "allergies") == ["none"]


def test_denied_symptom_is_left_out():
    assert values(extract("Symptoms: poor appetite, no fever."), "symptoms") == ["poor appetite"]


def test_stopped_medicine_is_left_out():
    assert values(extract("Stop ibuprofen 400 mg daily."), "medications") == []


def test_past_exam_is_left_out():
    assert values(extract("Last spirometry in March was normal."), "exams_ordered") == []


@pytest.mark.parametrize("path", NOTES, ids=lambda p: p.stem)
def test_rules_never_invent(path):
    note = path.read_text(encoding="utf-8")
    assert unsupported_items(extract(note), note) == []


def test_count_matches_each_answer_once():
    assert count(["cough", "cough", "fever"], ["dry cough", "rash"]) == (1, 2, 1)


def test_f1():
    assert f1(1, 1, 0) == pytest.approx(2 / 3)
    assert f1(0, 1, 1) == 0.0
