import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

const HOOK_STYLES = [
  "curiosity", "pain_point", "contrarian", "proof", "personal_story", "before_and_after",
  "mistake", "list", "authority", "direct_benefit", "emotional", "educational",
];

export default function HookLabPage() {
  const [form, setForm] = useState({ niche: "", topic: "", audience: "" });
  const [selectedStyles, setSelectedStyles] = useState([]);
  const [results, setResults] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  function toggleStyle(style) {
    setSelectedStyles((prev) => (prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]));
  }

  async function submit(e) {
    e.preventDefault();
    setError(null);
    setResults(null);
    setBusy(true);
    try {
      const data = await api.post("/content/hooks", {
        ...form,
        styles: selectedStyles.length > 0 ? selectedStyles : null,
      });
      setResults(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Hook Lab" description="Generate and rate hooks across proven styles for your topic." />
      <div className="content-area">
        <form onSubmit={submit} className="card" style={{ marginBottom: 16 }}>
          <div className="grid grid-3">
            <div className="field">
              <label>Niche *</label>
              <input required type="text" value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} />
            </div>
            <div className="field">
              <label>Topic *</label>
              <input required type="text" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
            </div>
            <div className="field">
              <label>Audience</label>
              <input type="text" value={form.audience} onChange={(e) => setForm({ ...form, audience: e.target.value })} />
            </div>
          </div>
          <div className="field">
            <label>Hook styles (leave blank for all)</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {HOOK_STYLES.map((style) => (
                <button
                  key={style}
                  type="button"
                  className={`btn ${selectedStyles.includes(style) ? "btn-accent" : "btn-outline"}`}
                  onClick={() => toggleStyle(style)}
                  style={{ padding: "5px 10px", fontSize: 12 }}
                >
                  {style.replaceAll("_", " ")}
                </button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Generating..." : "Generate hooks"}</button>
        </form>

        <ErrorNotice error={error} />

        {results && (
          <div className="grid grid-2">
            {results.map((hook, i) => (
              <div className="card" key={i}>
                <span className="badge badge-green">{hook.style.replaceAll("_", " ")}</span>
                <h3 style={{ marginTop: 8 }}>{hook.text}</h3>
                <p style={{ fontSize: 12, color: "var(--color-muted)" }}>
                  Expected strength: {hook.expected_strength}/10
                </p>
                <p style={{ fontSize: 13 }}>{hook.rationale}</p>
                <p style={{ fontSize: 12 }}><strong>Visual opening:</strong> {hook.visual_opening}</p>
                <p style={{ fontSize: 12 }}><strong>Matching caption:</strong> {hook.matching_caption}</p>
                <p style={{ fontSize: 12 }}><strong>Matching CTA:</strong> {hook.matching_cta}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
