import { useEffect, useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading } from "../components/Common";

export default function CompetitorNotesPage() {
  const [form, setForm] = useState({
    competitor_name: "", profile_reference: "", content_type: "reel", hook: "", topic: "",
    offer: "", visual_style: "", estimated_engagement: "", notes: "", why_it_worked: "",
  });
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  function loadSummary() {
    api.get("/competitors/summary").then(setSummary).catch(setError);
  }

  useEffect(() => { loadSummary(); }, []);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      await api.post("/competitors/notes", form);
      setForm({ ...form, hook: "", offer: "", notes: "", why_it_worked: "" });
      loadSummary();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Competitor Notes" description="Manually log what you observe from competitors -- never scraped." />
      <div className="content-area">
        <div className="grid grid-2" style={{ alignItems: "start" }}>
          <form onSubmit={submit} className="card">
            <h2>Add an observation</h2>
            <div className="field"><label>Competitor name *</label><input required value={form.competitor_name} onChange={(e) => setForm({ ...form, competitor_name: e.target.value })} /></div>
            <div className="field"><label>Profile reference (plain text, not a scrape)</label><input value={form.profile_reference} onChange={(e) => setForm({ ...form, profile_reference: e.target.value })} placeholder="e.g. instagram.com/example (manually noted)" /></div>
            <div className="grid grid-2">
              <div className="field"><label>Content type</label>
                <select value={form.content_type} onChange={(e) => setForm({ ...form, content_type: e.target.value })}>
                  <option value="reel">Reel</option><option value="story">Story</option>
                  <option value="carousel">Carousel</option><option value="static">Static post</option>
                </select>
              </div>
              <div className="field"><label>Topic</label><input value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} /></div>
            </div>
            <div className="field"><label>Hook</label><input value={form.hook} onChange={(e) => setForm({ ...form, hook: e.target.value })} /></div>
            <div className="field"><label>Offer</label><input value={form.offer} onChange={(e) => setForm({ ...form, offer: e.target.value })} /></div>
            <div className="field"><label>Visual style</label><input value={form.visual_style} onChange={(e) => setForm({ ...form, visual_style: e.target.value })} /></div>
            <div className="field"><label>Estimated engagement</label><input value={form.estimated_engagement} onChange={(e) => setForm({ ...form, estimated_engagement: e.target.value })} placeholder="your own visual estimate, e.g. 'high'" /></div>
            <div className="field"><label>Notes</label><textarea value={form.notes} onChange={(e) => setForm({ ...form, notes: e.target.value })} /></div>
            <div className="field"><label>Why it may have worked</label><textarea value={form.why_it_worked} onChange={(e) => setForm({ ...form, why_it_worked: e.target.value })} /></div>
            <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Saving..." : "Save observation"}</button>
          </form>

          <div>
            <ErrorNotice error={error} />
            {!summary && <Loading />}
            {summary && summary.message && <div className="empty-state">{summary.message}</div>}
            {summary && !summary.message && (
              <div className="card">
                <h2>Pattern analysis</h2>
                {["patterns", "gaps", "ideas_to_test", "positioning_opportunities", "differentiated_angles"].map((key) => (
                  <div key={key} style={{ marginBottom: 12 }}>
                    <h3>{key.replaceAll("_", " ")}</h3>
                    <ul className="suggestion-list">{(summary[key] || []).map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
