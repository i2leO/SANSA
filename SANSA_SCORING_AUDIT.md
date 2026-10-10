# SANSA Scoring Audit — 0/2/4

Audit date: 2026-10-08  
Scope: current working tree (including uncommitted local changes), read-only review  
Primary specification: `EDIT SANSA ONLINE (revised).pdf`, pages 5–9 and 11

No business logic, database row, migration, production service, or UI was changed as part of this audit.

## A. Executive Summary

**Overall status: INCORRECT / PARTIAL.**

- The application has a complete technical path for 16 answer fields, per-item stored scores, D1/D2/D3 summation, Model 3 logits, numerically stable softmax, persistence, display, and export.
- The current per-item score definition is **not the PDF 0/2/4 definition**. It is explicitly sourced from `Code_Self_2026-02-03` and assigns intermediate scores 1 and 3 to many answers.
- Because D2 and D3 are summed from the stored per-item scores, the prediction engine receives structurally correct variables but potentially **semantically wrong D2/D3 values** relative to the PDF.
- The Model 3 equation, softmax, predictor list, age grouping, and exclusion of Screening/D1 match page 11.
- The database can preserve raw answers and scores, but `scoring_version_id` does not actually select a versioned item mapping: the active version row is recorded while the executable mapping remains the single current Python definition. Historical reproducibility is therefore incomplete.
- The focused tests pass, but they validate the current `Code_Self`/revised4 implementation—not the PDF 0/2/4 contract. A passing suite is not evidence of conformance to the requested PDF.

Status legend: **Implemented** = complete and aligned; **Partial** = plumbing exists but not fully aligned; **Incorrect** = conflicts with PDF; **Missing** = absent; **Unable to verify** = insufficient evidence.

## B. Scoring Audit Matrix

Application field numbering is Q1–Q16. PDF fields are shown separately because its names differ from the database names.

| PDF field | App/DB answer + score | PDF expected mapping | Current executable mapping | Status | Evidence |
|---|---|---|---|---|---|
| `scr_bw` | `q1_weight_change`, `q1_score` | decrease=0, stable=2, increase=4 | decrease=2, stable=0, increase=2 | **Incorrect** | `sansa_definition.py:26`; model columns `models.py:324-325` |
| `scr_app` | `q2_food_intake`, `q2_score` | decrease=0, normal=2, increase=4 | decrease=2, normal=0, increase=2 | **Incorrect** | `sansa_definition.py:27`; `models.py:326-327` |
| `scr_act` | `q3_daily_activities`, `q3_score` | cannot/slower=0, normal=2; no 4 | cannot=2, slower=1, normal=0 | **Incorrect** | `sansa_definition.py:28`; `models.py:328-329` |
| `scr_dx` | `q4_chronic_disease`, `q4_score` | no=2, yes=4; no 0 | no=0, yes=1 | **Incorrect** | `sansa_definition.py:29`; `models.py:330-331` |
| `ass_meal` | `q5_meals_per_day`, `q5_score` | rarely/1=0; 2/3=2; >3=4 | rarely=0; 1=1; 2=2; 3=3; >3=4 | **Incorrect** | `sansa_definition.py:30`; `models.py:332-333` |
| `ass_intake` | `q6_portion_size`, `q6_score` | 25/50/75=0; 100=2; >100=4 | 25=0; 50=1; 75=2; 100=3; >100=4 | **Incorrect** | `sansa_definition.py:31`; `models.py:334-335` |
| `ass_type` | `q7_food_texture`, `q7_score` | liquid/soft=0; normal=2; no 4 | liquid=0; soft=1; normal=4 | **Incorrect** | `sansa_definition.py:32`; `models.py:336-337` |
| `ass_rice_starch` | `q8_rice_starch`, `q8_score` | none/1–3/4–6=0; 7–9=2; >9=4 | 0/1/2/3/4 across five bands | **Incorrect** | `sansa_definition.py:33`; `models.py:338-339` |
| `ass_meat_egg` | `q9_protein`, `q9_score` | none/1–2=0; 3–5=2; 6–8/>8=4 | 0/1/2/3/4 across five bands | **Incorrect** | `sansa_definition.py:34`; `models.py:340-341` |
| `ass_milk` | `q10_milk`, `q10_score` | none/<1=0; 1/2=2; 3/4=4 | 0/1/2/3/4; `<1` only a legacy alias for 0 | **Incorrect** | `sansa_definition.py:35`; `models.py:342-343` |
| `ass_fruit` | `q11_fruits`, `q11_score` | none/1–2=0; 3–5=2; 6–8/>8=4 | 0/1/2/3/4 across five bands | **Incorrect** | `sansa_definition.py:36`; `models.py:344-345` |
| `ass_veget` | `q12_vegetables`, `q12_score` | none/0–1=0; 2–3/4/>4=2; no 4 | 0/1/2/3/4; creates prohibited score 4 | **Incorrect** | `sansa_definition.py:37`; `models.py:346-347` |
| `ass_water` | `q13_water`, `q13_score` | rarely/1–3/4–6=0; 7–8/>8=2; no 4 | 0/1/2/3/4; creates prohibited score 4 | **Incorrect** | `sansa_definition.py:38`; `models.py:348-349` |
| `ass_sweetdrink` | `q14_sweet_drinks`, `q14_score` | no score 0; rarely/1=2; 2/3/>3=4 | none=0; 1=1; 2=2; 3=3; >3=4 | **Incorrect** | `sansa_definition.py:39`; `models.py:350-351` |
| `ass_cook` | `q15_cooking_method`, `q15_score` | no score 0; boil/stew/steam/bake/yum/grill/stir=2; coconut curry/deep fry=4 | non-coconut=0; stir=1; coconut=2; fried=4 | **Incorrect** | `sansa_definition.py:40`; `models.py:352-353` |
| `ass_oil` | `q16_oil_coconut`, `q16_score` | rarely/1–2/3–4=0; 5–6=2; >6=4 | 0/1/2/3/4 across five bands | **Incorrect** | `sansa_definition.py:41`; `models.py:354-355` |

