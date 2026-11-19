# Validation record

Validated locally on 19 November 2026 using Python 3.14, Node 24.21 and SQLite. Dependency versions are pinned in the committed lockfiles.

## Automated results

`./scripts/verify.sh` completed successfully:

- **72 pytest tests passed**: every specified scoring band boundary; invalid response validation; PHQ-9 item 9 values 1–3 independently of total score; explicit English and Arabic crisis phrases; immediate item 9 signals; consent scopes and revocation; user/provider isolation; raw SQL audit UPDATE/DELETE rejection; synthetic reproducibility; all demographic grouping dimensions; small-group endpoint suppression; sparse metric suppression; claim ownership and explicit human resolution; adverse-event redaction; UTC handling; cache/host/origin boundaries; same-instrument trend and a full check-in-to-follow-up integration flow.
- **3 Node tests passed**: deterministic keyword cases and boundaries, explicit negation behaviour, and matching English/Arabic translation-key coverage including safety labels.
- **Vite production build passed**. No build errors or CSS warnings in the final run.
- One upstream deprecation warning from Starlette's use of the httpx TestClient remains. It does not fail the suite; migration should be reviewed during dependency maintenance.

Tests use isolated in-memory SQLite databases and ephemeral encryption keys. The test lifespan skips production database initialisation when dependencies are overridden. No real patient data is used.

## Browser observations

Using the local app and its real APIs, verified:

- Moderate PHQ-9 demonstration score 10, plain-language limitations, primary-care match and transparent fictional provider labels.
- Referral creation with synthetic physical-health context.
- Provider read denied before consent, succeeded after all requested scopes were granted, and denied again immediately after revocation.
- Suggested → accepted → booked → attended transitions; follow-up saved and reloaded.
- Repeat PHQ-9 score 7; trend displayed 10 → 7 and difference −3 with the UNVERIFIED threshold note.
- Urgent button showed guidance and created a task; simulated reviewer claimed, recorded contact and explicitly resolved it.
- Final build displayed guidance immediately for item 9 before form submission and for a configured keyword entered in participant text. Keyboard activation was also exercised.
- Synthetic metric values rendered with labels, and Arabic RTL translated the outcome screen.
- Desktop layout inspected at 1440×960, mobile screenshots inspected at the default narrow viewport, and Arabic document width checked at 390 pixels with no page-level horizontal overflow. Wide tables intentionally scroll within their containers.
- No browser console error was reported in the inspected final refresh.

`docs/preview.jpg` is an actual screenshot of the running local prototype, not a mockup.

## Limits of this evidence

No live PostgreSQL server, real clinician, provider, emergency service, real questionnaire wording, real patient, regulatory review, production authentication, penetration test or clinical outcome study was exercised. Clinical validation and Arabic language accuracy are not established by software tests. Cross-browser PWA installation and backend-stopped cache recovery were not comprehensively tested. No claim of statistically reliable change, fairness or clinical effectiveness is made.

The app's network-independent runtime follows from its local services and bundled assets; initial installation needs dependencies. The browser checks were performed against the local server, not a hosted deployment. See the verification register for unresolved items.

## Phase checkpoints

| Phase | Proven checkpoint | Simulated / cut | Demo risks |
| --- | --- | --- | --- |
| A | 40 scoring/crisis/pathway tests | Placeholder items, unreviewed policy; no risk model | Exact keywords miss variants |
| B | 46 tests including consent, audit and handoffs | Providers/bookings; no real integration | Missing scopes correctly cause denial |
| C | Participant UI built; 46 backend tests | No validated instrument wording | Local server must run; placeholder interpretation only |
| D | 52 tests; cohort, privacy, queue and metrics built | Staffing and outcome records | Sparse values intentionally suppressed |
| E | Final 72 backend + 3 frontend tests and browser flows | No real clinical service, external reminders or production identity | Unverified clinical configuration, live PostgreSQL untested |

## Git history

Work was pushed incrementally. The first nine commits used the machine's pre-existing Git identity, attributed by GitHub to `jayanthmail9108-spec`. The repository-local identity was then set to `344406021+jayanthv-git@users.noreply.github.com`; GitHub's commit API verified attribution to `jayanthv-git`. Ten subsequent meaningful implementation, test and documentation commits use that account. The original published history was preserved; no force push or date manipulation was used. Multiple same-day commits do not establish a multi-day streak.
