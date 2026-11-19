# Verification register

This is a synthetic software prototype. Passing tests proves the implemented behaviour, not clinical validity, safety in practice, effectiveness, fairness, regulatory compliance, or readiness for patients.

| Item | Current implementation | Required verification |
| --- | --- | --- |
| Original problem statement | Only the supplied analysis DOCX was available; not `Problem_statement.pdf` | Compare against the organiser's original six-point statement |
| Instrument item wording | Numbered placeholders in English and Arabic | Obtain authorised PHQ-9, GAD-7 and WHO-5 item wording, response labels and timeframes; verify versions and permissions; clinician and native Arabic review before replacement |
| Scoring | PHQ-9 bands 0–4, 5–9, 10–14, 15–19, 20–27; GAD-7 0–4, 5–9, 10–14, 15–21; WHO-5 raw sum ×4, raw <13 lower wellbeing | Arithmetic cross-checked against sources below. Local appropriateness and clinical interpretation remain unverified. Placeholder answers do not constitute these validated measures |
| Pathway policy | `config/pathways.yaml`, version `demo-1.0`; band, language, cost, channel, urgency, physical-health preference | A licensed local professional must review indications, contraindications, urgency, eligibility and service availability |
| Change thresholds | PHQ-9 5, GAD-7 4, WHO-5 10 scaled points; all explicitly UNVERIFIED | These are demonstration constants, not clinical claims. Select and document an instrument/population-appropriate threshold. A true reliable-change index needs reliability and variability estimates; this implementation is only an absolute score difference |
| Hotlines | Only the three user-supplied records in `config/hotlines.yaml`; `verified_at: null` | Contact official UAE service authorities; record exact current service page, coverage, hours, languages, eligibility, number and verification date. Current `source_url` values are authority lookup starting points, not evidence for the numbers. UI does not provide call links |
| Crisis wording | Exact English/Arabic list with case/diacritic normalisation, PHQ-9 item 9 >0, urgent button | Clinician and native-language review; test variants and false positives. No negation inference, semantic assessment, or coverage guarantee. A person answering zero can still need urgent help |
| Review target | 15 minutes, visibly UNVERIFIED | Agree a staffed clinical service standard. This timer is a demonstration target, not an SLA or promise |
| Follow-up interval | 7 days, visibly UNVERIFIED | Agree a clinical/service protocol; this app only shows due dates when open |
| Arabic UI | Full key coverage and RTL; developer translation | Native Arabic usability, accessibility and clinical review. No claim of validated instrument translation |
| Providers | Five fictional records | Replace only with verified licensed services, eligibility and intake details |
| PostgreSQL | SQLAlchemy portable types and PostgreSQL audit trigger definition | Execute the integration suite against a supported live PostgreSQL server. SQLite is the tested runtime |
| PWA installation | Manifest and static-only service worker; local app serves successfully | Cross-browser install behaviour and device testing. Offline means no internet with local backend running; server-offline is a reduced shell, not a functioning care system |
| Identity/security/compliance | Explicitly open demo persona/role selector; random bearer tokens isolate request roles | Production authentication, session expiry, threat modelling, key management, backups, independent security review, UAE consent/legal/retention review, ADHICS and applicable DoH requirements |
| Real impact | None measured | Approved prospective pilot with an accountable clinical partner; synthetic outcome/fairness values are not evidence |

## Scoring references

- [PHQ and GAD-7 instruction manual hosted by Washington State DSHS](https://www.dshs.wa.gov/media/4471/download?inline=), especially severity scoring tables and the note that self-harm risk requires clinical evaluation.
- [WHO Five Well-Being Index official publication](https://www.who.int/publications/m/item/WHO-UCN-MSD-MHE-2024.01) and [official English document](https://cdn.who.int/media/docs/default-source/mental-health/who-5_english-original4da539d6ed4b49389e3afe47cda2326a.pdf).

No clinical item text is copied into this project. There is no claim that a source endorses this app. The available hotline lookup tool returned US information rather than UAE information; it was not used to verify or replace the user-supplied UAE fixtures.
