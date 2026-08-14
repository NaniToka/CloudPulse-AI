import React, { useState, useEffect, useCallback } from 'react';
import { topologyService, TopologyFilterParams } from '../../services/topologyService';
import {
  BlastRadiusAnalysisResponse,
  FailureSimulationResponse,
  SpofListResponse,
  TopologyGraphResponse,
  TopologyNodeItem,
  TopologyOverviewResponse,
} from '../../types/topology';
import { TopologyHeader } from '../../components/topology/TopologyHeader';
import { TopologyGraphViewer } from '../../components/topology/TopologyGraphViewer';
import { TopologyResourcePanel } from '../../components/topology/TopologyResourcePanel';
import { BlastRadiusPanel } from '../../components/topology/BlastRadiusPanel';
import { FailureSimulationModal } from '../../components/topology/FailureSimulationModal';
import { SpofDashboardPanel } from '../../components/topology/SpofDashboardPanel';

export const CloudTopologyPage: React.FC = () => {
  const [overview, setOverview] = useState<TopologyOverviewResponse | null>(null);
  const [graphData, setGraphData] = useState<TopologyGraphResponse | null>(null);
  const [spofData, setSpofData] = useState<SpofListResponse | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('ALL');
  const [selectedRegion, setSelectedRegion] = useState('ALL');
  const [isSyncing, setIsSyncing] = useState(false);
  const [loading, setLoading] = useState(true);

  const [selectedNode, setSelectedNode] = useState<TopologyNodeItem | null>(null);
  const [upstreamNodes, setUpstreamNodes] = useState<TopologyNodeItem[]>([]);
  const [downstreamNodes, setDownstreamNodes] = useState<TopologyNodeItem[]>([]);
  const [blastRadius, setBlastRadius] = useState<BlastRadiusAnalysisResponse | null>(null);

  const [isSimulateModalOpen, setIsSimulateModalOpen] = useState(false);
  const [simulationResult, setSimulationResult] = useState<FailureSimulationResponse | null>(null);
  const [simulating, setSimulating] = useState(false);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      const filters: TopologyFilterParams = {
        provider: selectedProvider,
        region: selectedRegion,
      };

      const [ovData, grData, spData] = await Promise.all([
        topologyService.getOverview(),
        topologyService.getGraph(filters),
        topologyService.getSpofs(),
      ]);

      setOverview(ovData);
      setGraphData(grData);
      setSpofData(spData);
    } catch (err) {
      console.error('Failed to load topology data', err);
    } finally {
      setLoading(false);
    }
  }, [selectedProvider, selectedRegion]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const handleSelectNode = async (node: TopologyNodeItem) => {
    setSelectedNode(node);
    try {
      const [up, down, blast] = await Promise.all([
        topologyService.getUpstreamDependencies(node.id),
        topologyService.getDownstreamDependencies(node.id),
        topologyService.getBlastRadius(node.id),
      ]);
      setUpstreamNodes(up);
      setDownstreamNodes(down);
      setBlastRadius(blast);
    } catch (err) {
      console.error('Failed to load node dependencies', err);
    }
  };

  const handleCalculateBlastRadius = async (nodeId: string) => {
    try {
      const blast = await topologyService.getBlastRadius(nodeId);
      setBlastRadius(blast);
    } catch (err) {
      console.error('Failed to calculate blast radius', err);
    }
  };

  const handleSelectNodeById = async (nodeId: string) => {
    if (!graphData) return;
    const target = graphData.nodes.find((n) => n.id === nodeId);
    if (target) {
      await handleSelectNode(target);
    }
  };

  const handleSimulate = async (nodeId: string, failureType: string) => {
    try {
      setSimulating(true);
      const res = await topologyService.simulateFailure({ node_id: nodeId, failure_type: failureType });
      setSimulationResult(res);
      setBlastRadius(res.blast_radius);
    } catch (err) {
      console.error('Failed to run simulation', err);
    } finally {
      setSimulating(false);
    }
  };

  const handleRefresh = async () => {
    try {
      setIsSyncing(true);
      await loadData();
    } finally {
      setIsSyncing(false);
    }
  };

  // Filter nodes locally by searchQuery
  const filteredNodes = (graphData?.nodes || []).filter((n) => {
    if (!searchQuery) return true;
    const q = searchQuery.toLowerCase();
    return n.name.toLowerCase().includes(q) || n.type.toLowerCase().includes(q) || n.provider.toLowerCase().includes(q);
  });

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 space-y-6">
      <TopologyHeader
        overview={overview}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedProvider={selectedProvider}
        onProviderChange={setSelectedProvider}
        selectedRegion={selectedRegion}
        onRegionChange={setSelectedRegion}
        onRefresh={handleRefresh}
        onOpenSimulateModal={() => setIsSimulateModalOpen(true)}
        isSyncing={isSyncing}
      />

      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
          Building Multi-Cloud Topology Graph...
        </div>
      ) : (
        <>
          <TopologyGraphViewer
            nodes={filteredNodes}
            edges={graphData?.edges || []}
            selectedNodeId={selectedNode?.id}
            onSelectNode={handleSelectNode}
          />

          <TopologyResourcePanel
            node={selectedNode}
            upstreamNodes={upstreamNodes}
            downstreamNodes={downstreamNodes}
            onSelectNode={handleSelectNode}
            onCalculateBlastRadius={handleCalculateBlastRadius}
          />

          <BlastRadiusPanel blastRadius={blastRadius} />

          <SpofDashboardPanel spofData={spofData} onSelectNodeById={handleSelectNodeById} />
        </>
      )}

      {isSimulateModalOpen && (
        <FailureSimulationModal
          nodes={graphData?.nodes || []}
          simulationResult={simulationResult}
          onSimulate={handleSimulate}
          onClose={() => setIsSimulateModalOpen(false)}
          isLoading={simulating}
        />
      )}
    </div>
  );
};
