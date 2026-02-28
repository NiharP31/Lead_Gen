import { useState } from 'react';
import type { RawLead, EnrichedLead } from '../types';

export function useEnrich() {
  const [enriching, setEnriching] = useState<Set<string>>(new Set());
  const [enriched, setEnriched] = useState<Record<string, EnrichedLead>>({});
  const [errors, setErrors] = useState<Record<string, string>>({});

  const enrich = async (lead: RawLead) => {
    setEnriching((prev) => new Set(prev).add(lead.lead_id));
    setErrors((prev) => {
      const next = { ...prev };
      delete next[lead.lead_id];
      return next;
    });

    try {
      const res = await fetch(`/api/leads/${lead.lead_id}/enrich`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(lead),
      });
      if (!res.ok) throw new Error(`Enrichment failed: ${res.status}`);
      const data: EnrichedLead = await res.json();
      setEnriched((prev) => ({ ...prev, [lead.lead_id]: data }));
    } catch (err) {
      setErrors((prev) => ({
        ...prev,
        [lead.lead_id]: err instanceof Error ? err.message : 'Unknown error',
      }));
    } finally {
      setEnriching((prev) => {
        const next = new Set(prev);
        next.delete(lead.lead_id);
        return next;
      });
    }
  };

  const getStatus = (leadId: string) => {
    if (enriching.has(leadId)) return 'enriching' as const;
    if (errors[leadId]) return 'failed' as const;
    if (enriched[leadId]) return 'enriched' as const;
    return 'raw' as const;
  };

  return { enrich, enriched, errors, getStatus };
}
