import { useState, useCallback } from 'react';
import type { RawLead } from '../types';

export function useLeads() {
  const [leads, setLeads] = useState<RawLead[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchLeads = useCallback((campaignId: string) => {
    setLoading(true);
    setError(null);
    fetch(`/api/campaigns/${campaignId}/leads`)
      .then((res) => {
        if (!res.ok) throw new Error(`Failed to fetch leads: ${res.status}`);
        return res.json();
      })
      .then(setLeads)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  return { leads, loading, error, fetchLeads };
}
