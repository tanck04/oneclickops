import { useState } from "react";

type EscalationPayload = { to: string; subject: string; body: string; };

export default function EscalationComposer({ moduleTag, incident }:{ moduleTag:string; incident:any; }) {
  const [payload, setPayload] = useState<EscalationPayload | null>(null);

  async function compose() {
    const res = await fetch(`http://localhost:8000/escalations/compose?module=${moduleTag}`, {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(incident)
    });
    setPayload(await res.json());
  }

  return (
    <div style={{border:'1px solid #ddd', borderRadius: 12, padding: 12}}>
      <div style={{fontWeight:600}}>Escalation Composer</div>
      <button style={{padding:'6px 10px', border:'1px solid #ccc', borderRadius:10, marginTop: 8}} onClick={compose}>Compose</button>
      {payload && (
        <div style={{marginTop: 12}}>
          <div><b>To:</b> {payload.to}</div>
          <div><b>Subject:</b> {payload.subject}</div>
          <textarea style={{width:'100%', height:200, padding:8, borderRadius:10, border:'1px solid #ddd'}}
            defaultValue={payload.body} />
          <div style={{fontSize:12, color:'#555', marginTop:6}}>Demo mode: use your email client to send.</div>
        </div>
      )}
    </div>
  );
}
