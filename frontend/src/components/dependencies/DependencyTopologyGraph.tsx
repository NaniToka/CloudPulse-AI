import React, { useState, useRef, useMemo, useEffect } from 'react';
import {
  ZoomIn,
  ZoomOut,
  Maximize2,
  RotateCcw,
  Server,
  Database,
  Layers,
  Activity,
  AlertTriangle,
  CheckCircle2,
  Flame,
  ArrowRight,
  Zap,
  Globe,
  Radio,
} from 'lucide-react';
import type { ServiceNode, ServiceDependency } from '@/types/dependency';

interface DependencyTopologyGraphProps {
  nodes: ServiceNode[];
  edges: ServiceDependency[];
  selectedNodeId?: string | null;
  highlightedPath?: string[];
  rootCauseService?: string | null;
  onSelectNode: (node: ServiceNode) => void;
  className?: string;
}

interface NodePosition {
  x: number;
  y: number;
  tier: number;
}

export const DependencyTopologyGraph: React.FC<DependencyTopologyGraphProps> = ({
  nodes,
  edges,
  selectedNodeId,
  highlightedPath = [],
  rootCauseService,
  onSelectNode,
  className = '',
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [zoom, setZoom] = useState<number>(1);
  const [pan, setPan] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState<boolean>(false);
  const [dragStart, setDragStart] = useState<{ x: number; y: number }>({ x: 0, y: 0 });
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);
  const [hoveredEdgeId, setHoveredEdgeId] = useState<string | null>(null);

  // Compute layered positions based on topological role
  const nodePositions = useMemo<Record<string, NodePosition>>(() => {
    const pos: Record<string, NodePosition> = {};
    if (!nodes.length) return pos;

    // Categorize nodes into 4 topological tiers:
    // Tier 0: Ingress / Gateway / Frontend
    // Tier 1: Core Business Microservices (order, checkout, auth)
    // Tier 2: Internal Microservices / Workers / Queues
    // Tier 3: Storage / Databases / Caches (postgres, redis, mysql)
    const tiers: Record<number, ServiceNode[]> = { 0: [], 1: [], 2: [], 3: [] };

    nodes.forEach((n) => {
      const name = n.name.toLowerCase();
      const type = n.type.toLowerCase();

      if (type === 'api' || type === 'gateway' || name.includes('gateway') || name.includes('ingress')) {
        tiers[0].push(n);
      } else if (type === 'database' || type === 'cache' || name.includes('db') || name.includes('postgres') || name.includes('redis')) {
        tiers[3].push(n);
      } else if (type === 'queue' || name.includes('worker') || name.includes('payment')) {
        tiers[2].push(n);
      } else {
        tiers[1].push(n);
      }
    });

    const tierY = [80, 240, 400, 560];
    const width = 900;

    Object.entries(tiers).forEach(([tierKey, tierNodes]) => {
      const t = Number(tierKey);
      const count = tierNodes.length;
      if (count === 0) return;

      const spacing = width / (count + 1);
      tierNodes.forEach((node, idx) => {
        pos[node.id] = {
          x: Math.round(spacing * (idx + 1)),
          y: tierY[t],
          tier: t,
        };
        // Also map by service name for resilient lookups
        pos[node.name.toLowerCase()] = pos[node.id];
      });
    });

    return pos;
  }, [nodes]);

  // Pan & Drag Handlers
  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === containerRef.current || (e.target as HTMLElement).tagName === 'svg') {
      setIsDragging(true);
      setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPan({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => setIsDragging(false);

  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomDelta = e.deltaY > 0 ? -0.1 : 0.1;
    setZoom((prev) => Math.min(2.5, Math.max(0.4, prev + zoomDelta)));
  };

  const resetView = () => {
    setZoom(1);
    setPan({ x: 0, y: 0 });
  };

  const getNodeColor = (node: ServiceNode) => {
    if (node.name.toLowerCase() === rootCauseService?.toLowerCase()) {
      return {
        border: 'border-rose-500 ring-4 ring-rose-500/30 shadow-rose-500/40',
        bg: 'bg-rose-950/80',
        text: 'text-rose-300',
        badge: 'bg-rose-500/20 text-rose-300 border-rose-500/40',
      };
    }
    switch (node.status) {
      case 'CRITICAL':
        return {
          border: 'border-rose-500/80 ring-2 ring-rose-500/20 shadow-rose-500/20',
          bg: 'bg-rose-950/50',
          text: 'text-rose-300',
          badge: 'bg-rose-500/20 text-rose-300 border-rose-500/30',
        };
      case 'DEGRADED':
        return {
          border: 'border-amber-500/80 ring-2 ring-amber-500/20 shadow-amber-500/20',
          bg: 'bg-amber-950/50',
          text: 'text-amber-300',
          badge: 'bg-amber-500/20 text-amber-300 border-amber-500/30',
        };
      case 'HEALTHY':
      default:
        return {
          border: 'border-emerald-500/50 hover:border-emerald-400',
          bg: 'bg-slate-900/90',
          text: 'text-emerald-300',
          badge: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
        };
    }
  };

  const getNodeIcon = (type: string) => {
    switch (type.toLowerCase()) {
      case 'database':
      case 'cache':
        return <Database className="w-4 h-4 text-cyan-400" />;
      case 'api':
      case 'gateway':
        return <Globe className="w-4 h-4 text-purple-400" />;
      case 'queue':
        return <Radio className="w-4 h-4 text-amber-400" />;
      default:
        return <Server className="w-4 h-4 text-blue-400" />;
    }
  };

  return (
    <div
      ref={containerRef}
      className={`relative w-full h-[620px] bg-slate-950/90 border border-slate-800/80 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-xl select-none ${className}`}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
      style={{ cursor: isDragging ? 'grabbing' : 'grab' }}
    >
      {/* Background Tech Grid */}
      <div
        className="absolute inset-0 opacity-20 pointer-events-none"
        style={{
          backgroundImage: `
            radial-gradient(circle at 1px 1px, rgba(56, 189, 248, 0.25) 1px, transparent 0),
            linear-gradient(to right, rgba(30, 41, 59, 0.3) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(30, 41, 59, 0.3) 1px, transparent 1px)
          `,
          backgroundSize: '32px 32px, 64px 64px, 64px 64px',
        }}
      />

      {/* Floating Canvas Controls */}
      <div className="absolute top-4 right-4 z-20 flex items-center gap-1.5 p-1.5 bg-slate-900/90 border border-slate-800 rounded-xl shadow-xl backdrop-blur-md">
        <button
          onClick={() => setZoom((z) => Math.min(2.5, z + 0.15))}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom In"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={() => setZoom((z) => Math.max(0.4, z - 0.15))}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Zoom Out"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <div className="w-px h-5 bg-slate-800 my-auto" />
        <button
          onClick={resetView}
          className="p-2 text-slate-400 hover:text-white hover:bg-slate-800 rounded-lg transition-colors"
          title="Reset View"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
        <div className="px-2.5 py-1 text-xs font-mono text-cyan-400 bg-cyan-950/40 rounded-md border border-cyan-900/50">
          {Math.round(zoom * 100)}%
        </div>
      </div>

      {/* Legend & Status Pills */}
      <div className="absolute bottom-4 left-4 z-20 flex items-center gap-3 p-2 bg-slate-900/90 border border-slate-800 rounded-xl shadow-xl backdrop-blur-md text-xs">
        <div className="flex items-center gap-1.5 text-emerald-400">
          <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm shadow-emerald-500/50" />
          <span>Healthy (100-85)</span>
        </div>
        <div className="flex items-center gap-1.5 text-amber-400">
          <span className="w-2.5 h-2.5 rounded-full bg-amber-500 shadow-sm shadow-amber-500/50" />
          <span>Degraded (84-50)</span>
        </div>
        <div className="flex items-center gap-1.5 text-rose-400">
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-ping" />
          <span className="w-2.5 h-2.5 rounded-full bg-rose-500 -ml-4" />
          <span>Critical (&lt;50)</span>
        </div>
        {rootCauseService && (
          <div className="flex items-center gap-1.5 px-2 py-0.5 bg-rose-950/60 border border-rose-500/50 rounded text-rose-300 font-medium">
            <Flame className="w-3.5 h-3.5 text-rose-400 animate-bounce" />
            <span>Root Cause: {rootCauseService}</span>
          </div>
        )}
      </div>

      {/* SVG Canvas for Links & Nodes */}
      <div
        className="w-full h-full transform-gpu origin-top-left transition-transform duration-75"
        style={{
          transform: `translate(${pan.x}px, ${pan.y}px) scale(${zoom})`,
        }}
      >
        <svg className="w-[1200px] h-[800px] overflow-visible">
          <defs>
            {/* Arrow Marker Definitions */}
            <marker
              id="arrow-normal"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b" />
            </marker>
            <marker
              id="arrow-highlight"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="7"
              markerHeight="7"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#f43f5e" />
            </marker>
            <marker
              id="arrow-cyan"
              viewBox="0 0 10 10"
              refX="22"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#38bdf8" />
            </marker>
          </defs>

          {/* Directed Dependency Edges */}
          {edges.map((edge) => {
            const srcPos = nodePositions[edge.source_service.toLowerCase()];
            const tgtPos = nodePositions[edge.target_service.toLowerCase()];
            if (!srcPos || !tgtPos) return null;

            const isPathHighlighted =
              highlightedPath.includes(edge.source_service.toLowerCase()) &&
              highlightedPath.includes(edge.target_service.toLowerCase());

            const isEdgeHovered = hoveredEdgeId === edge.id;

            // Bezier curve calculation
            const dx = tgtPos.x - srcPos.x;
            const dy = tgtPos.y - srcPos.y;
            const cx1 = srcPos.x;
            const cy1 = srcPos.y + dy * 0.5;
            const cx2 = tgtPos.x;
            const cy2 = tgtPos.y - dy * 0.5;

            const pathD = `M ${srcPos.x} ${srcPos.y} C ${cx1} ${cy1}, ${cx2} ${cy2}, ${tgtPos.x} ${tgtPos.y}`;

            const midX = (srcPos.x + tgtPos.x) / 2;
            const midY = (srcPos.y + tgtPos.y) / 2;

            const strokeColor = isPathHighlighted
              ? '#f43f5e'
              : edge.error_rate > 5
              ? '#fbbf24'
              : '#38bdf8';

            return (
              <g
                key={edge.id}
                className="transition-all duration-300"
                onMouseEnter={() => setHoveredEdgeId(edge.id)}
                onMouseLeave={() => setHoveredEdgeId(null)}
              >
                {/* Glow underlay on highlight */}
                {isPathHighlighted && (
                  <path
                    d={pathD}
                    fill="none"
                    stroke="#f43f5e"
                    strokeWidth="6"
                    strokeOpacity="0.4"
                    strokeLinecap="round"
                    className="animate-pulse"
                  />
                )}

                {/* Primary Edge Line */}
                <path
                  d={pathD}
                  fill="none"
                  stroke={strokeColor}
                  strokeWidth={isPathHighlighted ? 2.5 : isEdgeHovered ? 2 : 1.5}
                  strokeDasharray={edge.discovered_from === 'config' ? '4,4' : undefined}
                  markerEnd={isPathHighlighted ? 'url(#arrow-highlight)' : 'url(#arrow-cyan)'}
                  opacity={isPathHighlighted || isEdgeHovered ? 1 : 0.65}
                />

                {/* Edge Telemetry Badge at midpoint */}
                <foreignObject
                  x={midX - 45}
                  y={midY - 12}
                  width="90"
                  height="24"
                  className="overflow-visible pointer-events-auto"
                >
                  <div
                    className={`flex items-center justify-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-mono border backdrop-blur-md shadow-lg ${
                      isPathHighlighted
                        ? 'bg-rose-950/90 text-rose-300 border-rose-500/60'
                        : edge.error_rate > 5
                        ? 'bg-amber-950/80 text-amber-300 border-amber-500/40'
                        : 'bg-slate-900/85 text-slate-300 border-slate-700/60'
                    }`}
                  >
                    <span>{edge.protocol || 'HTTP'}</span>
                    <span className="text-slate-500">•</span>
                    <span>{Math.round(edge.latency_ms)}ms</span>
                  </div>
                </foreignObject>
              </g>
            );
          })}
        </svg>

        {/* Interactive Microservice Node Cards */}
        {nodes.map((node) => {
          const pos = nodePositions[node.id] || nodePositions[node.name.toLowerCase()];
          if (!pos) return null;

          const isSelected = selectedNodeId === node.id || selectedNodeId === node.name;
          const isRootCause = node.name.toLowerCase() === rootCauseService?.toLowerCase();
          const colors = getNodeColor(node);

          return (
            <div
              key={node.id}
              onClick={() => onSelectNode(node)}
              onMouseEnter={() => setHoveredNodeId(node.id)}
              onMouseLeave={() => setHoveredNodeId(null)}
              className={`absolute transform -translate-x-1/2 -translate-y-1/2 cursor-pointer transition-all duration-200 z-10 ${
                isSelected ? 'scale-105 z-30' : 'hover:scale-102 hover:z-20'
              }`}
              style={{ left: pos.x, top: pos.y }}
            >
              <div
                className={`w-52 p-3 rounded-xl border backdrop-blur-xl shadow-xl transition-all ${colors.border} ${colors.bg}`}
              >
                {/* Node Header */}
                <div className="flex items-center justify-between gap-2 mb-2">
                  <div className="flex items-center gap-2 min-w-0">
                    <div className="p-1.5 rounded-lg bg-slate-800/80 border border-slate-700/50">
                      {getNodeIcon(node.type)}
                    </div>
                    <div className="min-w-0">
                      <h4 className="text-xs font-semibold text-white truncate max-w-[110px]" title={node.name}>
                        {node.name}
                      </h4>
                      <span className="text-[10px] text-slate-400 font-mono capitalize">
                        {node.environment}
                      </span>
                    </div>
                  </div>

                  {/* Health Score Pill */}
                  <div
                    className={`px-1.5 py-0.5 rounded-md text-[10px] font-bold font-mono border ${colors.badge}`}
                  >
                    {Math.round(node.health_score)}%
                  </div>
                </div>

                {/* Telemetry Metrics Grid */}
                <div className="grid grid-cols-3 gap-1 pt-2 border-t border-slate-800/60 text-[10px] font-mono">
                  <div className="bg-slate-950/40 rounded p-1 text-center">
                    <div className="text-slate-400 text-[9px]">P99</div>
                    <div className="text-slate-200 font-semibold">{Math.round(node.latency_p99_ms)}ms</div>
                  </div>
                  <div className="bg-slate-950/40 rounded p-1 text-center">
                    <div className="text-slate-400 text-[9px]">Error</div>
                    <div className={node.error_rate > 2 ? 'text-rose-400 font-bold' : 'text-slate-200'}>
                      {node.error_rate.toFixed(1)}%
                    </div>
                  </div>
                  <div className="bg-slate-950/40 rounded p-1 text-center">
                    <div className="text-slate-400 text-[9px]">RPS</div>
                    <div className="text-slate-200 font-semibold">{Math.round(node.request_rate)}</div>
                  </div>
                </div>

                {/* Root Cause or Active Incident Badge */}
                {isRootCause && (
                  <div className="mt-2 flex items-center justify-center gap-1 py-0.5 bg-rose-500/20 border border-rose-500/50 rounded text-[10px] font-semibold text-rose-300 animate-pulse">
                    <Flame className="w-3 h-3 text-rose-400" />
                    <span>PRIMARY ROOT CAUSE</span>
                  </div>
                )}
                {!isRootCause && node.active_incidents_count > 0 && (
                  <div className="mt-2 flex items-center justify-center gap-1 py-0.5 bg-amber-500/20 border border-amber-500/40 rounded text-[10px] font-medium text-amber-300">
                    <AlertTriangle className="w-3 h-3 text-amber-400" />
                    <span>{node.active_incidents_count} Active Incident{node.active_incidents_count > 1 ? 's' : ''}</span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
