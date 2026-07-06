import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../store/auth";
import ContentScorerPage from "../pages/ContentScorerPage";
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

const SCORE_RESPONSE = {
  overall_score: 7.2, hook_score: 8, clarity_score: 7, novelty_score: 6, audience_fit_score: 7,
  emotional_pull_score: 6.5, usefulness_score: 7, shareability_score: 7, saveability_score: 7.5,
  trust_score: 8, cta_score: 7, retention_risk: "low",
  improvement_suggestions: ["Tighten the hook further", "Add a clearer CTA"],
  method: "blended",
};

describe("ContentScorerPage", () => {
  it("submits a content idea and displays the score", async () => {
    api.post.mockResolvedValueOnce(SCORE_RESPONSE);

    render(
      <MemoryRouter>
        <AuthProvider>
          <ContentScorerPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Content idea/), { target: { value: "A morning routine reel" } });
    fireEvent.click(screen.getByText("Score this content"));

    await waitFor(() => expect(screen.getByText("7.2/10")).toBeInTheDocument());
    expect(screen.getByText("low retention risk")).toBeInTheDocument();
    expect(screen.getByText("Tighten the hook further")).toBeInTheDocument();
    expect(api.post).toHaveBeenCalledWith("/content/score", expect.objectContaining({ content_idea: "A morning routine reel" }));
  });
});
