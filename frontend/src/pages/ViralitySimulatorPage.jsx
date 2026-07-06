import { useEffect, useState } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from "recharts";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading } from "../components/Common";

const NETWORK_STRUCTURES = [
  "random", "small_world", "influencer_hub", "niche_cluster",
  "dense_local_community", "sparse_network", "multi_community",
];

const SLIDERS = [
  ["hook_strength", "Hook strength"], ["visual_quality", "Visual quality"],
  ["emotional_intensity", "Emotional intensity"], ["usefulness", "Usefulness"],
  ["novelty", "Novelty"], ["controversy", "Controversy"], ["clarity", "Clarity"],
  ["cta_strength", "CTA strength"], ["creator_trust", "Creator trust"],
];

export default function ViralitySimulatorPage() {
  const [form, setForm] = useState({
    name: "Test run", network_structure: "small_world", num_users: 300, num_ticks: 30,
    topic: "fitness", posting_hour: 18,
    hook_strength: 0.6, visual_quality: 0.6, emotional_intensity: 0.5, usefulness: 0.5,
    novelty: 0.5, controversy: 0.2, clarity: 0.6, cta_strength: 0.5, creator_trust: 0.6,
  });
  const [result, setResult] = useState(null);
  const [runs, setRuns] = useState([]);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  function loadRuns() {
    api.get("/simulation/runs").then(setRuns).catch(() => {});
  }
  useEffect(() => { loadRuns(); }, []);

  async function runSimulation(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const data = await api.post("/simulation/run", form);
      setResult(data);
      loadRuns();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Virality Simulator" description="A closed, synthetic network sandbox for strategy testing -- never touches real Instagram." />
      <div className="content-area">
        <form onSubmit={runSimulation} className="card" style={{ marginBottom: 16 }}>
          <div className="grid grid-3">
            <div className="field"><label>Run name</label><input value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} /></div>
            <div className="field">
              <label>Network structure</label>
              <select value={form.network_structure} onChange={(e) => setForm({ ...form, network_structure: e.target.value })}>
                {NETWORK_STRUCTURES.map((s) => <option key={s} value={s}>{s.replaceAll("_", " ")}</option>)}
              </select>
            </div>
            <div className="field"><label>Topic</label><input value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} /></div>
          </div>
          <div className="grid grid-3">
            <div className="field"><label>Simulated users</label><input type="number" min={50} max={5000} value={form.num_users} onChange={(e) => setForm({ ...form, num_users: Number(e.target.value) })} /></div>
            <div className="field"><label>Ticks (time steps)</label><input type="number" min={5} max={100} value={form.num_ticks} onChange={(e) => setForm({ ...form, num_ticks: Number(e.target.value) })} /></div>
            <div className="field"><label>Posting hour (0-23)</label><input type="number" min={0} max={23} value={form.posting_hour} onChange={(e) => setForm({ ...form, posting_hour: Number(e.target.value) })} /></div>
          </div>

          <h3 style={{ marginTop: 10 }}>Content attributes</h3>
          <div className="grid grid-3">
            {SLIDERS.map(([key, label]) => (
              <div className="field" key={key}>
                <label>{label}: {form[key]}</label>
                <input type="range" min={0} max={1} step={0.05} value={form[key]} onChange={(e) => setForm({ ...form, [key]: Number(e.target.value) })} />
              </div>
            ))}
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Simulating..." : "Run simulation"}</button>
        </form>

        <ErrorNotice error={error} />

        {result && (
          <>
            <div className="grid grid-4" style={{ marginBottom: 16 }}>
              <div className="card stat-card"><div className="stat-value">{result.final_reach}</div><div className="stat-label">Final reach</div></div>
              <div className="card stat-card"><div className="stat-value">{result.final_engagement.likes}</div><div className="stat-label">Likes</div></div>
              <div className="card stat-card"><div className="stat-value">{result.final_engagement.shares}</div><div className="stat-label">Shares</div></div>
              <div className="card stat-card"><div className="stat-value">{result.simulated_follower_conversion_estimate}</div><div className="stat-label">Est. follower conversion</div></div>
            </div>

            <div className="card">
              <h3>Reach over time</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={result.reach_curve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="tick" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="cumulative_reach" stroke="var(--color-primary)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="card" style={{ marginTop: 16 }}>
              <h3>Engagement over time</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={result.engagement_curve}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="tick" tick={{ fontSize: 11 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip /><Legend />
                  <Line type="monotone" dataKey="likes" stroke="var(--color-accent)" dot={false} />
                  <Line type="monotone" dataKey="comments" stroke="var(--color-amber)" dot={false} />
                  <Line type="monotone" dataKey="saves" stroke="var(--color-primary)" dot={false} />
                  <Line type="monotone" dataKey="shares" stroke="var(--color-danger)" dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-2" style={{ marginTop: 16 }}>
              <div className="card">
                <h3>Why content spread</h3>
                <ul className="suggestion-list">{result.why_content_spread.map((x, i) => <li key={i}>{x}</li>)}</ul>
              </div>
              <div className="card">
                <h3>Why content stalled</h3>
                {result.why_content_stalled.length === 0 ? <p style={{ color: "var(--color-muted)" }}>No major stall detected in this run.</p> :
                  <ul className="suggestion-list">{result.why_content_stalled.map((x, i) => <li key={i}>{x}</li>)}</ul>}
              </div>
            </div>

            <div className="alert alert-amber" style={{ marginTop: 16 }}>{result.disclaimer}</div>
          </>
        )}

        {!result && <Loading label="Run a simulation to see results here." />}

        {runs.length > 0 && (
          <div className="card" style={{ marginTop: 24 }}>
            <h3>Past runs</h3>
            <table>
              <thead><tr><th>Name</th><th>Network</th><th>Users</th><th>Run at</th></tr></thead>
              <tbody>
                {runs.map((r) => (
                  <tr key={r.id}><td>{r.name}</td><td>{r.network_structure}</td><td>{r.num_users}</td><td>{new Date(r.created_at).toLocaleString()}</td></tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </>
  );
}
