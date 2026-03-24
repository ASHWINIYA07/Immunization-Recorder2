import { useState, useEffect, useRef } from "react";

const VACCINES = [
  { id: 1, name: "BCG", age: "At Birth", dose: "1", disease: "Tuberculosis", status: false, dueDate: "2024-01-10" },
  { id: 2, name: "Hepatitis B", age: "At Birth", dose: "1st", disease: "Hepatitis B", status: false, dueDate: "2024-01-10" },
  { id: 3, name: "OPV", age: "6 Weeks", dose: "1st", disease: "Polio", status: false, dueDate: "2024-02-21" },
  { id: 4, name: "DTwP", age: "6 Weeks", dose: "1st", disease: "Diphtheria, Tetanus, Pertussis", status: true, dueDate: "2024-02-21" },
  { id: 5, name: "Hib", age: "6 Weeks", dose: "1st", disease: "Haemophilus Influenzae", status: true, dueDate: "2024-02-21" },
  { id: 6, name: "PCV", age: "6 Weeks", dose: "1st", disease: "Pneumococcal Disease", status: false, dueDate: "2024-02-21" },
  { id: 7, name: "Rotavirus", age: "6 Weeks", dose: "1st", disease: "Rotavirus Diarrhoea", status: false, dueDate: "2024-02-21" },
  { id: 8, name: "MMR", age: "9 Months", dose: "1st", disease: "Measles, Mumps, Rubella", status: false, dueDate: "2024-10-10" },
  { id: 9, name: "Varicella", age: "15 Months", dose: "1st", disease: "Chickenpox", status: false, dueDate: "2025-04-10" },
  { id: 10, name: "Typhoid", age: "2 Years", dose: "1st", disease: "Typhoid Fever", status: false, dueDate: "2026-01-10" },
];

const CLINICS = [
  { name: "Apollo Children's Hospital", address: "15, Shafee Mohammed Rd, Chennai", dist: "2.1 km", rating: 4.8, phone: "+91 44 4600 0000", open: true },
  { name: "Kanchi Kamakoti CHILDS Trust", address: "12A, Nageswara Rd, Nungambakkam", dist: "3.4 km", rating: 4.7, phone: "+91 44 2827 2727", open: true },
  { name: "MIOT International", address: "4/112, Mount Poonamallee Rd", dist: "5.8 km", rating: 4.6, phone: "+91 44 4200 2288", open: false },
  { name: "Sri Ramachandra Hospital", address: "No.1 Ramachandra Nagar, Porur", dist: "7.2 km", rating: 4.5, phone: "+91 44 4592 8600", open: true },
];

const FAQ_KB = {
  "side effect": "Common vaccine side effects include mild fever (37.5–38.5°C), soreness at injection site, and fussiness — these are normal immune responses lasting 1–3 days. Rare severe reactions like anaphylaxis occur in <1 in 1,000,000 doses. Always monitor for 15 minutes post-vaccination.",
  "fever": "A mild fever after vaccination (up to 38.5°C) is normal and indicates the immune system is responding. Use paracetamol (10–15 mg/kg) if uncomfortable. Seek medical help if fever exceeds 39°C or lasts >48 hours.",
  "dose gap": "Vaccine dose gaps are scientifically designed for optimal immunity. DTwP/IPV requires minimum 4-week intervals between primary doses. MMR 2nd dose needs 3–4 weeks after 1st. Never administer earlier — it reduces efficacy. Delayed doses are generally safe; restart is rarely needed.",
  "gap": "Vaccine dose gaps are scientifically designed for optimal immunity. DTwP/IPV requires minimum 4-week intervals between primary doses. MMR 2nd dose needs 3–4 weeks after 1st. Never administer earlier — it reduces efficacy. Delayed doses are generally safe; restart is rarely needed.",
  "miss": "If a vaccine dose is missed, do not restart the series. Simply continue from where you left off — this is called the 'catch-up' schedule. Consult your pediatrician for a personalized catch-up plan using the IAP schedule.",
  "safe": "All vaccines in the national immunization schedule undergo rigorous clinical trials and WHO/CDSCO approval. Serious adverse events are exceedingly rare. The risk of the disease is always far greater than the risk of the vaccine.",
  "mmr": "MMR (Measles, Mumps, Rubella) vaccine is given at 9 months and again at 15–18 months. It does NOT cause autism — this has been definitively disproven in multiple large studies involving millions of children.",
  "polio": "OPV (Oral Polio Vaccine) is given as drops at birth, 6, 10, 14 weeks, and 18 months. IPV (injectable) is added at 6 and 14 weeks. India has been polio-free since 2014.",
  "bcg": "BCG is given at birth and protects against severe forms of tuberculosis in children. A small bump/ulcer at the injection site is normal and expected — it heals in 6–12 weeks leaving a small scar.",
  "hepatitis": "Hepatitis B vaccine is given in 3 doses (birth, 6 weeks, 6 months). It provides lifelong protection against liver disease and liver cancer caused by Hepatitis B virus.",
  "schedule": "The IAP (Indian Academy of Pediatrics) 2023 schedule recommends vaccines at: Birth, 6 weeks, 10 weeks, 14 weeks, 6 months, 9 months, 12 months, 15 months, 18 months, 2 years, and 5 years.",
  "store": "Vaccines must be stored at 2–8°C (cold chain). Always verify the cold chain was maintained at your clinic. Vaccines exposed to heat or freezing must be discarded.",
  "covid": "COVID-19 vaccines for children 12+ (Corbevax, ZyCOV-D) are recommended. Consult your pediatrician for the appropriate vaccine based on your child's age.",
};

