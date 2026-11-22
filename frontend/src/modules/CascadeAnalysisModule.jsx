import React, { useState, useEffect } from 'react';
import {
  TrendingUp, RadioTower, Globe, Zap, Clock, ShieldAlert, BarChart3, AlertCircle
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, AreaChart, Area
} from 'recharts';
import { fetchCascade } from '../services/api';
import MetricCard from '../components/MetricCard';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function CascadeAnalysisModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [cascadeData, setCascadeData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  useEffect(() => {
    if (selectedTopicId) {
      setLoading(true);
      fetchCascade(selectedTopicId)
        .then((data) => setCascadeData(data))
        .catch((err) => console.error('Failed to fetch cascade:', err))
        .finally(() => setLoading(false));
    }
  }, [selectedTopicId]);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics available for cascade activity modeling. Collect public streams to compute cascade metrics."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const metrics = cascadeData?.cascade_metrics || {};
  const topic = cascadeData?.topic || {};
  const articles = cascadeData?.articles || [];

  return (
    <div>
      {/* Selector Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        background: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: 12,
        padding: '12px 18px',
        marginBottom: 20,
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <TrendingUp size={18} style={{ color: '#db2777' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Cascade Modeling Topic:</span>
          <select
            value={selectedTopicId || ''}
            onChange={(e) => setSelectedTopicId(e.target.value)}
            style={{
              padding: '7px 12px',
              borderRadius: 8,
              border: '1px solid #cbd5e1',
              fontSize: 12,
              fontFamily: 'inherit',
              maxWidth: 420
            }}
          >
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label.length > 65 ? t.label.substring(0, 65) + '...' : t.label} ({t.article_count} reports)
              </option>
            ))}
          </select>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
          <span className="badge badge-pink">
            Score: {metrics.cascade_score ?? 0}/100
          </span>
          <span className="badge badge-blue">
            Trend: {metrics.activity_trend || 'steady'}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Computing cascade activity parameters...
        </div>
      ) : (
        <div>
          {/* Metrics Overview Cards */}
          <div className="metrics-grid">
            <MetricCard
              icon={<Zap size={22} />}
              label="Cascade Activity Score"
              value={`${metrics.cascade_score ?? 0}/100`}
              hint="Composite volume & spread indicator"
              tone="pink"
            />
            <MetricCard
              icon={<RadioTower size={22} />}
              label="Measured Article Volume"
              value={metrics.measured_volume ?? articles.length}
              hint="Deduplicated public reports"
              tone="blue"
            />
            <MetricCard
              icon={<Globe size={22} />}
              label="Publisher Diversity Score"
              value={`${metrics.source_diversity_score ?? 0}/30`}
              hint="Multi-newsroom coverage"
              tone="lavender"
            />
            <MetricCard
              icon={<Clock size={22} />}
              label="Recency & Velocity"
              value={`${metrics.recency_score ?? 0}/30`}
              hint="Acceleration in past 24h"
              tone="yellow"
            />
          </div>

          {/* Deep Component Breakdown */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(320px, 1fr)', gap: 20 }}>
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Transparent Cascade Indicator Composition</h3>
                  <p className="card-subtitle">Detailed mathematical factor weights contributing to the 0–100 score</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                {/* Volume component */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, color: '#334155' }}>1. Measured Public Volume Factor (Max 40 pts)</span>
                    <strong>{Math.min(40, Math.round((metrics.measured_volume || 1) * 7.5))} pts</strong>
                  </div>
                  <div className="progress-bar-container">
                    <div className="progress-bar-fill" style={{ width: `${Math.min(100, ((metrics.measured_volume || 1) * 7.5 / 40) * 100)}%`, background: '#db2777' }} />
                  </div>
                </div>

                {/* Source Diversity component */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, color: '#334155' }}>2. Cross-Publisher Diversity Factor (Max 30 pts)</span>
                    <strong>{metrics.source_diversity_score ?? 0} pts</strong>
                  </div>
                  <div className="progress-bar-container">
                    <div className="progress-bar-fill" style={{ width: `${Math.min(100, ((metrics.source_diversity_score || 0) / 30) * 100)}%`, background: '#0284c7' }} />
                  </div>
                </div>

                {/* Recency Factor */}
                <div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 12, marginBottom: 4 }}>
                    <span style={{ fontWeight: 600, color: '#334155' }}>3. Recency & Reporting Acceleration (Max 30 pts)</span>
                    <strong>{metrics.recency_score ?? 0} pts</strong>
                  </div>
                  <div className="progress-bar-container">
                    <div className="progress-bar-fill" style={{ width: `${Math.min(100, ((metrics.recency_score || 0) / 30) * 100)}%`, background: '#ca8a04' }} />
                  </div>
                </div>
              </div>

              {/* Research Methodology Notice */}
              <div style={{
                marginTop: 24,
                padding: '12px 14px',
                background: '#f8fafc',
                borderRadius: 8,
                border: '1px solid #e2e8f0',
                fontSize: 12,
                color: '#475569',
                lineHeight: 1.5
              }}>
                <strong>Distinction between Media Coverage & Public Spread: </strong>
                {metrics.research_caveat || 'This score measures public journalistic publishing volume and source diversity. It does not measure user retweets, likes, or dark-social virality.'}
              </div>
            </div>

            {/* Articles Table in Cascade */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Contributing Journalistic Coverage</h3>
                  <p className="card-subtitle">{articles.length} verified articles in cascade</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8, maxHeight: 320, overflowY: 'auto' }}>
                {articles.map((art, idx) => (
                  <div
                    key={art.id || idx}
                    style={{
                      padding: '10px 12px',
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: 8
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 3 }}>
                      {art.title}
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10, color: '#64748b' }}>
                      <span className="badge badge-lavender">{art.source}</span>
                      <span>{art.published_at ? new Date(art.published_at).toLocaleDateString() : 'Recent'}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <ResearchCaveat text="News article volume is NOT equivalent to social-media propagation. Measured coverage reflects independent editorial publishing decisions across newsrooms, not peer-to-peer diffusion." />
    </div>
  );
}

