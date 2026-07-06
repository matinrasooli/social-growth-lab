import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

const CAPTION_STYLES = [
  "short", "founder_style", "educational", "storytelling", "premium_brand",
  "casual_human", "direct_sales", "soft_cta", "comment_bait_authentic", "community_building",
];

export default function CaptionLabPage() {
  const [form, setForm] = useState({ topic: "", niche: "", brand_voice: "" });
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
      const data = await api.post("/content/captions", { ...form, styles: selectedStyles.length > 0 ? selectedStyles : null });
      setResults(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Caption Lab" description="Generate caption variations. No spammy language, fake urgency, or exaggerated claims." />
      <div className="content-area">
        <form onSubmit={submit} className="card" style={{ marginBottom: 16 }}>
          <div className="grid grid-3">
            <div className="field">
              <label>Topic *</label>
              <input required type="text" value={form.topic} onChange={(e) => setForm({ ...form, topic: e.target.value })} />
            </div>
            <div className="field">
              <label>Niche</label>
              <input type="text" value={form.niche} onChange={(e) => setForm({ ...form, niche: e.target.value })} />
            </div>
            <div className="field">
              <label>Brand voice</label>
              <input type="text" value={form.brand_voice} onChange={(e) => setForm({ ...form, brand_voice: e.target.value })} placeholder="e.g. warm, direct, playful" />
            </div>
          </div>
          <div className="field">
            <label>Caption styles (leave blank for all)</label>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {CAPTION_STYLES.map((style) => (
                <button key={style} type="button" className={`btn ${selectedStyles.includes(style) ? "btn-accent" : "btn-outline"}`}
                        onClick={() => toggleStyle(style)} style={{ padding: "5px 10px", fontSize: 12 }}>
                  {style.replaceAll("_", " ")}
                </button>
              ))}
            </div>
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Generating..." : "Generate captions"}</button>
        </form>

        <ErrorNotice error={error} />

        {results && (
          <div className="grid grid-2">
            {results.map((c, i) => (
              <div className="card" key={i}>
                <span className="badge badge-green">{c.style.replaceAll("_", " ")}</span>
                <p style={{ marginTop: 8 }}>{c.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </>
  );
}
