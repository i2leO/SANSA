# SANSA REWORK — Tasks 5–6

## Status and authorization

User subsequently authorized Tasks 5–6 and local MAMP setup/testing. Implementation and local validation completed 2026-09-13. Production deployment remains pending. Tasks 2–4 history is in `REWORK_CONTEXT.md`. Excel revised4 remains the primary reference; original requirements follow below.

## Task 5 — BIA nutrition reference classification

Mode when authorized: IMPLEMENT ONLY.

Objective: derive reference nutritional classification from existing respondent/BIA sources: age, sex, BMI and body fat percentage (PBF). No new BIA table and no changes to raw measurements.

### Functions and rules

`classify_bmi_glim(age, bmi)`:

1. Round BMI to one decimal place before classification.
2. Age <70: BMI <18.5 → UNDER; BMI >=25 → OVER; otherwise NORMAL.
3. Age >=70: BMI <20 → UNDER; BMI >=25 → OVER; otherwise NORMAL.

`classify_body_fat(sex, pbf)`:

| Sex | UNDER | NORMAL | OVER |
| --- | --- | --- | --- |
| Male | PBF <15 | 15 through 25 inclusive | PBF >25 |
| Female | PBF <20 | 20 through 35 inclusive | PBF >35 |

Do not invent rules for unsupported sex values. Follow existing project validation behavior.

`derive_nutrition_reference()`:

- If either BMI class or PBF class is UNDER → UNDER.
- Otherwise, if either class is OVER → OVER.
- Otherwise → NORMAL.

Return `bmi_rounded`, `bmi_class`, `pbf_class`, `nutrition_reference`.

### Focused tests

- Ages: 69, 70.
- BMI: 18.4, 18.5, 19.9, 20.0, 24.9, 25.0.
- Male PBF: 14.9, 15, 25, 25.1.
- Female PBF: 19.9, 20, 35, 35.1.
- Priority: UNDER overrides OVER.

### Strict exclusions

No new BIA table, raw BIA edits, prediction coefficient changes, SANSA scoring changes, MNA/satisfaction/frontend modifications or architecture redesign.

### Required completion report

1. Files changed
2. Functions created
3. Rules implemented
4. Boundary test results
5. Out-of-scope findings

Stop after reporting. Do not automatically proceed to another task.

## Task 6 — Integration and final validation

Mode when authorized: IMPLEMENT ONLY. Requires Task 5 completion; the supplied task's statement that five backend components are completed is a prerequisite, not their current status.

Objective: integrate existing domain scores, age-group derivation, prediction engine, prediction storage and BIA reference classification into the existing application. Reuse these components; do not rewrite them.

### Required result for an existing visit

| Group | Fields |
| --- | --- |
| SANSA | D1_total, D2_total, D3_total |
| Prediction | P_UNDER, P_NORMAL, P_OVER, predicted_group, model_version |
| Reference | BMI class, PBF class, nutrition_reference |
| Comparison | predicted_group versus nutrition_reference |

### API

- Reuse existing API/router/service patterns; no parallel API architecture.
- Add only necessary endpoints or response fields.
- Prefer safely extending an existing visit/result endpoint over duplicate endpoints.

### Frontend

Reuse the existing SANSA result page/component without redesign. Display only the necessary additions:

1. SANSA domain scores
2. Predicted nutritional group
3. Probability values
4. Reference nutritional group when BIA data exists
5. Model version where appropriate

If BIA data does not exist, follow defined project behavior, never invent waist circumference, and clearly handle missing required prediction inputs.

### Validation

Use available revised SANSA Excel reference data/test cases when practical. Compare calculated outputs against reference values for:

1. D1/D2/D3
2. age_group01
3. Waist source
4. Logits
5. Probabilities
6. Predicted group
7. BMI classification
8. PBF classification
9. Nutrition reference
10. Database persistence
11. API result
12. UI display

For mismatches, report the exact mismatch and likely cause; do not broaden scope. Do not include participant records in logs or documentation; identify affected reference locations and field-level discrepancies without copying full records.

### Strict exclusions and testing

- No UI/database redesign, existing-module rewrite, authentication/user-management/facilities changes, package upgrades, unrelated refactoring, cleanup or optimization.
- Do not change MNA/satisfaction unless a direct integration blocker exists.
- Report unrelated problems only.
- Run focused SANSA integration tests first. Do not repeatedly scan the repository or run expensive broad analysis.
- Broader regression tests: at most once at the end, only if an appropriate existing project command is available.

