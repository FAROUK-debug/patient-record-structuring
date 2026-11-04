import pytest
from pydantic import ValidationError

from checks import unsupported_items
from schema import FIELDS, NOT_MENTIONED, Item, PatientRecord

NOTE = "Patient takes two pills daily.\nAllergic to  Penicillin."


def record(value, source):
    return PatientRecord(allergies=[Item(value=value, source=source)])


def test_has_the_seven_fields():
    assert len(FIELDS) == 7


def test_empty_field_shows_not_mentioned():
    assert PatientRecord().display("allergies") == NOT_MENTIONED


def test_display_joins_items():
    source = "HbA1c and lipids ordered."
    rec = PatientRecord(exams_ordered=[Item(value="HbA1c", source=source), Item(value="lipids", source=source)])
    assert rec.display("exams_ordered") == "HbA1c, lipids"


def test_unknown_field_is_refused():
    with pytest.raises(ValidationError):
        PatientRecord(diagnosis=[])


def test_empty_value_is_refused():
    with pytest.raises(ValidationError):
        Item(value="", source="Allergic to penicillin.")


def test_supported_item_passes_ignoring_case_and_spacing():
    assert unsupported_items(record("penicillin", "allergic to penicillin."), NOTE) == []


def test_invented_value_is_caught():
    assert unsupported_items(record("aspirin", "Allergic to Penicillin."), NOTE)


def test_invented_source_is_caught():
    assert unsupported_items(record("aspirin", "Allergic to aspirin."), NOTE)


def test_value_must_be_whole_words():
    assert unsupported_items(record("ill", "Patient takes two pills daily."), NOTE)
