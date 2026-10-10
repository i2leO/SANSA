# Participant dataset replacement — deferred until production preparation

## Updated user decision (2026-09-16)

Keep the current local dataset for ongoing development and testing. Do not import the revised4 cohort or remove existing local respondents now. When preparing the real deployment, first settle the approved real dataset and replacement procedure, then clear and populate the intended target database with safeguards. No database changes were made for this decision.

## Earlier proposal (superseded)

Work through the six remaining areas one at a time. First, make the local participant dataset consist only of the 200 populated participants in `Use SANSA Integrated WebApp Data (revised4).xlsx`; remove participants outside that cohort. This is a local-data task, not production deployment. Preserve system accounts, scoring configuration, facilities, knowledge, and migrations because they are needed to operate the application.

## Verified current state

- Local MAMP database `sansa_rework_local`: 246 respondents, 243 visits, 241 SANSA responses, 208 MNA responses, 208 BIA records, 206 satisfaction responses, and one prediction result (read-only count on 2026-09-16).
- Respondent code groups: 215 `RES`, 30 `PILOT`, one synthetic. No Excel revised4 participant import has been performed.
- The workbook has 200 populated participant rows and 100 template rows. Its record numbers are not proven to identify existing database respondents; earlier candidate matching differed on age and sex. Do not delete by code prefix or assume row number equals respondent ID.
- Assessment dates and staff identifiers are absent in the workbook. Do not fabricate historical visits or operators.

## Reference checklist for the later real-data task (not active now)

1. Take a restorable backup of the current local database and verify it can be read. Never apply this replacement to production.
2. Build a dry-run import plan from the 200 populated workbook rows, with explicit mappings for demographics, SANSA raw answers/scores, BIA, MNA, satisfaction, and prediction. Keep missing distinct from zero and skip the 100 template rows. Report fields that cannot be mapped without guessing.
3. Import into a new isolated local database first. Verify exactly 200 respondents, referential integrity, source-to-destination counts, approved scoring and prediction outputs, and export readability. Do not assign today's date as an assessment date.
4. Only after the isolated result is complete and reviewable, replace the participant cohort in `sansa_rework_local` while preserving operational tables. Recheck UI, QR access, admin lists, results, and CSV exports.

## Pending decision

The workbook does not contain a verified crosswalk to the existing 246 respondents. Treat this as a new replacement cohort, not a merge into existing people. If the owner later requires preservation of any existing identities or visit history, obtain an approved crosswalk before changing those records.

No database rows were changed for this plan.
