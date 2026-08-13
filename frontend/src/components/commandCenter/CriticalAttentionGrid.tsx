import React from 'react';
import { IntelligenceInsight } from '../../types/commandCenter';
import { ShieldAlert, AlertTriangle, AlertCircle, ArrowUpRight } from 'lucide-react';

interface CriticalAttentionGridProps {
  insights: IntelligenceInsight[];
  onSelectInsight?: (insight: IntelligenceInsight) => void;
}

export const CriticalAttentionGrid: React.FC<CriticalAttentionGridProps> = ({
  insights,
  onSelectInsight,
}) => {
  const getSeverityBadge = (severity: string) => {
    switch (severity.toUpperCase()) {
      case 'CRITICAL':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'HIGH':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'MEDIUM':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-slate-500/10 text-slate-400 border-slate-500/30';
    }
  };

  return (
    <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-base font-bold text-white">Critical Attention Required</h3>
          <p className="text-xs text-slate-400">High-priority correlated items requiring operator intervention.</p>
        </div>
        <span className="text-xs text-slate-400 font-semibold">{insights.length} Correlated Items</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Issue</th>
              <th className="py-3 px-4">Affected Service</th>
              <th className="py-3 px-4">Business Impact</th>
              <th className="py-3 px-4">Source System</th>
              <th className="py-3 px-4 text-right">Recommended Action</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {insights.length === 0 ? (
              <tr>
                <td colSpan={6} className="py-8 text-center text-slate-500">
                  No active critical issues requiring attention.
                </td>
              </tr>
            ) : (
              insights.map((item) => (
                <tr
                  key={item.id}
                  onClick={() => onSelectInsight && onSelectInsight(item)}
                  className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                >
                  <td className="py-3 px-4">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getSeverityBadge(
                        item.severity
                      )}`}
                    >
                      {item.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-semibold text-white max-w-xs">{item.title}</td>
                  <td className="py-3 px-4 font-mono font-bold text-indigo-300">
                    {item.affected_service || 'N/A'}
                  </td>
                  <td className="py-3 px-4 text-amber-200 max-w-xs">{item.business_impact}</td>
                  <td className="py-3 px-4 uppercase text-[10px] font-bold text-slate-400">
                    {item.source_system}
                  </td>
                  <td className="py-3 px-4 text-right font-medium text-slate-200 max-w-xs truncate">
                    {item.recommended_action}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};
