import React from 'react';
import { ShieldCheck, AlertTriangle } from 'lucide-react';
import { RiskMatrixItem } from '../../types/executive';

interface Props {
  matrix: RiskMatrixItem[];
}

export const CloudRiskMatrixTable: React.FC<Props> = ({ matrix }) => {
  const getBadge = (risk: string) => {
    switch (risk.toUpperCase()) {
      case 'CRITICAL':
        return <span className="px-2 py-0.5 bg-rose-500/20 text-rose-400 border border-rose-500/40 text-xs font-bold rounded">CRITICAL</span>;
      case 'HIGH':
        return <span className="px-2 py-0.5 bg-amber-500/20 text-amber-400 border border-amber-500/40 text-xs font-bold rounded">HIGH</span>;
      case 'MEDIUM':
        return <span className="px-2 py-0.5 bg-blue-500/20 text-blue-400 border border-blue-500/40 text-xs font-bold rounded">MEDIUM</span>;
      default:
        return <span className="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 text-xs font-bold rounded">LOW</span>;
    }
  };

  return (
    <div className="p-6 bg-slate-900/80 border border-slate-800/80 rounded-xl backdrop-blur-md shadow-xl overflow-x-auto">
      <h3 className="text-base font-bold text-slate-100 tracking-tight mb-1">Cloud Risk Matrix</h3>
      <p className="text-xs text-slate-400 mb-4">Domain-level risk assessment across key operational vectors</p>

      <table className="w-full text-left text-xs text-slate-300">
        <thead className="bg-slate-950/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-800">
          <tr>
            <th className="py-2.5 px-3">Domain</th>
            <th className="py-2.5 px-3">Risk Level</th>
            <th className="py-2.5 px-3">Impact Summary</th>
            <th className="py-2.5 px-3">Recommended Action</th>
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-800/50">
          {matrix.map((row, idx) => (
            <tr key={idx} className="hover:bg-slate-800/30 transition-colors">
              <td className="py-3 px-3 font-bold text-slate-200">{row.domain}</td>
              <td className="py-3 px-3">{getBadge(row.risk_level)}</td>
              <td className="py-3 px-3 text-slate-300 max-w-xs">{row.impact_summary}</td>
              <td className="py-3 px-3 text-indigo-400 font-medium max-w-xs">{row.recommended_action}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
