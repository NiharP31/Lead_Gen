import type { RawLead } from '../types';
import { useEnrich } from '../hooks/useEnrich';
import { LeadRow } from './LeadRow';

interface Props {
  leads: RawLead[];
  loading: boolean;
}

export function LeadsTable({ leads, loading }: Props) {
  const { enrich, enriched, errors, getStatus } = useEnrich();

  if (loading) {
    return <p className="py-8 text-center text-gray-500">Loading leads…</p>;
  }

  if (leads.length === 0) {
    return <p className="py-8 text-center text-gray-500">No leads found. Select a campaign above.</p>;
  }

  return (
    <div className="overflow-x-auto rounded-lg border border-gray-200">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Name</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Email</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Organization</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Designation</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">LinkedIn</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Status</th>
            <th className="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-600">Action</th>
          </tr>
        </thead>
        <tbody>
          {leads.map((lead) => (
            <LeadRow
              key={lead.lead_id}
              lead={lead}
              status={getStatus(lead.lead_id)}
              enrichedData={enriched[lead.lead_id]}
              error={errors[lead.lead_id]}
              onEnrich={() => enrich(lead)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}
