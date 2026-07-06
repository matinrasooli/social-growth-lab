import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

export default function UploadInsightsPage() {
  const [mode, setMode] = useState("file");
  const [file, setFile] = useState(null);
  const [pastedText, setPastedText] = useState("");
  const [manual, setManual] = useState({ post_date: "", content_type: "reel", topic: "", reach: "", likes: "", saves: "" });
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function submitFile(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    if (!file) return setError({ message: "Choose a CSV or JSON file first." });
    setBusy(true);
    try {
      const formData = new FormData();
      formData.append("file", file);
      const data = await api.postForm("/insights/import", formData);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function submitPastedText(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const formData = new FormData();
      formData.append("pasted_text", pastedText);
      const data = await api.postForm("/insights/import", formData);
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  async function submitManual(e) {
    e.preventDefault();
    setError(null);
    setResult(null);
    setBusy(true);
    try {
      const record = {
        ...manual,
        reach: manual.reach ? Number(manual.reach) : null,
        likes: manual.likes ? Number(manual.likes) : null,
        saves: manual.saves ? Number(manual.saves) : null,
        post_date: manual.post_date || null,
      };
      const data = await api.post("/insights/import-manual", { records: [record] });
      setResult(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Upload Insights" description="Manually import Instagram Insights exports. Nothing here scrapes or connects to Instagram automatically." />
      <div className="content-area">
        <div className="tabs">
          <button className={`tab-btn${mode === "file" ? " active" : ""}`} onClick={() => setMode("file")}>CSV / JSON file</button>
          <button className={`tab-btn${mode === "text" ? " active" : ""}`} onClick={() => setMode("text")}>Paste text</button>
          <button className={`tab-btn${mode === "manual" ? " active" : ""}`} onClick={() => setMode("manual")}>Manual entry</button>
        </div>

        <div className="card" style={{ maxWidth: 560 }}>
          <ErrorNotice error={error} />
          {result && <div className="alert alert-accent">Imported {result.imported} record(s).</div>}

          {mode === "file" && (
            <form onSubmit={submitFile}>
              <div className="field">
                <label>Instagram Insights export (.csv or .json)</label>
                <input type="file" accept=".csv,.json" onChange={(e) => setFile(e.target.files[0])} />
              </div>
              <p style={{ fontSize: 12, color: "var(--color-muted)" }}>
                A sample export is included at <code>/sample_data/instagram_insights_sample.csv</code>.
              </p>
              <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Importing..." : "Import file"}</button>
            </form>
          )}

          {mode === "text" && (
            <form onSubmit={submitPastedText}>
              <div className="field">
                <label>Paste a single post's insights</label>
                <textarea
                  value={pastedText}
                  onChange={(e) => setPastedText(e.target.value)}
                  placeholder={"Date: 2026-05-01\nContent type: reel\nReach: 12,400\nLikes: 800\nSaves: 210"}
                  rows={7}
                />
              </div>
              <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Importing..." : "Import text"}</button>
            </form>
          )}

          {mode === "manual" && (
            <form onSubmit={submitManual}>
              <div className="grid grid-2">
                <div className="field">
                  <label>Post date</label>
                  <input type="date" value={manual.post_date} onChange={(e) => setManual({ ...manual, post_date: e.target.value })} />
                </div>
                <div className="field">
                  <label>Content type</label>
                  <select value={manual.content_type} onChange={(e) => setManual({ ...manual, content_type: e.target.value })}>
                    <option value="reel">Reel</option>
                    <option value="story">Story</option>
                    <option value="carousel">Carousel</option>
                    <option value="static">Static post</option>
                  </select>
                </div>
              </div>
              <div className="field">
                <label>Topic</label>
                <input type="text" value={manual.topic} onChange={(e) => setManual({ ...manual, topic: e.target.value })} />
              </div>
              <div className="grid grid-3">
                <div className="field">
                  <label>Reach</label>
                  <input type="number" value={manual.reach} onChange={(e) => setManual({ ...manual, reach: e.target.value })} />
                </div>
                <div className="field">
                  <label>Likes</label>
                  <input type="number" value={manual.likes} onChange={(e) => setManual({ ...manual, likes: e.target.value })} />
                </div>
                <div className="field">
                  <label>Saves</label>
                  <input type="number" value={manual.saves} onChange={(e) => setManual({ ...manual, saves: e.target.value })} />
                </div>
              </div>
              <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Saving..." : "Save entry"}</button>
            </form>
          )}
        </div>
      </div>
    </>
  );
}
