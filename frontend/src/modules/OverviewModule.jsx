import React from 'react';
import {
  FileText, TrendingUp, Globe2, RadioTower, Clock, Sparkles, ExternalLink
} from 'lucide-react';
import {
  ResponsiveContainer, AreaChart, Area, BarChart, Bar,
  XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';
import MetricCard from '../components/MetricCard';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function OverviewModule({ overview, topics, onSelectTopic, onCollect, isCollecting }) {
  if (!overview || overview.total_articles === 0) {
    return (
      <EmptyState
        message="The research database currently has 0 articles. Initiate public data collection to gather reports from GDELT, BBC, The Guardian, UN, WHO, Open-Meteo, and NASA."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const timeline = overview.timeline || [];
  const sourcesBreakdown = overview.sources_breakdown || [];
  const ranking = overview.topics_ranking || [];
  const recentArticles = overview.recent_articles || [];

  return (
    <div>
      {/* Metrics Row */}
      <div className="metrics-grid">
        <MetricCard
          icon={<FileText size={22} />}
          label="Total Collected Articles"
          value={overview.total_articles}
          hint="Deduplicated & indexed"
          tone="blue"
        />
        <MetricCard
          icon={<TrendingUp size={22} />}
          label="Emerging Topics"
          value={overview.emerging_topics}
          hint="Activity score > 30"
          tone="pink"
        />
        <MetricCard
          icon={<Globe2 size={22} />}
          label="Distinct Publishers"
          value={overview.distinct_publishers}
          hint="Multi-source coverage"
          tone="lavender"
        />
        <MetricCard
          icon={<RadioTower size={22} />}
          label="Increasing Coverage"
          value={overview.increasing_coverage_topics}
          hint="Accelerating clusters"
          tone="yellow"
        />
      </div>

      {/* Collection Metadata Badge */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: 12,
        background: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: 10,
        padding: '10px 16px',
        fontSize: 12,
        color: '#475569',
        marginBottom: 20
      }}>
        <Clock size={15} style={{ color: '#0284c7' }} />
        <span>
          Last successful collection: <strong>{overview.last_collection_time ? new Date(overview.last_collection_time).toLocaleString() : 'Just now'}</strong>
        </span>
        <span style={{ margin: '0 8px', color: '#cbd5e1' }}>•</span>
        <span className="badge badge-green">Real Stored Data</span>
      </div>

      {/* Charts Grid */}
      <div className="charts-grid">
        {/* Chart 1: Topic Activity Over Time */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Observed Coverage Activity Timeline</h2>
              <p className="card-subtitle">Stored articles grouped by timestamp</p>
            </div>
          </div>
          <div style={{ height: 240 }}>
            {timeline.length > 0 ? (
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={timeline} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                  <defs>
                    <linearGradient id="blueArea" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#38bdf8" stopOpacity={0.6}/>
                      <stop offset="95%" stopColor="#38bdf8" stopOpacity={0.0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="time" tick={{ fontSize: 11 }} />
                  <YAxis allowDecimals={false} tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Area type="monotone" dataKey="count" stroke="#0284c7" strokeWidth={2} fill="url(#blueArea)" name="Articles" />
                </AreaChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ display: 'grid', placeItems: 'center', height: '100%', color: '#94a3b8', fontSize: 12 }}>
                Timeline data will build as subsequent collections occur.
              </div>
            )}
          </div>
        </div>

        {/* Chart 2: Source Distribution */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Public Source Distribution</h2>
              <p className="card-subtitle">Breakdown of indexed publishers & data feeds</p>
            </div>
          </div>
          <div style={{ height: 240 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={sourcesBreakdown} layout="vertical" margin={{ top: 5, right: 20, left: 20, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" allowDecimals={false} tick={{ fontSize: 11 }} />
                <YAxis dataKey="source" type="category" width={140} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="count" fill="#a855f7" radius={[0, 6, 6, 0]} name="Reports" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 3: Emerging Topics Ranking */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Emerging Topics Ranking</h2>
              <p className="card-subtitle">Ranked by calculated Cascade Activity Score (0–100)</p>
            </div>
          </div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ranking} layout="vertical" margin={{ top: 5, right: 20, left: 10, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#f1f5f9" />
                <XAxis type="number" domain={[0, 100]} tick={{ fontSize: 11 }} />
                <YAxis dataKey="label" type="category" width={160} tick={{ fontSize: 10 }} />
                <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Bar dataKey="cascade_score" fill="#db2777" radius={[0, 6, 6, 0]} name="Cascade Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 4: Multi-metric Growth Comparison */}
        <div className="card">
          <div className="card-header">
            <div>
              <h2 className="card-title">Cascade vs. Corroboration Comparison</h2>
              <p className="card-subtitle">Activity score compared against source corroboration</p>
            </div>
          </div>
          <div style={{ height: 250 }}>
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={ranking} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                <XAxis dataKey="label" tick={{ fontSize: 9 }} angle={-20} textAnchor="end" />
                <YAxis domain={[0, 100]} tick={{ fontSize: 11 }} />
                <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: 12 }} />
                <Bar dataKey="cascade_score" fill="#38bdf8" radius={[4, 4, 0, 0]} name="Cascade Activity" />
                <Bar dataKey="corroboration_score" fill="#eab308" radius={[4, 4, 0, 0]} name="Corroboration Score" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Recently Discovered Information List */}
      <div className="card">
        <div className="card-header">
          <div>
            <h2 className="card-title">Recently Discovered Information Records</h2>
            <p className="card-subtitle">Raw latest articles with verified timestamps and original publisher links</p>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
          {recentArticles.map((art) => (
            <div
              key={art.id}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 14px',
                border: '1px solid #f1f5f9',
                borderRadius: 10,
                background: '#fafaf9'
              }}
            >
              <div>
                <h3 style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 4 }}>
                  {art.title}
                </h3>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 11, color: '#64748b' }}>
                  <span className="badge badge-blue">{art.source}</span>
                  <span>Published: {art.published_at ? new Date(art.published_at).toLocaleString() : 'N/A'}</span>
                </div>
              </div>
              <a
                href={art.url}
                target="_blank"
                rel="noreferrer"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 4,
                  fontSize: 12,
                  color: '#0284c7',
                  textDecoration: 'none',
                  fontWeight: 600,
                  flexShrink: 0,
                  marginLeft: 16
                }}
              >
                <span>Original</span>
                <ExternalLink size={13} />
              </a>
            </div>
          ))}
        </div>
      </div>

      <ResearchCaveat text="All dashboard indicators are derived exclusively from genuine stored records collected across public newsrooms and APIs. They do not simulate social engagement or extrapolate unobserved private metrics." />
    </div>
  );
}

