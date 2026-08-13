import React, { useState } from 'react';
import { SloViolation } from '../../types/slo';
import { AlertCircle, ShieldAlert, Link as LinkIcon, Search } from 'lucide-react';

interface SloViolationsTableProps {
  violations: SloViolation[];
  onViewIncident?: (incidentId: string) => void;
}

export const SloViolationsTable: React.FC<SloViolationsTableProps> = ({
  violations,
  onViewIncident,
}) => {
  const [severityFilter, setSeverityFilter] = useState('ALL');

  const filteredViolations = violations.filter(
    (v) => severityFilter === 'ALL' || v.severity.toUpperCase() === severityFilter
  );

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
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-4">
        <div>
          <h3 className="text-base font-semibold text-white">Active SLO & SLA Breaches</h3>
          <p className="text-xs text-slate-400">
            Detected availability, latency, error-rate breaches and correlated incidents.
          </p>
        </div>

        <div className="flex items-center gap-1.5 bg-slate-800/80 p-1 rounded-lg border border-slate-700">
          {['ALL', 'CRITICAL', 'HIGH', 'MEDIUM'].map((sev) => (
            <button
              key={sev}
              onClick={() => setSeverityFilter(sev)}
              className={`px-2.5 py-1 text-xs font-semibold rounded-md transition-colors ${
                severityFilter === sev
                  ? 'bg-rose-500 text-white shadow'
                  : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {sev}
            </button>
          ))}
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-800/60 text-slate-400 uppercase text-[10px] tracking-wider border-b border-slate-700">
            <tr>
              <th className="py-3 px-4">Severity</th>
              <th className="py-3 px-4">Service</th>
              <th className="py-3 px-4">Violation Type</th>
              <th className="py-3 px-4">Target vs Actual</th>
              <th className="py-3 px-4">Difference</th>
              <th className="py-3 px-4">Explanation</th>
              <th className="py-3 px-4 text-right">Correlated Incident</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {filteredViolations.length === 0 ? (
              <tr>
                <td colSpan={7} className="py-8 text-center text-slate-500">
                  No active SLO violations match current criteria.
                </td>
              </tr>
            ) : (
              filteredViolations.map((v) => (
                <tr key={v.id} className="hover:bg-slate-800/30 transition-colors">
                  <td className="py-3 px-4">
                    <span
                      className={`px-2.5 py-0.5 rounded-full text-[10px] font-bold border ${getSeverityBadge(
                        v.severity
                      )}`}
                    >
                      {v.severity}
                    </span>
                  </td>
                  <td className="py-3 px-4 font-mono font-bold text-white">{v.service}</td>
                  <td className="py-3 px-4 font-semibold text-slate-300">{v.violation_type}</td>
                  <td className="py-3 px-4 font-mono text-slate-300">
                    {v.actual_value} (Target: {v.target_value})
                  </td>
                  <td className="py-3 px-4 font-mono text-rose-400 font-bold">
                    -{v.difference}
                  </td>
                  <td className="py-3 px-4 text-slate-400 max-w-xs truncate">{v.explanation}</td>
                  <td className="py-3 px-4 text-right">
                    {v.incident_id && (
                      <button
                        onClick={() => onViewIncident && onViewIncident(v.incident_id!)}
                        className="inline-flex items-center gap-1.5 px-2.5 py-1 bg-indigo-500/10 hover:bg-indigo-500/20 text-indigo-300 border border-indigo-500/30 rounded text-xs font-semibold transition-colors"
                      >
                        <LinkIcon className="w-3 h-3" /> Incident
                      </button>
                    )}
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
