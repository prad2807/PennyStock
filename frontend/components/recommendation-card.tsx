import type { WeeklyRecommendation } from "../lib/types";

interface RecommendationCardProps {
  recommendation: WeeklyRecommendation;
}

export function RecommendationCard({ recommendation }: RecommendationCardProps) {
  const isBuy = recommendation.action === "Buy";

  return (
    <article className="rounded-2xl border border-sky-400/20 bg-slate-950/70 p-5">
      <div className="flex items-start justify-between gap-4">
        <div>
          <p className="text-sm text-slate-400">{recommendation.symbol}</p>
          <h3 className="text-xl font-semibold text-white">{recommendation.companyName}</h3>
        </div>
        <span className="rounded-full border border-white/10 px-3 py-1 text-sm text-sky-200">{recommendation.action}</span>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="rounded-xl bg-white/[0.04] p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Allocation</p>
          <p className="mt-1 text-2xl font-semibold text-white">{isBuy ? `₹${recommendation.allocationAmount}` : "₹0"}</p>
        </div>
        <div className="rounded-xl bg-white/[0.04] p-3">
          <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Conviction</p>
          <p className="mt-1 text-2xl font-semibold text-white">{recommendation.convictionScore}/100</p>
        </div>
      </div>
      <ul className="mt-4 space-y-2 text-sm text-slate-300">
        {recommendation.reasons.map((reason) => (
          <li key={reason} className="flex gap-2">
            <span className="mt-2 h-1.5 w-1.5 rounded-full bg-sky-300" />
            <span>{reason}</span>
          </li>
        ))}
      </ul>
    </article>
  );
}
