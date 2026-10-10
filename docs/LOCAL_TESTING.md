# Local SANSA testing — 2026-09-13

## Environment

- Frontend: http://127.0.0.1:5173/
- Synthetic example: http://127.0.0.1:5173/result/243
- Backend: http://127.0.0.1:8000

### LAN QR test (2026-09-19)

- Current Mac LAN IP: `192.168.1.44`.
- Frontend is running on `0.0.0.0:5173` and is available at `http://192.168.1.44:5173/`.
- Backend is running on `0.0.0.0:8000`; local frontend environment points to `http://192.168.1.44:8000` and backend `FRONTEND_URL` allows `http://192.168.1.44:5173`.
- HTTP checks returned 200 for both LAN URLs. CORS preflight for participant login returned the exact LAN frontend origin.
- Open the admin panel through the LAN URL before issuing a test QR. QR uses `window.location.origin`; a QR issued while the admin page is opened on `127.0.0.1` will remain unsuitable for a phone.
- Phone and Mac must use the same home network. The LAN IP may change after DHCP/network reconnect; update both local env values and restart both processes when it changes. These settings are for local testing only.
- MAMP MySQL 5.7.39, socket `/Applications/MAMP/tmp/mysql/mysql.sock`.
- Dedicated database: `sansa_rework_local`. Existing `SANSA` database untouched. No VPS access/deployment in this work.
- Original `sansa_db.sql` unchanged; temporary import copy only translated utf8mb3 to utf8 for MySQL5.7 compatibility.
- Imported 16 application tables; Alembic head `20260913_02` applied successfully. It adds `sansa_prediction_results`, `respondents.qr_secret_hash`, migration metadata and the QR unique index. Prediction visit FK and unique visit/model version verified.
- Original 244 respondents/242 visits preserved. One synthetic respondent/visit added for UI testing: final 245 respondents/243 visits, one prediction result. Synthetic respondent code `SYNTHETIC-LOCAL-TEST`; visit 243. No Excel participant import.
- Ignored `backend/.env` selects this local database (permissions600); no credentials copied into docs.

## Start if servers stop

Keep MAMP MySQL running. Commands assume project root as current directory.

```sh
cd backend
/private/tmp/sansa-task4-venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Separate terminal, from project root:

```sh
cd frontend
npm run dev -- --host 127.0.0.1
```

The Python environment is temporary and may need recreating after OS cleanup. Current servers were left running for user review. Do not run seed/reset/import scripts against the imported database. Do not reapply SQL dump as an ordinary startup step.

## Validation

37 backend tests pass; 200 populated revised4 cases match cached expected outputs. Frontend build passes; full lint has zero errors and five existing assessment-page warnings. Browser checks cover every admin menu, live aggregate counts, public data pages, respondent pagination, QR administration/login screens, scoring rules and the prediction result. API tests against local MySQL cover QR issue/login/rotation, ownership enforcement and prediction persistence. Details and limitations are in `TASKS_5_6.md` and `THEME_LOCAL_REWORK.md`.

```sh
cd backend
DATABASE_URL=sqlite:// DEBUG=False /private/tmp/sansa-task4-venv/bin/python -m unittest discover -s tests
```

These automated tests use isolated SQLite; the browser/API persistence check additionally ran against MAMP MySQL. MySQL5.7 does not enforce CHECK constraints. Production migration and deployment remain pending.
