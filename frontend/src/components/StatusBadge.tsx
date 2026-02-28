import type { LeadStatus } from '../types';

const config: Record<LeadStatus, { label: string; className: string }> = {
  raw: { label: 'Raw', className: 'bg-gray-100 text-gray-700' },
  enriching: { label: 'Enriching…', className: 'bg-yellow-100 text-yellow-800 animate-pulse' },
  enriched: { label: 'Enriched', className: 'bg-green-100 text-green-800' },
  failed: { label: 'Failed', className: 'bg-red-100 text-red-800' },
};

export function StatusBadge({ status }: { status: LeadStatus }) {
  const { label, className } = config[status];
  return (
    <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${className}`}>
      {label}
    </span>
  );
}
