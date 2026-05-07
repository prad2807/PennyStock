export type RecommendationAction = "Buy" | "Hold" | "Watch" | "Avoid";

export interface WeeklyRecommendation {
  symbol: string;
  companyName: string;
  action: RecommendationAction;
  allocationAmount: number;
  convictionScore: number;
  reasons: string[];
}

export interface DashboardState {
  monthlyLimit: number;
  monthlyInvested: number;
  investmentPool: number;
  mode: "active" | "watchlist_only";
  message?: string;
  recommendations: WeeklyRecommendation[];
  watchlist: string[];
}
