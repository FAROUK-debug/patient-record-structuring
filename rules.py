"""
rules.py — First version of the extractor: section labels and keywords, no AI.

This is the baseline the AI model has to beat. Every value is cut out of the note, so
it can't invent anything, but it misses whatever the rules don't cover.
Labels and keywords come from the build notes only; the test notes stay unseen by the rules.
"""

import re

from schema import FIELDS, Item, PatientRecord

# None = a known label that has no field of its own: its text is read as prose.
LABELS = {
    "main_complaint": r"chief complaint|cc|presenting complaint|(main )?reason for (visit|consultation)|complaint|visit type",
    "symptoms": r"(other )?symptoms|complaints|ros|associated",
    "medical_history": r"pmh|(past )?(medical )?history|background|known conditions",
    "medications": r"(current )?(medications|drugs|treatment)|meds|treatment at home",
    "allergies": r"allergies",
    "exams_ordered": r"orders|tests|investigations",
    "follow_up": r"follow-up|next visit",
    None: r"plan|p|a|assessment|exam(ination)?|objective|subject|hpi|patient|family|advice|history of present illness",
}

DRUG_FORM = r"(?:syrup|cream|tablets?|sachets|inhaler|eye drops|nasal spray)"
END_OF_ITEM = r"[^,.;]*?(?= and |[,.;]|$)"
MEDICATION = re.compile(rf"\b[a-z][a-z-]+(?: {DRUG_FORM})? \d[\d.]* ?(?:mg|mcg|g)\b{END_OF_ITEM}"
                        rf"|\b[a-z][a-z-]+ {DRUG_FORM}\b{END_OF_ITEM}"
                        r"|\b[a-z]+ PRN\b", re.I)
EXAMS = re.compile(r"\b(chest x-ray|x-ray of the [a-z ]+|ecg|echo|mri of the [a-z ]+|[a-z]+ ultrasound|hba1c|tsh|free t4|"
                   r"fbc|tfts|u&e|troponin|stress test|blood tests?|urine culture|urine albumin|sputum culture|"
                   r"fasting lipid panel|full blood count|ferritin|spirometry|[a-z]+ stool test)\b", re.I)
NOT_ORDERED = re.compile(r"\b(last|in the emergency|was normal|showed|not needed|done)\b|today:", re.I)
ALLERGY = re.compile(r"\b(NKDA|NKA|no known (?:drug )?allerg\w+|no allergies(?: are)?(?: known)?)\b"
                     r"|allergic to (?P<to>[^,.;]+)|\b(?P<before>\w+) allergy\b", re.I)
FOLLOW_UP = re.compile(r"^(review|return|come back|see |f/?u\b|r/v\b|recheck|reassess|next |telephone|if no\b)"
                       r"|\b(referral|clinic|opd)\b", re.I)
COMPLAINT = re.compile(r"\b(?:seen (?:today )?for|presents with|c/o|because of|complains of|came in for|with)\s+(?:a |an )?(?P<v>.+)"
                       r"|^\d+ ?(?:y/o )?[MF],?\s+(?P<terse>.+)", re.I)
HISTORY = re.compile(r"\b(?:history of|history includes|known)\s+(?:a )?(?P<v>[^,.;]+)", re.I)
STATED_NONE = re.compile(r"\b(no (?:medical|health) problems|no prior [a-z ]+|no pmh|otherwise healthy)\b"
                         r"|\b(?P<meds>no regular [a-z]+|no medicines)\b", re.I)
NEGATED = re.compile(r"^(no|not|denies|nil)\b", re.I)
# Words before a match that flip its meaning: the word is in the note, the fact is not true.
DENIED = re.compile(r"\b(no|not|never|denies|denied|without|negative for)\b", re.I)
OTHER_PERSON = re.compile(r"\b(family|mother|father|parents?|brother|sister|son|daughter|grand(?:mother|father)|aunt|uncle)\b", re.I)
NOT_TAKEN = re.compile(r"\b(stop\w*|discontinu\w+|not tak\w+|no longer|refus\w+|declin\w+)\b", re.I)
TIME = re.compile(r"\s+(since|for|x \d|after)\b.*$", re.I)
SPLIT = re.compile(r",|;| and | \+ ")