### Domain totals

| Domain | PDF contract | Current behavior | Status | Evidence |
|---|---|---|---|---|
| Screening | store answer codes 0/2/4; do not sum/use in Model 3 | scores Q1–Q4 and calculates/stores `screening_total`; not used by Model 3 | **Partial / Incorrect legacy total** | `scoring_service.py:116-135`; `models.py:356` |
| D1 | Q5+Q6+Q7; expected range 0–10; exclude from Model 3 | sums Q5–Q7; excluded from prediction; current mapping permits 0–12 | **Partial** | `sansa_domain_service.py:12-18`; `sansa_result_service.py:40-43` |
| D2 | Q8–Q13; expected range 0–20; raw sum | sums stored Q8–Q13 without averaging/normalizing; current mapping permits 0–24 | **Structurally implemented, semantically incorrect** | `sansa_domain_service.py:14-17` |
| D3 | Q14–Q16; expected range 4–12 | sums stored Q14–Q16; current mapping permits 0–12 and prohibited score 0 | **Structurally implemented, semantically incorrect** | `sansa_domain_service.py:18` |

### Validation and storage

- All 16 answers are required and canonical values are validated server-side (`schemas.py:271-300`).
- The server calculates scores; it does not accept client-supplied scores (`routers/sansa.py:41-94`).
- Raw answer and score columns exist for all 16 items (`models.py:323-355`). Numeric zero remains distinguishable from null.
- `visit_id` is unique, preventing two SANSA rows for one visit (`models.py:311-317`).
- Missing D1/D2/D3 scores are not silently treated as zero (`sansa_domain_service.py:21-31`).
- New writes record an active `scoring_version_id`, but the actual per-item mapping comes from Python, not the selected database rule version (`routers/sansa.py:41-54`; `scoring_service.py:74-90`). **Version provenance is therefore partial.**

## C. Function & Dependency Map

