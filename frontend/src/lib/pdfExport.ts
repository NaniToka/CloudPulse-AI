import type { LogAnalysis } from "@/types/log_analysis";

export function exportAnalysisToPdf(analysis: LogAnalysis): void {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Please allow pop-ups to export the PDF analysis report.");
    return;
  }

  const severityColor =
    analysis.severity === "critical"
      ? "#ef4444"
      : analysis.severity === "high"
      ? "#f97316"
      : analysis.severity === "medium"
      ? "#eab308"
      : "#3b82f6";

  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>CloudPulse AI Log Analysis - ${analysis.filename}</title>
        <style>
          @page {
            size: A4;
            margin: 20mm;
          }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a;
            line-height: 1.5;
            margin: 0;
            padding: 0;
            background-color: #ffffff;
          }
          .header {
            border-bottom: 2px solid #e2e8f0;
            padding-bottom: 16px;
            margin-bottom: 24px;
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
          }
          .logo {
            font-size: 20px;
            font-weight: 700;
            color: #2563eb;
            letter-spacing: -0.5px;
          }
          .sub {
            font-size: 12px;
            color: #64748b;
            margin-top: 4px;
          }
          .meta-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 12px;
            background: #f8fafc;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 24px;
          }
          .meta-item {
            font-size: 12px;
          }
          .meta-label {
            color: #64748b;
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 4px;
          }
          .meta-val {
            font-weight: 600;
            color: #1e293b;
          }
          .badge {
            display: inline-block;
            padding: 2px 10px;
            border-radius: 9999px;
            color: white;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            background-color: ${severityColor};
          }
          .section {
            margin-bottom: 24px;
          }
          .section-title {
            font-size: 14px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: #334155;
            border-bottom: 1px solid #cbd5e1;
            padding-bottom: 6px;
            margin-bottom: 12px;
          }
          .box {
            background-color: #f8fafc;
            border-left: 4px solid #3b82f6;
            padding: 14px 18px;
            border-radius: 0 6px 6px 0;
            font-size: 13px;
            white-space: pre-wrap;
          }
          .box.critical {
            border-left-color: ${severityColor};
            background-color: #fef2f2;
          }
          .list {
            margin: 0;
            padding-left: 20px;
            font-size: 13px;
          }
          .list li {
            margin-bottom: 8px;
          }
          .footer {
            margin-top: 40px;
            padding-top: 16px;
            border-top: 1px solid #e2e8f0;
            font-size: 11px;
            color: #94a3b8;
            text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="logo">CloudPulse AI — Root Cause Analysis Report</div>
            <div class="sub">Generated on ${new Date().toLocaleString()}</div>
          </div>
        </div>

        <div class="meta-grid">
          <div class="meta-item">
            <div class="meta-label">File Name</div>
            <div class="meta-val">${analysis.filename}</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Severity</div>
            <div><span class="badge">${analysis.severity || "Unknown"}</span></div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Confidence Score</div>
            <div class="meta-val">${Math.round((analysis.confidence_score || 0) * 100)}%</div>
          </div>
          <div class="meta-item">
            <div class="meta-label">Total Lines / Errors</div>
            <div class="meta-val">${analysis.total_lines} lines (${analysis.error_count} ERR, ${analysis.critical_count} CRIT)</div>
          </div>
        </div>

        <div class="section">
          <div class="section-title">Executive Summary</div>
          <div class="box">
            ${analysis.executive_summary || "No executive summary generated."}
          </div>
        </div>

        <div class="section">
          <div class="section-title">Root Cause Analysis</div>
          <div class="box critical">
            ${analysis.root_cause || "No root cause identified."}
          </div>
        </div>

        <div class="section">
          <div class="section-title">Recommended Fixes</div>
          <div class="box">
            ${analysis.recommended_fixes || "No recommended fixes provided."}
          </div>
        </div>

        <div class="section">
          <div class="section-title">Preventive Measures</div>
          <div class="box">
            ${analysis.preventive_measures || "No preventive measures specified."}
          </div>
        </div>

        <div class="footer">
          Confidential — CloudPulse AI Intelligent Incident Response Platform &bull; Powered by Google Gemini
        </div>

        <script>
          window.onload = function() {
            window.print();
          };
        </script>
      </body>
    </html>
  `;

  printWindow.document.write(htmlContent);
  printWindow.document.close();
}
