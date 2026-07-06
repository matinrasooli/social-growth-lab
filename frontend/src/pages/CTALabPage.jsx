import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

export default function CTALabPage() {
  const [form, setForm] = useState({ topic: "", content_type: "reel", funnel_stage: "", audience_intent: "" });
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setResults(null);
    setBusy(true);
    try {
      const data = await api.post("/content/ctas", form);
      setResults(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="CTA Lab" description="Generate calls-to-action matched to funnel stage, content type, and audience intent." />
      <div className="content-area">
        <form onSubmit={submit} className="card" style={{ marginBottom: 16, maxWidth: 560 }}>
          <div className="field">
            <label>Topic *</label>
            <input required type="text" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
          </div>
          <div className="grid grid-2">
            <div className="field">
              <label>Content type</label>
              <select value={form.content_type} onChange={(e) => setForm({ ...form, content_type: e.target.value })}>
                <option value="reel">Reel</option>
                <option value="story">Story</option>
                <option value="carousel">Carousel</option>
                <option value="static">Static post</option>
              </select>
            </div>
            <div className="field">
              <label>Funnel stage</label>
              <select value={form.funnel_stage} onChange={(e) => setForm({ ...form, funnel_stage: e.target.value })}>
                <option value="">Any</option>
                <option value="awareness">Awareness</option>
                <option value="consideration">Consideration</option>
                <option value="conversion">Conversion</option>
                <option value="retention">Retention</option>
              </select>
            </div>
          </div>
          <div className="field">
            <label>Audience intent</label>
            <input type="text" value={form.audience_intent} onChange={(e) => setForm({ ...form, audience_intent: e.target.value })} placeholder="e.g. curious but undecided" />
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Generating..." : "Generate CTAs"}</button>
        </form>

        <ErrorNotice error={error} />

        {results && (
          <table>
            <thead>
              <tr><th>CTA</th><th>Funnel stage</th><th>Content type</th><th>Audience intent</th></tr>
            </thead>
            <tbody>
              {results.map((c, i) => (
                <tr key={i}>
                  <td>{c.text}</td>
                  <td><span className="badge badge-muted">{c.funnel_stage}</span></td>
                  <td>{c.content_type}</td>
                  <td>{c.audience_intent || "--"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
