from fastapi import FastAPI, Body
from .db import SessionLocal
from . import analyzer, runbooks, escalations

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="HarbourLight API")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.post("/incident/analyze")
def analyze(payload: dict = Body(...)):
    with SessionLocal() as db:
        return analyzer.analyze_payload(db, payload)

@app.post("/actions/expire-advice/{advice_no}")
def expire_advice(advice_no:int, dry_run: bool=True):
    if dry_run: return {"ok":True, "dry_run":True}
    with SessionLocal() as db:
        runbooks.expire_active_advice(db, advice_no); db.commit()
    return {"ok":True}

@app.post("/actions/prune-duplicates/{cntr_no}")
def prune_dupes(cntr_no:str, dry_run: bool=True):
    if dry_run: return {"ok":True, "dry_run":True}
    with SessionLocal() as db:
        runbooks.prune_container_duplicates(db, cntr_no); db.commit()
    return {"ok":True}

@app.post("/actions/manual-ack/{edi_id}")
def manual_ack(edi_id:int, dry_run: bool=True):
    if dry_run: return {"ok":True, "dry_run":True}
    with SessionLocal() as db:
        runbooks.manual_ack(db, edi_id); db.commit()
    return {"ok":True}

@app.post("/escalations/compose")
def compose_escalation(module: str, incident: dict = Body(...)):
    return escalations.compose(module, incident)
