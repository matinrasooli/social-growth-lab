import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../store/auth";

export default function LoginPage() {
  const { login, register, isAuthenticated } = useAuth();
  const navigate = useNavigate();
  const [mode, setMode] = useState("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [busy, setBusy] = useState(false);

  if (isAuthenticated) {
    navigate("/", { replace: true });
  }

  async function handleSubmit(e) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "login") await login(username, password);
      else await register(username, password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login-shell">
      <div className="login-card">
        <h1 style={{ color: "var(--color-primary)" }}>Social Growth Lab</h1>
        <p style={{ color: "var(--color-ink-soft)", marginBottom: 22 }}>
          Local-first Instagram content strategy, analytics, and virality simulation --
          no fake engagement, no scraping, no automation.
        </p>

        <div className="tabs">
          <button className={`tab-btn${mode === "login" ? " active" : ""}`} onClick={() => setMode("login")} type="button">
            Log in
          </button>
          <button className={`tab-btn${mode === "register" ? " active" : ""}`} onClick={() => setMode("register")} type="button">
            Create account
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" type="text" value={username} onChange={(e) => setUsername(e.target.value)} required />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} />
          </div>
          {error && <div className="alert alert-danger">{error}</div>}
          <button className="btn btn-primary" type="submit" disabled={busy} style={{ width: "100%", justifyContent: "center" }}>
            {busy ? "Please wait..." : mode === "login" ? "Log in" : "Create account"}
          </button>
        </form>
      </div>
    </div>
  );
}
