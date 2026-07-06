import { useEffect, useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading, EmptyState } from "../components/Common";

const VARIABLES = [
  "hook_type", "caption_style", "thumbnail_style", "video_length", "opening_scene",
  "cta", "posting_time", "topic", "format", "music_choice", "talking_head_vs_broll", "text_overlay_style",
];

export default function ExperimentTrackerPage() {
  const [experiments, setExperiments] = useState(null);
  const [error, setError] = useState(null);
  const [form, setForm] = useState({ variable: VARIABLES[0], hypothesis: "", expected_metric_improvement: "" });
  const [resultForms, setResultForms] = useState({});
  const [busy, setBusy] = useState(false);

  function load() {
    api.get("/experiments").then(setExperiments).catch(setError);
  }

  useEffect(() => { load(); }, []);

  async function createExperiment(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.post("/experiments", form);
      setForm({ variable: VARIABLES[0], hypothesis: "", expected_metric_improvement: "" });
      load();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function submitResult(experimentId) {
    const r = resultForms[experimentId] || {};
    if (!r.actual_results || !r.winner_or_loser) return;
    try {
      await api.post("/experiments/results", {
        experiment_id: experimentId,
        actual_results: r.actual_results,
        winner_or_loser: r.winner_or_loser,
        lesson_learned: r.lesson_learned || "",
        next_recommended_test: r.next_recommended_test || "",
      });
      load();
    } catch (err) {
      setError(err);
    }
  }

  function updateResultForm(id, field, value) {
    setResultForms((prev) => ({ ...prev, [id]: { ...prev[id], [field]: value } }));
  }

  return (
    <>
      <TopBar title="Experiment Tracker" description="Track hypotheses, results, and lessons learned across your content tests." />
      <div className="content-area">
        <form onSubmit={createExperiment} className="card" style={{ marginBottom: 16, maxWidth: 600 }}>
          <div className="field">
            <label>Variable being tested</label>
            <select value={form.variable} onChange={(e) => setForm({ ...form, variable: e.target.value })}>
              {VARIABLES.map((v) => <option key={v} value={v}>{v.replaceAll("_", " ")}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Hypothesis *</label>
            <textarea required value={form.hypothesis} onChange={(e) => setForm({ ...form, hypothesis: e.target.value })} />
          </div>
          <div className="field">
            <label>Expected metric improvement *</label>
            <input required type="text" value={form.expected_metric_improvement} onChange={(e) => setForm({ ...form, expected_metric_improvement: e.target.value })} />
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Saving..." : "Create experiment"}</button>
        </form>

        <ErrorNotice error={error} />
        {!experiments && <Loading />}
        {experiments && experiments.length === 0 && <EmptyState>No experiments yet. Create one above.</EmptyState>}

        {experiments && experiments.map((exp) => (
          <div className="card" key={exp.id}>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <h3>{exp.variable.replaceAll("_", " ")}</h3>
              <span className={`badge ${exp.status === "complete" ? "badge-green" : "badge-muted"}`}>{exp.status}</span>
            </div>
            <p style={{ fontSize: 13 }}><strong>Hypothesis:</strong> {exp.hypothesis}</p>
            <p style={{ fontSize: 13 }}><strong>Expected improvement:</strong> {exp.expected_metric_improvement}</p>

            {exp.status !== "complete" && (
              <div style={{ marginTop: 10, borderTop: "1px solid var(--color-border)", paddingTop: 10 }}>
                <div className="grid grid-2">
                  <div className="field">
                    <label>Actual results</label>
                    <input type="text" onChange={(e) => updateResultForm(exp.id, "actual_results", e.target.value)} />
                  </div>
                  <div className="field">
                    <label>Winner or loser</label>
                    <select onChange={(e) => updateResultForm(exp.id, "winner_or_loser", e.target.value)} defaultValue="">
                      <option value="" disabled>Choose...</option>
                      <option value="winner">Winner</option>
                      <option value="loser">Loser</option>
                      <option value="inconclusive">Inconclusive</option>
                    </select>
                  </div>
                </div>
                <div className="field">
                  <label>Lesson learned</label>
                  <input type="text" onChange={(e) => updateResultForm(exp.id, "lesson_learned", e.target.value)} />
                </div>
                <div className="field">
                  <label>Next recommended test</label>
                  <input type="text" onChange={(e) => updateResultForm(exp.id, "next_recommended_test", e.target.value)} />
                </div>
                <button className="btn btn-outline" onClick={() => submitResult(exp.id)}>Log result</button>
              </div>
            )}
          </div>
        ))}
      </div>
    </>
  );
}
