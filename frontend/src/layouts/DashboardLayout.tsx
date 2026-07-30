import { useState } from "react";
import { Outlet } from "react-router-dom";
import Sidebar from "@/components/dashboard/Sidebar";
import Navbar from "@/components/dashboard/Navbar";

export default function DashboardLayout() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-bg-void">
      <Sidebar
        collapsed={collapsed}
        onCollapse={setCollapsed}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />

      <div className="flex flex-1 flex-col min-w-0">
        <Navbar
          sidebarCollapsed={collapsed}
          onMobileMenuOpen={() => setMobileOpen(true)}
        />

        <main className="flex-1 overflow-y-auto">
          <div className="p-4 sm:p-6 max-w-[1600px] mx-auto">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
