import type { LeadStatus } from '../types';

interface Props {
  status: LeadStatus;
  onClick: () => void;
}

export function EnrichButton({ status, onClick }: Props) {
  if (status === 'enriched') return null;

  return (
    <button
      onClick={onClick}
      disabled={status === 'enriching'}
      className="rounded bg-blue-600 px-3 py-1 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
    >
      {status === 'enriching' ? (
        <span className="flex items-center gap-1.5">
          <svg className="h-3.5 w-3.5 animate-spin" viewBox="0 0 24 24" fill="none">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z" />
          </svg>
          Enriching…
        </span>
      ) : status === 'failed' ? (
        'Retry'
      ) : (
        'Enrich'
      )}
    </button>
  );
}
