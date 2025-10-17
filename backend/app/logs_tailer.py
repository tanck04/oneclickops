from pathlib import Path
import re
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

LOG_DIR = Path("/app/logs")

ts_re = re.compile(r"(?P<ts>\d{4}-\d{2}-\d{2}T[0-9:.]+Z)")
evt_re = re.compile(r"event_type=(?P<type>[A-Z]+)\s+cntr_no=(?P<cntr>[A-Z0-9]+)\s+correlation_id=(?P<corr>\S+)")
stow_re = re.compile(r'"stow":"(?P<stow>[\d\-]+)"')

def parse_api_events() -> List[Dict[str, Any]]:
    p = LOG_DIR / "api_event_service.log"
    if not p.exists():
        return []
    rows = []
    last_evt = None
    with open(p, "r", errors="ignore") as f:
        for line in f:
            m_ts = ts_re.search(line)
            m_evt = evt_re.search(line)
            if m_ts and m_evt:
                ts = datetime.fromisoformat(m_ts.group("ts").replace("Z","+00:00"))
                last_evt = {
                    "ts": ts, "type": m_evt.group("type"),
                    "cntr_no": m_evt.group("cntr"), "corr": m_evt.group("corr"),
                    "stow": None
                }
                rows.append(last_evt)
            else:
                m_stow = stow_re.search(line)
                if m_stow and last_evt is not None and last_evt.get("stow") is None:
                    last_evt["stow"] = m_stow.group("stow")
    return rows

def detect_stow_conflicts(window_minutes:int=30) -> List[Dict[str, Any]]:
    events = parse_api_events()
    if not events:
        return []
    from collections import defaultdict
    by_cntr = defaultdict(list)
    for e in events:
        if e.get("stow") and e.get("type") in ("LOAD", "STOW"):
            by_cntr[e["cntr_no"]].append(e)
    out = []
    window = timedelta(minutes=window_minutes)
    for cntr, lst in by_cntr.items():
        lst.sort(key=lambda x: x["ts"])
        for i in range(len(lst)):
            base = lst[i]
            stows = {base["stow"]}
            evid = [base]
            j = i + 1
            while j < len(lst) and (lst[j]["ts"] - base["ts"]) <= window:
                evid.append(lst[j])
                stows.add(lst[j]["stow"])
                j += 1
            if len(stows) > 1:
                uniq = {}
                for e in evid:
                    uniq.setdefault(e["stow"], e)
                stow_pairs = sorted([(k, v["ts"].isoformat(), v["corr"]) for k, v in uniq.items()])
                out.append({
                    "type": "VS.BAYPLAN_INCONSISTENCY",
                    "cntr_no": cntr,
                    "conflicting_stows": [s[0] for s in stow_pairs],
                    "evidence": [{"stow": s[0], "ts": s[1], "corr": s[2]} for s in stow_pairs],
                    "recommended_action": "Prefer latest eventTime; confirm with Vessel Ops; update bayplan; document rollback."
                })
                break
    return out
