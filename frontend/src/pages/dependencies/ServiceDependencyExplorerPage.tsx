import React, { useState, useEffect, useMemo } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  Network,
  RefreshCw,
  Zap,
  Flame,
  Search,
  Filter,
  Layers,
  Server,
  Database,
  Activity,
  AlertTriangle,
  CheckCircle2,
  ArrowRight,
  TrendingUp,
  Cpu,
  Radio,
  Play,
  ShieldAlert,
  Bot,
  ExternalLink,
  ChevronRight,
  Sliders,
  DollarSign,
} from 'lucide-react';
import { DependencyTopologyGraph } from '@/components/dependencies/DependencyTopologyGraph';
import { dependencyService } from '@/services/dependencyService';
import type {
  ServiceNode,
  ServiceDependency,
  DependencyGraph,
  ServiceNodeDetail,
  BlastRadiusResult,
  RootCauseRankingResult,
} from '@/types/dependency';

export const ServiceDependencyExplorerPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();

  // URL Query Parameters
  const initialService = searchParams.get('service');
  const initialIncidentId = searchParams.get('incident_id');

  // State
  const [graphData, setGraphData] = useState<DependencyGraph | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [discovering, setDiscovering] = useState<boolean>(false);
  const [selectedNode, setSelectedNode] = useState<ServiceNode | null>(null);
  const [selectedNodeDetail, setSelectedNodeDetail] = useState<ServiceNodeDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState<boolean>(false);

  // Filters
  const [envFilter, setEnvFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [viewMode, setViewMode] = useState<'graph' | 'matrix' | 'blast'>('graph');

  // Intelligence & RCA State
  const [blastRadius, setBlastRadius] = useState<BlastRadiusResult | null>(null);
  const [blastLoading, setBlastLoading] = useState<boolean>(false);
  const [rcaResult, setRcaResult] = useState<RootCauseRankingResult | null>(null);
  const [rcaLoading, setRcaLoading] = useState<boolean>(false);
  const [drawerTab, setDrawerTab] = useState<'overview' | 'blast' | 'rca'>('overview');

  // Fetch Graph Data
  const loadGraph = async () => {
    try {
      setLoading(true);
      const data = await dependencyService.getGraph({
        environment: envFilter !== 'all' ? envFilter : undefined,
      });
      setGraphData(data);

      // If initial service from URL is present, select it
      if (initialService && data.nodes) {
        const found = data.nodes.find(
          (n) => n.name.toLowerCase() === initialService.toLowerCase()
        );
        if (found) {
          handleSelectNode(found);
        }
      }
    } catch (err) {
      console.error('Failed to load dependency graph:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadGraph();
  }, [envFilter]);

  // Handle Incident Deep-Linking RCA
  useEffect(() => {
    if (initialIncidentId) {
      handleRunIncidentRCA(initialIncidentId);
    }
  }, [initialIncidentId]);

  // Handle Node Selection
  const handleSelectNode = async (node: ServiceNode) => {
    setSelectedNode(node);
    try {
      setDetailLoading(true);
      const detail = await dependencyService.getServiceDetail(node.id);
      setSelectedNodeDetail(detail);
    } catch (err) {
      console.error('Failed to load service detail:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  // Trigger Multi-Modal Discovery
  const handleTriggerDiscovery = async () => {
    try {
      setDiscovering(true);
      await dependencyService.discoverDependencies({
        include_traces: true,
        include_k8s: true,
        include_cloud: true,
        include_logs: true,
      });
      await loadGraph();
    } catch (err) {
      console.error('Discovery failed:', err);
    } finally {
      setDiscovering(false);
    }
  };

  // Simulate Blast Radius
  const handleSimulateBlastRadius = async (serviceName?: string) => {
    const target = serviceName || selectedNode?.name || 'payment-service';
    try {
      setBlastLoading(true);
      setDrawerTab('blast');
      const result = await dependencyService.calculateBlastRadius({
        service_name: target,
        depth: 5,
      });
      setBlastRadius(result);
    } catch (err) {
      console.error('Blast radius calculation failed:', err);
    } finally {
      setBlastLoading(false);
    }
  };

  // Run AI Root Cause Analysis
  const handleRunRCA = async (serviceName?: string) => {
    const target = serviceName || selectedNode?.name || 'api-gateway';
    try {
      setRcaLoading(true);
      setDrawerTab('rca');
      const result = await dependencyService.rankRootCauses({
        service_name: target,
      });
      setRcaResult(result);
      if (result.blast_radius) {
        setBlastRadius(result.blast_radius);
      }
    } catch (err) {
      console.error('Root cause analysis failed:', err);
    } finally {
      setRcaLoading(false);
    }
  };

  // Run RCA for Incident
  const handleRunIncidentRCA = async (incidentId: string) => {
    try {
      setRcaLoading(true);
      setDrawerTab('rca');
      const result = await dependencyService.getIncidentAnalysis(incidentId);
      setRcaResult(result);
      if (result.blast_radius) {
        setBlastRadius(result.blast_radius);
      }
    } catch (err) {
      console.error('Incident RCA failed:', err);
    } finally {
      setRcaLoading(false);
    }
  };

  // Filtered Nodes & Edges
  const filteredNodes = useMemo(() => {
    if (!graphData?.nodes) return [];
    return graphData.nodes.filter((node) => {
      const matchEnv = envFilter === 'all' || node.environment.toLowerCase() === envFilter.toLowerCase();
      const matchStatus = statusFilter === 'all' || node.status.toLowerCase() === statusFilter.toLowerCase();
      const matchSearch =
        !searchQuery ||
        node.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.type.toLowerCase().includes(searchQuery.toLowerCase());
      return matchEnv && matchStatus && matchSearch;
    });
  }, [graphData, envFilter, statusFilter, searchQuery]);

  const filteredEdges = useMemo(() => {
    if (!graphData?.edges) return [];
    const validNodeNames = new Set(filteredNodes.map((n) => n.name.toLowerCase()));
    return graphData.edges.filter(
      (e) => validNodeNames.has(e.source_service.toLowerCase()) && validNodeNames.has(e.target_service.toLowerCase())
    );
  }, [graphData, filteredNodes]);

  // Highlighted failure paths
  const highlightedPath = useMemo(() => {
    if (blastRadius?.affected_services) {
      return blastRadius.affected_services.map((s) => s.toLowerCase());
    }
    if (rcaResult?.primary_root_cause) {
      return [rcaResult.primary_root_cause.toLowerCase()];
    }
    return [];
  }, [blastRadius, rcaResult]);

  // Aggregate Stats
  const stats = useMemo(() => {
    const total = graphData?.nodes?.length || 0;
    const healthy = graphData?.nodes?.filter((n) => n.status === 'HEALTHY').length || 0;
    const degraded = graphData?.nodes?.filter((n) => n.status === 'DEGRADED').length || 0;
    const critical = graphData?.nodes?.filter((n) => n.status === 'CRITICAL').length || 0;
    const avgLatency =
      total > 0
        ? Math.round(
            (graphData?.nodes?.reduce((acc, n) => acc + (n.latency_p99_ms || 0), 0) || 0) / total
          )
        : 0;

    return { total, healthy, degraded, critical, avgLatency };
  }, [graphData]);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4 border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <div className="p-2 rounded-xl bg-cyan-500/10 border border-cyan-500/30 text-cyan-400">
              <Network className="w-6 h-6" />
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                Service Dependency & Root-Cause Engine
                <span className="px-2 py-0.5 text-xs font-semibold uppercase bg-cyan-500/20 text-cyan-300 border border-cyan-500/30 rounded-full">
                  Enterprise AIOps
                </span>
              </h1>
              <p className="text-sm text-slate-400">
                Topological graph modeling, live health scoring, failure blast radius simulation, and Grounded Gemini diagnostics.
              </p>
            </div>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex flex-wrap items-center gap-2.5">
          <button
            onClick={handleTriggerDiscovery}
            disabled={discovering}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-slate-900 hover:bg-slate-800 text-cyan-300 border border-cyan-500/30 hover:border-cyan-500/60 shadow-lg shadow-cyan-950/40 transition-all disabled:opacity-50"
          >
            <Zap className={`w-4 h-4 text-cyan-400 ${discovering ? 'animate-spin' : ''}`} />
            <span>{discovering ? 'Discovering Telemetry...' : 'Auto-Discover Graph'}</span>
          </button>

          <button
            onClick={() => handleSimulateBlastRadius()}
            disabled={blastLoading}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-amber-950/60 hover:bg-amber-900/60 text-amber-300 border border-amber-500/40 shadow-lg transition-all disabled:opacity-50"
          >
            <Flame className="w-4 h-4 text-amber-400" />
            <span>{blastLoading ? 'Simulating Blast Radius...' : 'Simulate Blast Radius'}</span>
          </button>

          <button
            onClick={() => handleRunRCA()}
            disabled={rcaLoading}
            className="flex items-center gap-2 px-3.5 py-2 text-xs font-semibold rounded-xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white shadow-lg shadow-purple-950/50 transition-all disabled:opacity-50"
          >
            <Bot className="w-4 h-4" />
            <span>{rcaLoading ? 'Analyzing Cascade...' : 'AI Root Cause Analysis'}</span>
          </button>

          <button
            onClick={loadGraph}
            disabled={loading}
            className="p-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-300 border border-slate-800 transition-colors"
            title="Refresh"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
        </div>
      </div>

      {/* KPI Stats Strip */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-3.5">
        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-xs text-slate-400 mb-1">
            <span>Total Services</span>
            <Server className="w-4 h-4 text-slate-500" />
          </div>
          <div className="text-2xl font-bold font-mono text-white">{stats.total}</div>
          <div className="text-[11px] text-slate-500 mt-1">{graphData?.total_edges || 0} active dependencies</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-xs text-emerald-400 mb-1">
            <span>Healthy Services</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-emerald-400">{stats.healthy}</div>
          <div className="text-[11px] text-slate-500 mt-1">
            {stats.total > 0 ? Math.round((stats.healthy / stats.total) * 100) : 100}% nominal
          </div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-xs text-amber-400 mb-1">
            <span>Degraded Services</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-amber-400">{stats.degraded}</div>
          <div className="text-[11px] text-slate-500 mt-1">Health &lt; 85%</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-xs text-rose-400 mb-1">
            <span>Critical Failures</span>
            <Flame className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-rose-400">{stats.critical}</div>
          <div className="text-[11px] text-slate-500 mt-1">Requires immediate intervention</div>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800/80 shadow-md">
          <div className="flex items-center justify-between text-xs text-cyan-400 mb-1">
            <span>Avg P99 Latency</span>
            <Activity className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-cyan-300">{stats.avgLatency}ms</div>
          <div className="text-[11px] text-slate-500 mt-1">Cluster baseline</div>
        </div>
      </div>

      {/* Filter & View Mode Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3 p-3 bg-slate-900/90 border border-slate-800 rounded-xl">
        <div className="flex flex-wrap items-center gap-3">
          {/* Search */}
          <div className="relative">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-500" />
            <input
              type="text"
              placeholder="Search services or types..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9 pr-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-200 focus:outline-none focus:border-cyan-500 w-52"
            />
          </div>

          {/* Environment Filter */}
          <select
            value={envFilter}
            onChange={(e) => setEnvFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Environments</option>
            <option value="production">Production</option>
            <option value="staging">Staging</option>
            <option value="development">Development</option>
          </select>

          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-3 py-1.5 bg-slate-950 border border-slate-800 rounded-lg text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="all">All Statuses</option>
            <option value="HEALTHY">Healthy</option>
            <option value="DEGRADED">Degraded</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>

        {/* View Mode Toggle */}
        <div className="flex items-center gap-1 bg-slate-950 p-1 rounded-lg border border-slate-800">
          <button
            onClick={() => setViewMode('graph')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              viewMode === 'graph' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
            }`}
          >
            Topology Graph
          </button>
          <button
            onClick={() => setViewMode('matrix')}
            className={`px-3 py-1 text-xs font-medium rounded-md transition-colors ${
              viewMode === 'matrix' ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40' : 'text-slate-400 hover:text-white'
            }`}
          >
            Service Matrix
          </button>
        </div>
      </div>

      {/* Main Content Area: Split Canvas + Inspector Drawer */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        {/* Left/Center Canvas (8 cols on large screens, or full width if drawer closed) */}
        <div className="lg:col-span-8 space-y-4">
          {viewMode === 'graph' ? (
            <DependencyTopologyGraph
              nodes={filteredNodes}
              edges={filteredEdges}
              selectedNodeId={selectedNode?.id}
              highlightedPath={highlightedPath}
              rootCauseService={rcaResult?.primary_root_cause}
              onSelectNode={handleSelectNode}
            />
          ) : (
            /* Service Matrix Table */
            <div className="bg-slate-900/90 border border-slate-800 rounded-2xl p-4 overflow-x-auto shadow-xl">
              <table className="w-full text-left text-xs">
                <thead>
                  <tr className="border-b border-slate-800 text-slate-400 font-mono">
                    <th className="pb-3 px-3">Service</th>
                    <th className="pb-3 px-3">Type</th>
                    <th className="pb-3 px-3">Health</th>
                    <th className="pb-3 px-3">Error Rate</th>
                    <th className="pb-3 px-3">P99 Latency</th>
                    <th className="pb-3 px-3">Throughput</th>
                    <th className="pb-3 px-3">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-slate-800/60 font-mono">
                  {filteredNodes.map((node) => (
                    <tr
                      key={node.id}
                      onClick={() => handleSelectNode(node)}
                      className={`hover:bg-slate-800/50 cursor-pointer transition-colors ${
                        selectedNode?.id === node.id ? 'bg-cyan-950/30' : ''
                      }`}
                    >
                      <td className="py-3 px-3 font-semibold text-white flex items-center gap-2">
                        <span
                          className={`w-2 h-2 rounded-full ${
                            node.status === 'HEALTHY'
                              ? 'bg-emerald-400'
                              : node.status === 'DEGRADED'
                              ? 'bg-amber-400'
                              : 'bg-rose-400'
                          }`}
                        />
                        {node.name}
                      </td>
                      <td className="py-3 px-3 text-slate-400 uppercase text-[10px]">{node.type}</td>
                      <td className="py-3 px-3 font-bold text-cyan-400">{Math.round(node.health_score)}%</td>
                      <td className="py-3 px-3 text-slate-300">{node.error_rate.toFixed(1)}%</td>
                      <td className="py-3 px-3 text-slate-300">{Math.round(node.latency_p99_ms)}ms</td>
                      <td className="py-3 px-3 text-slate-300">{Math.round(node.request_rate)} rps</td>
                      <td className="py-3 px-3">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleSimulateBlastRadius(node.name);
                          }}
                          className="px-2 py-1 bg-amber-950/60 text-amber-300 hover:bg-amber-900 border border-amber-500/30 rounded text-[10px]"
                        >
                          Blast Radius
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Inspection & Diagnostics Drawer (4 cols) */}
        <div className="lg:col-span-4 bg-slate-900/90 border border-slate-800 rounded-2xl p-5 shadow-2xl backdrop-blur-xl space-y-5">
          {/* Drawer Tabs */}
          <div className="flex items-center justify-between border-b border-slate-800 pb-3">
            <div className="flex items-center gap-1.5">
              <button
                onClick={() => setDrawerTab('overview')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  drawerTab === 'overview'
                    ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Service Detail
              </button>
              <button
                onClick={() => setDrawerTab('blast')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  drawerTab === 'blast'
                    ? 'bg-amber-500/20 text-amber-300 border border-amber-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                Blast Radius
              </button>
              <button
                onClick={() => setDrawerTab('rca')}
                className={`px-3 py-1.5 text-xs font-semibold rounded-lg transition-colors ${
                  drawerTab === 'rca'
                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/40'
                    : 'text-slate-400 hover:text-white'
                }`}
              >
                AI RCA
              </button>
            </div>
          </div>

          {/* TAB 1: SERVICE OVERVIEW & METRICS */}
          {drawerTab === 'overview' && (
            <div className="space-y-4">
              {selectedNode ? (
                <>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-base font-bold text-white flex items-center gap-2">
                        {selectedNode.name}
                        <span
                          className={`px-2 py-0.5 text-[10px] font-mono rounded-full border ${
                            selectedNode.status === 'HEALTHY'
                              ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                              : selectedNode.status === 'DEGRADED'
                              ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                              : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
                          }`}
                        >
                          {selectedNode.status}
                        </span>
                      </h3>
                      <p className="text-xs text-slate-400 font-mono capitalize">
                        Type: {selectedNode.type} • Region: {selectedNode.region}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-xl font-bold font-mono text-cyan-400">
                        {Math.round(selectedNode.health_score)}%
                      </div>
                      <span className="text-[10px] text-slate-500">Health Score</span>
                    </div>
                  </div>

                  {/* Quick Action Bar for selected node */}
                  <div className="grid grid-cols-2 gap-2">
                    <button
                      onClick={() => handleSimulateBlastRadius(selectedNode.name)}
                      className="py-1.5 px-2 bg-amber-950/50 hover:bg-amber-900/50 border border-amber-500/30 text-amber-300 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5"
                    >
                      <Flame className="w-3.5 h-3.5" />
                      <span>Test Blast Radius</span>
                    </button>
                    <button
                      onClick={() => handleRunRCA(selectedNode.name)}
                      className="py-1.5 px-2 bg-purple-950/50 hover:bg-purple-900/50 border border-purple-500/30 text-purple-300 rounded-lg text-xs font-semibold flex items-center justify-center gap-1.5"
                    >
                      <Bot className="w-3.5 h-3.5" />
                      <span>Diagnose RCA</span>
                    </button>
                  </div>

                  {/* Upstream & Downstream Dependency Lists */}
                  {selectedNodeDetail && (
                    <div className="space-y-3 pt-2">
                      <div>
                        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
                          <span>Upstream Callers ({selectedNodeDetail.downstream_dependents?.length || 0})</span>
                          <span className="text-[10px] text-slate-500 lowercase">services calling this</span>
                        </h4>
                        <div className="space-y-1.5">
                          {selectedNodeDetail.downstream_dependents?.length ? (
                            selectedNodeDetail.downstream_dependents.map((dep) => (
                              <div
                                key={dep.id}
                                className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs"
                              >
                                <span className="font-mono text-cyan-300">{dep.source_service}</span>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {dep.protocol} • {Math.round(dep.latency_ms)}ms
                                </span>
                              </div>
                            ))
                          ) : (
                            <div className="text-xs text-slate-500 italic p-2">Ingress gateway (no upstream callers)</div>
                          )}
                        </div>
                      </div>

                      <div>
                        <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2 flex items-center justify-between">
                          <span>Downstream Dependencies ({selectedNodeDetail.upstream_dependencies?.length || 0})</span>
                          <span className="text-[10px] text-slate-500 lowercase">services called by this</span>
                        </h4>
                        <div className="space-y-1.5">
                          {selectedNodeDetail.upstream_dependencies?.length ? (
                            selectedNodeDetail.upstream_dependencies.map((dep) => (
                              <div
                                key={dep.id}
                                className="flex items-center justify-between p-2 rounded-lg bg-slate-950 border border-slate-800 text-xs"
                              >
                                <span className="font-mono text-purple-300">{dep.target_service}</span>
                                <span className="text-[10px] text-slate-500 font-mono">
                                  {dep.protocol} • {Math.round(dep.latency_ms)}ms
                                </span>
                              </div>
                            ))
                          ) : (
                            <div className="text-xs text-slate-500 italic p-2">Leaf backend dependency</div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-12 text-slate-500 space-y-2">
                  <Network className="w-10 h-10 mx-auto text-slate-600 opacity-60" />
                  <p className="text-sm">Click any service node in the graph to inspect live telemetry and dependencies.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: BLAST RADIUS & PROPAGATION */}
          {drawerTab === 'blast' && (
            <div className="space-y-4">
              {blastRadius ? (
                <>
                  <div className="p-3 bg-amber-950/40 border border-amber-500/40 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                        <Flame className="w-4 h-4 text-amber-400" />
                        Root Failure Component
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-mono bg-amber-500/20 text-amber-200 rounded">
                        Impact: {blastRadius.estimated_user_impact}
                      </span>
                    </div>
                    <div className="text-base font-bold font-mono text-white">{blastRadius.root_component}</div>
                    <div className="flex items-center justify-between text-xs text-slate-300 pt-1 border-t border-amber-900/60 font-mono">
                      <span>Financial Risk:</span>
                      <span className="text-amber-400 font-bold">{blastRadius.financial_risk_estimate}</span>
                    </div>
                  </div>

                  {/* Cascading Hops Simulation */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Cascading Failure Propagation ({blastRadius.propagation_hops?.length || 0} Hops)
                    </h4>
                    <div className="space-y-2 max-h-60 overflow-y-auto pr-1">
                      {blastRadius.propagation_hops?.map((hop, idx) => (
                        <div
                          key={idx}
                          className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1 font-mono"
                        >
                          <div className="flex items-center justify-between text-slate-300">
                            <span className="text-rose-400 font-semibold">{hop.source}</span>
                            <ArrowRight className="w-3.5 h-3.5 text-slate-500" />
                            <span className="text-amber-400 font-semibold">{hop.target}</span>
                          </div>
                          <div className="flex items-center justify-between text-[10px] text-slate-500">
                            <span>Latency: +{Math.round(hop.latency_increase_percent)}%</span>
                            <span className="text-rose-400 font-semibold">Error: {hop.error_rate}%</span>
                            <span className="px-1.5 py-0.2 bg-slate-900 rounded text-slate-400">{hop.propagation_risk}</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Affected Resource List */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-1.5">
                      Affected Services ({blastRadius.affected_services?.length || 0})
                    </h4>
                    <div className="flex flex-wrap gap-1.5">
                      {blastRadius.affected_services?.map((svc) => (
                        <span
                          key={svc}
                          className="px-2 py-0.5 text-[11px] font-mono bg-slate-800 text-slate-200 border border-slate-700 rounded-md"
                        >
                          {svc}
                        </span>
                      ))}
                    </div>
                  </div>
                </>
              ) : (
                <div className="text-center py-10 text-slate-500 space-y-2">
                  <Flame className="w-8 h-8 mx-auto text-amber-500 opacity-60" />
                  <p className="text-sm">Click "Simulate Blast Radius" to trace failure propagation paths.</p>
                </div>
              )}
            </div>
          )}

          {/* TAB 3: ROOT CAUSE INTELLIGENCE & AI DIAGNOSTICS */}
          {drawerTab === 'rca' && (
            <div className="space-y-4">
              {rcaResult ? (
                <>
                  {/* Primary Root Cause Badge */}
                  <div className="p-3.5 bg-gradient-to-r from-rose-950/80 to-purple-950/60 border border-rose-500/50 rounded-xl space-y-2">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold text-rose-300 flex items-center gap-1.5">
                        <Flame className="w-4 h-4 text-rose-400" />
                        PRIMARY ROOT CAUSE
                      </span>
                      <span className="px-2 py-0.5 text-[10px] font-mono bg-rose-500/20 text-rose-200 border border-rose-500/40 rounded-full">
                        Confidence: {Math.round(rcaResult.confidence * 100)}%
                      </span>
                    </div>
                    <div className="text-lg font-bold font-mono text-white">{rcaResult.primary_root_cause}</div>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400">
                      <span>Engine:</span>
                      <span className="font-mono text-purple-300 uppercase px-1.5 py-0.5 bg-purple-950/80 rounded border border-purple-500/30">
                        {rcaResult.analysis_engine}
                      </span>
                    </div>
                  </div>

                  {/* AI Reasoning Summary */}
                  <div className="p-3 bg-slate-950 border border-slate-800 rounded-xl space-y-1">
                    <div className="text-xs font-semibold text-purple-300 flex items-center gap-1.5">
                      <Bot className="w-3.5 h-3.5 text-purple-400" />
                      Diagnostic Reasoning
                    </div>
                    <p className="text-xs text-slate-300 leading-relaxed">{rcaResult.reasoning_summary}</p>
                  </div>

                  {/* Candidate Ranking List */}
                  <div>
                    <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wider mb-2">
                      Ranked Root Cause Candidates
                    </h4>
                    <div className="space-y-2 max-h-52 overflow-y-auto pr-1">
                      {rcaResult.candidates?.slice(0, 4).map((c) => (
                        <div
                          key={c.service_name}
                          className="p-2.5 rounded-lg bg-slate-950 border border-slate-800 text-xs space-y-1"
                        >
                          <div className="flex items-center justify-between font-mono">
                            <span className="font-semibold text-white">
                              #{c.rank} {c.service_name}
                            </span>
                            <span className="text-cyan-400 font-bold">{Math.round(c.score * 100)}%</span>
                          </div>
                          <div className="grid grid-cols-4 gap-1 text-[9px] font-mono text-slate-400">
                            <div>Temp: {c.temporal_score}</div>
                            <div>Topo: {c.dependency_score}</div>
                            <div>Anom: {c.anomaly_score}</div>
                            <div>Prop: {c.propagation_score}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommended Remediation Actions */}
                  {rcaResult.recommended_actions?.length > 0 && (
                    <div className="space-y-2 pt-2 border-t border-slate-800">
                      <h4 className="text-xs font-semibold text-emerald-400 uppercase tracking-wider">
                        Recommended Remediation
                      </h4>
                      <div className="space-y-1.5">
                        {rcaResult.recommended_actions.map((act, idx) => (
                          <div
                            key={idx}
                            className="flex items-center justify-between p-2 bg-emerald-950/30 border border-emerald-500/30 rounded-lg text-xs"
                          >
                            <span className="text-slate-200">{act.title || JSON.stringify(act)}</span>
                            <button className="px-2 py-0.5 bg-emerald-500 text-slate-950 hover:bg-emerald-400 rounded text-[10px] font-bold">
                              Execute
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <div className="text-center py-10 text-slate-500 space-y-2">
                  <Bot className="w-8 h-8 mx-auto text-purple-500 opacity-60" />
                  <p className="text-sm">Click "AI Root Cause Analysis" to generate explainable diagnostic rankings.</p>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ServiceDependencyExplorerPage;
