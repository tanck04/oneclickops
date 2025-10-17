MATRIX = {
    "CNTR": {"owner": "Mark Lee", "role": "Product Ops Manager", "email": "mark.lee@psa123.com"},
    "VS":   {"owner": "Jaden Smith", "role": "Vessel Operations",  "email": "jaden.smith@psa123.com"},
    "EA":   {"owner": "Tom Tan",     "role": "EDI/API Lead",       "email": "tom.tan@psa123.com"},
    "SRE":  {"owner": "Jacky Chan",  "role": "Infra/SRE",          "email": "jacky.chan@psa123.com"},
}

def route(module_tag:str):
    return MATRIX.get(module_tag, MATRIX["SRE"])

def compose(module_tag:str, incident:dict):
    target = route(module_tag)
    what = incident.get("summary") or incident.get("title") or "Operational incident"
    signals = incident.get("signals", [])
    actions = incident.get("actions", [])
    blast = incident.get("blast_radius", "Unknown")
    ask = incident.get("ask", "Please advise and approve the recommended step(s).")

    return {
        "to": f'{target["owner"]} <{target["email"]}>',
        "subject": f'[Escalation][{module_tag}] {what}',
        "body": (
            f"Hi {target['owner']},\n\n"
            f"**What happened**: {what}\n"
            f"**Evidence**: {signals}\n"
            f"**Impact / blast radius**: {blast}\n"
            f"**Actions tried / recommended**: {actions}\n\n"
            f"**Ask**: {ask}\n\n"
            f"Thanks,\nHarbourLight Bot"
        )
    }