def split_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _label(line: str) -> tuple[bool, str | None, str]:
    """Return (is a label, its field, text after it)."""
    head, _, rest = line.partition(":")
    for field, pattern in LABELS.items():
        if re.fullmatch(pattern, head.strip(), re.I):
            return True, field, rest.strip()
    return False, None, line


def _sentences(note: str) -> list[tuple[str | None, str, str]]:
    """Return (field or None, whole sentence, its text without the label)."""
    out = []
    current = None
    for line in note.splitlines():
        line = line.strip()
        if not line:
            current = None
            continue
        is_label, field, rest = _label(line)
        if is_label and not rest:  # label alone on its line, for the lines below
            current = field
            continue
        for i, sentence in enumerate(split_sentences(line)):
            body = sentence.partition(":")[2].strip() if is_label and i == 0 else sentence
            out.append((field if is_label else current, sentence, body))
    return out


def _parts(body: str) -> list[str]:
    parts = (p.strip(" .") for p in SPLIT.split(body))
    return [p for p in parts if p and not NEGATED.match(p)]


def _true_of_patient(sentence: str, start: int) -> bool:
    """False when the earlier words of its clause deny the fact or give it to a relative."""
    before = re.split(r"[,;]", sentence[:start])[-1]
    return not DENIED.search(before) and not OTHER_PERSON.search(before)


def _from_section(field: str, body: str) -> list[str]:
    body = body.strip(" .")
    if field in ("medical_history", "medications", "allergies"):
        body = re.sub(r"\s*\(.*?\)", "", body)
        if NEGATED.match(body) or body.casefold() == "none":
            return [body]  # a stated absence is kept
    if field in ("main_complaint", "symptoms"):
        body = TIME.sub("", body)
    if field == "exams_ordered":
        body = re.sub(r"\s+(requested|ordered|today)$", "", body, flags=re.I)
    parts = _parts(body)
    return [p for p in parts if not NOT_TAKEN.search(p)] if field == "medications" else parts


def _from_prose(sentence: str) -> dict[str, list[str]]:
    found = {field: [] for field in FIELDS}
    if not NOT_TAKEN.search(sentence):
        for m in MEDICATION.finditer(sentence):
            found["medications"].append(re.sub(r"\s+(prescribed|started|were prescribed)$", "", m.group().strip()))
    if not NOT_ORDERED.search(sentence):
        found["exams_ordered"] = [m.group() for m in EXAMS.finditer(sentence)]
    for m in ALLERGY.finditer(sentence):
        named = m["to"] or m["before"]
        if named is None or named.casefold() == "no":  # "NKDA", "No allergy": a stated absence
            found["allergies"].append(m.group())
        elif _true_of_patient(sentence, m.start()):
            found["allergies"].append(named)
    if FOLLOW_UP.search(sentence):
        found["follow_up"].append(sentence.rstrip(" ."))
    if (m := HISTORY.search(sentence)) and _true_of_patient(sentence, m.start()):
        found["medical_history"].append(m["v"].strip())
    if m := STATED_NONE.search(sentence):
        found["medications" if m["meds"] else "medical_history"].append(m.group())
    return found


def extract(note: str) -> PatientRecord:
    found = {field: [] for field in FIELDS}
    seen = set()

    def add(field: str, value: str, source: str) -> None:
        if (field, value.casefold()) not in seen:
            seen.add((field, value.casefold()))
            found[field].append(Item(value=value, source=source))

    sentences = _sentences(note)
    for field, sentence, body in sentences:
        if field:
            for value in _from_section(field, body):
                add(field, value, sentence)
        else:
            for prose_field, values in _from_prose(sentence).items():
                for value in values:
                    add(prose_field, value, sentence)

    # No labelled complaint: the first sentence usually says why the patient came.
    if not found["main_complaint"] and sentences:
        first = sentences[0][1]
        if m := COMPLAINT.search(first):
            for value in _parts(TIME.sub("", (m["v"] or m["terse"]).rstrip(" ."))):
                add("main_complaint", value, first)
    return PatientRecord(**found)
