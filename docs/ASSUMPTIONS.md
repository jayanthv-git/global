# Scope and source assumptions

The supplied file was `Challenge 10 Earlier, Safer Mental Wellbeing Support.docx`, fully extracted and read before implementation. It is an analysis/prototype plan, not the original challenge PDF. The original six-point statement was not supplied. This prototype maps the six points in the user's brief; fidelity to the original PDF is unverified.

The document favours PostgreSQL and verified hotlines. The explicit build brief allows SQLite locally and requests unverified hotline fixtures. We use SQLite with SQLAlchemy types suitable for PostgreSQL and clearly mark the fixtures. PostgreSQL execution must be verified separately.

Team size and deadline were unspecified. Scope assumes a first-year student demonstrating on one laptop, with no real patients or actual clinical staff. A single loopback server serves a built React app and FastAPI; initial dependency installation needs internet, subsequent runtime does not. No claim of a first-ever install without dependencies or internet.

Questionnaire items are numbered placeholders in both languages. They are not validated assessments. Scoring arithmetic uses published scoring rules; clinical wording, Arabic validation, licensing and pathway review remain prerequisites to real use. UI Arabic is a demonstration translation, not clinically approved.

## Synthetic cohort assumptions

`data/generate.py` uses Python `random.Random(1042)` to generate 120 participants. Baseline is fixed at 2026-11-01 09:00 UTC; repeated scores are 14 days later. Age bands, gender, nationality, language and geography use deterministic rotations, deliberately not representative of any population. Scores and changes are bounded integer draws. Referral statuses, follow-up delays and contact delays are illustrative random draws; crisis and adverse-event membership use explicit index patterns.

The generator's logical records are reproducible. Ciphertexts use fresh encryption randomness and UUID identifiers vary. Existing cohort records are not overwritten on startup. Cohort generation is not a clinical simulation: the synthetic escalation flags are scenario fixtures, not inferred from the generated questionnaire answers. This independence is deliberate and unsuitable for model training.

The fixed cohort feeds the outcome/fairness dashboard. The two interactive demo personas have `cohort=false` and are excluded, visibly explained in the UI, so repeated rehearsals do not alter the reference dashboard. Their actual workflow state is visible in referral, trend, access-history and clinician screens.

All data is synthetic, including typed demo values. Nationality categories are simply `Emirati` and `other`; no statistical or policy inference is warranted. The generator excludes minors. The demo account is an adult fixture; real age eligibility verification is out of scope.
