import type { Campaign } from '../types';

interface Props {
  campaigns: Campaign[];
  loading: boolean;
  selected: string;
  onChange: (id: string) => void;
}

export function CampaignSelector({ campaigns, loading, selected, onChange }: Props) {
  if (loading) {
    return <p className="text-sm text-gray-500">Loading campaigns…</p>;
  }

  return (
    <div className="flex items-center gap-3">
      <label htmlFor="campaign" className="text-sm font-medium text-gray-700">
        Campaign
      </label>
      <select
        id="campaign"
        value={selected}
        onChange={(e) => onChange(e.target.value)}
        className="rounded-md border border-gray-300 bg-white px-3 py-2 text-sm shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500"
      >
        <option value="">Select a campaign…</option>
        {campaigns.map((c) => (
          <option key={c.id} value={c.id}>
            {c.name || c.id}
          </option>
        ))}
      </select>
    </div>
  );
}
