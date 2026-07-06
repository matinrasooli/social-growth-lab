import { useAuth } from "../store/auth";
import TopBar from "../components/TopBar";
import { API_BASE } from "../api/client";

export default function SettingsPage() {
  const { username, logout } = useAuth();

  return (
    <>
      <TopBar title="Settings" description="Account and environment info." />
      <div className="content-area">
        <div className="card" style={{ maxWidth: 560 }}>
          <h2>Account</h2>
          <p><strong>Username:</strong> {username}</p>
          <button className="btn btn-outline" onClick={logout}>Log out</button>
        </div>

        <div className="card" style={{ maxWidth: 560 }}>
          <h2>Environment</h2>
          <p><strong>API base URL:</strong> <code>{API_BASE}</code></p>
          <p style={{ fontSize: 13, color: "var(--color-ink-soft)" }}>
            The LLM provider (OpenAI, Anthropic, Ollama, or mock) is configured server-side via the
            backend's <code>.env</code> file (<code>DEFAULT_LLM_PROVIDER</code>). It cannot be changed
            from this page, since API keys should never be entered into the frontend.
          </p>
        </div>

        <div className="card" style={{ maxWidth: 560 }}>
          <h2>What this product will never do</h2>
          <ul className="suggestion-list">
            <li>Automate likes, comments, views, follows, shares, saves, story views, or DMs</li>
            <li>Scrape Instagram or any other platform</li>
            <li>Store or request your Instagram password</li>
            <li>Bypass CAPTCHAs, rate limits, or platform detection</li>
            <li>Create fake accounts or fake engagement</li>
          </ul>
        </div>
      </div>
    </>
  );
}