const SUGGESTIONS = [
  { icon: "📅", text: "Book appointment for OPV Dose 2", action: "book", urgent: true },
  { icon: "💉", text: "PCV Dose 1 is overdue by 3 days", action: "alert", urgent: true },
  { icon: "📋", text: "Download your vaccination certificate", action: "cert", urgent: false },
  { icon: "🔔", text: "Set reminder for Rotavirus Dose 2", action: "remind", urgent: false },
];

function generatePDFContent(vaccineData) {
  const completed = vaccineData.filter(v => v.status);
  const pending = vaccineData.filter(v => !v.status);
  return `
VACCINATION HEALTH LEDGER
Generated: ${new Date().toLocaleDateString("en-IN", { dateStyle: "long" })}
Child: Aryan Kumar | DOB: 10 Jan 2024 | ID: VCC-2024-00847

COMPLETED VACCINATIONS (${completed.length})
${"─".repeat(50)}
${completed.map(v => `✓ ${v.name.padEnd(15)} ${v.disease.padEnd(30)} ${v.age}`).join("\n")}

PENDING VACCINATIONS (${pending.length})
${"─".repeat(50)}
${pending.map(v => `○ ${v.name.padEnd(15)} ${v.disease.padEnd(30)} Due: ${v.dueDate}`).join("\n")}

Certified by VacciTrack Digital Health System
This is an auto-generated digital health record.
  `.trim();
}

