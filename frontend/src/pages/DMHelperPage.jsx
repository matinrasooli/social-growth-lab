import { useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice } from "../components/Common";

const TONES = ["friendly", "concise", "professional", "founder_style", "playful", "support_focused", "sales_focused"];

export default function DMHelperPage() {
  const [dmText, setDmText] = useState("");
  const [classification, setClassification] = useState(null);
  const [selectedTones, setSelectedTones] = useState(["friendly", "professional"]);
  const [drafts, setDrafts] = useState(null);
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  function toggleTone(tone) {
    setSelectedTones((prev) => (prev.includes(tone) ? prev.filter((t) => t !== tone) : [...prev, tone]));
  }

  async function classifyAndDraft(e) {
    e.preventDefault();
    setError(null);
    setDrafts(null);
    setBusy(true);
    try {
      const classifyResult = await api.post("/comments/classify", { texts: [dmText] });
      const cls = classifyResult[0]?.classification;
      setClassification(cls);
      const draftResult = await api.post("/comments/reply-draft", { comment_text: dmText, classification: cls, tones: selectedTones });
      setDrafts(draftResult);
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="DM Helper" description="Paste a DM to classify it and draft a reply. Drafts only -- nothing is ever sent automatically." />
      <div className="content-area">
        <div className="alert alert-amber" style={{ maxWidth: 620 }}>
          This product never connects to Instagram DMs directly and never sends messages on your behalf.
          Paste a message you received, review the drafts, and send manually from the Instagram app.
        </div>

        <form onSubmit={classifyAndDraft} className="card" style={{ maxWidth: 620 }}>
          <div className="field">
            <label>DM text</label>
            <textarea rows={4} required value={dmText} onChange={(e) => setDmText(e.target.value)} />
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
          <button className="btn btn-primary" type="submit" disabled={busy}>{busy ? "Working..." : "Classify & draft replies"}</button>
        </form>

        <ErrorNotice error={error} />

        {classification && (
          <div className="card" style={{ maxWidth: 620, marginTop: 16 }}>
            <p>Classified as: <span className="badge badge-muted">{classification}</span></p>
            {drafts && (
              <>
                <div className="alert alert-amber">{drafts.note}</div>
                {drafts.drafts.map((d, i) => (
                  <div key={i} style={{ marginBottom: 10 }}>
                    <span className="badge badge-muted">{d.tone.replaceAll("_", " ")}</span>
                    <p style={{ marginTop: 4 }}>{d.text}</p>
                  </div>
                ))}
              </>
            )}
          </div>
        )}
      </div>
    </>
  );
}
