# OneClickOps — Step-by-step Guide

[![Watch the demo: ](IMAGE_URL)](https://youtu.be/j4UQnAiG-GQ?si=JcdJr_3yczFB195Y)


This repo is a turnkey demo of the L2 Ops Copilot. It includes:

- FastAPI backend with detectors & runbooks
- React UI with Escalation Composer
- MySQL 8.0 (uses your `seed/db.sql`)
- Qdrant (placeholder for future KB RAG)
- Seed log file to trigger **bay/position conflict**

## 0) Prereqs
- Docker Desktop or docker + docker compose
- Ports available: 3306, 8000, 5173

## 1) Get the code
Unzip this folder and `cd` into it:

```bash
cd harbourlight
```

## 2) Start services
```bash
docker compose up --build
```
Wait until you see `Uvicorn running on http://0.0.0.0:8000` and Node dev server on 5173.

## 3) Verify API is up
```bash
curl -X POST http://localhost:8000/incident/analyze -H "Content-Type: application/json" -d '{"system_vessel_name":"MV Lion City 07","cntr_no":"MSCU0000007"}'
```

Expected JSON includes `VS.BAYPLAN_INCONSISTENCY` (from the demo logs) and empty/partial DB signals if your schema is minimal.

## 4) Open the UI
- Go to http://localhost:5173
- Enter `MSCU0000007` in **cntr_no**
- Click **Analyze** → See signals in the left panel.
- In the **Escalation Composer** (right), click **Compose** → see a draft email routed to the right owner.

## 5) Swap in your real logs (optional)
Place your logs in `./logs` (same filenames). Re-run `Analyze`. Conflicts from your data will show up.

## 6) Execute actions (guarded)
By default endpoints are **dry_run**. For a real write, call with `?dry_run=false` (not recommended for demo).

## Troubleshooting
- If MySQL init fails, ensure `seed/db.sql` is valid; check container logs: `docker compose logs -f mysql`.
- If UI can’t reach API, confirm port 8000 and CORS (dev mode uses simple fetch to localhost).

## What to tell judges (talk track)
**Hook**: “Ops firefighting steals time. HarbourLight makes every duty officer a superhero.”  
**Problem**: noisy incidents, unclear owners, slow MTTA/MTTR.  
**Solution**: Auto-triage + executable runbooks + escalation drafts grounded in your schema and logs.  
**Impact**: -50% MTTA, -30–60% MTTR on EA/VS golden paths.  
**Closing**: “Ready for pilot next week.”

## Safe runbooks
- Expire active vessel advice before creating a new one.
- Keep-latest container snapshot; bounded delete older rows.
- Manual ACK only on `PARSED & ack_at IS NULL`.

Enjoy the demo! 🏆
