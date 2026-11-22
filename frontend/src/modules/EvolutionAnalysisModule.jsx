import React, { useState, useEffect } from 'react';
import {
  Clock, GitCommit, Tag, ArrowRight, ShieldCheck, AlertCircle, FileText, CheckCircle2
} from 'lucide-react';
import { fetchEvolution } from '../services/api';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function EvolutionAnalysisModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [evolutionData, setEvolutionData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  useEffect(() => {
    if (selectedTopicId) {
      setLoading(true);
      fetchEvolution(selectedTopicId)
        .then((data) => setEvolutionData(data))
        .catch((err) => console.error('Failed to fetch evolution:', err))
        .finally(() => setLoading(false));
    }
  }, [selectedTopicId]);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No information cascades available for temporal evolution analysis. Collect public news streams to observe narrative development."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const timeline = evolutionData?.timeline || [];

  return (
    <div>
      {/* Topic Switcher Bar */}
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
          <Clock size={18} style={{ color: '#0284c7' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Analyze Narrative Evolution:</span>
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

        {evolutionData && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, fontSize: 12, color: '#64748b' }}>
            <span><strong>{evolutionData.total_steps}</strong> Chronological Steps</span>
            <span>•</span>
            <span><strong>{evolutionData.all_accumulated_entities?.length || 0}</strong> Cumulative Entities</span>
          </div>
        )}
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Performing longitudinal textual difference analysis...
        </div>
      ) : timeline.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#94a3b8' }}>
          Insufficient sequential reports to compute lexical delta for this topic.
        </div>
      ) : (
        <div className="card">
          <div className="card-header" style={{ marginBottom: 20 }}>
            <div>
              <h2 className="card-title">Chronological Information Evolution Timeline</h2>
              <p className="card-subtitle">
                Tracks entity emergence, lexical stability, and claims shifts from initial report to latest update
              </p>
            </div>
          </div>

          {/* Timeline Stream */}
          <div style={{ position: 'relative', paddingLeft: 28 }}>
            {/* Vertical timeline spine */}
            <div style={{
              position: 'absolute',
              left: 10,
              top: 14,
              bottom: 14,
              width: 2,
              background: '#e2e8f0'
            }} />

            {timeline.map((step, idx) => {
              const isFirst = idx === 0;
              const isLast = idx === timeline.length - 1;
              const badgeClass =
                step.evidence_classification === 'Confirmed Textual Baseline' ? 'badge-blue' :
                step.evidence_classification === 'Confirmed Textual Difference' ? 'badge-pink' :
                step.evidence_classification === 'Similarity-Based Relationship' ? 'badge-green' : 'badge-yellow';

              return (
                <div key={step.article_id || idx} style={{ position: 'relative', marginBottom: 28 }}>
                  {/* Step Marker Dot */}
                  <div style={{
                    position: 'absolute',
                    left: -28 + 5,
                    top: 4,
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    background: isFirst ? '#0284c7' : (isLast ? '#db2777' : '#8b5cf6'),
                    border: '2px solid white',
                    boxShadow: '0 0 0 2px #cbd5e1'
                  }} />

                  <div style={{
                    background: '#f8fafc',
                    border: '1px solid #e2e8f0',
                    borderRadius: 12,
                    padding: '16px 18px'
                  }}>
                    {/* Header */}
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8, flexWrap: 'wrap', gap: 8 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                        <span style={{ fontSize: 11, fontWeight: 800, color: '#64748b' }}>
                          STEP #{step.step_index}
                        </span>
                        <span className={`badge ${badgeClass}`}>
                          {step.evidence_classification}
                        </span>
                      </div>
                      <div style={{ fontSize: 11, color: '#94a3b8' }}>
                        {step.published_at ? new Date(step.published_at).toLocaleString() : 'Timestamp not specified'}
                      </div>
                    </div>

                    <h3 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
                      {step.title}
                    </h3>

                    <div style={{ fontSize: 11, color: '#64748b', marginBottom: 12 }}>
                      Reported by: <strong>{step.source}</strong> • Lexical Overlap with Origin: <strong>{Math.round((step.overlap_ratio || 0) * 100)}%</strong>
                    </div>

                    {/* Entities Breakdown: Persistent vs Newly Appearing */}
                    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 12, marginBottom: 12 }}>
                      {/* Newly Appearing Entities */}
                      <div style={{ background: 'white', padding: '10px 12px', borderRadius: 8, border: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: '#be185d', marginBottom: 6 }}>
                          + Newly Appearing Entities ({step.newly_appearing_entities ? step.newly_appearing_entities.length : 0})
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                          {step.newly_appearing_entities && step.newly_appearing_entities.length > 0 ? (
                            step.newly_appearing_entities.map((ent, i) => (
                              <span key={i} className="badge badge-pink">{ent}</span>
                            ))
                          ) : (
                            <span style={{ fontSize: 11, color: '#94a3b8' }}>No new entities introduced.</span>
                          )}
                        </div>
                      </div>

                      {/* Persistent Retained Entities */}
                      <div style={{ background: 'white', padding: '10px 12px', borderRadius: 8, border: '1px solid #e2e8f0' }}>
                        <div style={{ fontSize: 11, fontWeight: 700, color: '#0369a1', marginBottom: 6 }}>
                          = Retained Persistent Entities ({step.persistent_entities ? step.persistent_entities.length : 0})
                        </div>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                          {step.persistent_entities && step.persistent_entities.length > 0 ? (
                            step.persistent_entities.map((ent, i) => (
                              <span key={i} className="badge badge-blue">{ent}</span>
                            ))
                          ) : (
                            <span style={{ fontSize: 11, color: '#94a3b8' }}>Baseline initial entity set.</span>
                          )}
                        </div>
                      </div>
                    </div>

                    {/* Analysis Notes */}
                    <div style={{ fontSize: 12, color: '#475569', background: '#fafaf9', padding: '8px 12px', borderRadius: 6, borderLeft: '3px solid #8b5cf6' }}>
                      <strong>Analytical Observation:</strong> {step.analysis_notes}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}

      <ResearchCaveat text="Information evolution distinguishes between 'Confirmed Textual Differences' (explicit linguistic and named entity variance) and 'Similarity-Based Relationships' (core consensus phrasing). It avoids subjective editorial bias." />
    </div>
  );
}

