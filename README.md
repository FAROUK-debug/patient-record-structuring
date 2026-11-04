# Patient Record Structuring

![tests](https://github.com/FAROUK-debug/patient-record-structuring/actions/workflows/ci.yml/badge.svg)
> **Prototype — not for medical use.** All notes in this repo are fictional.

Turns a free-text consultation note into a structured patient record. Each field is shown next to the sentence it came from, anything missing is marked "not mentioned", and the doctor corrects the result before exporting it.

Work in progress. So far: the record format ([`schema.py`](schema.py)), the anti-invention check ([`checks.py`](checks.py)) and the first fictional notes with hand-marked answers ([`data/`](data), rules in [`docs/annotation_guide.md`](docs/annotation_guide.md)).

```bash
pip install -r requirements-dev.txt
pytest -q
```
