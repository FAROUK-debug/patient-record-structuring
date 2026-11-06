# Patient Record Structuring

![tests](https://github.com/FAROUK-debug/patient-record-structuring/actions/workflows/ci.yml/badge.svg)
> **Prototype — not for medical use.** All notes in this repo are fictional.

Turns a free-text consultation note into a structured patient record. Each field is shown next to the sentence it came from, anything missing is marked "not mentioned", and the doctor corrects the result before exporting it.

## Status

Work in progress.

**Built:**
- The record format ([`schema.py`](schema.py)).
- The anti-invention check ([`checks.py`](checks.py)).
- 50 fictional notes with hand-marked answers ([`data/`](data): 30 to build, 20 to test, rules in [`docs/annotation_guide.md`](docs/annotation_guide.md)).
- A rule-based baseline ([`rules.py`](rules.py)).

**Next:** a Gemini extractor, linking each item to its sentence, and the doctor's review screen.

## Baseline results

The rule-based baseline on the 30 build notes, the same notes its rules were written from, so expect lower scores on unseen notes. The 20 test notes stay unscored until the final comparison.

| Field | F1 |
|---|---|
| Main complaint | 85.7% |
| Symptoms | 43.6% |
| Medical history | 79.4% |
| Medications | 93.8% |
| Allergies | 90.0% |
| Exams ordered | 98.6% |
| Follow-up | 94.1% |
| **Overall** | **84.8%** (74.4% counting only identical text) |

An item counts as found if it matches the answer or one contains the other as whole words. The exact score is shown because that rule is generous.

No item was invented, but that check has a limit: it proves the words are in the note, not that the meaning is right. "Not allergic to penicillin" contains the word "penicillin", so denied facts and facts about relatives are covered by their own tests in [`tests/test_rules.py`](tests/test_rules.py).

## Run it

Needs Python 3.10 or newer.

```bash
pip install -r requirements-dev.txt
pytest -q
python -m scripts.evaluate
```
