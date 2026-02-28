import { useState } from 'react';
import { Layout } from './components/Layout';
import { CampaignSelector } from './components/CampaignSelector';
import { LeadsTable } from './components/LeadsTable';
import { useCampaigns } from './hooks/useCampaigns';
import { useLeads } from './hooks/useLeads';

function App() {
  const [selectedCampaign, setSelectedCampaign] = useState('');
  const { campaigns, loading: campaignsLoading, error: campaignsError } = useCampaigns();
  const { leads, loading: leadsLoading, error: leadsError, fetchLeads } = useLeads();

  const handleCampaignChange = (id: string) => {
    setSelectedCampaign(id);
    if (id) fetchLeads(id);
  };

  return (
    <Layout>
      <div className="space-y-6">
        <CampaignSelector
          campaigns={campaigns}
          loading={campaignsLoading}
          selected={selectedCampaign}
          onChange={handleCampaignChange}
        />

        {campaignsError && (
          <p className="text-sm text-red-600">Error loading campaigns: {campaignsError}</p>
        )}
        {leadsError && (
          <p className="text-sm text-red-600">Error loading leads: {leadsError}</p>
        )}

        <LeadsTable leads={leads} loading={leadsLoading} />
      </div>
    </Layout>
  );
}

export default App;
