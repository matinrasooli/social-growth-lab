export function ComplianceBlockNotice({ error }) {
  if (!error || !error.detail) return null;
  const { message, compliant_alternative, category } = error.detail;
  return (
    <div className="compliance-block" role="alert">
      <strong>Request blocked{category ? ` -- ${category.replaceAll("_", " ")}` : ""}</strong>
      <p style={{ margin: "6px 0 0 0" }}>{message}</p>
      {compliant_alternative && <p className="alt">{compliant_alternative}</p>}
    </div>
  );
}

export function ErrorNotice({ error }) {
  if (!error) return null;
  if (error.status === 400 && error.detail && error.detail.compliant_alternative) {
    return <ComplianceBlockNotice error={error} />;
  }
  return <div className="alert alert-danger">{error.message || "Something went wrong."}</div>;
}

export function StatCard({ label, value }) {
  return (
    <div className="card stat-card">
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
    </div>
  );
}

export function Loading({ label = "Loading..." }) {
  return <div className="empty-state">{label}</div>;
}

export function EmptyState({ children }) {
  return <div className="empty-state">{children}</div>;
}
