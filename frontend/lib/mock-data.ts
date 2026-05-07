import type { DashboardState } from "./types";

export const dashboardState: DashboardState = {
  monthlyLimit: 1000,
  monthlyInvested: 700,
  investmentPool: 840,
  mode: "active",
  recommendations: [
    {
      symbol: "PIXTRANS",
      companyName: "Pix Transmissions",
      action: "Buy",
      allocationAmount: 250,
      convictionScore: 78.4,
      reasons: [
        "Improving revenue growth with conservative leverage",
        "Volume breakout after multi-week consolidation",
        "Promoter holding remains above the screening threshold"
      ]
    },
    {
      symbol: "KILITCH",
      companyName: "Kilitch Drugs",
      action: "Hold",
      allocationAmount: 0,
      convictionScore: 73.1,
      reasons: ["Existing holding remains valid", "Risk engine shows no major governance penalty"]
    }
  ],
  watchlist: ["KILITCH", "PIXTRANS", "SJS", "HPL"]
};
