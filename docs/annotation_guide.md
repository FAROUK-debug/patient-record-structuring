# Annotation guide

How the correct answers in `data/` were marked by hand. All notes are fictional.

## General rules

- **Value:** copy the shortest phrase that keeps the meaning, word for word. Keep doses and qualifiers ("amlodipine 5 mg once daily"). Don't expand abbreviations ("HTN" stays "HTN").
- **Source:** copy the whole sentence or line the value comes from.
- **Lists:** one item per thing. "HbA1c and lipid panel ordered" gives two items with the same source.
- **Missing:** if the note doesn't say, the list is empty. It is shown as "not mentioned". Never infer: a patient on lisinopril does not get "hypertension" unless the note says so.

## Field rules

| Field | Include | Leave out |
|---|---|---|
| Main complaint | Everything given as the reason for today's visit | |
| Symptoms | Other symptoms the patient reports | The main complaint again; denied symptoms ("no fever"); exam findings and measurements ("temperature 38.1 C") |
| Medical history | The patient's own conditions, past events and operations; pregnancy; a stated absence ("no medical problems") | Family history; smoking and alcohol; today's diagnosis |
| Medications | Taken now or prescribed today; a stated absence ("no regular medication") | Medicines stopped |
| Allergies | Known allergies; a stated absence ("NKDA") | "Not asked" |
| Exams ordered | Tests requested at this visit | Past tests; exams done during the visit with their result already known; tests said not to be needed |
| Follow-up | When or how the patient is seen or contacted again, including referrals | General advice |

**Why a stated absence counts:** "no known allergies" means the doctor asked. "Not mentioned" means nobody knows. A record must keep that difference. Symptoms are the exception: denied symptoms are left out, so the list only shows what the patient has.
