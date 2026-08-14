import React, { useState, useEffect } from 'react';
import { assetService, AssetFilterParams } from '../../services/assetService';
import {
  AssetDetailResponse,
  AssetOverviewResponse,
  AssetProviderStat,
  AssetResourceItem,
  AssetTopologyResponse,
  OrphanedResourcesResponse,
} from '../../types/assets';
import { AssetHeader } from '../../components/assets/AssetHeader';
import { AssetOverviewCards } from '../../components/assets/AssetOverviewCards';
import { AssetProviderDistribution } from '../../components/assets/AssetProviderDistribution';
import { AssetResourceTable } from '../../components/assets/AssetResourceTable';
import { AssetTopologyGraph } from '../../components/assets/AssetTopologyGraph';
import { OrphanedResourcesPanel } from '../../components/assets/OrphanedResourcesPanel';
import { AssetDetailModal } from '../../components/assets/AssetDetailModal';

export const AssetIntelligencePage: React.FC = () => {
  const [overview, setOverview] = useState<AssetOverviewResponse | null>(null);
  const [providers, setProviders] = useState<AssetProviderStat[]>([]);
  const [resources, setResources] = useState<AssetResourceItem[]>([]);
  const [topology, setTopology] = useState<AssetTopologyResponse | null>(null);
  const [orphanedData, setOrphanedData] = useState<OrphanedResourcesResponse | null>(null);

  const [searchQuery, setSearchQuery] = useState('');
  const [selectedProvider, setSelectedProvider] = useState('ALL');
  const [selectedType, setSelectedType] = useState('ALL');
  const [isSyncing, setIsSyncing] = useState(false);
  const [loading, setLoading] = useState(true);

  const [selectedResourceDetail, setSelectedResourceDetail] = useState<AssetDetailResponse | null>(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const filters: AssetFilterParams = {
        provider: selectedProvider,
        resource_type: selectedType,
        search: searchQuery,
      };

      const [ovData, provData, resData, topData, orphData] = await Promise.all([
        assetService.getOverview(),
        assetService.getProviders(),
        assetService.getResources(filters),
        assetService.getTopology(),
        assetService.getOrphaned(),
      ]);

      setOverview(ovData);
      setProviders(provData.providers);
      setResources(resData);
      setTopology(topData);
      setOrphanedData(orphData);
    } catch (err) {
      console.error('Failed to load asset intelligence data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [selectedProvider, selectedType, searchQuery]);

  const handleRefresh = async () => {
    try {
      setIsSyncing(true);
      await assetService.triggerRefresh();
      await loadData();
    } finally {
      setIsSyncing(false);
    }
  };

  const handleDiscover = async () => {
    try {
      setIsSyncing(true);
      await assetService.triggerDiscover();
      await loadData();
    } finally {
      setIsSyncing(false);
    }
  };

  const handleSelectResource = async (resItem: AssetResourceItem) => {
    try {
      const detail = await assetService.getResourceDetail(resItem.id);
      setSelectedResourceDetail(detail);
    } catch (err) {
      console.error('Failed to load resource detail', err);
    }
  };

  const handleSelectResourceById = async (id: string) => {
    try {
      const detail = await assetService.getResourceDetail(id);
      setSelectedResourceDetail(detail);
    } catch (err) {
      console.error('Failed to load resource detail by id', err);
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8 space-y-6">
      <AssetHeader
        modeIndicator={overview?.mode_indicator}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedProvider={selectedProvider}
        onProviderChange={setSelectedProvider}
        selectedType={selectedType}
        onTypeChange={setSelectedType}
        onRefresh={handleRefresh}
        onDiscover={handleDiscover}
        isSyncing={isSyncing}
      />

      {loading ? (
        <div className="flex items-center justify-center p-12 text-slate-400">
          <div className="w-6 h-6 border-2 border-indigo-500 border-t-transparent rounded-full animate-spin mr-3" />
          Loading Multi-Cloud Asset Graph...
        </div>
      ) : (
        <>
          <AssetOverviewCards overview={overview} />
          <AssetProviderDistribution providers={providers} />
          <OrphanedResourcesPanel orphanedData={orphanedData} onSelectResourceById={handleSelectResourceById} />
          <AssetResourceTable resources={resources} onSelectResource={handleSelectResource} />
          <AssetTopologyGraph topology={topology} />
        </>
      )}

      {selectedResourceDetail && (
        <AssetDetailModal
          detail={selectedResourceDetail}
          onClose={() => setSelectedResourceDetail(null)}
        />
      )}
    </div>
  );
};
