# Research system repair register — updated 2026-10-04

This register supersedes earlier claims that build success meant the staff workflow was complete. Work remains unapproved for deployment. No historical rows are recalculated by these changes.

## Confirmed issues and current work

| Issue | State | Evidence / required completion |
| --- | --- | --- |
| Missing/unknown MNA answers silently score zero | Code corrected; regression tests added | Scoring rejects unsupported answers before write |
| Screening >11 skips assessment then produces a full-score diagnosis | Code corrected; regression tests added | Full MNA requires all 18 answers; maximum case is 14+16=30 |
| MNA page omits questions K–R and never loads/updates existing record | Closed in code; user verification pending | API tests cover definition, create, update, reload same ID; frontend build/lint pass |
| BIA export uses kg for vfat_level | Regression verified | Export test uses distinct level 7 and mass 2; exported level is 7 |
| BIA edit opens empty form and POSTs instead of updating | Closed in code; user verification pending | Loads the existing record, PUTs the same ID, clears derived BMI when inputs are removed, and uses the backend BMI category |
| Staff PDF requires editable inline forms | Closed in code; user verification pending | Staff visit page includes inline BIA and full MNA A–R sections alongside general data and SANSA answers |
| MNA version selection hardcoded to 1 (SANSA in dump) | Closed for new writes | Active MNA version is resolved by instrument; update retains the record's MNA version and rejects non-MNA versions |
| MNA R stored in legacy q7/mna_s7; dump has q19/mna_a12 | Closed without historical rewrite | Canonical R is q19/mna_a12; conditional migration adds missing columns and export preserves zero versus missing |
| Demographic/SANSA labels duplicated or raw codes shown | Closed in current staff/form UI | Shared field-specific display definitions translate known codes; unknown historical values are marked for review rather than guessed |
| MNA summary labels incomplete historical answers as a current diagnosis | Closed in code | Stored historical totals are displayed separately; records with a missing/non-MNA version are read-only and flagged for review |
| Auth refresh/state synchronization | Closed with regression coverage | Concurrent 401s share one refresh; expired refresh logs out; a late refresh cannot overwrite a newer login |
| Missing/unknown SANSA answers silently score zero | Closed with validation | All 16 answers are required; unsupported values fail before write; duplicate assessment attempts do not pretend to succeed |
| Export conflates missing list/disease flags with zero | Closed in current export | Missing values export blank; explicit absence exports zero; age and numeric zero remain intact |
| Production can start with sample JWT/local DB/debug | Closed with startup guards | Production mode requires an explicit non-local DB, a non-sample JWT secret of at least 32 characters, and DEBUG=false |

## Acceptance standard

- Each closed issue needs behavior-level evidence, not only lint/build.
- Verify read, edit, save, reload and export on synthetic fixtures only.
- Verify staff/admin/participant permissions at API level.
- Preserve respondent identity, visit identity, raw answers, true zero, missing values and historical score versions.
- No database resets, imports, account creation or deployment as part of this audit.

## Verification performed in this repair

- Backend suite, including MNA, BIA, export, authorization, migration and revised4 workflow regressions: **63 tests passed** on 2026-10-05.
- Frontend production build and lint passed after the latest staff workspace, shared-label, SANSA validation and BIA changes.
- Frontend auth-refresh regression script passed for concurrency, logout and login-race cases.
- Python compile check and `git diff --check` passed.
- Tests use in-memory SQLite; no local participant records or credentials copied to this register.
- Local migration `20261004_07` was applied without backfilling or recalculating historical records.
- User browser verification is intentionally pending. This is not production-readiness certification and production deployment remains paused.

## Decisions still requiring research-owner approval

- Exact per-item clinical advice/recommendation text after a prediction. It was not invented from the reference PDF.
- An approved identity crosswalk or correction plan for historical rows with absent/wrong scoring-version provenance. They are flagged, not silently rewritten.
- The exact historical mapping for ambiguous legacy income codes such as `over20k` into the revised export ranges. Raw meaning is preserved rather than guessed.

## 2026-10-05 revised4 workflow enforcement

- Closed: new completed demographic profiles accept only revised4 options and cannot omit required fields.
- Closed: income-source and disease questions require an explicit UI response while preserving an intentional empty list as distinct from an unanswered field.
- Closed: all 16 SANSA answers and all seven satisfaction ratings are required by the API; satisfaction comments remain optional.
- Closed: the staff BIA save path now accepts only the complete revised4 measurement set (waist, height, weight, fat mass, body-fat percentage, visceral-fat level, muscle mass, bone mass, body water, BMR, MAC and CC). The participant waist-only path remains separate for Model 3.
- Removed from the current staff workflow because revised4 does not define them: visceral-fat mass in kilograms, weight-management selection, free-form food recommendation and typed staff signature. Historical database columns are retained to avoid destructive data loss.
- Closed: Model 3 version provenance now uses the workbook name `Model3_Reduced_UnderRef_v1`; its inputs and equations match `Model_Logic`.
- Historical records are preserved read-only as recorded. They are not coerced into revised4 categories.

## 2026-10-07 local result-data audit

- `visit_id=243` is the documented `SYNTHETIC-LOCAL-TEST` fixture added after the SQL snapshot. It was created with score-only values and has no stored SANSA raw answers. It was not imported from revised4 and must not be used as evidence that the staff answer table matches the supplied PDF example.
- The blank answer cells on the staff page are therefore source-data absence, not a frontend/API field-loss defect. The API returns the stored null raw-answer fields and the recorded score fields.
- The legacy answer-to-score map is not an approved revised4 codebook and conflicts with the supplied staff reference examples: the reference shows stable weight = 2, normal appetite = 2, slower food activity = 0 and chronic disease present = 4, while the current legacy service maps those same values to 0, 0, 1 and 2. Do not use that service to backfill or reverse-map historical/revised4 numeric rows.
- Model 3 itself is complete and matches revised4: inputs are D2, D3, waist centimetres and AgeGroup01. Screening items and D1 are retained research fields but are not Model 3 predictors. The current visit 243 prediction is mathematically computed from its synthetic scores, but it is not a valid UI acceptance fixture for raw-answer display.
- Required closure: establish the approved raw-answer/code-to-score mapping for all 16 SANSA items, then create a complete synthetic acceptance fixture or an approved Excel-to-visit test mapping. Do not attach revised4 rows to existing respondents by row number.
- Detailed field-by-field evidence and mapping status: [SANSA_16_ITEM_MAPPING_AUDIT.md](SANSA_16_ITEM_MAPPING_AUDIT.md).