```text
GET /sansa/definition
  -> public_definition()
  -> SANSA_QUESTIONS (current Code_Self mapping)
  -> SANSAFormPage renders labels/options

User selection
  -> react-hook-form + zod (all 16 required)
  -> POST /sansa with raw answer codes only
  -> SANSAResponseCreate validates canonical values
  -> ScoringService.calculate_sansa_scores()
  -> calculate_sansa_question_score()
  -> score_answer() from SANSA_QUESTIONS
  -> server stores raw answers + q1_score...q16_score + legacy totals

GET /sansa/visit/{visit_id}
  -> revised_visit_result()
  -> calculate_sansa_domain_scores()
       D1 = q5+q6+q7
       D2 = q8+q9+q10+q11+q12+q13
       D3 = q14+q15+q16
  -> age_group01(): age < 70 => 0, otherwise 1
  -> unique BIA waist_cm
  -> predict_sansa_nutrition_status(D2,D3,wc_cm,AgeGroup01)
  -> stable softmax + argmax
  -> optionally save_sansa_prediction() by model version
  -> API/admin display/export
```

Frontend definition load: `frontend/src/pages/SANSAFormPage.tsx:74-80`.  
Definition endpoint: `backend/app/routers/instruments.py:8-14`, mounted before protected assessment routers at `backend/app/main.py:55-60`.

## D. Findings

### Critical

1. **All 16 executable mappings are not aligned with the revised PDF.** The system currently implements an ordinal 0/1/2/3/4 codebook, while the PDF specifies grouped 0/2/4 categories and intentionally missing categories for several items.
2. **Model 3 can receive wrong D2/D3 values.** The equation is correct, but it consumes sums of stored scores produced by the wrong item mapping. Correct mathematics applied to incorrect inputs still yields an invalid research result.
3. **Conflicting authorities are embedded in the repository.** `sansa_definition.py:1-13` declares `Code_Self` authoritative, while this audit request declares the revised PDF authoritative. This must be resolved explicitly before implementation.

### High

4. **Score version selection does not version the mapping.** `scoring_version_id` is selected/stored, but `score_answer()` always uses the current module constant. Editing the Python definition changes future calculation behavior without a database-bound immutable mapping snapshot.
5. **Historical stored answer/score pairs may already be inconsistent.** Read-only inspection of the local staff page found an existing answer `normal` for food texture paired with score `0.00`; both the current definition (4) and revised PDF (2) disagree. This was not corrected because historical identity/provenance and approved rescore policy are absent.
6. **Exports propagate stored score semantics.** SANSA export emits the 16 stored scores and derived domains; prediction export emits stored or read-only-derived Model 3 results. Incorrect historic/current scores therefore flow into research exports (`export_service.py:93-138`, `144-184`, `487-503`).

### Medium

7. **Legacy threshold classification is unrelated to revised PDF Model 3.** `calculate_sansa_scores()` also creates `screening_total`, `diet_total`, `total_score`, and threshold-based `result_level` using 38/25 cutoffs (`scoring_service.py:163-181`). The revised PDF defines the primary result through Model 3, not these thresholds. Although participant output is separated, these fields remain stored and can confuse reports or staff interpretation.
8. **No domain range guard exists.** The domain service accepts any numeric stored values, including decimals and out-of-contract totals. Tests explicitly demonstrate D3=4.3 is accepted (`test_sansa_domain_service.py:33-39`).
9. **Field naming requires an explicit research crosswalk.** PDF `ass_meat_egg` maps to application `q9_protein`; the mapping is reasonable but not encoded as a formal external-field alias in the instrument definition.

### Low

10. Pydantic and SQLAlchemy deprecation warnings remain in the focused test run. They did not cause failures but should be handled separately from scoring repair.

## E. Duplicate Logic

- Current item options/scores are centralized in `sansa_definition.py`; backend scoring and participant form consume it. This reduces duplication for new writes.
- Staff display retains a fallback question/label list in `researchLabels.ts` when the live definition endpoint is unavailable. The fallback is display-only, but labels can drift.
- Legacy total/status logic in `ScoringService.calculate_sansa_scores()` coexists with Model 3 logic. These are separate outcome systems and create semantic duplication/confusion.
- Export can use an already stored prediction or derive one read-only (`export_service.py:487-503`). The shared prediction function prevents formula duplication, but correctness still depends on the stored per-item scores.

## F. Test Results

Command executed without source modification:

