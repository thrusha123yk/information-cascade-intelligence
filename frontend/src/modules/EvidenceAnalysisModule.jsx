import React, { useState, useEffect } from 'react';
import {
  ShieldCheck, AlertTriangle, HelpCircle, CheckCircle2,
  ExternalLink, FileWarning, Search, Info
} from 'lucide-react';
import { fetchEvidence } from '../services/api';
import MetricCard from '../components/MetricCard';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function EvidenceAnalysisModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [evidenceData, setEvidenceData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  useEffect(() => {
    if (selectedTopicId) {
      setLoading(true);
      fetchEvidence(selectedTopicId)
        .then((data) => setEvidenceData(data))
        .catch((err) => console.error('Failed to fetch evidence:', err))
        .finally(() => setLoading(false));
    }
  }, [selectedTopicId]);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics available for evidentiary analysis. Collect public news streams to observe source corroboration."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const record = evidenceData?.evidence_record || {};
  const topic = evidenceData?.topic || {};
  const articles = evidenceData?.articles || [];

  const corroborationLevel = record.corroboration_level || 'insufficient';
  const levelBadgeClass =
    corroborationLevel === 'high' ? 'badge-green' :
    corroborationLevel === 'moderate' ? 'badge-blue' :
    corroborationLevel === 'low' ? 'badge-yellow' : 'badge-pink';

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
          <ShieldCheck size={18} style={{ color: '#0284c7' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Evidentiary Audit Topic:</span>
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
          <span className={`badge ${levelBadgeClass}`}>
            {record.status_label || 'Evaluating Evidence'}
          </span>
          <span className="badge badge-lavender">
            {record.independent_sources_count ?? 1} Independent Sources
          </span>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Analyzing multi-source agreement and identifying evidentiary gaps...
        </div>
      ) : (
        <div>
          {/* Top Metrics Grid */}
          <div className="metrics-grid">
            <MetricCard
              icon={<ShieldCheck size={22} />}
              label="Source Corroboration"
              value={`${record.corroboration_score ?? 0}/100`}
              hint="Cross-publisher consensus indicator"
              tone={corroborationLevel === 'high' ? 'blue' : (corroborationLevel === 'moderate' ? 'lavender' : 'yellow')}
            />
            <MetricCard
              icon={<CheckCircle2 size={22} />}
              label="Independent Sources"
              value={record.independent_sources_count ?? 1}
              hint="Distinct publishing domains"
              tone="blue"
            />
            <MetricCard
              icon={<AlertTriangle size={22} />}
              label="Conflicting Details"
              value={record.conflicting_points ? record.conflicting_points.length : 0}
              hint="Variance in claims or metrics"
              tone="pink"
            />
            <MetricCard
              icon={<HelpCircle size={22} />}
              label="Evidence Gaps"
              value={record.evidence_gaps ? record.evidence_gaps.length : 0}
              hint="Unverified narrative elements"
              tone="yellow"
            />
          </div>

          {/* Primary Consensus Lead */}
          <div className="card" style={{ background: '#f8fafc', borderLeft: '4px solid #0284c7' }}>
            <div style={{ fontSize: 11, fontWeight: 800, color: '#0369a1', textTransform: 'uppercase', marginBottom: 4 }}>
              Observed Core Consensus Statement
            </div>
            <p style={{ fontSize: 14, fontWeight: 600, color: '#0f172a', lineHeight: 1.5 }}>
              "{record.consensus_claim || topic.label}"
            </p>
          </div>

          {/* 2-Column Split: Discrepancies & Gaps + Supporting Articles */}
          <div style={{ display: 'grid', gridTemplateColumns: 'minmax(320px, 1.2fr) minmax(320px, 1fr)', gap: 20 }}>
            {/* Left: Conflicting points & Unresolved questions */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Evidentiary Scrutiny & Gaps</h3>
                  <p className="card-subtitle">Transparent detection of missing context and conflicting claims</p>
                </div>
              </div>

              {/* Conflicting Points */}
              <div style={{ marginBottom: 18 }}>
                <h4 style={{ fontSize: 13, fontWeight: 700, color: '#be185d', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <AlertTriangle size={15} />
                  <span>Conflicting Reporting Details ({record.conflicting_points ? record.conflicting_points.length : 0})</span>
                </h4>
                {record.conflicting_points && record.conflicting_points.length > 0 ? (
                  <ul style={{ paddingLeft: 20, fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
                    {record.conflicting_points.map((pt, idx) => (
                      <li key={idx} style={{ marginBottom: 6 }}>{pt}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: 12, color: '#16a34a' }}>
                    ✓ No conflicting quantitative figures or contradictory attributions detected among current reports.
                  </p>
                )}
              </div>

              {/* Evidence Gaps */}
              <div style={{ marginBottom: 18 }}>
                <h4 style={{ fontSize: 13, fontWeight: 700, color: '#b45309', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <FileWarning size={15} />
                  <span>Identified Evidentiary Gaps</span>
                </h4>
                {record.evidence_gaps && record.evidence_gaps.length > 0 ? (
                  <ul style={{ paddingLeft: 20, fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
                    {record.evidence_gaps.map((gap, idx) => (
                      <li key={idx} style={{ marginBottom: 6 }}>{gap}</li>
                    ))}
                  </ul>
                ) : (
                  <p style={{ fontSize: 12, color: '#64748b' }}>No major documentation gaps flagged.</p>
                )}
              </div>

              {/* Unresolved Questions */}
              <div>
                <h4 style={{ fontSize: 13, fontWeight: 700, color: '#0369a1', display: 'flex', alignItems: 'center', gap: 6, marginBottom: 8 }}>
                  <HelpCircle size={15} />
                  <span>Critical Unresolved Questions</span>
                </h4>
                <ul style={{ paddingLeft: 20, fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
                  {(record.unresolved_questions || []).map((q, idx) => (
                    <li key={idx} style={{ marginBottom: 6 }}>{q}</li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Right: Supporting Article Evidences */}
            <div className="card">
              <div className="card-header">
                <div>
                  <h3 className="card-title">Supporting Source Records</h3>
                  <p className="card-subtitle">Direct links to original journalistic and institutional coverage</p>
                </div>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 10, maxHeight: 420, overflowY: 'auto' }}>
                {articles.map((art, idx) => (
                  <div
                    key={art.id || idx}
                    style={{
                      padding: '12px',
                      background: '#f8fafc',
                      border: '1px solid #e2e8f0',
                      borderRadius: 8,
                      display: 'flex',
                      alignItems: 'flex-start',
                      justifyContent: 'space-between',
                      gap: 12
                    }}
                  >
                    <div>
                      <h5 style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 4, lineHeight: 1.35 }}>
                        {art.title}
                      </h5>
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
              </div>
            </div>
          </div>
        </div>
      )}

      <ResearchCaveat text="Never assume an article is true merely because multiple publishers syndicate the same wire report. Corroboration measures reporting independence, not infallible epistemological truth." />
    </div>
  );
}

