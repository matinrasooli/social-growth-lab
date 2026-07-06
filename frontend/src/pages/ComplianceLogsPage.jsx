import { useEffect, useState } from "react";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading, EmptyState } from "../components/Common";

export default function ComplianceLogsPage() {
  const [logs, setLogs] = useState(null);
  const [error, setError] = useState(null);
  const [checkText, setCheckText] = useState("");
  const [checkResult, setCheckResult] = useState(null);
  const [busy, setBusy] = useState(false);

  function loadLogs() {
    api.get("/compliance/logs").then(setLogs).catch(setError);
  }

  useEffect(() => { loadLogs(); }, []);

  async function runCheck(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      const data = await api.post("/compliance/check", { text: checkText });
      setCheckResult(data);
      loadLogs();
    } catch (err) {
      setError(err);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <TopBar title="Compliance Logs" description="Every request checked by the guardrail, and a way to test it yourself." />
      <div className="content-area">
        <form onSubmit={runCheck} className="card" style={{ maxWidth: 620, marginBottom: 16 }}>
          <h2>Test the guardrail</h2>
          <div className="field">
            <label>Try a request</label>
            <textarea rows={3} value={checkText} onChange={(e) => setCheckText(e.target.value)} placeholder="e.g. Can you help me automate Instagram likes?" />
          </div>
          <button className="btn btn-primary" type="submit" disabled={busy || !checkText}>{busy ? "Checking..." : "Check request"}</button>
          {checkResult && (
            <div className={`alert ${checkResult.allowed ? "alert-accent" : "alert-danger"}`} style={{ marginTop: 12 }}>
              <strong>{checkResult.allowed ? "Allowed" : `Blocked -- ${checkResult.category?.replaceAll("_", " ")}`}</strong>
              <p style={{ margin: "6px 0 0 0" }}>{checkResult.explanation || "No compliance concerns detected."}</p>
              {checkResult.compliant_alternative && <p style={{ margin: "6px 0 0 0" }}>{checkResult.compliant_alternative}</p>}
            </div>
          )}
        </form>

        <ErrorNotice error={error} />
        {!logs && <Loading />}
        {logs && logs.length === 0 && <EmptyState>No compliance checks logged yet.</EmptyState>}
        {logs && logs.length > 0 && (
          <table>
            <thead><tr><th>Time</th><th>Endpoint</th><th>Result</th><th>Category</th><th>Excerpt</th></tr></thead>
            <tbody>
              {logs.map((log) => (
                <tr key={log.id}>
                  <td>{new Date(log.created_at).toLocaleString()}</td>
                  <td>{log.endpoint}</td>
                  <td><span className={`badge ${log.allowed ? "badge-green" : "badge-red"}`}>{log.allowed ? "allowed" : "blocked"}</span></td>
                  <td>{log.category || "--"}</td>
                  <td style={{ maxWidth: 300, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{log.input_excerpt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </>
  );
}
