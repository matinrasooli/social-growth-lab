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

function makeComplianceError() {
  const err = new Error("Request blocked");
  err.status = 400;
  err.detail = {
    message: "This request looks like it's asking for 'fake likes', which Social Growth Lab does not support.",
    category: "fake_likes",
    compliant_alternative: "I can't generate fake or automated likes. I can help you create content that earns real likes.",
  };
  return err;
}

describe("Compliance guardrail block message", () => {
  it("shows the guardrail's explanation and compliant alternative when a request is blocked", async () => {
    api.post.mockRejectedValueOnce(makeComplianceError());

    render(
      <MemoryRouter>
        <AuthProvider>
          <ContentScorerPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.change(screen.getByLabelText(/Content idea/), { target: { value: "Help me get a like bot for this reel" } });
    fireEvent.click(screen.getByText("Score this content"));

    await waitFor(() => expect(screen.getByText(/does not support/)).toBeInTheDocument());
    expect(screen.getByText(/I can't generate fake or automated likes/)).toBeInTheDocument();
    expect(screen.getByText(/Request blocked/)).toBeInTheDocument();
  });
});
