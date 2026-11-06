"""
schema.py — The patient record format.

Every field is a list of items, and every item keeps the sentence it came from, so the
doctor can check it. An empty list means the note doesn't say: it is shown as
"not mentioned", never guessed.
"""

from pydantic import BaseModel, ConfigDict, Field

NOT_MENTIONED = "not mentioned"


class Item(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    value: str = Field(min_length=1, description="Copied word for word from the note.")
    source: str = Field(min_length=1, description="The sentence of the note that contains the value.")


class PatientRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    main_complaint: list[Item] = Field(default_factory=list, description="Why the patient came today.")
    symptoms: list[Item] = Field(default_factory=list, description="Other symptoms the patient reports.")
    medical_history: list[Item] = Field(default_factory=list, description="The patient's own past or ongoing conditions.")
    medications: list[Item] = Field(default_factory=list, description="Taken now or prescribed today, with dose as written.")
    allergies: list[Item] = Field(default_factory=list, description="Known allergies, or a stated absence of allergies.")
    exams_ordered: list[Item] = Field(default_factory=list, description="Tests requested at this visit.")
    follow_up: list[Item] = Field(default_factory=list, description="When or how the patient is seen again.")

    def display(self, field: str) -> str:
        return ", ".join(item.value for item in getattr(self, field)) or NOT_MENTIONED


FIELDS = tuple(PatientRecord.model_fields)
