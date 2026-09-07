import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Budget from "../Budget";
import { LanguageProvider } from "../../context/LanguageContext";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: [] }),
    post: vi.fn().mockResolvedValue({}),
    patch: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  },
}));

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});
afterEach(() => vi.unstubAllGlobals());

function renderBudget() {
  return render(
    <LanguageProvider>
      <MemoryRouter>
        <Budget />
      </MemoryRouter>
    </LanguageProvider>
  );
}

describe("Budget feature page", () => {
  it("renders the embedded Kemi chat widget (conversation-first)", () => {
    renderBudget();

    expect(screen.getByRole("button", { name: "Kemi chat" })).toBeInTheDocument();
    expect(screen.getByRole("heading", { name: "Budgets" })).toBeInTheDocument();
  });

  it("opens the chat panel from the feature page and shows persona prompts", () => {
    renderBudget();

    const toggle = screen.getByRole("button", { name: "Kemi chat" });
    fireEvent.click(toggle);

    expect(screen.getAllByText("AI Financial Advisor").length).toBeGreaterThan(0);
    expect(screen.getByText("Create a budget for food")).toBeInTheDocument();
  });
});