export default function VacciTrackApp() {
  const [activeTab, setActiveTab] = useState("dashboard");
  const [vaccines, setVaccines] = useState(VACCINES);
  const [chatMessages, setChatMessages] = useState([
    { role: "bot", text: "👋 Hello! I'm VacciBot. Ask me anything about vaccines, side effects, dose schedules, or your child's immunization!" }
  ]);
  const [chatInput, setChatInput] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [locationLoading, setLocationLoading] = useState(false);
  const [locationGranted, setLocationGranted] = useState(false);
  const [certDownloaded, setCertDownloaded] = useState(false);
  const [toast, setToast] = useState(null);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatMessages, isTyping]);

  const showToast = (msg, type = "success") => {
    setToast({ msg, type });
    setTimeout(() => setToast(null), 3000);
  };

  const toggleVaccine = (id) => {
    setVaccines(prev => prev.map(v => {
      if (v.id === id) {
        const newStatus = !v.status;
        showToast(newStatus ? `✅ ${v.name} marked as completed!` : `↩️ ${v.name} marked as pending`);
        return { ...v, status: newStatus };
      }
      return v;
    }));
  };

  const handleChat = async () => {
    if (!chatInput.trim()) return;
    const userMsg = chatInput.trim();
    setChatInput("");
    setChatMessages(prev => [...prev, { role: "user", text: userMsg }]);
    setIsTyping(true);

    await new Promise(r => setTimeout(r, 800 + Math.random() * 600));

    const lower = userMsg.toLowerCase();
    let answer = null;
    for (const [key, val] of Object.entries(FAQ_KB)) {
      if (lower.includes(key)) { answer = val; break; }
    }

    if (!answer) {
      // Call Claude API
      try {
        const res = await fetch("https://api.anthropic.com/v1/messages", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            model: "claude-sonnet-4-20250514",
            max_tokens: 1000,
            system: "You are VacciBot, a friendly pediatric vaccination assistant for Indian parents. Answer questions about vaccines, immunization schedules (IAP 2023), side effects, and child health concisely in 2-4 sentences. Always recommend consulting a pediatrician for medical decisions. Use simple language parents can understand.",
            messages: [{ role: "user", content: userMsg }]
          })
        });
        const data = await res.json();
        answer = data.content?.[0]?.text || "I'm not sure about that. Please consult your pediatrician for accurate guidance.";
      } catch {
        answer = "I couldn't connect right now. For vaccine questions, please consult your pediatrician or call the national immunization helpline: 1800-180-1104.";
      }
    }

    setIsTyping(false);
    setChatMessages(prev => [...prev, { role: "bot", text: answer }]);
  };

  const getLocation = () => {
    setLocationLoading(true);
    setTimeout(() => {
      setLocationLoading(false);
      setLocationGranted(true);
    }, 1800);
  };

  const downloadCert = () => {
    const content = generatePDFContent(vaccines);
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "Vaccination_Certificate_Aryan_Kumar.txt";
    a.click();
    URL.revokeObjectURL(url);
    setCertDownloaded(true);
    showToast("📄 Health Ledger downloaded successfully!");
  };

  const completed = vaccines.filter(v => v.status).length;
  const progress = Math.round((completed / vaccines.length) * 100);

  const tabs = [
    { id: "dashboard", label: "Dashboard", icon: "🏠" },
    { id: "checkoff", label: "Check-Off", icon: "✅" },
    { id: "bot", label: "VacciBot", icon: "🤖" },
    { id: "clinics", label: "Clinics", icon: "📍" },
    { id: "ledger", label: "Ledger", icon: "📋" },
  ];

  return (
    <div style={{
      fontFamily: "'Nunito', 'Segoe UI', sans-serif",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
      minHeight: "100vh",
      color: "#e2e8f0",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Background blobs */}
      <div style={{ position: "fixed", top: -100, right: -100, width: 400, height: 400, borderRadius: "50%", background: "radial-gradient(circle, rgba(56,189,248,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />
      <div style={{ position: "fixed", bottom: -100, left: -100, width: 350, height: 350, borderRadius: "50%", background: "radial-gradient(circle, rgba(167,139,250,0.08) 0%, transparent 70%)", pointerEvents: "none" }} />

      {/* Toast */}
      {toast && (
        <div style={{
          position: "fixed", top: 20, right: 20, zIndex: 1000,
          background: toast.type === "success" ? "linear-gradient(135deg,#059669,#10b981)" : "#ef4444",
          color: "#fff", padding: "12px 20px", borderRadius: 12,
          fontSize: 14, fontWeight: 600, boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
          animation: "slideIn 0.3s ease"
        }}>
          {toast.msg}
        </div>
      )}

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Space+Mono:wght@400;700&display=swap');
        * { box-sizing: border-box; margin: 0; padding: 0; }
        ::-webkit-scrollbar { width: 4px; } ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        @keyframes slideIn { from { transform: translateX(100px); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.5; } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes bounce { 0%,80%,100% { transform:scale(0); } 40% { transform:scale(1); } }
        .tab-btn { transition: all 0.2s ease; }
        .tab-btn:hover { opacity: 0.85; }
        .vaccine-row { transition: all 0.2s ease; }
        .vaccine-row:hover { background: rgba(255,255,255,0.05) !important; }
        .toggle { cursor: pointer; transition: all 0.25s ease; }
        .card { backdrop-filter: blur(12px); }
        .chat-bubble { animation: fadeUp 0.3s ease; }
        @keyframes fadeUp { from { opacity:0; transform:translateY(8px); } to { opacity:1; transform:translateY(0); } }
        .clinic-card { transition: all 0.2s ease; }
        .clinic-card:hover { transform: translateY(-2px); }
      `}</style>

      {/* Header */}
      <div style={{
        background: "rgba(15,23,42,0.9)", backdropFilter: "blur(20px)",
        borderBottom: "1px solid rgba(148,163,184,0.1)",
        padding: "16px 20px", display: "flex", alignItems: "center", justifyContent: "space-between",
        position: "sticky", top: 0, zIndex: 100
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 12,
            background: "linear-gradient(135deg, #38bdf8, #818cf8)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontSize: 20, fontWeight: 900, boxShadow: "0 4px 15px rgba(56,189,248,0.3)"
          }}>💉</div>
          <div>
            <div style={{ fontWeight: 900, fontSize: 18, letterSpacing: "-0.5px", background: "linear-gradient(135deg, #38bdf8, #818cf8)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent" }}>VacciTrack</div>
            <div style={{ fontSize: 11, color: "#64748b", fontWeight: 600 }}>Smart Immunization System</div>
          </div>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <div style={{ width: 8, height: 8, borderRadius: "50%", background: "#10b981", animation: "pulse 2s infinite" }} />
          <span style={{ fontSize: 12, color: "#10b981", fontWeight: 700 }}>LIVE</span>
        </div>
      </div>

      {/* Tab Nav */}
      <div style={{
        display: "flex", background: "rgba(15,23,42,0.8)", backdropFilter: "blur(10px)",
        borderBottom: "1px solid rgba(148,163,184,0.08)", padding: "0 8px",
        overflowX: "auto", position: "sticky", top: 73, zIndex: 99
      }}>
        {tabs.map(t => (
          <button key={t.id} className="tab-btn" onClick={() => setActiveTab(t.id)} style={{
            flex: "0 0 auto", padding: "12px 16px", border: "none", cursor: "pointer",
            background: "transparent", color: activeTab === t.id ? "#38bdf8" : "#64748b",
            fontWeight: activeTab === t.id ? 800 : 600, fontSize: 13,
            borderBottom: activeTab === t.id ? "2px solid #38bdf8" : "2px solid transparent",
            display: "flex", alignItems: "center", gap: 6, whiteSpace: "nowrap",
            transition: "all 0.2s ease"
          }}>
            <span>{t.icon}</span>{t.label}
          </button>
        ))}
      </div>

      <div style={{ padding: "20px 16px", maxWidth: 680, margin: "0 auto", paddingBottom: 40 }}>

        {/* DASHBOARD */}
        {activeTab === "dashboard" && (
          <div>
            {/* Child card */}
            <div className="card" style={{
              background: "linear-gradient(135deg, rgba(56,189,248,0.15), rgba(129,140,248,0.15))",
              border: "1px solid rgba(56,189,248,0.2)", borderRadius: 20, padding: 20, marginBottom: 16
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                <div style={{
                  width: 60, height: 60, borderRadius: 18,
                  background: "linear-gradient(135deg, #38bdf8, #818cf8)",
                  display: "flex", alignItems: "center", justifyContent: "center", fontSize: 28
                }}>👶</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 900, fontSize: 20, marginBottom: 2 }}>Aryan Kumar</div>
                  <div style={{ color: "#94a3b8", fontSize: 13 }}>DOB: 10 Jan 2024 · Age: 14 months</div>
                  <div style={{ color: "#94a3b8", fontSize: 12, fontFamily: "'Space Mono', monospace", marginTop: 2 }}>ID: VCC-2024-00847</div>
                </div>
              </div>
              <div style={{ marginTop: 16 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
                  <span style={{ fontSize: 13, color: "#94a3b8", fontWeight: 600 }}>Immunization Progress</span>
                  <span style={{ fontSize: 13, fontWeight: 800, color: "#38bdf8" }}>{completed}/{vaccines.length} doses</span>
                </div>
                <div style={{ height: 8, background: "rgba(255,255,255,0.1)", borderRadius: 8, overflow: "hidden" }}>
                  <div style={{
                    height: "100%", width: `${progress}%`, borderRadius: 8,
                    background: "linear-gradient(90deg, #38bdf8, #818cf8)",
                    transition: "width 0.6s ease", boxShadow: "0 0 10px rgba(56,189,248,0.4)"
                  }} />
                </div>
                <div style={{ fontSize: 12, color: "#10b981", fontWeight: 700, marginTop: 6 }}>{progress}% Complete</div>
              </div>
            </div>

            {/* Smart Suggestions */}
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 14, fontWeight: 800, color: "#94a3b8", marginBottom: 12, letterSpacing: "0.05em", textTransform: "uppercase" }}>💡 Smart Suggestions</div>
              {SUGGESTIONS.map((s, i) => (
                <div key={i} className="card" style={{
                  background: s.urgent ? "rgba(239,68,68,0.08)" : "rgba(255,255,255,0.04)",
                  border: `1px solid ${s.urgent ? "rgba(239,68,68,0.25)" : "rgba(148,163,184,0.1)"}`,
                  borderRadius: 14, padding: "12px 16px", marginBottom: 10,
                  display: "flex", alignItems: "center", justifyContent: "space-between", cursor: "pointer"
                }} onClick={() => {
                  if (s.action === "cert") { setActiveTab("ledger"); }
                  else if (s.action === "book") { setActiveTab("clinics"); }
                  else if (s.action === "alert") { setActiveTab("checkoff"); }
                  else showToast("⏰ Reminder set for Rotavirus Dose 2!");
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: 20 }}>{s.icon}</span>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 700, color: s.urgent ? "#fca5a5" : "#e2e8f0" }}>{s.text}</div>
                      {s.urgent && <div style={{ fontSize: 11, color: "#ef4444", fontWeight: 600, marginTop: 2 }}>⚠️ Requires attention</div>}
                    </div>
                  </div>
                  <span style={{ color: "#64748b", fontSize: 18 }}>›</span>
                </div>
              ))}
            </div>

            {/* Quick Stats */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 12 }}>
              {[
                { label: "Completed", value: completed, color: "#10b981", icon: "✅" },
                { label: "Pending", value: vaccines.length - completed, color: "#f59e0b", icon: "⏳" },
                { label: "Overdue", value: 2, color: "#ef4444", icon: "🚨" }
              ].map((s, i) => (
                <div key={i} className="card" style={{
                  background: "rgba(255,255,255,0.04)", border: "1px solid rgba(148,163,184,0.1)",
                  borderRadius: 16, padding: 16, textAlign: "center"
                }}>
                  <div style={{ fontSize: 24, marginBottom: 4 }}>{s.icon}</div>
                  <div style={{ fontSize: 24, fontWeight: 900, color: s.color }}>{s.value}</div>
                  <div style={{ fontSize: 11, color: "#64748b", fontWeight: 600, marginTop: 2 }}>{s.label}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* CHECK-OFF */}
        {activeTab === "checkoff" && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 22, fontWeight: 900, marginBottom: 4 }}>Vaccination Check-Off ✅</div>
              <div style={{ color: "#64748b", fontSize: 14 }}>Tap the toggle to self-report completed vaccinations</div>
            </div>
            {["At Birth", "6 Weeks", "9 Months", "15 Months", "2 Years"].map(ageGroup => {
              const groupVaccines = vaccines.filter(v => v.age === ageGroup);
              if (!groupVaccines.length) return null;
              return (
                <div key={ageGroup} style={{ marginBottom: 20 }}>
                  <div style={{
                    fontSize: 12, fontWeight: 800, color: "#38bdf8", letterSpacing: "0.08em",
                    textTransform: "uppercase", marginBottom: 10, display: "flex", alignItems: "center", gap: 8
                  }}>
                    <div style={{ flex: 1, height: 1, background: "rgba(56,189,248,0.2)" }} />
                    {ageGroup}
                    <div style={{ flex: 1, height: 1, background: "rgba(56,189,248,0.2)" }} />
                  </div>
                  {groupVaccines.map(v => (
                    <div key={v.id} className="vaccine-row card" style={{
                      background: v.status ? "rgba(16,185,129,0.08)" : "rgba(255,255,255,0.04)",
                      border: `1px solid ${v.status ? "rgba(16,185,129,0.25)" : "rgba(148,163,184,0.1)"}`,
                      borderRadius: 14, padding: "14px 16px", marginBottom: 8,
                      display: "flex", alignItems: "center", justifyContent: "space-between"
                    }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
                          <span style={{ fontWeight: 800, fontSize: 15, color: v.status ? "#10b981" : "#e2e8f0" }}>{v.name}</span>
                          <span style={{
                            fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 6,
                            background: v.status ? "rgba(16,185,129,0.2)" : "rgba(245,158,11,0.15)",
                            color: v.status ? "#10b981" : "#f59e0b"
                          }}>Dose {v.dose}</span>
                        </div>
                        <div style={{ fontSize: 12, color: "#64748b" }}>{v.disease}</div>
                        <div style={{ fontSize: 11, color: "#475569", marginTop: 2, fontFamily: "'Space Mono', monospace" }}>
                          Due: {v.dueDate}
                        </div>
                      </div>
                      <div className="toggle" onClick={() => toggleVaccine(v.id)} style={{
                        width: 52, height: 28, borderRadius: 14,
                        background: v.status ? "linear-gradient(135deg, #10b981, #059669)" : "rgba(100,116,139,0.4)",
                        position: "relative", transition: "all 0.3s ease",
                        boxShadow: v.status ? "0 0 12px rgba(16,185,129,0.4)" : "none"
                      }}>
                        <div style={{
                          position: "absolute", top: 3, left: v.status ? 26 : 3,
                          width: 22, height: 22, borderRadius: "50%", background: "#fff",
                          transition: "left 0.3s ease", boxShadow: "0 2px 6px rgba(0,0,0,0.3)"
                        }} />
                      </div>
                    </div>
                  ))}
                </div>
              );
            })}
          </div>
        )}

        {/* VACCIBOT */}
        {activeTab === "bot" && (
          <div>
            <div style={{ marginBottom: 16 }}>
              <div style={{ fontSize: 22, fontWeight: 900, marginBottom: 4 }}>🤖 VacciBot AI</div>
              <div style={{ color: "#64748b", fontSize: 14 }}>RAG-powered FAQ assistant for vaccine guidance</div>
            </div>

            {/* Quick chips */}
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: 16 }}>
              {["Side effects?", "Dose gap rules", "Missed vaccine?", "MMR safety", "IAP Schedule"].map(q => (
                <button key={q} onClick={() => { setChatInput(q); }} style={{
                  padding: "6px 12px", borderRadius: 20, border: "1px solid rgba(56,189,248,0.3)",
                  background: "rgba(56,189,248,0.08)", color: "#38bdf8", fontSize: 12,
                  fontWeight: 700, cursor: "pointer"
                }}>{q}</button>
              ))}
            </div>

            {/* Chat area */}
            <div style={{
              background: "rgba(255,255,255,0.03)", border: "1px solid rgba(148,163,184,0.1)",
              borderRadius: 20, padding: 16, height: 380, overflowY: "auto", marginBottom: 12
            }}>
              {chatMessages.map((msg, i) => (
                <div key={i} className="chat-bubble" style={{
                  display: "flex", justifyContent: msg.role === "user" ? "flex-end" : "flex-start",
                  marginBottom: 12
                }}>
                  {msg.role === "bot" && (
                    <div style={{
                      width: 32, height: 32, borderRadius: 10, background: "linear-gradient(135deg,#38bdf8,#818cf8)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      fontSize: 16, marginRight: 8, flexShrink: 0, alignSelf: "flex-end"
                    }}>🤖</div>
                  )}
                  <div style={{
                    maxWidth: "75%", padding: "10px 14px", borderRadius: msg.role === "user" ? "18px 18px 4px 18px" : "18px 18px 18px 4px",
                    background: msg.role === "user"
                      ? "linear-gradient(135deg, #38bdf8, #818cf8)"
                      : "rgba(255,255,255,0.07)",
                    color: "#e2e8f0", fontSize: 13, lineHeight: 1.6, fontWeight: 500
                  }}>{msg.text}</div>
                </div>
              ))}
              {isTyping && (
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 10, background: "linear-gradient(135deg,#38bdf8,#818cf8)",
                    display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16
                  }}>🤖</div>
                  <div style={{ background: "rgba(255,255,255,0.07)", padding: "12px 16px", borderRadius: "18px 18px 18px 4px", display: "flex", gap: 4 }}>
                    {[0, 1, 2].map(i => (
                      <div key={i} style={{
                        width: 6, height: 6, borderRadius: "50%", background: "#38bdf8",
                        animation: `bounce 1.4s ${i * 0.2}s infinite`
                      }} />
                    ))}
                  </div>
                </div>
              )}
              <div ref={chatEndRef} />
            </div>

            <div style={{ display: "flex", gap: 8 }}>
              <input
                value={chatInput}
                onChange={e => setChatInput(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleChat()}
                placeholder="Ask about vaccines, side effects, schedules..."
                style={{
                  flex: 1, padding: "12px 16px", borderRadius: 14,
                  background: "rgba(255,255,255,0.07)", border: "1px solid rgba(148,163,184,0.2)",
                  color: "#e2e8f0", fontSize: 13, outline: "none"
                }}
              />
              <button onClick={handleChat} style={{
                padding: "12px 18px", borderRadius: 14,
                background: "linear-gradient(135deg, #38bdf8, #818cf8)",
                border: "none", color: "#fff", fontSize: 18, cursor: "pointer",
                fontWeight: 700, boxShadow: "0 4px 15px rgba(56,189,248,0.3)"
              }}>↑</button>
            </div>
          </div>
        )}

        {/* CLINICS */}
        {activeTab === "clinics" && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 22, fontWeight: 900, marginBottom: 4 }}>📍 Nearby Clinics</div>
              <div style={{ color: "#64748b", fontSize: 14 }}>GPS-based hospital & vaccine center finder</div>
            </div>

            {!locationGranted ? (
              <div className="card" style={{
                background: "rgba(56,189,248,0.08)", border: "1px solid rgba(56,189,248,0.2)",
                borderRadius: 20, padding: 32, textAlign: "center"
              }}>
                <div style={{ fontSize: 56, marginBottom: 16 }}>📍</div>
                <div style={{ fontWeight: 800, fontSize: 18, marginBottom: 8 }}>Enable Location Access</div>
                <div style={{ color: "#64748b", fontSize: 14, marginBottom: 24, lineHeight: 1.6 }}>
                  Allow VacciTrack to find nearby vaccination clinics, hospitals, and immunization centers based on your GPS location.
                </div>
                <button onClick={getLocation} style={{
                  padding: "14px 32px", borderRadius: 14,
                  background: "linear-gradient(135deg, #38bdf8, #818cf8)",
                  border: "none", color: "#fff", fontSize: 15, fontWeight: 800,
                  cursor: locationLoading ? "wait" : "pointer",
                  display: "flex", alignItems: "center", gap: 8, margin: "0 auto",
                  boxShadow: "0 4px 20px rgba(56,189,248,0.3)"
                }}>
                  {locationLoading ? (
                    <>
                      <div style={{ width: 18, height: 18, border: "3px solid rgba(255,255,255,0.3)", borderTop: "3px solid #fff", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                      Locating...
                    </>
                  ) : "📍 Find Clinics Near Me"}
                </button>
              </div>
            ) : (
              <div>
                <div className="card" style={{
                  background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.2)",
                  borderRadius: 14, padding: "10px 14px", marginBottom: 16, fontSize: 13,
                  color: "#10b981", fontWeight: 600, display: "flex", alignItems: "center", gap: 8
                }}>
                  <span>📍</span> Located: Salem, Tamil Nadu · Showing 4 nearby centers
                </div>
                {CLINICS.map((c, i) => (
                  <div key={i} className="clinic-card card" style={{
                    background: "rgba(255,255,255,0.04)", border: "1px solid rgba(148,163,184,0.1)",
                    borderRadius: 18, padding: 16, marginBottom: 12, cursor: "pointer"
                  }} onClick={() => showToast(`📞 Calling ${c.name}...`)}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 8 }}>
                      <div>
                        <div style={{ fontWeight: 800, fontSize: 15, marginBottom: 4 }}>{c.name}</div>
                        <div style={{ fontSize: 12, color: "#64748b" }}>{c.address}</div>
                      </div>
                      <div style={{
                        padding: "4px 10px", borderRadius: 20, fontSize: 11, fontWeight: 700,
                        background: c.open ? "rgba(16,185,129,0.15)" : "rgba(239,68,68,0.15)",
                        color: c.open ? "#10b981" : "#ef4444"
                      }}>{c.open ? "Open" : "Closed"}</div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 13 }}>
                        <span style={{ color: "#f59e0b" }}>★</span>
                        <span style={{ fontWeight: 700 }}>{c.rating}</span>
                      </div>
                      <div style={{ fontSize: 13, color: "#38bdf8", fontWeight: 700 }}>📏 {c.dist}</div>
                      <div style={{ fontSize: 13, color: "#94a3b8" }}>📞 {c.phone}</div>
                    </div>
                    <div style={{ marginTop: 12, display: "flex", gap: 8 }}>
                      <button onClick={e => { e.stopPropagation(); showToast("🗺️ Opening maps..."); }} style={{
                        flex: 1, padding: "8px", borderRadius: 10, border: "1px solid rgba(56,189,248,0.3)",
                        background: "transparent", color: "#38bdf8", fontSize: 12, fontWeight: 700, cursor: "pointer"
                      }}>🗺️ Directions</button>
                      <button onClick={e => { e.stopPropagation(); showToast(`📅 Booking at ${c.name}...`); }} style={{
                        flex: 1, padding: "8px", borderRadius: 10,
                        background: "linear-gradient(135deg, #38bdf8, #818cf8)",
                        border: "none", color: "#fff", fontSize: 12, fontWeight: 700, cursor: "pointer"
                      }}>📅 Book Appointment</button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* LEDGER */}
        {activeTab === "ledger" && (
          <div>
            <div style={{ marginBottom: 20 }}>
              <div style={{ fontSize: 22, fontWeight: 900, marginBottom: 4 }}>📋 Digital Health Ledger</div>
              <div style={{ color: "#64748b", fontSize: 14 }}>Official vaccination certificate & records</div>
            </div>

            {/* Certificate card */}
            <div className="card" style={{
              background: "linear-gradient(135deg, rgba(56,189,248,0.1), rgba(129,140,248,0.1))",
              border: "1px solid rgba(56,189,248,0.25)", borderRadius: 20, padding: 24, marginBottom: 16,
              position: "relative", overflow: "hidden"
            }}>
              <div style={{ position: "absolute", top: -20, right: -20, width: 120, height: 120, borderRadius: "50%", background: "rgba(56,189,248,0.05)" }} />
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 16 }}>
                <div style={{ fontSize: 40 }}>🏅</div>
                <div>
                  <div style={{ fontWeight: 900, fontSize: 16 }}>Vaccination Certificate</div>
                  <div style={{ color: "#64748b", fontSize: 12, fontFamily: "'Space Mono', monospace" }}>VCC-2024-00847 · {new Date().toLocaleDateString("en-IN")}</div>
                </div>
              </div>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                {[
                  { label: "Child Name", value: "Aryan Kumar" },
                  { label: "Date of Birth", value: "10 Jan 2024" },
                  { label: "Guardian", value: "Rajesh Kumar" },
                  { label: "Completion", value: `${progress}%` },
                ].map((f, i) => (
                  <div key={i} style={{ background: "rgba(255,255,255,0.05)", borderRadius: 10, padding: 12 }}>
                    <div style={{ fontSize: 10, color: "#64748b", fontWeight: 700, textTransform: "uppercase", marginBottom: 4 }}>{f.label}</div>
                    <div style={{ fontWeight: 800, fontSize: 14 }}>{f.value}</div>
                  </div>
                ))}
              </div>
              <button onClick={downloadCert} style={{
                width: "100%", padding: "14px", borderRadius: 14,
                background: certDownloaded ? "linear-gradient(135deg,#10b981,#059669)" : "linear-gradient(135deg, #38bdf8, #818cf8)",
                border: "none", color: "#fff", fontSize: 15, fontWeight: 800,
                cursor: "pointer", boxShadow: "0 4px 20px rgba(56,189,248,0.3)",
                display: "flex", alignItems: "center", justifyContent: "center", gap: 8
              }}>
                {certDownloaded ? "✅ Downloaded!" : "⬇️ Download Health Certificate (PDF)"}
              </button>
            </div>

            {/* Full record table */}
            <div style={{ fontWeight: 800, fontSize: 14, color: "#94a3b8", marginBottom: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Complete Immunization Record</div>
            {vaccines.map((v, i) => (
              <div key={i} className="card" style={{
                background: "rgba(255,255,255,0.03)", border: "1px solid rgba(148,163,184,0.08)",
                borderRadius: 12, padding: "12px 14px", marginBottom: 8,
                display: "flex", alignItems: "center", gap: 12
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 10, flexShrink: 0,
                  background: v.status ? "rgba(16,185,129,0.2)" : "rgba(100,116,139,0.2)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 16
                }}>{v.status ? "✅" : "⏳"}</div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: 13, display: "flex", alignItems: "center", gap: 6 }}>
                    {v.name}
                    <span style={{ fontSize: 10, color: "#64748b", fontWeight: 600 }}>· {v.age}</span>
                  </div>
                  <div style={{ fontSize: 11, color: "#64748b", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{v.disease}</div>
                </div>
                <div style={{
                  fontSize: 11, fontWeight: 700, padding: "3px 8px", borderRadius: 8, flexShrink: 0,
                  background: v.status ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)",
                  color: v.status ? "#10b981" : "#f59e0b"
                }}>{v.status ? "Done" : "Pending"}</div>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
}
