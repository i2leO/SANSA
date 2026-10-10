# SANSA 16-item mapping audit — corrected 2026-10-07

## Source roles

- `src/ปรับแก้ Test Data THESIS PHASE2 03022026.xlsx`, sheet `Code_Self`: SANSA question and scoring codebook.
- `Use SANSA Integrated WebApp Data (revised4).xlsx`: collected research data plus supplied Model 3 calculations. Its observed values are not the questionnaire codebook.
- `ฝั่งเจ้าหน้าที่.pdf`: staff layout/reference example. Values shown in its mock participant table are not scoring authority when they conflict with `Code_Self`.
- SQL/local database: historical and synthetic records. Existing values are evidence of what was stored, not scoring authority.

No participant record was changed or rescored during this audit.

## Model domains

| Items | Codebook variables | Domain | Model 3 input |
| --- | --- | --- | --- |
| Q1–Q4 | `scr_bw`, `scr_app`, `scr_act`, `scr_dx` | Screening | No |
| Q5–Q7 | `ass_meal`, `ass_intake`, `ass_type` | D1 | No |
| Q8–Q13 | `ass_rice_strach` through `ass_water` | D2 | Yes, through D2 total |
| Q14–Q16 | `ass_sweetdrink`, `ass_cook`, `ass_oil` | D3 | Yes, through D3 total |

Screening and D1 remain recorded research fields. “No” means they are not predictors in `Model3_Reduced_UnderRef_v1`.

## Codebook comparison

| Q | Codebook scoring | Current implementation assessment |
| ---: | --- | --- |
| 1 | decrease 2; stable 0; increase 2 | Matches codebook. PDF mock row showing stable = 2 conflicts with codebook. |
| 2 | decrease 2; normal 0; increase 2 | Matches codebook. PDF mock row showing normal = 2 conflicts with codebook. |
| 3 | cannot 2; slower 1; normal 0 | Matches codebook. PDF mock row showing slower = 0 conflicts with codebook. |
| 4 | no 0; yes 1 | Defect: service currently gives yes = 2. PDF mock row showing yes = 4 also conflicts with codebook. |
| 5 | rarely 0; 1/2/3/>3 meals = 1/2/3/4 | Matches codebook. |
| 6 | 25/50/75/100/>100 percent = 0/1/2/3/4 | Matches codebook. |
| 7 | liquid 0; soft 1; normal 4 | Defect: service currently gives soft = 2. |
| 8 | none 0; 1–3/4–6/7–9/>9 fists = 1/2/3/4 | Matches codebook mapping. |
| 9 | none 0; 1–2/3–5/6–8/>8 palms = 1/2/3/4 | Matches codebook mapping. |
| 10 | no milk 0; 1/2/3/4 glasses = 1/2/3/4 | Defect in wording: form uses `<1` for score 0, broader than “ไม่ได้ดื่ม”. |
| 11 | none 0; 1–2/3–5/6–8/>8 fists = 1/2/3/4 | Matches codebook mapping. |
| 12 | none 0; 0–1/2–3/4/>4 double handfuls = 1/2/3/4 | Matches codebook mapping. |
| 13 | rarely 0; 1–3/4–6/7–8/>8 glasses = 1/2/3/4 | Matches codebook mapping. |
| 14 | rarely 0; 1/2/3/>3 glasses = 1/2/3/4 | Matches codebook mapping. |
| 15 | non-coconut curry 0; stir-fry 1; coconut curry 2; fried 4 | Defect: current form substitutes boil/steam for the codebook's non-coconut curry option. |
| 16 | rarely 0; 1–2/3–4/5–6/>6 thumbs = 1/2/3/4 | Matches codebook mapping. |

## Confirmed implementation defects

1. Q4 `yes/มี` must score 1, not 2.
2. Q7 `soft/อาหารอ่อนนิ่ม` must score 1, not 2.
3. Q10 score-zero wording must mean no milk, not every value below one glass.
4. Q15 score-zero option must represent non-coconut curry. Boil/steam is not the codebook label and cannot silently replace it.
5. The staff PDF mock-answer scores for Q1–Q4 cannot be copied into scoring logic because they conflict with the codebook.
6. `ass_rice_strach` is misspelled in the old workbook codebook; application/database field `q8_rice_starch` remains canonical and requires an explicit import alias.

## Data findings

- revised4 has 200 populated research rows, but its numeric values are already-recorded data.
- Most local historical SANSA rows contain scores without raw-answer strings and must not be reverse-mapped or automatically rescored.
- Visit 239 is the only local row currently found with all 16 raw answers plus Model 3 inputs; its answers were recorded under legacy behavior and do not certify corrected scoring.
- Visit 243 is the score-only `SYNTHETIC-LOCAL-TEST` fixture and is not valid for raw-answer acceptance testing.

## Implementation status — 2026-10-07

- Created the versioned machine-readable definition `Code_Self_2026-02-03` in `backend/app/services/sansa_definition.py`.
- New-write validation, backend item scoring, the public read-only definition API, and the participant SANSA form now consume that definition.
- Corrected Q4 and Q7 scores and corrected the Q10/Q15 options offered by the form.
- Legacy aliases remain readable for existing records but are not offered or accepted for new submissions.
- Added focused regression coverage for Q4, Q7, Q10, Q15, canonical-write validation, legacy-read compatibility, and definition completeness.
- Corrected the staff update route's stale Q8/Q9/Q10/Q13 attribute names.
- No historical row was changed or recalculated.

The “Current implementation assessment” column above records the defects found before this implementation and is retained as audit evidence.
