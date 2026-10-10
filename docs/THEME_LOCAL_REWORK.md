# Local theme alignment — 2026-09-13

## Authorization and reference
User requested local theme improvement based on the deployed SANSA public homepage and admin dashboard, with two supplied screenshots. Read both live pages and public stylesheet; the deployed UI differs from the Git baseline. This does not establish whether source was unpushed. No deployed files or production data changed.

## Changes
- `frontend/src/pages/HomePage.tsx`: white header, centered introduction, six-step visual matching host, turquoise assessment CTA and four existing navigation cards. Existing link destinations retained.
- `frontend/src/pages/admin/AdminLayout.tsx`: shared sidebar navigation, active state, account/logout and website link; narrow-screen horizontal navigation via CSS. Existing authentication/role checks retained.
- `frontend/src/pages/AdminDashboard.tsx` and `backend/app/routers/dashboard.py`: greeting banner, management cards and four live aggregate counts from the local database. Counts exclude soft-deleted records and use Bangkok time for today's visits.
- `frontend/src/pages/admin/adminMenu.ts` and `AdminIcon.tsx`: shared menu definitions and inline SVG navigation icons; no icon dependency added.
- `frontend/src/index.css`, `frontend/tailwind.config.js`: turquoise palette, cards, spacing, focus outlines, reduced-motion support and responsive layout. Shared tokens/font also affect other existing pages; no form/business logic rewritten.
- `frontend/index.html`: Thai document language and Noto Sans Thai via Google Fonts, matching deployed font. System fallback remains if offline.
- `FacilitiesPage.tsx` and `KnowledgePage.tsx`: removed hardcoded English samples. Both public pages now load visible records from the existing APIs, show loading/error/empty states, and provide search. Knowledge displays stored summary/content; facilities display stored contact/map data.
- Existing admin content/facility/user tables now use shared search and pagination controls. Respondent listing uses server-side search, total count and pagination instead of silently stopping at the first 100 records.
- Admin knowledge/facility forms now capture the existing content, summary, description and map-link fields needed by their public pages. No new content tables were added.
- 2026-09-15 menu parity pass: all top-level admin pages now share the deployed page-heading treatment, expandable create panels, list headers with counts/refresh, full-width search, table footer pagination, status/table styling and responsive spacing. The dashboard cards now include the deployed target-ring presentation while retaining live database counts.
- The admin top bar now includes working menu search, a local notification popover, public-site shortcut and account identity. These controls do not add a backend notification system.
- 2026-09-15 CRUD completion pass: knowledge and facility menus can edit and soft-delete existing records; user management can edit email/name/role/status and deactivate accounts; respondent detail can edit core contact/demographic fields and soft-delete the respondent. Existing backend PUT/DELETE routes are reused, and destructive actions require confirmation.
- 2026-09-15 facility dataset: validated the supplied Bangkok public-health-center workbook (69 complete, unique rows), added a repeatable dry-run/upsert importer, and added an address-based embedded Google Map with a selectable facility list and original Google Maps links on the public facility page. Imported into `sansa_rework_local`; production remains unchanged.
- 2026-09-15 question illustrations: copied the 12 numbered source pictures from `uploads/PICTURE ประกอบคำถาม` into the frontend public assets and mapped them to SANSA dietary questions Q5–Q16. The separate `wc_cm.jpg` now appears beside the BIA waist field. Answer options, field names, scoring, and raw source uploads remain unchanged.
- 2026-09-15 account roles: account management now supports `user`, `staff`, and `admin`. Migration `20260915_03` extends the existing MySQL enum and was applied only to `sansa_rework_local`. `user` is the default selection in the admin creation form and is explicitly redirected away from `/admin`; staff/admin API dependencies remain unchanged. Public knowledge/facility list options no longer treat an authenticated `user` as staff.

## Personal QR access

