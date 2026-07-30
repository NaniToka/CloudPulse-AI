import PageHeader from "@/components/shared/PageHeader";
import InfraHealthPanel from "@/components/dashboard/InfraHealthPanel";
import CpuChart from "@/components/dashboard/CpuChart";
import MemoryChart from "@/components/dashboard/MemoryChart";
import NetworkChart from "@/components/dashboard/NetworkChart";

export default function InfrastructurePage() {
  return (
    <div className="space-y-6">
      <PageHeader title="Infrastructure Monitor" subtitle="Real-time health across all cloud providers" />
      <InfraHealthPanel />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2 xl:grid-cols-3">
        <CpuChart />
        <MemoryChart />
        <NetworkChart />
      </div>
    </div>
  );
}
