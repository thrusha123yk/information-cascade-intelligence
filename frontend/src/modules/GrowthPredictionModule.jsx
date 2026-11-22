import React, { useState, useEffect } from 'react';
import {
  TrendingUp, Calendar, AlertCircle, ArrowUpRight, ArrowDownRight, Minus, BarChart2
} from 'lucide-react';
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, CartesianGrid, Legend
} from 'recharts';
import { fetchPredictions } from '../services/api';
import MetricCard from '../components/MetricCard';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

export default function GrowthPredictionModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  useEffect(() => {
    if (selectedTopicId) {
      setLoading(true);
      fetchPredictions(selectedTopicId)
        .then((data) => setPredictionData(data))
        .catch((err) => console.error('Failed to fetch predictions:', err))
        .finally(() => setLoading(false));
    }
  }, [selectedTopicId]);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics available for coverage growth forecasting. Collect public data to generate 24h–72h predictive intervals."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  const preds = predictionData?.predictions || [];
  const topic = predictionData?.topic || {};
  const methodology = predictionData?.methodology || {};

  const chartData = preds.map((p) => ({
    name: `+${p.horizon_hours} Hours`,
    'Lower Bound': p.lower_bound,
    'Expected Volume': p.expected_volume,
    'Upper Bound': p.upper_bound,
    trajectory: p.trajectory,
    confidence: `${Math.round((p.confidence_score || 0.7) * 100)}%`
  }));

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
          <TrendingUp size={18} style={{ color: '#0284c7' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Growth Forecasting Horizon:</span>
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
          <span className="badge badge-blue">
            Current: {topic.current_volume || 0} Reports
          </span>
          <span className="badge badge-lavender">
            Model: Exponential Decay
          </span>
        </div>
      </div>

      {loading ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#64748b' }}>
          Computing predictive confidence intervals for +24h, +48h, and +72h horizons...
        </div>
      ) : preds.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '60px 20px', color: '#94a3b8' }}>
          Insufficient historical observations to establish a baseline growth trajectory.
        </div>
      ) : (
        <div>
          {/* Horizon Cards */}
          <div className="metrics-grid">
            {preds.map((p) => {
              const trajIcon =
                p.trajectory === 'accelerating' ? <ArrowUpRight size={22} color="#16a34a" /> :
                p.trajectory === 'decaying' ? <ArrowDownRight size={22} color="#ea580c" /> :
                <Minus size={22} color="#0284c7" />;

              return (
                <div key={p.horizon_hours} className="metric-card blue">
                  <div className="metric-icon">{trajIcon}</div>
                  <div>
                    <div className="metric-val">{p.expected_volume} <small style={{ fontSize: 13, fontWeight: 600, color: '#64748b' }}>reports</small></div>
                    <div className="metric-label">Horizon: +{p.horizon_hours} Hours</div>
                    <div className="metric-hint">
                      Range: [{p.lower_bound} – {p.upper_bound}] • Conf: {Math.round((p.confidence_score || 0.7) * 100)}%
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Forecasting Prediction Intervals Chart */}
          <div className="card">
            <div className="card-header">
              <div>
                <h3 className="card-title">Forecasted Article Coverage Volume Trajectory</h3>
                <p className="card-subtitle">Expected journalistic volume with lower and upper confidence bounds</p>
              </div>
            </div>

            <div style={{ height: 280 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData} margin={{ top: 20, right: 30, left: 0, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" />
                  <XAxis dataKey="name" tick={{ fontSize: 12 }} />
                  <YAxis tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ borderRadius: 8, fontSize: 12 }} />
                  <Legend verticalAlign="top" height={36} wrapperStyle={{ fontSize: 12 }} />
                  <Bar dataKey="Lower Bound" fill="#bae6fd" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Expected Volume" fill="#0284c7" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Upper Bound" fill="#db2777" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Model Limitations & Scientific Notes */}
          <div className="card" style={{ background: '#fafaf9' }}>
            <h4 style={{ fontSize: 13, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
              Model Governance & Technical Limitations
            </h4>
            <p style={{ fontSize: 12, color: '#475569', lineHeight: 1.6 }}>
              {methodology.limitations || 'Predictions utilize baseline time-decay and velocity modeling from observed journalistic articles. Coverage can be non-linearly influenced by new breaking statements, official press conferences, or editorial reassessments.'}
            </p>
          </div>
        </div>
      )}

      <ResearchCaveat text="Forecasting predicts expected journalistic reporting volume across monitored RSS and GDELT publishers. Never interpret coverage forecasting as a certainty prediction of real-world event escalation." />
    </div>
  );
}

