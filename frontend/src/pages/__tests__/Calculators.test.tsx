import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import Calculators from "../Calculators";
import { LanguageProvider } from "../../context/LanguageContext";

vi.mock("../../api/client", () => ({
  default: {
    get: vi.fn().mockResolvedValue({ data: {} }),
    post: vi.fn().mockResolvedValue({ data: { monthly_payment: 1073.64, total_payment: 386511.57, total_interest: 186511.57, monthly_rate_pct: 0.42 } }),
    patch: vi.fn().mockResolvedValue({}),
    delete: vi.fn().mockResolvedValue({}),
  },
}));

beforeEach(() => {
  localStorage.clear();
  vi.clearAllMocks();
});
afterEach(() => vi.unstubAllGlobals());

function renderCalculators() {
  return render(
    <LanguageProvider>
      <MemoryRouter>
        <Calculators />
      </MemoryRouter>
    </LanguageProvider>
  );
}

describe("Calculators page", () => {
  it("renders the heading and all 8 calculator tabs", () => {
    renderCalculators();

    expect(screen.getByRole("heading", { name: "Calculators" })).toBeInTheDocument();
    for (const tab of ["Mortgage", "Stock / Investment Return", "Mutual Fund / Money Market", "Bond Yield", "Treasury Bill", "Commercial Paper", "Real Estate", "Goal Projection"]) {
      expect(screen.getByRole("button", { name: tab })).toBeInTheDocument();
    }
  });

  it("embeds the Musa chat widget (conversation-first)", () => {
    renderCalculators();

    expect(screen.getByRole("button", { name: "Musa chat" })).toBeInTheDocument();
  });

  it("submits the mortgage form and renders results", async () => {
    const { default: client } = await import("../../api/client");
    renderCalculators();

    const inputs = screen.getAllByRole("spinbutton");
    const loanInput = inputs[0];
    const rateInput = inputs[1];
    const termInput = inputs[2];

    fireEvent.change(loanInput, { target: { value: "200000" } });
    fireEvent.change(rateInput, { target: { value: "5" } });
    fireEvent.change(termInput, { target: { value: "30" } });

    fireEvent.click(screen.getByRole("button", { name: "Calculate" }));

    expect(await screen.findByText("Results")).toBeInTheDocument();
    expect(screen.getByText("₦1,073.64")).toBeInTheDocument();
    expect(client.post).toHaveBeenCalledWith(
      "/calculators/mortgage",
      { principal: 200000, annual_rate_pct: 5, term_years: 30 }
    );
  });
});