# Scope and source assumptions

The supplied file was `Challenge 10 Earlier, Safer Mental Wellbeing Support.docx`, fully extracted and read before implementation. It is an analysis/prototype plan, not the original challenge PDF. The original six-point statement was not supplied. This prototype maps the six points in the user's brief; fidelity to the original PDF is unverified.

The document favours PostgreSQL and verified hotlines. The explicit build brief allows SQLite locally and requests unverified hotline fixtures. We use SQLite with SQLAlchemy types suitable for PostgreSQL and clearly mark the fixtures. PostgreSQL execution must be verified separately.

Team size and deadline were unspecified. Scope assumes a first-year student demonstrating on one laptop, with no real patients or actual clinical staff. A single loopback server serves a built React app and FastAPI; initial dependency installation needs internet, subsequent runtime does not. No claim of a first-ever install without dependencies or internet.

Questionnaire items are numbered placeholders in both languages. They are not validated assessments. Scoring arithmetic uses published scoring rules; clinical wording, Arabic validation, licensing and pathway review remain prerequisites to real use. UI Arabic is a demonstration translation, not clinically approved.
