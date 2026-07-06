import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../store/auth";
import ViralitySimulatorPage from "../pages/ViralitySimulatorPage";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: { get: vi.fn(), post: vi.fn(), postForm: vi.fn() },
  setToken: vi.fn(),
  API_BASE: "http://localhost:8000",
}));

const RUN_RESPONSE = {
  run_id: 1,
  final_reach: 42,
  final_engagement: { likes: 10, comments: 2, saves: 5, shares: 3, negative_feedback: 0 },
  reach_curve: [{ tick: 0, cumulative_reach: 5 }, { tick: 1, cumulative_reach: 42 }],
  engagement_curve: [{ tick: 0, likes: 1, comments: 0, saves: 0, shares: 0 }],
  why_content_spread: ["Strong hook kept viewers watching."],
  why_content_stalled: [],
  simulated_follower_conversion_estimate: 1.2,
  disclaimer: "This is a synthetic, closed-network simulation for strategy testing only.",
};

beforeEach(() => {
  localStorage.setItem("sgl_username", "testuser");
  vi.clearAllMocks();
  api.get.mockResolvedValue([]);
});

describe("ViralitySimulatorPage", () => {
  it("runs a simulation and displays the results", async () => {
    api.post.mockResolvedValueOnce(RUN_RESPONSE);

    render(
      <MemoryRouter>
        <AuthProvider>
          <ViralitySimulatorPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText("Run simulation"));

    await waitFor(() => expect(screen.getByText("42")).toBeInTheDocument());
    expect(screen.getByText("Final reach")).toBeInTheDocument();
    expect(screen.getByText(/synthetic, closed-network simulation/)).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith("/simulation/run", expect.objectContaining({ network_structure: "small_world" }));
  });
});
