import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../store/auth";
import DashboardPage from "../pages/DashboardPage";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: { get: vi.fn(), post: vi.fn(), postForm: vi.fn() },
  setToken: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

beforeEach(() => {
  localStorage.setItem("sgl_username", "testuser");
  vi.clearAllMocks();
});

describe("DashboardPage", () => {
  it("renders summary stats once data loads", async () => {
    api.get.mockResolvedValueOnce({
      insights_uploaded: 12,
      calendar_items_planned: 5,
      experiments_tracked: 3,
      competitor_notes: 2,
      simulation_runs: 1,
      getting_started: false,
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText("12")).toBeInTheDocument());
    expect(screen.getByText("Insights uploaded")).toBeInTheDocument();
    expect(screen.getByText("Suggested next steps")).toBeInTheDocument();
  });

  it("shows a getting-started message when there is no data yet", async () => {
    api.get.mockResolvedValueOnce({
      insights_uploaded: 0, calendar_items_planned: 0, experiments_tracked: 0,
      competitor_notes: 0, simulation_runs: 0, getting_started: true,
    });

    render(
      <MemoryRouter>
        <AuthProvider>
          <DashboardPage />
        </AuthProvider>
      </MemoryRouter>
    );

    await waitFor(() => expect(screen.getByText(/Welcome!/)).toBeInTheDocument());
  });
});
