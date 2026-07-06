import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

const SCORE_FIELDS = [
  ["hook_score", "Hook"], ["clarity_score", "Clarity"], ["novelty_score", "Novelty"],
  ["audience_fit_score", "Audience fit"], ["emotional_pull_score", "Emotional pull"],
  ["usefulness_score", "Usefulness"], ["shareability_score", "Shareability"],
  ["saveability_score", "Saveability"], ["trust_score", "Trust"], ["cta_score", "CTA"],
];

function riskColor(risk) {
  return risk === "high" ? "badge-red" : risk === "medium" ? "badge-amber" : "badge-green";
}

export default function ContentScorerPage() {
  const [form, setForm] = useState({
    content_type: "reel", niche: "", target_audience: "", business_goal: "",
    content_idea: "", hook: "", caption: "", cta: "", thumbnail_description: "",
  });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const data = await api.post("/content/score", form);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Content Scorer" description="Score a reel, story, carousel, or post idea before you produce it." />
      <div className="content-area">
        <div className="grid grid-2" style={{ alignItems: "start" }}>
          <form onSubmit={submit} className="card">
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
              <label htmlFor="content_idea">Content idea *</label>
              <textarea id="content_idea" required value={form.content_idea} onChange={(e) => setForm({ ...form, content_idea: e.target.value })} />
            </div>
            <div className="field">
              <label>Hook</label>
              <input type="text" value={form.hook} onChange={(e) => setForm({ ...form, hook: e.target.value })} />
            </div>
            <div className="field">
              <label>Caption</label>
              <textarea value={form.caption} onChange={(e) => setForm({ ...form, caption: e.target.value })} />
            </div>
            <div className="grid grid-2">
              <div className="field">
                <label>CTA</label>
                <input type="text" value={form.cta} onChange={(e) => setForm({ ...form, cta: e.target.value })} />
              </div>
              <div className="field">
                <label>Niche</label>
                <input type="text" value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} />
              </div>
            </div>
            <div className="grid grid-2">
              <div className="field">
                <label>Target audience</label>
                <input type="text" value={form.target_audience} onChange={(e) => setForm({ ...form, target_audience: e.target.value })} />
              </div>
              <div className="field">
                <label>Business goal</label>
                <input type="text" value={form.business_goal} onChange={(e) => setForm({ ...form, business_goal: e.target.value })} />
              </div>
            </div>
            <div className="field">
              <label>Thumbnail description</label>
              <input type="text" value={form.thumbnail_description} onChange={(e) => setForm({ ...form, thumbnail_description: e.target.value })} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Scoring..." : "Score this content"}</button>
          </form>

          <div>
            <ErrorNotice error={error} />
            {result && (
              <div className="card">
                <div style={{ display: "flex", alignItems: "baseline", gap: 10, marginBottom: 6 }}>
                  <div className="score-ring">{result.overall_score}/10</div>
                  <span className={`badge ${riskColor(result.retention_risk)}`}>{result.retention_risk} retention risk</span>
                  <span className="badge badge-muted">{result.method}</span>
                </div>
                <div className="grid grid-2" style={{ marginTop: 14 }}>
                  {SCORE_FIELDS.map(([key, label]) => (
                    <div key={key} style={{ fontSize: 13 }}>
                      <strong>{label}:</strong> {result[key]}/10
                    </div>
                  ))}
                </div>
                <h3 style={{ marginTop: 16 }}>Improvement suggestions</h3>
                <ul className="suggestion-list">
                  {result.improvement_suggestions.map((s, i) => <li key={i}>{s}</li>)}
                </ul>
              </div>
            )}
            {!result && !error && (
              <div className="empty-state">Fill in a content idea and score it to see results here.</div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
