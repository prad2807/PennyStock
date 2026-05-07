import { RecommendationCard } from "../components/recommendation-card";
import { StatCard } from "../components/stat-card";
import { dashboardState } from "../lib/mock-data";

export default function HomePage() {
  const remaining = Math.max(dashboardState.monthlyLimit - dashboardState.monthlyInvested, 0);
  const usagePercent = Math.round((dashboardState.monthlyInvested / dashboardState.monthlyLimit) * 100);

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_rgba(56,189,248,0.18),_transparent_32rem),#07111f] px-6 py-8">
      <div className="mx-auto max-w-7xl">
        <header className="flex flex-col gap-4 border-b border-white/10 pb-8 lg:flex-row lg:items-end lg:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-sky-300">Experimental investing discipline</p>
            <h1 className="mt-3 text-4xl font-semibold tracking-tight text-white md:text-6xl">Hidden Growth + Momentum</h1>
            <p className="mt-4 max-w-3xl text-slate-300">
              Convert avoided unhealthy spending into a capped investment pool. The platform recommends only one or two high-conviction Indian small-cap ideas per week and will hold cash when the setup is not clean.
            </p>
          </div>
          <div className="rounded-2xl border border-amber-300/30 bg-amber-300/10 p-4 text-amber-100">
            <p className="text-sm uppercase tracking-[0.25em]">Hard cap</p>
            <p className="mt-1 text-3xl font-bold">₹4000/month</p>
            <p className="mt-1 text-sm">₹1000 total weekly recommendation cap</p>
          </div>
        </header>

        <section className="mt-8 grid gap-4 md:grid-cols-5">
          <StatCard label="Budget used" value={`₹${dashboardState.monthlyInvested}`} helper={`${usagePercent}% of monthly cap consumed`} />
          <StatCard label="Remaining" value={`₹${remaining}`} helper="Monthly recommendation room" />
          <StatCard label="Weekly cap" value={`₹${dashboardState.weeklyRecommendationLimit}`} helper="Total buy allocation this week" />
          <StatCard label="Investment pool" value={`₹${dashboardState.investmentPool}`} helper="From skipped impulsive spending" />
          <StatCard label="Active positions" value="5 max" helper="Prevents overdiversification and churn" />
        </section>

        <section className="mt-8 grid gap-6 lg:grid-cols-[1.35fr_0.65fr]">
          <div className="rounded-3xl border border-white/10 bg-white/[0.03] p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <p className="text-sm uppercase tracking-[0.25em] text-slate-400">Monday recommendation</p>
                <h2 className="mt-2 text-2xl font-semibold text-white">This week</h2>
              </div>
              <span className="rounded-full bg-emerald-400/10 px-4 py-2 text-sm text-emerald-200">{dashboardState.mode}</span>
            </div>
            <div className="mt-6 grid gap-4 xl:grid-cols-2">
              {dashboardState.recommendations.map((recommendation) => (
                <RecommendationCard key={recommendation.symbol} recommendation={recommendation} />
              ))}
            </div>
          </div>

          <aside className="space-y-6">
            <section className="rounded-3xl border border-white/10 bg-white/[0.04] p-6">
              <h2 className="text-xl font-semibold text-white">Watchlist changes</h2>
              <p className="mt-2 text-sm text-slate-400">Watchlist mode is used when the monthly cap is reached or no clean breakout exists.</p>
              <div className="mt-5 flex flex-wrap gap-2">
                {dashboardState.watchlist.map((symbol) => (
                  <span key={symbol} className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-200">{symbol}</span>
                ))}
              </div>
            </section>

            <section className="rounded-3xl border border-white/10 bg-slate-950/80 p-6">
              <h2 className="text-xl font-semibold text-white">Behavioral rules</h2>
              <ul className="mt-4 space-y-3 text-sm text-slate-300">
                <li>No leverage, derivatives, margin, or intraday trades.</li>
                <li>Prefer adding to existing conviction positions before fresh buys.</li>
                <li>Every investment requires thesis, catalyst, risk, timeline, and emotional note.</li>
                <li>Sometimes the correct recommendation is: no good opportunities this week, hold cash.</li>
              </ul>
            </section>
          </aside>
        </section>
      </div>
    </main>
  );
}
