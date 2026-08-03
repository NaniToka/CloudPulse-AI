import React from "react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function CostLoadingSkeleton() {
  return (
    <div className="space-y-6">
      {/* 4 Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {[1, 2, 3, 4].map((i) => (
          <Card key={i} className="border-white/[0.08] bg-card/60">
            <CardContent className="p-5 space-y-3">
              <div className="h-3 bg-white/10 rounded w-1/2 animate-pulse" />
              <div className="h-7 bg-white/10 rounded w-3/4 animate-pulse" />
              <div className="h-3 bg-white/10 rounded w-1/3 animate-pulse" />
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Chart Skeletons */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        <Card className="xl:col-span-2 border-white/[0.08] bg-card/60">
          <CardHeader className="pb-2">
            <div className="h-4 bg-white/10 rounded w-1/3 animate-pulse" />
          </CardHeader>
          <CardContent className="h-[220px] flex items-center justify-center">
            <div className="w-full h-full bg-white/[0.03] rounded animate-pulse" />
          </CardContent>
        </Card>

        <Card className="border-white/[0.08] bg-card/60">
          <CardHeader className="pb-2">
            <div className="h-4 bg-white/10 rounded w-1/2 animate-pulse" />
          </CardHeader>
          <CardContent className="h-[220px] flex items-center justify-center">
            <div className="w-32 h-32 rounded-full border-4 border-white/10 animate-pulse" />
          </CardContent>
        </Card>
      </div>

      {/* Recommendations Skeleton */}
      <Card className="border-white/[0.08] bg-card/60">
        <CardHeader>
          <div className="h-5 bg-white/10 rounded w-1/4 animate-pulse" />
        </CardHeader>
        <CardContent className="space-y-3">
          <div className="h-16 bg-white/[0.04] rounded animate-pulse" />
          <div className="h-16 bg-white/[0.04] rounded animate-pulse" />
        </CardContent>
      </Card>
    </div>
  );
}
