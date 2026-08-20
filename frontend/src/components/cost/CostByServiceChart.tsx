import React, { useState } from "react";
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Sector } from "recharts";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PieChart as PieIcon, Layers } from "lucide-react";
import type { ServiceCostItem } from "@/types/cost";

interface CostByServiceChartProps {
  services: ServiceCostItem[];
}

export default function CostByServiceChart({ services }: CostByServiceChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  const total = services.reduce((acc, s) => acc + s.cost, 0);
  const activeService = activeIndex !== null ? services[activeIndex] : null;

  const onPieEnter = (_: any, index: number) => {
    setActiveIndex(index);
  };

  const onPieLeave = () => {
    setActiveIndex(null);
  };

  return (
    <Card className="border-slate-800/80 bg-slate-900/70 backdrop-blur-xl shadow-2xl relative overflow-hidden">
      {/* Accent Line */}
      <div className="absolute top-0 left-0 right-0 h-0.5 bg-gradient-to-r from-purple-500 via-indigo-500 to-pink-500" />

      <CardHeader className="pb-2 flex flex-row items-center justify-between">
        <div>
          <div className="flex items-center gap-2">
            <div className="p-1.5 rounded-lg bg-purple-500/10 border border-purple-500/20 text-purple-400">
              <PieIcon className="w-4 h-4" />
            </div>
            <CardTitle className="text-sm font-bold text-slate-100">Cost by Service</CardTitle>
          </div>
          <p className="text-xs text-slate-400 mt-1">Monthly spending distribution across services</p>
        </div>
        <span className="text-xs font-semibold px-2.5 py-1 rounded-full bg-slate-800/80 text-slate-300 border border-slate-700/80">
          {services.length} Services
        </span>
      </CardHeader>

      <CardContent>
        <div className="flex flex-col md:flex-row items-center gap-6 pt-1">
          {/* Donut Chart Container */}
          <div className="relative shrink-0 mx-auto">
            <ResponsiveContainer width={180} height={180}>
              <PieChart>
                <Pie
                  data={services}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={74}
                  paddingAngle={3}
                  dataKey="cost"
                  stroke="none"
                  onMouseEnter={onPieEnter}
                  onMouseLeave={onPieLeave}
                >
                  {services.map((entry, i) => {
                    const isSelected = activeIndex === i;
                    return (
                      <Cell
                        key={i}
                        fill={entry.fill || "#3b82f6"}
                        className="transition-all duration-300 cursor-pointer"
                        stroke={isSelected ? "#ffffff" : "none"}
                        strokeWidth={isSelected ? 2 : 0}
                        style={{
                          transform: isSelected ? "scale(1.05)" : "scale(1)",
                          transformOrigin: "center center",
                        }}
                      />
                    );
                  })}
                </Pie>
                <Tooltip
                  content={({ active, payload }) => {
                    if (!active || !payload || !payload.length) return null;
                    const dataItem = payload[0].payload as ServiceCostItem;
                    return (
                      <div className="bg-slate-950/95 border border-slate-800 p-2.5 rounded-xl shadow-2xl backdrop-blur-md text-xs space-y-1 font-sans">
                        <div className="flex items-center gap-2 font-bold text-slate-200">
                          <div className="w-2.5 h-2.5 rounded-full" style={{ background: dataItem.fill || "#3b82f6" }} />
                          <span>{dataItem.service}</span>
                        </div>
                        <div className="flex items-center justify-between gap-4 text-slate-300 pt-0.5">
                          <span>Spend: <strong className="font-mono text-white">${dataItem.cost.toLocaleString()}</strong></span>
                          <span className="text-purple-400 font-bold">{dataItem.percentage}%</span>
                        </div>
                      </div>
                    );
                  }}
                />
              </PieChart>
            </ResponsiveContainer>

            {/* Dynamic Center Label */}
            <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none text-center px-2">
              {activeService ? (
                <>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-purple-400 truncate max-w-[110px]">
                    {activeService.service}
                  </span>
                  <span className="text-sm font-extrabold font-mono text-slate-100">
                    ${activeService.cost >= 1000 ? `${(activeService.cost / 1000).toFixed(1)}k` : activeService.cost}
                  </span>
                  <span className="text-[10px] text-purple-300 font-semibold">{activeService.percentage}% Share</span>
                </>
              ) : (
                <>
                  <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400">Total Spend</span>
                  <span className="text-sm font-extrabold font-mono text-slate-100">${(total / 1000).toFixed(1)}k</span>
                  <span className="text-[10px] text-slate-400">100% Allocated</span>
                </>
              )}
            </div>
          </div>

          {/* Interactive Legend List */}
          <div className="flex-1 space-y-2.5 w-full max-h-[220px] overflow-y-auto pr-1 custom-scrollbar">
            {services.map((item, idx) => {
              const isHovered = activeIndex === idx;
              return (
                <div
                  key={item.service}
                  onMouseEnter={() => setActiveIndex(idx)}
                  onMouseLeave={() => setActiveIndex(null)}
                  className={`flex items-center justify-between text-xs font-mono p-1.5 rounded-lg transition-all duration-200 cursor-pointer ${
                    isHovered
                      ? "bg-slate-800/90 border border-purple-500/40 shadow-lg scale-[1.01]"
                      : "bg-slate-950/40 border border-transparent hover:bg-slate-800/50"
                  }`}
                >
                  <div className="flex items-center gap-2 min-w-0">
                    <div
                      className="h-2.5 w-2.5 rounded-full shrink-0 transition-transform duration-200"
                      style={{
                        background: item.fill || "#3b82f6",
                        transform: isHovered ? "scale(1.3)" : "scale(1)",
                      }}
                    />
                    <span className={`font-sans truncate ${isHovered ? "text-white font-bold" : "text-slate-300"}`}>
                      {item.service}
                    </span>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className="text-slate-400 font-medium">{item.percentage}%</span>
                    <span className="font-bold text-slate-100">${item.cost.toLocaleString()}</span>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
