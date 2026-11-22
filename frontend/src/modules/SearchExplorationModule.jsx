import React, { useState, useEffect } from 'react';
import {
  Search, Filter, ExternalLink, Columns2, ArrowRightLeft,
  Calendar, Globe, TrendingUp, Tag
} from 'lucide-react';
import { searchEcosystem, compareTopics } from '../services/api';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function SearchExplorationModule({ topics, onCollect, isCollecting }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedSource, setSelectedSource] = useState('');
  const [minScore, setMinScore] = useState('');
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);

  // Comparison State
  const [compareMode, setCompareMode] = useState(false);
  const [topicAId, setTopicAId] = useState(topics && topics.length > 0 ? topics[0].id : '');
  const [topicBId, setTopicBId] = useState(topics && topics.length > 1 ? topics[1].id : '');
  const [comparisonResult, setComparisonResult] = useState(null);
  const [compareLoading, setCompareLoading] = useState(false);

  // Collect distinct sources for filter dropdown
  const allSources = Array.from(
    new Set((topics || []).flatMap((t) => t.sources || []))
  );

  const executeSearch = async () => {
    setLoading(true);
    try {
      const data = await searchEcosystem(
        searchTerm,
        selectedSource,
        minScore ? parseFloat(minScore) : null
      );
      setResults(data);
    } catch (err) {
      console.error('Search failed:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    executeSearch();
  }, [searchTerm, selectedSource, minScore]);

  const handleCompare = async () => {
    if (!topicAId || !topicBId || topicAId === topicBId) return;
    setCompareLoading(true);
    try {
      const comp = await compareTopics(topicAId, topicBId);
      setComparisonResult(comp);
    } catch (err) {
      console.error('Comparison failed:', err);
    } finally {
      setCompareLoading(false);
    }
  };

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No data collected yet. Search and exploration features activate after the initial data harvest."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const matchedTopics = results?.topics || [];
  const matchedArticles = results?.articles || [];

  return (
    <div>
      {/* Search Header & Mode Toggle */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: 20,
        flexWrap: 'wrap',
        gap: 12
      }}>
        <div>
          <h2 className="card-title" style={{ fontSize: 18 }}>Information Ecosystem Search & Exploration</h2>
          <p className="card-subtitle">Cross-examine stored articles, topic clusters, and publisher networks</p>
        </div>
        <button
          className="collect-btn"
          style={{ background: compareMode ? '#7c3aed' : '#0284c7' }}
          onClick={() => {
            setCompareMode(!compareMode);
            if (!compareMode && topicAId && topicBId) {
              handleCompare();
            }
          }}
        >
          <ArrowRightLeft size={15} />
          <span>{compareMode ? 'Switch to Standard Search' : 'Topic Comparison Mode'}</span>
        </button>
      </div>

      {compareMode ? (
        /* Side-by-Side Topic Comparison View */
        <div className="card">
          <div className="card-header">
            <div>
              <h3 className="card-title">Comparative Cascade Analysis</h3>
              <p className="card-subtitle">Select two discovered topics to evaluate differences in velocity and coverage</p>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginBottom: 20 }}>
            <div>
              <label style={{ fontSize: 11, fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 6 }}>
                Topic A:
              </label>
              <select
                value={topicAId}
                onChange={(e) => setTopicAId(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 12 }}
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label.length > 55 ? t.label.substring(0, 55) + '...' : t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label style={{ fontSize: 11, fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 6 }}>
                Topic B:
              </label>
              <select
                value={topicBId}
                onChange={(e) => setTopicBId(e.target.value)}
                style={{ width: '100%', padding: '9px 12px', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 12 }}
              >
                {topics.map((t) => (
                  <option key={t.id} value={t.id}>
                    {t.label.length > 55 ? t.label.substring(0, 55) + '...' : t.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div style={{ textAlign: 'center', marginBottom: 24 }}>
            <button className="collect-btn" onClick={handleCompare} disabled={compareLoading}>
              <Columns2 size={15} />
              <span>{compareLoading ? 'Comparing...' : 'Run Comparative Analysis'}</span>
            </button>
          </div>

          {comparisonResult && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 20 }}>
              {/* Topic A Card */}
              <div style={{ background: 'var(--blue-subtle)', border: '1px solid var(--blue-border)', borderRadius: 12, padding: 16 }}>
                <span className="badge badge-blue" style={{ marginBottom: 6 }}>Topic A</span>
                <h4 style={{ fontSize: 14, fontWeight: 800, color: '#0f172a', marginBottom: 8 }}>
                  {comparisonResult.topic_a.label}
                </h4>
                <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.8 }}>
                  <div>Cascade Score: <strong>{comparisonResult.topic_a.cascade_score}/100</strong></div>
                  <div>Corroboration: <strong>{comparisonResult.topic_a.corroboration_score}/100</strong></div>
                  <div>Reports: <strong>{comparisonResult.topic_a.article_count}</strong></div>
                  <div>Sources: <strong>{(comparisonResult.topic_a.sources || []).join(', ')}</strong></div>
                </div>
              </div>

              {/* Topic B Card */}
              <div style={{ background: 'var(--lavender-subtle)', border: '1px solid var(--lavender-border)', borderRadius: 12, padding: 16 }}>
                <span className="badge badge-lavender" style={{ marginBottom: 6 }}>Topic B</span>
                <h4 style={{ fontSize: 14, fontWeight: 800, color: '#0f172a', marginBottom: 8 }}>
                  {comparisonResult.topic_b.label}
                </h4>
                <div style={{ fontSize: 12, color: '#475569', lineHeight: 1.8 }}>
                  <div>Cascade Score: <strong>{comparisonResult.topic_b.cascade_score}/100</strong></div>
                  <div>Corroboration: <strong>{comparisonResult.topic_b.corroboration_score}/100</strong></div>
                  <div>Reports: <strong>{comparisonResult.topic_b.article_count}</strong></div>
                  <div>Sources: <strong>{(comparisonResult.topic_b.sources || []).join(', ')}</strong></div>
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        /* Standard Filter & Search View */
        <div>
          {/* Filter Bar */}
          <div className="card" style={{ padding: '16px 20px', marginBottom: 20 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'minmax(240px, 2fr) minmax(180px, 1fr) minmax(160px, 1fr)', gap: 14 }}>
              <div>
                <label style={{ fontSize: 11, fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>
                  Keyword Search
                </label>
                <div style={{ position: 'relative' }}>
                  <input
                    type="text"
                    placeholder="Search keywords, headlines, summaries..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    style={{
                      width: '100%',
                      padding: '9px 12px 9px 34px',
                      borderRadius: 8,
                      border: '1px solid #cbd5e1',
                      fontSize: 13,
                      outline: 'none'
                    }}
                  />
                  <Search size={15} style={{ position: 'absolute', left: 11, top: 11, color: '#94a3b8' }} />
                </div>
              </div>

              <div>
                <label style={{ fontSize: 11, fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>
                  Publisher / Source
                </label>
                <select
                  value={selectedSource}
                  onChange={(e) => setSelectedSource(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 12 }}
                >
                  <option value="">All Monitored Sources</option>
                  {allSources.map((s) => (
                    <option key={s} value={s}>{s}</option>
                  ))}
                </select>
              </div>

              <div>
                <label style={{ fontSize: 11, fontWeight: 700, color: '#64748b', display: 'block', marginBottom: 4 }}>
                  Min Cascade Score
                </label>
                <select
                  value={minScore}
                  onChange={(e) => setMinScore(e.target.value)}
                  style={{ width: '100%', padding: '9px 12px', borderRadius: 8, border: '1px solid #cbd5e1', fontSize: 12 }}
                >
                  <option value="">Any Cascade Score</option>
                  <option value="30">&gt; 30 (Emerging)</option>
                  <option value="50">&gt; 50 (Accelerating)</option>
                  <option value="70">&gt; 70 (High Cascade)</option>
                </select>
              </div>
            </div>
          </div>

          {/* Results Display */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(320px, 1fr)', gap: 20 }}>
            {/* Matched Topics */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Matching Topic Clusters ({matchedTopics.length})</h3>
                  <p className="card-subtitle">Clustered narrative threads matching criteria</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 480, overflowY: 'auto' }}>
                {matchedTopics.map((t) => (
                  <div
                    key={t.id}
                    style={{
                      padding: '12px 14px',
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: 10
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                      <span className="badge badge-pink">Cascade: {t.cascade_score}</span>
                      <span style={{ fontSize: 10, color: '#64748b' }}>{t.article_count} articles</span>
                    </div>
                    <h4 style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
                      {t.label}
                    </h4>
                    <div style={{ fontSize: 11, color: '#64748b' }}>
                      Sources: {(t.sources || []).join(', ')}
                    </div>
                  </div>
                ))}
                {matchedTopics.length === 0 && (
                  <div style={{ textAlign: 'center', padding: 30, color: '#94a3b8', fontSize: 12 }}>
                    No topics matched the search filter.
                  </div>
                )}
              </div>
            </div>

            {/* Matched Raw Articles */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Matching Primary Articles ({matchedArticles.length})</h3>
                  <p className="card-subtitle">Raw journalistic reports with direct original links</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 480, overflowY: 'auto' }}>
                {matchedArticles.map((art) => (
                  <div
                    key={art.id}
                    style={{
                      padding: '12px 14px',
                      background: '#fafaf9',
                      border: '1px solid #f1f5f9',
                      borderRadius: 10,
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: 10
                    }}
                  >
                    <div>
                      <h4 style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 4, lineHeight: 1.35 }}>
                        {art.title}
                      </h4>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, fontSize: 10, color: '#64748b' }}>
                        <span className="badge badge-lavender">{art.source}</span>
                        <span>{art.published_at ? new Date(art.published_at).toLocaleDateString() : 'Recent'}</span>
                      </div>
                    </div>
                    {art.url && (
                      <a
                        href={art.url}
                        target="_blank"
                        rel="noreferrer"
                        style={{ color: '#0284c7', padding: 4 }}
                        title="Open Source Article"
                      >
                        <ExternalLink size={14} />
                      </a>
                    )}
                  </div>
                ))}
                {matchedArticles.length === 0 && (
                  <div style={{ textAlign: 'center', padding: 30, color: '#94a3b8', fontSize: 12 }}>
                    No direct articles match this filter.
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      <ResearchCaveat text="Exploration queries execute against stored Postgres/SQLite full-text indexes. Filtering by publisher displays editorial patterns without claiming bias or inaccuracy." />
    </div>
  );
}

