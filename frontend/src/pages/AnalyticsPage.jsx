import { useEffect, useState } from "react";
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { ErrorNotice, Loading, EmptyState, StatCard } from "../components/Common";

function ComparisonBarChart({ title, data, dataKey = "avg" }) {
  if (!data || data.length === 0) return null;
  return (
    <div className="card">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
          <XAxis dataKey="key" tick={{ fontSize: 11 }} />
          <YAxis tick={{ fontSize: 11 }} />
          <Tooltip />
          <Bar dataKey={dataKey} fill="var(--color-accent)" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default function AnalyticsPage() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [filters, setFilters] = useState({ content_type: "", topic: "" });

  function load(currentFilters) {
    const params = new URLSearchParams();
    Object.entries(currentFilters).forEach(([k, v]) => v && params.append(k, v));
    api.get(`/analytics/performance?${params.toString()}`).then(setData).catch(setError);
  }

  useEffect(() => { load(filters); }, []); // eslint-disable-line

  function applyFilters(e) {
    e.preventDefault();
    load(filters);
  }

  return (
    <>
      <TopBar title="Analytics" description="Performance across everything you've uploaded to Instagram Insights." />
      <div className="content-area">
        <form onSubmit={applyFilters} className="card" style={{ display: "flex", gap: 12, alignItems: "flex-end", marginBottom: 16 }}>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Content type</label>
            <select value={filters.content_type} onChange={(e) => setFilters({ ...filters, content_type: e.target.value })}>
              <option value="">All</option>
              <option value="reel">Reel</option>
              <option value="story">Story</option>
              <option value="carousel">Carousel</option>
              <option value="static">Static</option>
            </select>
          </div>
          <div className="field" style={{ marginBottom: 0 }}>
            <label>Topic</label>
            <input type="text" value={filters.topic} onChange={(e) => setFilters({ ...filters, topic: e.target.value })} placeholder="e.g. meal prep" />
          </div>
          <button className="btn btn-primary" type="submit">Apply filters</button>
        </form>

        <ErrorNotice error={error} />
        {!data && !error && <Loading />}

        {data && data.count === 0 && (
          <EmptyState>{data.message || "No data yet. Upload Instagram Insights to see analytics here."}</EmptyState>
        )}

        {data && data.count > 0 && (
          <>
            <div className="grid grid-4" style={{ marginBottom: 16 }}>
              <StatCard label="Posts analyzed" value={data.count} />
              <StatCard label="Save rate" value={data.save_rate_pct != null ? `${data.save_rate_pct}%` : "--"} />
              <StatCard label="Share rate" value={data.share_rate_pct != null ? `${data.share_rate_pct}%` : "--"} />
              <StatCard label="Comment rate" value={data.comment_rate_pct != null ? `${data.comment_rate_pct}%` : "--"} />
            </div>

            <div className="card">
              <h3>Reach over time</h3>
              <ResponsiveContainer width="100%" height={240}>
                <LineChart data={data.reach_over_time}>
                  <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                  <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip />
                  <Line type="monotone" dataKey="reach" stroke="var(--color-primary)" strokeWidth={2} dot={false} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-2" style={{ marginTop: 16 }}>
              <ComparisonBarChart title="Content type comparison (avg reach)" data={data.content_type_comparison} />
              <ComparisonBarChart title="Hook style comparison (avg reach)" data={data.hook_style_comparison} />
              <ComparisonBarChart title="Topic comparison (avg reach)" data={data.topic_comparison} />
              <ComparisonBarChart title="Best posting days (avg reach)" data={data.best_posting_days} />
            </div>

            {data.strategy_recommendations && (
              <div className="card" style={{ marginTop: 16 }}>
                <h2>Strategy recommendations</h2>
                <p style={{ fontSize: 12, color: "var(--color-muted)" }}>{data.strategy_recommendations.data_confidence_note}</p>
                <div className="grid grid-2">
                  <div>
                    <h3>Post more</h3>
                    <ul className="suggestion-list">{data.strategy_recommendations.post_more?.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </div>
                  <div>
                    <h3>Best hooks</h3>
                    <ul className="suggestion-list">{data.strategy_recommendations.best_hooks?.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </div>
                  <div>
                    <h3>Best CTAs</h3>
                    <ul className="suggestion-list">{data.strategy_recommendations.best_ctas?.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </div>
                  <div>
                    <h3>Next experiments</h3>
                    <ul className="suggestion-list">{data.strategy_recommendations.next_experiments?.map((x, i) => <li key={i}>{x}</li>)}</ul>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>
    </>
  );
}