- Admin can create a respondent and issue or rotate a personal QR from the respondent detail page. The QR contains a 256-bit random secret in a URL fragment. The readable secret is returned only at issue time with `Cache-Control: no-store`; the database stores only SHA-256.
- Participant login exchanges the secret for a one-hour participant token kept in `sessionStorage`. The frontend removes the QR fragment from browser history immediately. A rotated QR invalidates the old QR and existing participant sessions.
- Participant-data routers require either staff/admin authentication or a valid participant token whose owner matches the respondent/visit/response. Anonymous access and cross-participant access are rejected. Public knowledge/facility APIs remain public.
- Migration `20260913_02_respondent_qr.py` adds only `respondents.qr_secret_hash` and its unique index. It was applied to `sansa_rework_local`; production was not changed.

## Verification and limitations
- TypeScript/Vite production build passed. Full frontend lint has zero errors and five pre-existing assessment-page warnings.
- All 37 backend tests passed, including QR randomness/hash/login/rotation/expiry, ownership denial, public visibility, dashboard/pagination, scoring-version serialization and the 200-row Excel reference comparison.
- Browser inspected the local public homepage, live-data knowledge/facility pages, QR login screen, authenticated dashboard, respondent pagination and QR administration panel. No exports or production mutations performed.
- Desktop screenshots reviewed. Attempted 390px viewport override remained at 1280px; mobile CSS implemented but real mobile visual validation remains outstanding. Override reset.
- Existing browserslist age and bundle-size warnings remain; no package upgrades.
- Visual structure now closely follows the deployed reference. Exact pixel parity and recovery of unpushed deployed source are not claimed.
- Existing imported local facility records include English sample content. The UI now shows database truth; content translation/correction requires an explicit data-edit task.
- Fixed the existing scoring API response mismatch: the public response field `rule_values` now reads the model relationship `scoring_rule_values`. The admin scoring menu was browser-verified after the fix.
- Production deployment, production migration and real-camera QR testing remain outstanding. Local setup: `LOCAL_TESTING.md`.
# Result completion (2026-09-15)

- Revised prediction now depends only on its approved inputs: D2, D3, respondent age group, and the visit's BIA waist. Missing D1 is reported and displayed as unavailable, but no longer blocks prediction.
- User and admin result pages automatically persist a valid prediction through the existing prediction endpoint. The existing `(visit_id, model_version)` upsert keeps one current row per model version.
- Both result views expose D1/D2/D3, Under/Normal/Over probabilities, predicted group, model version, BIA reference classification, and the comparison result.
- Focused backend tests: 21 passed. Frontend TypeScript/Vite production build: passed.

# Admin form guidance (2026-09-15)

- Added Thai labels, examples, required markers, and field-level help to user, facility, knowledge, and scoring forms.
- Added hover/focus descriptions to admin navigation, header actions, shared create/list controls, searches, and sensitive user actions.
- User-role choices now explain `user`, `staff`, and `admin` at the selection point.
- Frontend TypeScript/Vite production build: passed.

# Excel CSV Thai text (2026-09-16)

- CSV downloads from SANSA, MNA, BIA, satisfaction, and combined export now include a UTF-8 BOM and explicit UTF-8 content type so Excel identifies Thai text correctly when opening downloaded CSV files.
- Export values, column order, and research code mappings were not changed.
- Focused synthetic encoding test: passed. Existing downloaded CSV files must be downloaded again to receive the marker.

## Runtime follow-up (2026-09-17)

- The newly downloaded `bia_2026-09-17.csv` still lacked the BOM because the local backend process had been running since before the export-router change and was not in reload mode. Source code alone had not updated that process.
- Restarted only the local backend on `127.0.0.1:8000`; no database content was changed. The former temporary-venv `uvicorn` launcher had no installed module, so the available Homebrew uvicorn was used and is running.
- Authenticated read-only API checks of all five CSV endpoints returned HTTP 200, a UTF-8 BOM, parseable rows/columns and zero Unicode replacement characters. Counts: SANSA 241, MNA 208, BIA 208, satisfaction 206, combined 243.
- Previously downloaded files remain unchanged. A fresh download is required for Excel verification.
