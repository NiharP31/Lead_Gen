import { useState, useEffect } from 'react';
import type { Campaign } from '../types';

export function useCampaigns() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch('/api/campaigns')
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch campaigns: ${res.status}`);
        return res.json();
      })
      .then(setCampaigns)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { campaigns, loading, error };
}
