import { useState } from "react";
import EscalationComposer from "./components/EscalationComposer";

export default function App() {
  const [payload, setPayload] = useState({ system_vessel_name: "", cntr_no: "" });
  const [result, setResult] = useState<any>(null);

  async function analyze() {
    const res = await fetch("http://localhost:8000/incident/analyze", {
      method: "POST", headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const json = await res.json();
    setResult(json);
  }

  const moduleTag = result?.signals?.find((s:any)=>String(s.type||"").startsWith("VS.")) ? "VS"
                   : result?.signals?.find((s:any)=>String(s.type||"").startsWith("CNTR.")) ? "CNTR"
                   : (result?.stuck_edi?.length ? "EA" : "SRE");

  const incident = {
    id: "INC-DEMO-001",
    title: "Auto-triaged incident",
    summary: result ? "See signals for detected issues" : "No analysis yet",
    signals: result?.signals || [],
    actions: [],
    blast_radius: "TBD by enrichment",
    ask: "Approve recommended runbook step(s) or advise alternative."
  };

  return (
    <div className="p-6" style={{fontFamily: 'system-ui, sans-serif'}}>
      <h1 style={{fontWeight: 700, fontSize: 24}}>HarbourLight – L2 Ops Copilot</h1>
      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 12, maxWidth: 800}}>
        <input style={{border:'1px solid #ccc', padding:8, borderRadius:12}} placeholder="system_vessel_name"
          onChange={e=>setPayload(p=>({...p, system_vessel_name:e.target.value}))}/>
        <input style={{border:'1px solid #ccc', padding:8, borderRadius:12}} placeholder="cntr_no"
          onChange={e=>setPayload(p=>({...p, cntr_no:e.target.value}))}/>
      </div>
      <button style={{padding:'8px 12px', borderRadius:12, border:'1px solid #ccc', marginTop: 12}} onClick={analyze}>Analyze</button>

      <div style={{display:'grid', gridTemplateColumns:'1fr 1fr', gap: 16, marginTop: 16}}>
        <pre style={{background:'#f7f7f7', padding:12, borderRadius:12, maxHeight: 400, overflow:'auto'}}>{JSON.stringify(result, null, 2)}</pre>
        <EscalationComposer moduleTag={moduleTag} incident={incident} />
      </div>
    </div>
  );
}
