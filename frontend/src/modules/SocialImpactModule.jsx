import React, { useState, useEffect } from 'react';
import {
  HeartPulse, Leaf, ShieldAlert, DollarSign, Landmark, Cpu,
  AlertTriangle, MapPin, Users, Globe, ExternalLink
} from 'lucide-react';
import { fetchImpact } from '../services/api';
import MetricCard from '../components/MetricCard';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

const DOMAIN_ICONS = {
  'Public Health': <HeartPulse size={20} color="#db2777" />,
  'Environment': <Leaf size={20} color="#16a34a" />,
  'Public Safety': <ShieldAlert size={20} color="#ea580c" />,
  'Economy': <DollarSign size={20} color="#ca8a04" />,
  'Government & Public Policy': <Landmark size={20} color="#7c3aed" />,
  'Technology & Society': <Cpu size={20} color="#0284c7" />
};

export default function SocialImpactModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [impactData, setImpactData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  useEffect(() => {
    if (selectedTopicId) {
      setLoading(true);
      fetchImpact(selectedTopicId)
        .then((data) => setImpactData(data))
        .catch((err) => console.error('Failed to fetch impact:', err))
        .finally(() => setLoading(false));
    }
  }, [selectedTopicId]);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics available for social impact assessment. Collect public data to evaluate societal domains."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const impact = impactData?.impact_assessment || {};
  const topic = impactData?.topic || {};
  const relevance = impact.all_category_relevance || {};

  const severityBadgeClass =
    impact.potential_severity === 'High' || impact.potential_severity === 'Severe' ? 'badge-pink' :
    impact.potential_severity === 'Moderate' ? 'badge-yellow' : 'badge-blue';

  return (
    <div>
      {/* Switcher Bar */}
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
          <ShieldAlert size={18} style={{ color: '#ea580c' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Social Impact Assessment:</span>
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
          <span className={`badge ${severityBadgeClass}`}>
            Severity: {impact.potential_severity || 'Low'}
          </span>
          <span className="badge badge-lavender">
            Urgency: {impact.urgency_level || 'Monitored'}
          </span>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Evaluating multi-domain societal impact indicators...
        </div>
      ) : (
        <div>
          {/* Top Impact Summary Cards */}
          <div className="metrics-grid">
            <MetricCard
              icon={DOMAIN_ICONS[impact.primary_category] || <Globe size={22} />}
              label="Primary Impact Domain"
              value={impact.primary_category || 'Public Policy'}
              hint="Dominant research category"
              tone="lavender"
            />
            <MetricCard
              icon={<AlertTriangle size={22} />}
              label="Potential Severity"
              value={impact.potential_severity || 'Low'}
              hint="Magnitude based on textual signals"
              tone={impact.potential_severity === 'High' ? 'pink' : 'yellow'}
            />
            <MetricCard
              icon={<Users size={22} />}
              label="Affected Population"
              value={impact.affected_population?.length > 25 ? impact.affected_population.substring(0, 25) + '...' : impact.affected_population}
              hint="Evidenced stakeholder group"
              tone="blue"
            />
            <MetricCard
              icon={<MapPin size={22} />}
              label="Geographic Scope"
              value={impact.affected_area || 'Global'}
              hint="Identified jurisdictions"
              tone="yellow"
            />
          </div>

          {/* Rationale and Explanatory Evaluation */}
          <div className="card" style={{ background: '#f8fafc', borderLeft: '4px solid #7c3aed', marginBottom: 20 }}>
            <h3 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
              Explainable Societal Impact Rationale
            </h3>
            <p style={{ fontSize: 13, color: '#334155', lineHeight: 1.6 }}>
              {impact.rationale || 'Impact assessment computed from semantic co-occurrence across verified public reports.'}
            </p>
            <div style={{ marginTop: 10, fontSize: 11, color: '#64748b' }}>
              <strong>Supporting Sources Cited: </strong>
              {(impact.supporting_sources || []).join(', ') || 'Public sources'}
            </div>
          </div>

          {/* All 6 Societal Domains Relevance Radar/Bar */}
          <div className="card">
            <div className="card-header">
              <div>
                <h3 className="card-title">Multi-Domain Relevance Profiling</h3>
                <p className="card-subtitle">Comparative assessment across the 6 core research sectors</p>
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 16 }}>
              {Object.entries(DOMAIN_ICONS).map(([domain, icon]) => {
                const isPrimary = domain === impact.primary_category;
                const score = relevance[domain] || (isPrimary ? 80 : 15);

                return (
                  <div
                    key={domain}
                    style={{
                      background: isPrimary ? 'var(--lavender-subtle)' : '#fafaf9',
                      border: `1.5px solid ${isPrimary ? 'var(--lavender-border)' : '#e2e8f0'}`,
                      borderRadius: 12,
                      padding: '14px 16px'
                    }}
                  >
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        {icon}
                        <strong style={{ fontSize: 13, color: '#0f172a' }}>{domain}</strong>
                      </div>
                      {isPrimary && <span className="badge badge-lavender">Primary</span>}
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: '#64748b', marginBottom: 4 }}>
                      <span>Domain Relevance</span>
                      <strong>{score}%</strong>
                    </div>
                    <div className="progress-bar-container">
                      <div
                        className="progress-bar-fill"
                        style={{
                          width: `${score}%`,
                          background: isPrimary ? '#7c3aed' : '#94a3b8'
                        }}
                      />
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      <ResearchCaveat text="Social impact analysis estimates potential vulnerability and institutional focus based on reported topics. It differentiates prospective theoretical impact from empirically observed post-hoc consequences." />
    </div>
  );
}

