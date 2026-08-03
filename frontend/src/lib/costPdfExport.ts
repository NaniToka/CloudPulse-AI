import type { CostOverviewResponse, CostAnalyzeResponse, RecommendationItem } from "@/types/cost";

export function exportCostReportToPdf(
  overview: CostOverviewResponse | null,
  aiAnalysis: CostAnalyzeResponse | null,
  recommendations: RecommendationItem[]
): void {
  const printWindow = window.open("", "_blank");
  if (!printWindow) {
    alert("Please allow pop-ups to export the PDF cost optimization report.");
    return;
  }

  const monthlyCost = overview?.monthly_cost || 0;
  const potentialSavings = overview?.potential_savings || 0;
  const efficiency = overview?.efficiency_score || 0;

  const recsListHtml = (recommendations || [])
    .map(
      (rec, i) => `
      <div style="border: 1px solid #e2e8f0; border-radius: 6px; padding: 12px; margin-bottom: 10px; background-color: #f8fafc;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
          <strong style="font-size: 13px; color: #1e293b;">${i + 1}. ${rec.title}</strong>
          <span style="font-weight: 700; color: #10b981; font-size: 12px;">Save $${rec.estimated_savings.toLocaleString()}/mo</span>
        </div>
        <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">
          Service: <b>${rec.service}</b> &bull; Resource: <b>${rec.resource_name}</b> &bull; Effort: <b>${rec.effort_level.toUpperCase()}</b> &bull; Risk: <b>${rec.risk_level.toUpperCase()}</b>
        </div>
        <div style="font-size: 12px; color: #334155; line-height: 1.4;">${rec.description}</div>
      </div>
    `
    )
    .join("");

  const htmlContent = `
    <!DOCTYPE html>
    <html>
      <head>
        <title>CloudPulse AI — Cloud Cost Optimization Report</title>
        <style>
          @page { size: A4; margin: 20mm; }
          body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            color: #0f172a; line-height: 1.5; margin: 0; padding: 0; background-color: #ffffff;
          }
          .header {
            border-bottom: 2px solid #e2e8f0; padding-bottom: 16px; margin-bottom: 20px;
            display: flex; justify-content: space-between; align-items: flex-start;
          }
          .logo { font-size: 20px; font-weight: 700; color: #2563eb; letter-spacing: -0.5px; }
          .sub { font-size: 12px; color: #64748b; margin-top: 4px; }
          .meta-grid {
            display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px;
            background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 8px; padding: 14px; margin-bottom: 20px;
          }
          .meta-label { color: #64748b; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 2px; }
          .meta-val { font-weight: 700; color: #0f172a; font-size: 15px; }
          .section { margin-bottom: 20px; }
          .section-title {
            font-size: 13px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.5px;
            color: #334155; border-bottom: 1px solid #cbd5e1; padding-bottom: 4px; margin-bottom: 10px;
          }
          .box {
            background-color: #f8fafc; border-left: 4px solid #2563eb; padding: 12px 16px;
            border-radius: 0 6px 6px 0; font-size: 12px; white-space: pre-wrap;
          }
          .footer {
            margin-top: 30px; padding-top: 12px; border-top: 1px solid #e2e8f0;
            font-size: 10px; color: #94a3b8; text-align: center;
          }
        </style>
      </head>
      <body>
        <div class="header">
          <div>
            <div class="logo">CloudPulse AI — FinOps Cost Optimization Report</div>
            <div class="sub">Generated on ${new Date().toLocaleString()}</div>
          </div>
        </div>

        <div class="meta-grid">
          <div>
            <div class="meta-label">Monthly MTD Spend</div>
            <div class="meta-val">$${monthlyCost.toLocaleString()}</div>
          </div>
          <div>
            <div class="meta-label">Potential Monthly Savings</div>
            <div class="meta-val" style="color: #10b981;">$${potentialSavings.toLocaleString()}</div>
          </div>
          <div>
            <div class="meta-label">Efficiency Score</div>
            <div class="meta-val">${efficiency} / 100</div>
          </div>
          <div>
            <div class="meta-label">Active Opportunities</div>
            <div class="meta-val">${recommendations.length} items</div>
          </div>
        </div>

        ${
          aiAnalysis?.cost_summary
            ? `
          <div class="section">
            <div class="section-title">FinOps AI Executive Summary</div>
            <div class="box">${aiAnalysis.cost_summary}</div>
          </div>
        `
            : ""
        }

        <div class="section">
          <div class="section-title">Optimization Recommendations</div>
          ${recsListHtml || "<p style='font-size: 12px; color: #64748b;'>No active optimization recommendations.</p>"}
        </div>

        <div class="footer">
          Confidential — CloudPulse AI Intelligent Cloud Optimization Platform &bull; Powered by Google FinOps AI Engine
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
