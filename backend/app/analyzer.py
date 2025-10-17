from datetime import datetime, timedelta
from sqlalchemy import text
from . import logs_tailer

def detect_vessel_name_collision(db, name:str):
    q = text("""SELECT 1 FROM vessel_advice
                WHERE system_vessel_name=:name AND effective_end_datetime IS NULL""")
    row = db.execute(q, {"name": name}).first()
    return {"type":"VS.VESSEL_ERR_4"} if row else None

def detect_duplicate_container_snapshots(db, cntr_no:str):
    q = text("""SELECT COUNT(*) AS cnt FROM container WHERE cntr_no=:c""")
    cnt = db.execute(q, {"c": cntr_no}).scalar()
    return {"type":"CNTR.DUP_SNAPSHOT","cntr_no":cntr_no} if (cnt and cnt>1) else None

def detect_stuck_edi_ack(db, minutes:int=15):
    q = text("""
      SELECT edi_id, message_ref, sent_at
      FROM edi_message
      WHERE direction='IN' AND status='PARSED' AND ack_at IS NULL
        AND sent_at < (NOW() - INTERVAL :m MINUTE)
      ORDER BY sent_at ASC
    """)
    return [dict(r) for r in db.execute(q, {"m": minutes}).mappings()]

def detect_bayplan_inconsistency():
    return logs_tailer.detect_stow_conflicts()

def analyze_payload(db, payload: dict):
    out = {"signals":[]}
    if v := payload.get("system_vessel_name"):
        sig = detect_vessel_name_collision(db, v)
        if sig: out["signals"].append(sig)
    if c := payload.get("cntr_no"):
        sig = detect_duplicate_container_snapshots(db, c)
        if sig: out["signals"].append(sig)
    stuck = detect_stuck_edi_ack(db, 15)
    if stuck: out["stuck_edi"] = stuck
    bay = detect_bayplan_inconsistency()
    if bay: out.setdefault("signals", []).extend(bay)
    return out
