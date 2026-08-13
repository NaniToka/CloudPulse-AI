import React from 'react';
import { ShieldCheck, PiggyBank, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const SecurityAndFinOpsSummary: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Security Posture Summary */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <ShieldCheck className="w-5 h-5 text-emerald-400" />
            <h3 className="text-base font-bold text-white">Security & Compliance Posture</h3>
          </div>
          <span className="text-xs text-slate-400 font-semibold">CIS Benchmark Score: 85.0</span>
        </div>

        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">Critical Vulnerabilities</div>
            <div className="text-lg font-bold font-mono text-rose-400 mt-1">0</div>
          </div>
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">High Severity Findings</div>
            <div className="text-lg font-bold font-mono text-amber-400 mt-1">1</div>
          </div>
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">Security Risk Score</div>
            <div className="text-lg font-bold font-mono text-emerald-400 mt-1">22.0</div>
          </div>
        </div>

        <p className="text-xs text-slate-300">
          Bucket <code className="text-amber-300 bg-slate-800 px-1 py-0.5 rounded">analytics-s3-prod</code> has public read access enabled. CIS Benchmark rule 2.1 violated.
        </p>
      </div>

      {/* FinOps Governance Summary */}
      <div className="bg-slate-900/70 border border-slate-800 rounded-xl p-5 shadow-lg backdrop-blur-md space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <PiggyBank className="w-5 h-5 text-indigo-400" />
            <h3 className="text-base font-bold text-white">FinOps & Cost Intelligence Summary</h3>
          </div>
          <span className="text-xs text-slate-400 font-semibold">Governance Score: 88.0</span>
        </div>

        <div className="grid grid-cols-3 gap-3 text-xs">
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">Monthly Spend</div>
            <div className="text-lg font-bold font-mono text-white mt-1">$42,500</div>
          </div>
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">Potential Savings</div>
            <div className="text-lg font-bold font-mono text-emerald-400 mt-1">$3,450</div>
          </div>
          <div className="p-3 bg-slate-800/50 rounded border border-slate-700">
            <div className="text-slate-400 text-[10px]">Cost Anomalies</div>
            <div className="text-lg font-bold font-mono text-amber-400 mt-1">1</div>
          </div>
        </div>

        <p className="text-xs text-slate-300">
          Detected 14 unattached gp3 EBS volumes and overprovisioned RDS database instance in us-east-1.
        </p>
      </div>
    </div>
  );
};
