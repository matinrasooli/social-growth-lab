import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

const TONES = ["friendly", "concise", "professional", "founder_style", "playful", "support_focused", "sales_focused"];

export default function CommentHelperPage() {
  const [bulkText, setBulkText] = useState("");
  const [classifications, setClassifications] = useState(null);
  const [selectedComment, setSelectedComment] = useState("");
  const [selectedClassification, setSelectedClassification] = useState("");
  const [selectedTones, setSelectedTones] = useState(["friendly", "concise", "professional"]);
  const [drafts, setDrafts] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  async function classify(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const texts = bulkText.split("\n").map((t) => t.trim()).filter(Boolean);
      const data = await api.post("/comments/classify", { texts });
      setClassifications(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  function toggleTone(tone) {
    setSelectedTones((prev) => (prev.includes(tone) ? prev.filter((t) => t !== tone) : [...prev, tone]));
  }

  async function draftReply(e) {
    e.preventDefault();
    setError(null);
    setDrafts(null);
    setBusy(true);
    try {
      const data = await api.post("/comments/reply-draft", {
        comment_text: selectedComment, classification: selectedClassification || null, tones: selectedTones,
      });
      setDrafts(data);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Comment Helper" description="Paste comments to classify them, then draft replies -- draft only, never auto-sent." />
      <div className="content-area">
        <div className="grid grid-2" style={{ alignItems: "start" }}>
          <form onSubmit={classify} className="card">
            <h2>1. Classify comments</h2>
            <div className="field">
              <label>Paste one comment per line</label>
              <textarea rows={6} value={bulkText} onChange={(e) => setBulkText(e.target.value)} />
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Classifying..." : "Classify"}</button>

            {classifications && (
              <table style={{ marginTop: 14 }}>
                <thead><tr><th>Comment</th><th>Classification</th></tr></thead>
                <tbody>
                  {classifications.map((c, i) => (
                    <tr key={i} style={{ cursor: "pointer" }} onClick={() => { setSelectedComment(c.text); setSelectedClassification(c.classification); }}>
                      <td>{c.text}</td>
                      <td><span className="badge badge-muted">{c.classification}</span></td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </form>

          <form onSubmit={draftReply} className="card">
            <h2>2. Draft a reply</h2>
            <div className="field">
              <label>Comment</label>
              <textarea rows={3} value={selectedComment} onChange={(e) => setSelectedComment(e.target.value)} required />
            </div>
            <div className="field">
              <label>Classification (optional)</label>
              <input type="text" value={selectedClassification} onChange={(e) => setSelectedClassification(e.target.value)} />
            </div>
            <div className="field">
              <label>Tones</label>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
                {TONES.map((tone) => (
                  <button key={tone} type="button" className={`btn ${selectedTones.includes(tone) ? "btn-accent" : "btn-outline"}`}
                          onClick={() => toggleTone(tone)} style={{ padding: "5px 10px", fontSize: 12 }}>
                    {tone.replaceAll("_", " ")}
                  </button>
                ))}
              </div>
            </div>
            <button className="btn btn-primary" type="submit" disabled={busy || !selectedComment}>{busy ? "Drafting..." : "Draft replies"}</button>

            <ErrorNotice error={error} />

            {drafts && (
              <div style={{ marginTop: 14 }}>
                <div className="alert alert-amber">{drafts.note}</div>
                {drafts.drafts.map((d, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <span className="badge badge-muted">{d.tone.replaceAll("_", " ")}</span>
                    <p style={{ marginTop: 4 }}>{d.text}</p>
                  </div>
                ))}
              </div>
            )}
          </form>
        </div>
      </div>
    </>
  );
}
