import type { EnrichedLead } from '../types';

export function LeadDetail({ data }: { data: EnrichedLead }) {
  return (
    <div className="grid gap-4 p-4 sm:grid-cols-2 lg:grid-cols-3">
      {/* Company Overview */}
      {data.company_overview && (
        <div className="rounded-lg border border-gray-200 p-3">
          <h4 className="mb-2 text-sm font-semibold text-gray-900">Company Overview</h4>
          <dl className="space-y-1 text-sm text-gray-600">
            {data.company_overview.description && (
              <div>
                <dt className="font-medium text-gray-700">Description</dt>
                <dd>{data.company_overview.description}</dd>
              </div>
            )}
            {data.company_overview.industry && <Detail label="Industry" value={data.company_overview.industry} />}
            {data.company_overview.headcount && <Detail label="Headcount" value={data.company_overview.headcount} />}
            {data.company_overview.founded_year && <Detail label="Founded" value={data.company_overview.founded_year} />}
            {data.company_overview.region && <Detail label="Region" value={data.company_overview.region} />}
            {data.company_overview.estimated_revenue && <Detail label="Revenue" value={data.company_overview.estimated_revenue} />}
          </dl>
        </div>
      )}

      {/* Tech Stack */}
      {data.tech_stack && data.tech_stack.length > 0 && (
        <div className="rounded-lg border border-gray-200 p-3">
          <h4 className="mb-2 text-sm font-semibold text-gray-900">Tech Stack</h4>
          <div className="flex flex-wrap gap-1.5">
            {data.tech_stack.map((tech, i) => (
              <span key={i} className="rounded bg-blue-50 px-2 py-0.5 text-xs text-blue-700">
                {tech}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Funding */}
      {data.funding && (
        <div className="rounded-lg border border-gray-200 p-3">
          <h4 className="mb-2 text-sm font-semibold text-gray-900">Funding</h4>
          <dl className="space-y-1 text-sm text-gray-600">
            {data.funding.total_funding_usd != null && (
              <Detail label="Total Funding" value={`$${data.funding.total_funding_usd.toLocaleString()}`} />
            )}
            {data.funding.news_summary && (
              <div>
                <dt className="font-medium text-gray-700">News</dt>
                <dd>{data.funding.news_summary}</dd>
              </div>
            )}
          </dl>
        </div>
      )}

      {/* LinkedIn Posts */}
      {data.linkedin_posts && data.linkedin_posts.length > 0 && (
        <div className="rounded-lg border border-gray-200 p-3 sm:col-span-2 lg:col-span-3">
          <h4 className="mb-2 text-sm font-semibold text-gray-900">LinkedIn Posts</h4>
          <ul className="space-y-2">
            {data.linkedin_posts.map((post, i) => (
              <li key={i} className="rounded bg-gray-50 p-2 text-sm text-gray-700">
                {post.length > 300 ? post.slice(0, 300) + '…' : post}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Metadata */}
      <div className="rounded-lg border border-gray-200 p-3">
        <h4 className="mb-2 text-sm font-semibold text-gray-900">Metadata</h4>
        <dl className="space-y-1 text-sm text-gray-600">
          <Detail label="Enriched At" value={new Date(data.enrichment_metadata.enriched_at).toLocaleString()} />
          <Detail label="Signals Found" value={data.enrichment_metadata.signals_found.join(', ') || 'None'} />
          <Detail label="Signals Missed" value={data.enrichment_metadata.signals_missed.join(', ') || 'None'} />
        </dl>
      </div>
    </div>
  );
}

function Detail({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <dt className="font-medium text-gray-700">{label}</dt>
      <dd>{value}</dd>
    </div>
  );
}
