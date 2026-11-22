import React, { useState, useEffect } from 'react';
import {
  Grid, CheckCircle2, Bookmark, HelpCircle, AlertOctagon,
  ChevronRight, ExternalLink, ShieldAlert
} from 'lucide-react';
import { fetchMatrix } from '../services/api';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function ClassificationMatrixModule({ topics, onSelectTopic, onCollect, isCollecting }) {
  const [matrixData, setMatrixData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedItem, setSelectedItem] = useState(null);

  useEffect(() => {
    setLoading(true);
    fetchMatrix()
      .then((data) => {
        setMatrixData(data);
        // Default select first item if available
        const qBreaking = data.quadrants['Verified Breaking News'] || [];
        const qNiche = data.quadrants['Niche Fact'] || [];
        const qViral = data.quadrants['Viral Disinformation'] || [];
        const qRumor = data.quadrants['Isolated Rumor'] || [];
        const first = qBreaking[0] || qNiche[0] || qViral[0] || qRumor[0];
        if (first) setSelectedItem(first);
      })
      .catch((err) => console.error('Failed to fetch classification matrix:', err))
      .finally(() => setLoading(false));
  }, []);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No classified information cascades yet. Collect public news data to plot topics across the 2×2 Research Matrix."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const quadrants = matrixData?.quadrants || {
    'Verified Breaking News': [],
    'Niche Fact': [],
    'Isolated Rumor': [],
    'Viral Disinformation': []
  };

  return (
    <div>
      <div className="card-header" style={{ marginBottom: 12 }}>
        <div>
          <h2 className="card-title">2×2 Information Cascade Classification Matrix</h2>
          <p className="card-subtitle">
            Academic taxonomy categorizing emerging information by Cascade Activity (X) vs. Multi-Source Corroboration (Y)
          </p>
        </div>
        <span className="badge badge-lavender">
          Total Classified: {matrixData?.total_classified || 0} Topics
        </span>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Mapping information clusters into research quadrants...
        </div>
      ) : (
        <div>
          {/* 2x2 Visual Grid */}
          <div className="matrix-container">
            {/* Quadrant 1: Verified Breaking News (High Corroboration, High Activity) */}
            <div className="matrix-quadrant q-breaking">
              <div className="quadrant-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <CheckCircle2 size={18} color="#0284c7" />
                  <span className="quadrant-title">1. Verified Breaking News</span>
                </div>
                <span className="badge badge-blue">
                  {quadrants['Verified Breaking News'].length} Topics
                </span>
              </div>
              <p className="quadrant-desc">
                High journalistic cascade activity backed by multi-publisher corroboration.
              </p>
              <div className="quadrant-items">
                {quadrants['Verified Breaking News'].map((item) => (
                  <div
                    key={item.topic_id}
                    className="quadrant-card"
                    onClick={() => setSelectedItem(item)}
                    style={{
                      borderLeft: selectedItem?.topic_id === item.topic_id ? '3px solid #0284c7' : '1px solid #e2e8f0'
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>
                      {item.label}
                    </div>
                    <div style={{ fontSize: 10, color: '#64748b' }}>
                      Cascade: {item.cascade_score} • Corroboration: {item.corroboration_score}
                    </div>
                  </div>
                ))}
                {quadrants['Verified Breaking News'].length === 0 && (
                  <div style={{ fontSize: 11, color: '#94a3b8', fontStyle: 'italic', padding: 8 }}>
                    No topics currently meeting &gt;50 activity &amp; &gt;50 corroboration criteria.
                  </div>
                )}
              </div>
            </div>

            {/* Quadrant 2: High Cascade Uncorroborated / Viral Disinformation Risk (Low Corroboration, High Activity) */}
            <div className="matrix-quadrant q-viral">
              <div className="quadrant-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <AlertOctagon size={18} color="#db2777" />
                  <span className="quadrant-title">4. Viral Disinformation Risk</span>
                </div>
                <span className="badge badge-pink">
                  {quadrants['Viral Disinformation'].length} Topics
                </span>
              </div>
              <p className="quadrant-desc">
                High activity with severe deficit in independent source corroboration. Critical review required.
              </p>
              <div className="quadrant-items">
                {quadrants['Viral Disinformation'].map((item) => (
                  <div
                    key={item.topic_id}
                    className="quadrant-card"
                    onClick={() => setSelectedItem(item)}
                    style={{
                      borderLeft: selectedItem?.topic_id === item.topic_id ? '3px solid #db2777' : '1px solid #e2e8f0'
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>
                      {item.label}
                    </div>
                    <div style={{ fontSize: 10, color: '#64748b' }}>
                      Cascade: {item.cascade_score} • Corroboration: {item.corroboration_score}
                    </div>
                  </div>
                ))}
                {quadrants['Viral Disinformation'].length === 0 && (
                  <div style={{ fontSize: 11, color: '#94a3b8', fontStyle: 'italic', padding: 8 }}>
                    No uncorroborated viral cascades identified.
                  </div>
                )}
              </div>
            </div>

            {/* Quadrant 3: Niche Fact (High Corroboration, Low Activity) */}
            <div className="matrix-quadrant q-niche">
              <div className="quadrant-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Bookmark size={18} color="#7c3aed" />
                  <span className="quadrant-title">2. Niche Fact</span>
                </div>
                <span className="badge badge-lavender">
                  {quadrants['Niche Fact'].length} Topics
                </span>
              </div>
              <p className="quadrant-desc">
                Documented by reputable sources, but with specialized, quiet, or local coverage.
              </p>
              <div className="quadrant-items">
                {quadrants['Niche Fact'].map((item) => (
                  <div
                    key={item.topic_id}
                    className="quadrant-card"
                    onClick={() => setSelectedItem(item)}
                    style={{
                      borderLeft: selectedItem?.topic_id === item.topic_id ? '3px solid #7c3aed' : '1px solid #e2e8f0'
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>
                      {item.label}
                    </div>
                    <div style={{ fontSize: 10, color: '#64748b' }}>
                      Cascade: {item.cascade_score} • Corroboration: {item.corroboration_score}
                    </div>
                  </div>
                ))}
                {quadrants['Niche Fact'].length === 0 && (
                  <div style={{ fontSize: 11, color: '#94a3b8', fontStyle: 'italic', padding: 8 }}>
                    No niche facts classified.
                  </div>
                )}
              </div>
            </div>

            {/* Quadrant 4: Isolated Rumor (Low Corroboration, Low Activity) */}
            <div className="matrix-quadrant q-rumor">
              <div className="quadrant-header">
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <HelpCircle size={18} color="#ca8a04" />
                  <span className="quadrant-title">3. Isolated Rumor / Unverified</span>
                </div>
                <span className="badge badge-yellow">
                  {quadrants['Isolated Rumor'].length} Topics
                </span>
              </div>
              <p className="quadrant-desc">
                Low volume single-source reports lacking secondary corroboration or empirical proof.
              </p>
              <div className="quadrant-items">
                {quadrants['Isolated Rumor'].map((item) => (
                  <div
                    key={item.topic_id}
                    className="quadrant-card"
                    onClick={() => setSelectedItem(item)}
                    style={{
                      borderLeft: selectedItem?.topic_id === item.topic_id ? '3px solid #ca8a04' : '1px solid #e2e8f0'
                    }}
                  >
                    <div style={{ fontSize: 12, fontWeight: 700, color: '#0f172a', marginBottom: 2 }}>
                      {item.label}
                    </div>
                    <div style={{ fontSize: 10, color: '#64748b' }}>
                      Cascade: {item.cascade_score} • Corroboration: {item.corroboration_score}
                    </div>
                  </div>
                ))}
                {quadrants['Isolated Rumor'].length === 0 && (
                  <div style={{ fontSize: 11, color: '#94a3b8', fontStyle: 'italic', padding: 8 }}>
                    No isolated rumors in current batch.
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Selected Item Detail Drawer */}
          {selectedItem && (
            <div className="card" style={{ marginTop: 20 }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 8 }}>
                <span className={`badge ${selectedItem.color_tone === 'pink' ? 'badge-pink' : (selectedItem.color_tone === 'yellow' ? 'badge-yellow' : (selectedItem.color_tone === 'lavender' ? 'badge-lavender' : 'badge-blue'))}`}>
                  Category: {selectedItem.quadrant}
                </span>
                <span style={{ fontSize: 11, color: '#64748b' }}>
                  Measured Activity: <strong>{selectedItem.cascade_score}/100</strong> • Corroboration: <strong>{selectedItem.corroboration_score}/100</strong>
                </span>
              </div>
              <h3 style={{ fontSize: 15, fontWeight: 800, color: '#0f172a', marginBottom: 6 }}>
                {selectedItem.label}
              </h3>
              <p style={{ fontSize: 12, color: '#475569', lineHeight: 1.5, marginBottom: 12 }}>
                {selectedItem.description}
              </p>
              {onSelectTopic && (
                <button
                  className="collect-btn"
                  style={{ fontSize: 12, padding: '7px 14px' }}
                  onClick={() => onSelectTopic(selectedItem.topic_id)}
                >
                  <span>Inspect Full Topic Narrative</span>
                  <ChevronRight size={14} />
                </button>
              )}
            </div>
          )}
        </div>
      )}

      <ResearchCaveat text="The Information Classification Matrix provides structured evidentiary taxonomy. It does not automatically designate uncorroborated topics as malicious disinformation without definitive forensic attribution." />
    </div>
  );
}

