import { useEffect, useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading, EmptyState } from "../components/Common";

const KANBAN_STAGES = ["idea", "scripted", "recorded", "edited", "scheduled", "posted", "analyzed"];

export default function ContentCalendarPage() {
  const [form, setForm] = useState({
    niche: "", audience: "", business_goal: "", product: "", brand_voice: "",
    posting_frequency_per_week: 5, days: 30,
  });
  const [items, setItems] = useState([]);
  const [view, setView] = useState("table");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [loaded, setLoaded] = useState(false);

  function loadExisting() {
    api.get("/calendar").then((data) => { setItems(data); setLoaded(true); }).catch(setError);
  }

  useEffect(() => { loadExisting(); }, []);

  async function generate(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const payload = { ...form, posting_frequency_per_week: Number(form.posting_frequency_per_week), days: Number(form.days) };
      const data = await api.post("/calendar/generate", payload);
      setItems((prev) => [...prev, ...data]);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Content Calendar" description="Generate and track a multi-week content plan." />
      <div className="content-area">
        <form onSubmit={generate} className="card" style={{ marginBottom: 16 }}>
          <div className="grid grid-3">
            <div className="field"><label>Niche *</label><input required value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} /></div>
            <div className="field"><label>Audience *</label><input required value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} /></div>
            <div className="field"><label>Business goal *</label><input required value={form.business_goal} onChange={(e) => setForm({ ...form, business_goal: e.target.value })} /></div>
          </div>
          <div className="grid grid-3">
            <div className="field"><label>Product</label><input value={form.product} onChange={(e) => setForm({ ...form, product: e.target.value })} /></div>
            <div className="field"><label>Posts / week</label><input type="number" min={1} max={14} value={form.posting_frequency_per_week} onChange={(e) => setForm({ ...form, posting_frequency_per_week: e.target.value })} /></div>
            <div className="field"><label>Days to plan</label><input type="number" min={7} max={90} value={form.days} onChange={(e) => setForm({ ...form, days: e.target.value })} /></div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Generating..." : "Generate calendar"}</button>
        </form>

        <ErrorNotice error={error} />

        <div className="tabs">
          {["table", "month", "week", "kanban"].map((v) => (
            <button key={v} className={`tab-btn${view === v ? " active" : ""}`} onClick={() => setView(v)}>{v[0].toUpperCase() + v.slice(1)} view</button>
          ))}
        </div>

        {!loaded && <Loading />}
        {loaded && items.length === 0 && <EmptyState>No calendar items yet. Generate one above.</EmptyState>}

        {items.length > 0 && view === "table" && (
          <table>
            <thead><tr><th>Date</th><th>Type</th><th>Topic</th><th>Hook</th><th>CTA</th><th>Difficulty</th><th>Status</th></tr></thead>
            <tbody>
              {items.map((item, i) => (
                <tr key={i}>
                  <td>{item.date}</td>
                  <td><span className="badge badge-muted">{item.content_type}</span></td>
                  <td>{item.topic}</td>
                  <td style={{ maxWidth: 220 }}>{item.hook}</td>
                  <td>{item.cta}</td>
                  <td>{item.production_difficulty}</td>
                  <td>{item.status}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {items.length > 0 && (view === "month" || view === "week") && (
          <div className="grid grid-3">
            {items
              .slice(0, view === "week" ? 7 : items.length)
              .map((item, i) => (
                <div className="card" key={i}>
                  <span className="badge badge-green">{item.date}</span>
                  <h3 style={{ marginTop: 6 }}>{item.topic}</h3>
                  <p style={{ fontSize: 12, color: "var(--color-muted)" }}>{item.content_type} -- {item.production_difficulty} difficulty</p>
                  <p style={{ fontSize: 13 }}>{item.hook}</p>
                  <p style={{ fontSize: 12 }}><strong>CTA:</strong> {item.cta}</p>
                </div>
              ))}
          </div>
        )}

        {items.length > 0 && view === "kanban" && (
          <div className="kanban-board">
            {KANBAN_STAGES.map((stage) => (
              <div className="kanban-column" key={stage}>
                <h4>{stage}</h4>
                {items.filter((item) => (item.status || "idea") === stage).map((item, i) => (
                  <div className="kanban-card" key={i}>
                    <strong>{item.topic}</strong>
                    <div style={{ color: "var(--color-muted)" }}>{item.date} -- {item.content_type}</div>
                  </div>
                ))}
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
