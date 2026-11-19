# Demonstration script

## Before presenting

1. Run `./run.sh` and open `http://127.0.0.1:8000`. Run `./scripts/verify.sh` before the presentation, not during it.
2. State: “This is a synthetic software demonstration of a closed care-navigation loop. It is not a care service, diagnostic tool or validated questionnaire administration.”
3. Explain that English and Arabic items are numbered placeholders because approved wording was not supplied. The displayed scores prove arithmetic and workflow only.
4. Open **Real vs simulated**. Explain that encryption, consent checks, revocation, audit enforcement and state transitions are real code; providers, appointments, clinician contacts and cohort outcomes are simulated.
5. Select English and **Adult demo persona**. Existing rehearsal data persists. For an entirely fresh rehearsal, stop the server and move the whole `.runtime` directory to a private backup outside the repository, keeping its key and database together, then restart. Do not delete the key alone. Fresh startup seeds the cohort again.

## Persona 1 — working-age adult and moderate score

This persona uses only synthetic values and the adult fixture; no demographic or clinical claim is being made.

1. **Check-in → Start a check-in → PHQ-9 → Fill moderate example.** The answers are `[2,2,2,1,1,1,1,0,0]`; submit with **See my result**. Show score 10 and the moderate band. Read the limitation explaining that this is not a diagnosis or valid personal result.
2. **Explore your next step.** Choose free, in person, and optionally the physical-health checkbox. Enter “Synthetic physical-health context: would like to discuss this with primary care.” Show the policy version, eligibility, next step, match reasons and FICTIONAL PROVIDER labels. Choose **Palm Primary Care**.
3. In **Your next steps**, expand **Test provider access** and press its inner button. Expect **Access denied** before any consent. This is a real HTTP 403, not a canned simulation message.
4. Open **Consent centre**. Choose Palm Primary Care. Check **Assessment scores**, **Physical-health context**, and **Follow-up history**; no boxes start selected. Grant access. Show the purpose, grantee, fields and grant timestamp.
5. Return to the referral. Expand **Test provider access** and read the summary. Show the synthetic context and score returned through the actual consent gate. Optional: grant scores alone and request only scores to demonstrate granularity.
6. Return to **Consent centre** and **Revoke access**. If previous rehearsals created several active grants for Palm, revoke all of them. Return to the same referral and test access again: expect **Access denied** immediately. Revocation cannot undo information already seen, but blocks the next read.
7. Use **Mark as Accepted → Mark as Booked → Mark as Attended**. These are simulated appointment status changes, not actual bookings. Expand **Add a follow-up**, select Yes, enter a synthetic note and Save. Show the recorded history and labelled, unverified seven-day reminder interval.
8. Make a second PHQ-9 check-in. Fill the moderate example, then reduce the first three responses from 2 to 1. Submit: score 7. Open **Your progress**: scores 10 → 7, difference −3, below the configured five-point demonstration threshold. Show UNVERIFIED and explain that this is not a statistically validated reliable-change index. The general regression test additionally exercises a difference that exceeds the threshold.
9. Open **Access history**. Point to provider role/grantee, allowed and denied reads, consent grant and revocation, and lifecycle events. The backend test suite rejects both raw UPDATE and DELETE operations on this ledger.

## Persona 2 — deterministic crisis signal and human review

1. Select **Crisis demo persona**. Press **I need urgent help**. Guidance appears immediately without waiting for the API. The UI explicitly says that no real clinician is monitoring the demo and not to wait for the queue.
2. Show the three user-supplied hotline fixtures, all marked **NEEDS VERIFICATION**. They are not verified resources or click-to-call recommendations. Do not call them during the demonstration.
3. Confirm “A simulated human-review task was created.” Open **Review queue**. The SIMULATED CLINICIAN label and unverified timer target are visible. The queue contains only operational markers, without participant answers or identity.
4. **Claim task**, then **Record simulated human contact**. The Resolve button stays disabled until contact is recorded and a note has been entered. Enter “Synthetic review completed by the demo teammate; no real contact” and choose **Resolve with a note**. Explain that this explicit human action is the only closure mechanism.
5. Optional alternative trigger: start a PHQ-9 check-in and select 1 for item 9 before filling the other items. Guidance appears immediately; submitting a complete assessment with item 9 positive creates an escalation regardless of total score. Each signal may create a separate task; none are automatically hidden or closed.
6. Optional keyword trigger: type the clearly synthetic text “Synthetic keyword test: suicide” in a participant note. The configured exact keyword triggers guidance while typing. Mention false positives, missed variants, and the absence of semantic risk assessment.
7. Expand **Log an adverse event** on a claimed task, choose a category, add a synthetic note and Save. The redacted event log shows category and time, without the encrypted note or patient ID.

## Outcomes and bilingual close

- Open **Outcome overview**. State explicitly that the reference cohort has 120 synthetic people, seed 1042. It excludes interactive personas, so rehearsals do not change its baseline. These numbers do not show clinical impact or fairness.
- Switch grouping through age band, gender, nationality, language and geography. A suppressed value is not zero. Group size and each metric's contributing population must meet the minimum; the automated tests prove groups of nine return no rows.
- Toggle **العربية**. Navigation, safety content, form labels, results and controls switch, and layout direction becomes RTL. This is developer-translated interface text needing native review, not a validated instrument translation.
- Finish on **Real vs simulated** and name the next real-world prerequisites: approved instruments, verified services, accountable staffing, clinical governance and production security.

## Failure recovery

- If port 8000 is occupied, use `PORT=8001 ./run.sh` and open the printed address.
- If API calls fail, keep emergency guidance visible; do not claim a review task saved. Restart the server and retry normal demo operations. No offline patient-data queue exists.
- A consent denial after a partial grant is expected; align the requested scopes or grant the missing fields. A wrong provider is denied even with another provider's consent.
- Refreshing the page creates a new demo session and returns to the start screen; SQLite records persist. Reopen the desired page. In-flight UI state is not durable.
- The local server must stay running for the complete loop. Initial dependency installation needs internet. The PWA is not a substitute for the backend or real crisis response.
