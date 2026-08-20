import React, { useState } from "react";
import { Globe, MapPin, Check } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import type { RegionCostItem } from "@/types/cost";

interface CostByRegionProps {
  regions: RegionCostItem[];
}

const getRegionProviderBadge = (region: string) => {
  const r = region.toLowerCase();
  if (r.includes('us-central') || r.includes('europe-west') || r.includes('asia-east')) {
    return <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-sky-500/10 text-sky-400 border border-sky-500/20 uppercase">GCP</span>;
  }
  if (r.includes('us-east') || r.includes('us-west') || r.includes('eu-central')) {
    return <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-amber-500/10 text-amber-400 border border-amber-500/20 uppercase">AWS</span>;
  }
  if (r.includes('eastus') || r.includes('westeurope') || r.includes('northeurope')) {
    return <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 uppercase">AZURE</span>;
  }
  return <span className="px-1.5 py-0.5 text-[9px] font-bold rounded bg-indigo-500/10 text-indigo-400 border border-indigo-500/20 uppercase">CLOUD</span>;
};

export default function CostByRegion({ regions }: CostByRegionProps) {
  const [selectedRegion, setSelectedRegion] = useState<string | null>(null);

  return (
    <Card className="border-slate-800/80 bg-slate-900/70 backdrop-blur-xl shadow-2xl relative overflow-hidden h-full flex flex-col justify-between">
      {/* Accent Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-sky-500 via-blue-500 to-indigo-500" />

      <div>
        <CardHeader className="pb-2 flex flex-row items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400">
              <Globe className="w-4 h-4" />
            </div>
            <div>
              <CardTitle className="text-sm font-bold text-slate-100">Cost by Region</CardTitle>
              <p className="text-xs text-slate-400 mt-0.5">Geographic infrastructure spend</p>
            </div>
          </div>
          <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700/80">
            {regions.length} Regions
          </span>
        </CardHeader>

        <CardContent className="space-y-3 pt-2">
          {regions.map((r) => {
            const isSelected = selectedRegion === r.region;
            return (
              <div
                key={r.region}
                onClick={() => setSelectedRegion(isSelected ? null : r.region)}
                className={`p-2 rounded-xl transition-all duration-200 cursor-pointer space-y-1.5 font-mono text-xs ${
                  isSelected
                    ? "bg-slate-800/90 border border-sky-500/40 shadow-lg"
                    : "bg-slate-950/40 border border-slate-800/60 hover:bg-slate-800/60 hover:border-slate-700/80"
                }`}
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    {getRegionProviderBadge(r.region)}
                    <span className="font-sans font-bold text-slate-200">{r.region}</span>
                  </div>
                  <div className="flex items-center gap-2.5">
                    <span className="text-slate-400 font-medium">{r.percentage}%</span>
                    <span className="font-extrabold text-slate-100">${r.cost.toLocaleString()}</span>
                  </div>
                </div>
                <Progress
                  value={r.percentage}
                  className={`h-1.5 rounded-full ${isSelected ? "bg-sky-950" : "bg-slate-900"}`}
                />
              </div>
            );
          })}
        </CardContent>
      </div>

      {selectedRegion && (
        <div className="p-3 mx-4 mb-4 bg-sky-500/10 border border-sky-500/30 rounded-xl text-xs flex items-center justify-between text-sky-300">
          <span>Active Filter: <strong>{selectedRegion}</strong></span>
          <button onClick={() => setSelectedRegion(null)} className="underline hover:text-white">Clear</button>
        </div>
      )}
    </Card>
  );
}
