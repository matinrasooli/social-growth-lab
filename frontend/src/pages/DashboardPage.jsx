import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import TopBar from "../components/TopBar";
import { StatCard, Loading, ErrorNotice } from "../components/Common";

export default function DashboardPage() {
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    api.get("/dashboard/summary").then(setSummary).catch(setError);
  }, []);

  return (
    <>
      <TopBar title="Dashboard" description="Your Social Growth Lab workspace at a glance." />
      <div className="content-area">
        <ErrorNotice error={error} />
        {!summary && !error && <Loading />}
        {summary && (
          <>
            {summary.getting_started && (
              <div className="alert alert-accent">
                Welcome! Start by uploading your Instagram Insights export, or explore with the
                sample data in <code>/sample_data</code>. Nothing here reads real Instagram data automatically --
                everything is either uploaded by you or generated in the closed simulator.
              </div>
            )}
            <div className="grid grid-4">
              <StatCard label="Insights uploaded" value={summary.insights_uploaded} />
              <StatCard label="Calendar items planned" value={summary.calendar_items_planned} />
              <StatCard label="Experiments tracked" value={summary.experiments_tracked} />
              <StatCard label="Simulation runs" value={summary.simulation_runs} />
            </div>

            <div className="card" style={{ marginTop: 16 }}>
              <h2>Suggested next steps</h2>
              <ul className="suggestion-list">
                <li><Link to="/insights">Upload Instagram Insights</Link> to unlock analytics and strategy recommendations.</li>
                <li><Link to="/scorer">Score a content idea</Link> before you script or shoot it.</li>
                <li><Link to="/calendar">Generate a 30-day content calendar</Link> for your niche and goal.</li>
                <li><Link to="/simulator">Run a virality simulation</Link> to compare hooks or posting times in a closed sandbox.</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </>
  );
}
