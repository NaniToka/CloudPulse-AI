import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
} from 'recharts';

interface SloPerformanceChartProps {
  selectedService?: string;
}

export const SloPerformanceChart: React.FC<SloPerformanceChartProps> = ({ selectedService = 'ALL' }) => {
  const chartData = [
    { day: 'Day 1', actual: 99.98, target: 99.9, forecast: 99.98 },
    { day: 'Day 5', actual: 99.95, target: 99.9, forecast: 99.96 },
    { day: 'Day 10', actual: 99.92, target: 99.9, forecast: 99.94 },
    { day: 'Day 15', actual: 98.40, target: 99.9, forecast: 98.60 },
    { day: 'Day 20', actual: 99.10, target: 99.9, forecast: 99.30 },
    { day: 'Day 25', actual: 99.85, target: 99.9, forecast: 99.88 },
    { day: 'Day 30', actual: 99.94, target: 99.9, forecast: 99.95 },
  ];

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">SLO Performance Trend & Forecast</h3>
          <p className="text-xs text-slate-400">
            Historical availability vs target SLO ({selectedService !== 'ALL' ? selectedService : 'All Monitored Services'})
          </p>
        </div>
        <div className="flex items-center gap-4 text-xs">
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-emerald-400"></span>
            <span className="text-slate-300 font-medium">Actual SLO</span>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded-full bg-rose-400"></span>
            <span className="text-slate-300 font-medium">Target SLO (99.9%)</span>
          </div>
        </div>
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
            <defs>
              <linearGradient id="sloGrad" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10b981" stopOpacity={0.4} />
                <stop offset="95%" stopColor="#10b981" stopOpacity={0.0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
            <XAxis dataKey="day" stroke="#94a3b8" fontSize={11} tickLine={false} />
            <YAxis domain={[97.0, 100.0]} stroke="#94a3b8" fontSize={11} tickLine={false} />
            <Tooltip
              contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px' }}
              itemStyle={{ fontSize: '12px', color: '#f8fafc' }}
            />
            <ReferenceLine y={99.9} stroke="#f43f5e" strokeDasharray="4 4" label={{ value: 'SLO Target (99.9%)', fill: '#f43f5e', fontSize: 10 }} />
            <Area type="monotone" dataKey="actual" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#sloGrad)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};
