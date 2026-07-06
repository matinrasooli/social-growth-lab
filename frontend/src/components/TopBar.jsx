import { useAuth } from "../store/auth";

export default function TopBar({ title, description }) {
  const { username, logout } = useAuth();
  return (
    <header className="topbar">
      <div>
        <h1>{title}</h1>
        {description && <p style={{ margin: 0 }}>{description}</p>}
      </div>
      <div className="topbar-user">
        <span>{username}</span>
        <button className="btn btn-outline" onClick={logout}>Log out</button>
      </div>
    </header>
  );
}
