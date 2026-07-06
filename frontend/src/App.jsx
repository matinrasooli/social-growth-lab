import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./store/auth";
import Sidebar from "./components/Sidebar";

import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import UploadInsightsPage from "./pages/UploadInsightsPage";
import AnalyticsPage from "./pages/AnalyticsPage";
import ContentScorerPage from "./pages/ContentScorerPage";
import HookLabPage from "./pages/HookLabPage";
import CaptionLabPage from "./pages/CaptionLabPage";
import CTALabPage from "./pages/CTALabPage";
import ContentCalendarPage from "./pages/ContentCalendarPage";
import ExperimentTrackerPage from "./pages/ExperimentTrackerPage";
import CommentHelperPage from "./pages/CommentHelperPage";
import DMHelperPage from "./pages/DMHelperPage";
import CompetitorNotesPage from "./pages/CompetitorNotesPage";
import ViralitySimulatorPage from "./pages/ViralitySimulatorPage";
import ComplianceLogsPage from "./pages/ComplianceLogsPage";
import SettingsPage from "./pages/SettingsPage";

function ProtectedLayout({ children }) {
  const { isAuthenticated } = useAuth();
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return (
    <div className="app-shell">
      <Sidebar />
      <div className="main-column">{children}</div>
    </div>
  );
}

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route path="/" element={<ProtectedLayout><DashboardPage /></ProtectedLayout>} />
          <Route path="/insights" element={<ProtectedLayout><UploadInsightsPage /></ProtectedLayout>} />
          <Route path="/analytics" element={<ProtectedLayout><AnalyticsPage /></ProtectedLayout>} />
          <Route path="/scorer" element={<ProtectedLayout><ContentScorerPage /></ProtectedLayout>} />
          <Route path="/hooks" element={<ProtectedLayout><HookLabPage /></ProtectedLayout>} />
          <Route path="/captions" element={<ProtectedLayout><CaptionLabPage /></ProtectedLayout>} />
          <Route path="/ctas" element={<ProtectedLayout><CTALabPage /></ProtectedLayout>} />
          <Route path="/calendar" element={<ProtectedLayout><ContentCalendarPage /></ProtectedLayout>} />
          <Route path="/experiments" element={<ProtectedLayout><ExperimentTrackerPage /></ProtectedLayout>} />
          <Route path="/comments" element={<ProtectedLayout><CommentHelperPage /></ProtectedLayout>} />
          <Route path="/dms" element={<ProtectedLayout><DMHelperPage /></ProtectedLayout>} />
          <Route path="/competitors" element={<ProtectedLayout><CompetitorNotesPage /></ProtectedLayout>} />
          <Route path="/simulator" element={<ProtectedLayout><ViralitySimulatorPage /></ProtectedLayout>} />
          <Route path="/compliance" element={<ProtectedLayout><ComplianceLogsPage /></ProtectedLayout>} />
          <Route path="/settings" element={<ProtectedLayout><SettingsPage /></ProtectedLayout>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;
