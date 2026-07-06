import { NavLink } from "react-router-dom";

const NAV_SECTIONS = [
  {
    label: "Workflow",
    items: [
      { to: "/", label: "Dashboard", index: "00" },
      { to: "/insights", label: "Upload Insights", index: "01" },
      { to: "/analytics", label: "Analytics", index: "02" },
      { to: "/scorer", label: "Content Scorer", index: "03" },
      { to: "/hooks", label: "Hook Lab", index: "04" },
      { to: "/captions", label: "Caption Lab", index: "05" },
      { to: "/ctas", label: "CTA Lab", index: "06" },
      { to: "/calendar", label: "Content Calendar", index: "07" },
      { to: "/experiments", label: "Experiment Tracker", index: "08" },
      { to: "/comments", label: "Comment Helper", index: "09" },
      { to: "/dms", label: "DM Helper", index: "10" },
      { to: "/competitors", label: "Competitor Notes", index: "11" },
      { to: "/simulator", label: "Virality Simulator", index: "12" },
    ],
  },
  {
    label: "System",
    items: [
      { to: "/compliance", label: "Compliance Logs" },
      { to: "/settings", label: "Settings" },
    ],
  },
];

export default function Sidebar() {
  return (
    <nav className="sidebar" aria-label="Main navigation">
      <div className="sidebar-brand">
        Social Growth Lab
        <small>v1.0</small>
      </div>
      {NAV_SECTIONS.map((section) => (
        <div key={section.label}>
          <div className="sidebar-section-label">{section.label}</div>
          {section.items.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === "/"}
              className={({ isActive }) => `sidebar-link${isActive ? " active" : ""}`}
            >
              {item.index && <span className="step-index">{item.index}</span>}
              {item.label}
            </NavLink>
          ))}
        </div>
      ))}
    </nav>
  );
}
