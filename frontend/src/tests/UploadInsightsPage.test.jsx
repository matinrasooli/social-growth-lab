import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { AuthProvider } from "../store/auth";
import UploadInsightsPage from "../pages/UploadInsightsPage";
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

describe("UploadInsightsPage", () => {
  it("imports pasted text and shows a confirmation", async () => {
    api.postForm.mockResolvedValueOnce({ imported: 1 });

    render(
      <MemoryRouter>
        <AuthProvider>
          <UploadInsightsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText("Paste text"));
    const textarea = screen.getByPlaceholderText(/Date: 2026-05-01/);
    fireEvent.change(textarea, { target: { value: "Date: 2026-05-01\nReach: 1000" } });
    fireEvent.click(screen.getByText("Import text"));

    await waitFor(() => expect(screen.getByText(/Imported 1 record/)).toBeInTheDocument());
    expect(api.postForm).toHaveBeenCalledWith("/insights/import", expect.any(FormData));
  });

  it("requires a file before submitting the file import form", async () => {
    render(
      <MemoryRouter>
        <AuthProvider>
          <UploadInsightsPage />
        </AuthProvider>
      </MemoryRouter>
    );

    fireEvent.click(screen.getByText("Import file"));
    await waitFor(() => expect(screen.getByText(/Choose a CSV or JSON file first/)).toBeInTheDocument());
    expect(api.postForm).not.toHaveBeenCalled();
  });
});
