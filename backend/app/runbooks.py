from sqlalchemy import text

def expire_active_advice(db, advice_no:int):
    db.execute(text("""UPDATE berth_application
                       SET vessel_close_datetime=NOW()
                       WHERE vessel_advice_no=:n AND deleted='N' AND berthing_status='A'"""), {"n": advice_no})
    db.execute(text("""UPDATE berth_application SET deleted='A'
                       WHERE vessel_advice_no=:n AND deleted='N'"""), {"n": advice_no})
    db.execute(text("""UPDATE vessel_advice
                       SET effective_end_datetime=NOW()
                       WHERE vessel_advice_no=:n AND effective_end_datetime IS NULL"""), {"n": advice_no})

def prune_container_duplicates(db, cntr_no:str):
    db.execute(text("""
      DELETE t FROM container t
      JOIN (SELECT cntr_no, MAX(created_at) keep_ts
            FROM container WHERE cntr_no=:c) k
        ON t.cntr_no=k.cntr_no
      WHERE t.created_at < k.keep_ts
    """), {"c": cntr_no})

def manual_ack(db, edi_id:int):
    db.execute(text("""
      UPDATE edi_message
      SET ack_at=NOW(), status='ACKED'
      WHERE edi_id=:id AND direction='IN' AND status='PARSED' AND ack_at IS NULL
    """), {"id": edi_id})
