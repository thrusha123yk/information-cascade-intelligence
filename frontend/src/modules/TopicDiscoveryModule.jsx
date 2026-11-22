import React, { useState } from 'react';
import {
  Layers, Tag, Calendar, Globe, TrendingUp, ExternalLink,
  ChevronRight, ArrowUpDown, Filter, ShieldCheck
} from 'lucide-react';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function TopicDiscoveryModule({ topics, onNavigateToNarrative, onCollect, isCollecting }) {
  const [selectedTopic, setSelectedTopic] = useState(topics && topics.length > 0 ? topics[0] : null);
  const [filterQuery, setFilterQuery] = useState('');
  const [sortBy, setSortBy] = useState('cascade');

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics discovered yet. Collect public data to initiate TF-IDF semantic clustering."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const filtered = topics.filter(t => {
    if (!filterQuery) return true;
    const q = filterQuery.toLowerCase();
    const inLabel = t.label.toLowerCase().includes(q);
    const inKws = (t.keywords || []).some(k => k.toLowerCase().includes(q));
    const inSrc = (t.sources || []).some(s => s.toLowerCase().includes(q));
    return inLabel || inKws || inSrc;
  });

  const activeTopic = selectedTopic || filtered[0] || topics[0];

  return (
    <div>
      {/* Search and Sort Toolbar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        marginBottom: 20,
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10, flex: 1, minWidth: 260 }}>
          <input
            type="text"
            placeholder="Filter discovered topics, keywords, or publishers..."
            value={filterQuery}
            onChange={(e) => setFilterQuery(e.target.value)}
            style={{
              width: '100%',
              maxWidth: 420,
              padding: '9px 14px',
              borderRadius: 10,
              border: '1px solid #cbd5e1',
              fontSize: 13,
              outline: 'none',
              fontFamily: 'inherit'
            }}
          />
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <span style={{ fontSize: 12, color: '#64748b', fontWeight: 600 }}>Sort by:</span>
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            style={{
              padding: '8px 12px',
              borderRadius: 8,
              border: '1px solid #cbd5e1',
              fontSize: 12,
              fontFamily: 'inherit',
              background: 'white',
              color: '#0f172a'
            }}
          >
            <option value="cascade">Highest Cascade Activity</option>
            <option value="articles">Most Related Articles</option>
            <option value="sources">Most Independent Sources</option>
          </select>
        </div>
      </div>

      {/* Main 2-Column Split: Topic List + Detail Inspector */}
      <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1fr) minmax(400px, 1.4fr)', gap: 20 }}>
        {/* Left Column: Topics List */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 'calc(100vh - 220px)', overflowY: 'auto' }}>
          {filtered.map((topic) => {
            const isSelected = activeTopic && activeTopic.id === topic.id;
            return (
              <div
                key={topic.id}
                onClick={() => setSelectedTopic(topic)}
                style={{
                  background: isSelected ? 'var(--blue-subtle)' : 'white',
                  border: `1.5px solid ${isSelected ? 'var(--blue-accent)' : '#e2e8f0'}`,
                  borderRadius: 12,
                  padding: '14px 16px',
                  cursor: 'pointer',
                  transition: 'all 0.15s ease',
                  boxShadow: isSelected ? 'var(--shadow-sm)' : 'none'
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
                  <span className={`badge ${topic.cascade_score >= 50 ? 'badge-pink' : (topic.cascade_score >= 30 ? 'badge-yellow' : 'badge-blue')}`}>
                    <TrendingUp size={11} />
                    Cascade: {topic.cascade_score}/100
                  </span>
                  <span style={{ fontSize: 11, color: '#64748b' }}>
                    {topic.article_count} reports • {topic.source_count} sources
                  </span>
                </div>
                <h3 style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 6, lineHeight: 1.4 }}>
                  {topic.label}
                </h3>
                {/* Keywords */}
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4, marginTop: 8 }}>
                  {(topic.keywords || []).slice(0, 4).map((kw, i) => (
                    <span key={i} style={{ fontSize: 10, background: '#f1f5f9', color: '#475569', padding: '2px 6px', borderRadius: 4 }}>
                      #{kw}
                    </span>
                  ))}
                </div>
              </div>
            );
          })}
        </div>

        {/* Right Column: Active Topic Deep Inspector */}
        {activeTopic && (
          <div className="card" style={{ height: 'fit-content' }}>
            <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 16, marginBottom: 16 }}>
              <div>
                <span className="brand-badge">Topic Cascade Detail</span>
                <h2 style={{ fontSize: 18, fontWeight: 800, color: '#0f172a', lineHeight: 1.35, marginTop: 4 }}>
                  {activeTopic.label}
                </h2>
              </div>
              <button
                className="collect-btn"
                style={{ background: '#7c3aed', padding: '7px 14px', fontSize: 12 }}
                onClick={() => onNavigateToNarrative && onNavigateToNarrative(activeTopic.id)}
              >
                <span>View Narrative Tree</span>
                <ChevronRight size={14} />
              </button>
            </div>

            {/* Quick Metrics Bar */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(3, 1fr)',
              gap: 12,
              background: '#f8fafc',
              border: '1px solid #e2e8f0',
              borderRadius: 10,
              padding: '12px 14px',
              marginBottom: 16
            }}>
              <div>
                <div style={{ fontSize: 11, color: '#64748b' }}>Cascade Score</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: '#db2777' }}>{activeTopic.cascade_score}/100</div>
              </div>
              <div>
                <div style={{ fontSize: 11, color: '#64748b' }}>Corroboration</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: '#0284c7' }}>{activeTopic.corroboration_score}/100</div>
              </div>
              <div>
                <div style={{ fontSize: 11, color: '#64748b' }}>Independent Sources</div>
                <div style={{ fontSize: 18, fontWeight: 800, color: '#7c3aed' }}>{activeTopic.source_count}</div>
              </div>
            </div>

            {/* Observation Timestamps */}
            <div style={{ fontSize: 12, color: '#475569', marginBottom: 16, lineHeight: 1.6 }}>
              <div><strong>First Observed:</strong> {activeTopic.first_observed_at ? new Date(activeTopic.first_observed_at).toLocaleString() : 'N/A'}</div>
              <div><strong>Latest Observed:</strong> {activeTopic.latest_observed_at ? new Date(activeTopic.latest_observed_at).toLocaleString() : 'N/A'}</div>
              <div><strong>Reporting Sources:</strong> {(activeTopic.sources || []).join(', ') || 'Independent publishers'}</div>
            </div>

            {/* Topic Description */}
            <div style={{
              fontSize: 13,
              color: '#334155',
              background: '#fafaf9',
              borderLeft: '3px solid #0284c7',
              padding: '10px 14px',
              borderRadius: '0 8px 8px 0',
              marginBottom: 20,
              lineHeight: 1.5
            }}>
              {activeTopic.description || 'Topic cluster identified through semantic TF-IDF overlap across news streams.'}
            </div>

            {/* Related Articles in Topic */}
            <h4 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 10 }}>
              Grouped Articles ({activeTopic.articles ? activeTopic.articles.length : 0})
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 340, overflowY: 'auto' }}>
              {(activeTopic.articles || []).map((art, idx) => (
                <div
                  key={art.id || idx}
                  style={{
                    padding: '10px 12px',
                    border: '1px solid #f1f5f9',
                    borderRadius: 8,
                    background: 'white',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    gap: 12
                  }}
                >
                  <div>
                    <h5 style={{ fontSize: 12, fontWeight: 600, color: '#0f172a', marginBottom: 3 }}>
                      {art.title}
                    </h5>
                    <div style={{ fontSize: 10, color: '#64748b' }}>
                      <span className="badge badge-lavender" style={{ marginRight: 6 }}>{art.source}</span>
                      <span>{art.published_at ? new Date(art.published_at).toLocaleDateString() : 'Recent'}</span>
                    </div>
                  </div>
                  {art.url && (
                    <a
                      href={art.url}
                      target="_blank"
                      rel="noreferrer"
                      style={{ color: '#0284c7', flexShrink: 0, padding: 4 }}
                      title="Open Original Article"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>

      <ResearchCaveat text="Topics are clustered mathematically based on TF-IDF cosine similarity between textual descriptions and titles. Grouping does not imply endorsement or editorial collusion between distinct news organizations." />
    </div>
  );
}