```text
PYTHONPATH=backend /opt/homebrew/bin/python3.10 -m pytest \
  backend/tests/test_sansa_definition.py \
  backend/tests/test_sansa_domain_service.py \
  backend/tests/test_sansa_prediction_service.py \
  backend/tests/test_revised4_workflow_validation.py \
  backend/tests/test_sansa_excel_reference.py -q
```

Result: **24 passed, 18 warnings, 0 failed (0.88s).**

Interpretation:

- **Pass:** D1/D2/D3 field grouping, missing-score rejection, age group, logits, stable softmax, argmax, invalid numeric inputs, and 200 revised4 reference rows.
- **Fail by specification (not test runner):** `test_sansa_definition.py:41-46` asserts Q4 yes=1 and Q7 soft=1, directly conflicting with revised PDF values 4 and 0.
- **Missing coverage:** exhaustive PDF 0/2/4 option matrix; D1 range 0–10; D2 range 0–20; D3 range 4–12; prohibited categories (D2 vegetables/water score 4 and D3 sweet/cook score 0); update/re-save endpoint with changed answers; immutable scoring-version replay; answer/score database consistency audit.
- The existing 200-row workbook test proves reproduction of revised4 stored calculations. It does not prove that the source answers were originally coded using the revised PDF.

## G. Recommended Corrections (not implemented)

1. **Owner decision:** confirm that `EDIT SANSA ONLINE (revised).pdf` supersedes the old `Code_Self` mapping for all new responses and define the effective date/version identifier.
2. Create an approved, immutable PDF-derived mapping specification with explicit application-field ↔ PDF-field crosswalk and every answer grouping.
3. Add exhaustive characterization tests for every PDF option, prohibited score category, and domain min/max **before** changing production logic.
4. Version the executable mapping, bind it immutably to `scoring_version_id`, and store an explicit instrument-definition version on each response/prediction or guarantee equivalent immutable provenance.
5. Update backend mapping and validation first; then have frontend render the same versioned definition. Do not allow client scores.
6. Add domain range validation and reject invalid stored/input scores before prediction.
7. Decide what to do with legacy `screening_total`, `diet_total`, `total_score`, and `result_level`; do not present them as Model 3 output.
8. Define a historical-data policy: preserve-as-recorded, flag inconsistency, or approved re-score into a new version. Never overwrite historical scores silently.
9. Update exports to include scoring-definition/model versions and an integrity/status flag so mixed-version data cannot be analyzed as one homogeneous dataset.
10. Run isolated integration tests and a synthetic end-to-end form → database → D2/D3 → prediction → export verification before deployment.

## H. Final Conclusion

1. **Are scoring functions present?** Yes. The code has complete calculation, storage, domain, prediction, display, and export functions.
2. **Does every item match the revised PDF 0/2/4 rules?** No. All 16 current mappings conflict in at least one option; most use prohibited 1/3 intermediate scores.
3. **Are D1/D2/D3 calculated and stored correctly?** The grouping and summation mechanics are correct, but the totals are not correct relative to the PDF because the source item scores are wrong. D1/D2/D3 are derived on read; predictions can be stored separately.
4. **Does Model 3 use the correct variables and equation?** Yes: D2, D3, waist cm, and AgeGroup01 only; formula, softmax, and argmax match page 11. However, D2/D3 may be semantically wrong due to upstream scoring.
5. **What must change?** After explicit approval, the primary targets are `backend/app/services/sansa_definition.py`, its validation/tests, domain range validation, immutable scoring-version provenance, frontend labels/options, and exports. Historical records require a separately approved policy and must not be silently rewritten.

## Open Questions

1. Does the revised PDF replace `Code_Self_2026-02-03` for all assessments from a specific effective date, or only for a new instrument version?
2. Should Screening 0/2/4 values be stored as “answer codes” only, with `screening_total` left null, as page 5 states?
3. For `ass_cook`, does “ผัด” always score 2 regardless of oil amount, while oil exposure is independently captured by `ass_oil`?
4. Should historical inconsistent rows be preserved with an integrity flag, or re-scored into a separate versioned result table after an approved identity/provenance review?
5. Should exports include raw answer codes in addition to score columns to allow independent research verification?
