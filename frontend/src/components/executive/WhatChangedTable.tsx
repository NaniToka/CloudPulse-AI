import React from 'react';
import { ArrowUpRight, ArrowDownRight, Sparkles, CheckCircle2 } from 'lucide-react';
import { WhatChangedItem } from '../../types/executive';

interface Props {
  changes: WhatChangedItem[];
}

export const WhatChangedTable: React.FC<Props> = ({ changes }) => {
  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl overflow-x-auto">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">What Changed (Period Delta Comparison)</h3>
      <p className="text-xs text-slate-400 mb-4">Key changes comparing current 30-day period with previous 30-day period</p>

      <table className="w-full text-left text-xs text-slate-300">
        <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-2.5 px-3">Category</th>
            <th className="py-2.5 px-3">Metric</th>
            <th className="py-2.5 px-3">Current Value</th>
            <th className="py-2.5 px-3">Previous Value</th>
            <th className="py-2.5 px-3">Change Delta</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {changes.map((item, idx) => (
            <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
              <td className="py-3 px-3 font-semibold text-indigo-400">{item.category}</td>
              <td className="py-3 px-3 font-medium text-slate-200">{item.metric}</td>
              <td className="py-3 px-3 font-mono font-bold text-slate-100">{item.current_value}</td>
              <td className="py-3 px-3 font-mono text-slate-400">{item.previous_value}</td>
              <td className="py-3 px-3">
                <span className={`px-2 py-0.5 text-xs font-semibold rounded ${
                  item.change_type === 'RESOLVED' || item.change_type === 'DECREASE' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'bg-amber-500/10 text-amber-400 border border-amber-500/30'
                }`}>
                  {item.change_type}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
