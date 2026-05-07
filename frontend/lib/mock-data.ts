import type { DashboardState } from "./types";

export const dashboardState: DashboardState = {
  monthlyLimit: 4000,
  monthlyInvested: 2700,
  weeklyRecommendationLimit: 1000,
  investmentPool: 3400,
  mode: "active",
  recommendations: [
    {
      symbol: "PIXTRANS",
      companyName: "Pix Transmissions",
      action: "Buy",
      allocationAmount: 1000,
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
