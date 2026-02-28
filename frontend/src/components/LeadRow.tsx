import { useState } from 'react';
import type { RawLead, EnrichedLead, LeadStatus } from '../types';
import { StatusBadge } from './StatusBadge';
import { EnrichButton } from './EnrichButton';
import { LeadDetail } from './LeadDetail';

interface Props {
  lead: RawLead;
  status: LeadStatus;
  enrichedData?: EnrichedLead;
  error?: string;
  onEnrich: () => void;
}

export function LeadRow({ lead, status, enrichedData, error, onEnrich }: Props) {
  const [expanded, setExpanded] = useState(false);

  return (
    <>
      <tr
        className="border-b border-gray-200 hover:bg-gray-50 cursor-pointer"
        onClick={() => status === 'enriched' && setExpanded(!expanded)}
      >
        <td className="px-4 py-3 text-sm text-gray-900">{lead.name}</td>
        <td className="px-4 py-3 text-sm text-gray-600">{lead.email || '—'}</td>
        <td className="px-4 py-3 text-sm text-gray-600">{lead.organization || '—'}</td>
        <td className="px-4 py-3 text-sm text-gray-600">{lead.designation || '—'}</td>
        <td className="px-4 py-3 text-sm">
          {lead.linkedin_url ? (
            <a
              href={lead.linkedin_url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:underline"
              onClick={(e) => e.stopPropagation()}
            >
              Profile
            </a>
          ) : (
            '—'
          )}
        </td>
        <td className="px-4 py-3">
          <StatusBadge status={status} />
        </td>
        <td className="px-4 py-3" onClick={(e) => e.stopPropagation()}>
          <EnrichButton status={status} onClick={onEnrich} />
        </td>
      </tr>
      {error && (
        <tr>
          <td colSpan={7} className="bg-red-50 px-4 py-2 text-sm text-red-700">
            {error}
          </td>
        </tr>
      )}
      {expanded && enrichedData && (
        <tr>
          <td colSpan={7} className="bg-gray-50">
            <LeadDetail data={enrichedData} />
          </td>
        </tr>
      )}
    </>
  );
}