### Required completion report

1. Files changed
2. API changes
3. UI changes
4. Validation results
5. Any Excel/reference mismatches
6. Tests passed/failed
7. Remaining risks
8. Out-of-scope findings

Stop. Do not start additional features.

## Known points to resolve within the relevant task

- Task 5 explicitly requests rounding BMI. Earlier Excel review also recorded one-decimal rounding of PBF. Preserve Excel authority and explicitly resolve this difference before implementing boundary behavior; do not silently choose a different rounding rule. Confirm rounding matches Excel at half-way values.
- Existing waist field: `BIARecord.waist_circumference_cm`. A visit can have multiple BIA records; authority/record selection has not yet been settled. Do not pick an arbitrary record or invent a waist when missing.
- Age/sex exist in both Respondent and BIA; define the source used for the visit without overwriting raw values.
- Task 4 storage flushes/refreshes; caller must commit/rollback. Migration was created but not applied to production. Prior storage tests used SQLite, with MySQL DDL compilation only.
- Excel record numbers are not an approved identity crosswalk to existing database respondents. Reference validation does not authorize importing/updating existing participant data.
- QR registration/login is separately agreed product scope, not part of Tasks 5–6.


## Implementation and local validation — 2026-09-13

- Added `backend/app/services/bia_reference_service.py`: BMI/PBF classification and UNDER-first reference. BMI and PBF round half-up to one decimal, matching authoritative revised4. Unsupported sex is rejected.
- Added `backend/app/services/sansa_result_service.py`: derives domains and prediction using respondent age/sex and the single BIA record attached to the visit. Missing or multiple BIA records produce explicit issues; no arbitrary selection or fabricated waist. Raw data and old scores remain unchanged.
- Extended `backend/app/schemas.py` and existing GET `/sansa/visit/{visit_id}` in `backend/app/routers/sansa.py` with `revised`; GET does not write. POST `/sansa/visit/{visit_id}/prediction` calculates server-side and commits/upserts through Task 4 storage. Missing inputs return 422; storage failure returns 503.
- Extended `frontend/src/pages/ResultPage.tsx` with domains, prediction probabilities/category/version, BIA reference/comparison, input-issue messages and explicit save button. Existing threshold results remain separately displayed.
- Direct build/tracking blockers: `frontend/tsconfig.json` ignoreDeprecations changed from unsupported 6.0 to 5.0 for installed TS5.9; `.gitignore` permits the Task4 migration. No dependency versions or lockfile changed.
- Focused tests: `test_bia_reference_service.py`, `test_sansa_result_integration.py`, `test_sansa_excel_reference.py`. All 30 backend tests passed, including earlier Tasks2–4 tests. Excel test compares cached revised4 outputs for 200 populated rows: domains, age group, waist transfer, logits, probabilities, predicted group, BMI/PBF/reference classes. No mismatch (numeric tolerance 1e-10). Template rows excluded; no identity crosswalk or Excel import performed.
- `npm run build` and focused ESLint on ResultPage passed. Browser verified synthetic result and save success; live local MySQL API repeat-save preserved the row ID and one result, probabilities sum to one.
- Local setup/details: `LOCAL_TESTING.md`.

### Remaining risks / out-of-scope findings

- MySQL5.7 ignores CHECK constraints; service validation remains active, unique/FK/ENUM constraints verified. Production MariaDB migration and behavior are not yet validated.
- Respondent demographics may differ from BIA snapshots; respondent is the selected source. Multiple BIA records intentionally block prediction until an explicit selection policy is approved.
- Excel validation uses cached workbook values, not a new Excel recalculation. Existing DB BMI precision can cause rounding differences from full-precision workbook calculations near boundaries.
- Old SANSA PUT field mappings are stale; not changed. Existing imported schema contains columns beyond Git models; not reconciled here.
- Original authentication policy is retained, including self-service result routes. No QR/auth changes or production readiness/security audit performed.
- Local runtime needed email-validator, already required by EmailStr but absent from requirements; installed only in temporary environment. Reproducible clean dependency installation remains to be addressed separately.
- Existing npm audit warnings (26), outdated browserslist, large build chunk and Pydantic model_version namespace warning remain. No unrelated fixes.
- Prediction save locks storage but does not implement a cross-record input snapshot/concurrency redesign. No historical recalculation or deployment performed.
