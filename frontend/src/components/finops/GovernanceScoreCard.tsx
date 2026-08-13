import React from "react";
import type { GovernanceScoreResponse } from "@/types/finopsGovernance";
import { ShieldCheck, AlertTriangle, TrendingUp, DollarSign, CheckCircle2 } from "lucide-react";

interface Props {
  score: GovernanceScoreResponse | null;
  loading: boolean;
}

export const GovernanceScoreCard: React.FC<Props> = ({ score, loading }) => {
  if (loading) {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 animate-pulse">
        <div className="h-6 bg-slate-800 rounded w-1/3 mb-4"></div>
        <div className="h-20 bg-slate-800 rounded mb-4"></div>
      </div>
    );
  }

  if (!score) return null;

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case "LOW":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">LOW RISK</span>;
      case "MEDIUM":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-amber-500/10 text-amber-400 border border-amber-500/20">MEDIUM RISK</span>;
      case "HIGH":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-orange-500/10 text-orange-400 border border-orange-500/20">HIGH RISK</span>;
      case "CRITICAL":
        return <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-rose-500/10 text-rose-400 border border-rose-500/20">CRITICAL RISK</span>;
      default:
        return null;
    }
  };

  const getScoreColor = (scoreVal: number) => {
    if (scoreVal >= 85) return "text-emerald-400 border-emerald-500/30";
    if (scoreVal >= 70) return "text-amber-400 border-amber-500/30";
    if (scoreVal >= 50) return "text-orange-400 border-orange-500/30";
    return "text-rose-400 border-rose-500/30";
  };

  return (
    <div className="bg-slate-900/90 backdrop-blur border border-slate-800 rounded-xl p-6 shadow-xl space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-indigo-500/10 border border-indigo-500/20 rounded-lg text-indigo-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <div>
            <h2 className="text-lg font-bold text-slate-100">FinOps Governance Score</h2>
            <p className="text-xs text-slate-400">Deterministic cost policy compliance index</p>
          </div>
        </div>
        {getRiskBadge(score.risk_level)}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6 items-center">
        {/* Big Score Radial/Circle Box */}
        <div className="lg:col-span-2 flex flex-col items-center justify-center p-6 bg-slate-950/60 rounded-xl border border-slate-800/80 text-center">
          <div className={`w-32 h-32 rounded-full border-4 flex flex-col items-center justify-center mb-3 shadow-inner ${getScoreColor(score.overall_score)}`}>
            <span className="text-4xl font-extrabold tracking-tight">{score.overall_score}</span>
            <span className="text-[10px] uppercase font-bold text-slate-400 tracking-wider">/ 100 Score</span>
          </div>
          <p className="text-xs text-slate-300 font-medium max-w-xs">{score.explanation}</p>
        </div>

        {/* Breakdown Sub-scores */}
        <div className="lg:col-span-3 space-y-3">
          {score.components.map((comp, idx) => (
            <div key={idx} className="p-3 bg-slate-950/40 rounded-lg border border-slate-800/50 hover:border-slate-700/60 transition-colors">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-semibold text-slate-200">{comp.name}</span>
                <div className="flex items-center gap-2">
                  <span className="text-xs font-bold text-slate-100">{comp.score}%</span>
                  <span className="text-[10px] text-slate-500 font-medium">({comp.weight_pct}% weight)</span>
                </div>
              </div>
              <div className="w-full bg-slate-800 rounded-full h-1.5 mb-1.5 overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    comp.score >= 80 ? "bg-emerald-500" : comp.score >= 60 ? "bg-amber-500" : "bg-rose-500"
                  }`}
                  style={{ width: `${comp.score}%` }}
                />
              </div>
              <p className="text-[11px] text-slate-400 flex items-center gap-1.5">
                {comp.status === "OPTIMAL" ? (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
                ) : (
                  <AlertTriangle className="w-3.5 h-3.5 text-amber-400 shrink-0" />
                )}
                {comp.details}
              </p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
