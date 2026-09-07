import { render, screen } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import { describe, expect, it, vi } from "vitest";
import AdBanner from "../AdBanner";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({}),
  },
}));

const mockUser = { plan: "free" };

vi.mock("../../context/AuthContext", () => ({
  useAuth: () => ({ user: mockUser }),
}));

describe("AdBanner", () => {
  it("renders without crashing", () => {
    render(
      <BrowserRouter>
        <AdBanner pageContext="dashboard" />
      </BrowserRouter>
    );
    expect(screen.getByText(/ad-free/i)).toBeInTheDocument();
  });
});
