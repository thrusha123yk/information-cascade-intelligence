import React from 'react';

export default function MetricCard({ icon, label, value, hint, tone = 'blue' }) {
  return (
    <div className={`metric-card ${tone}`}>
      <div className="metric-icon">{icon}</div>
      <div>
        <div className="metric-val">{value}</div>
        <div className="metric-label">{label}</div>
        {hint && <div className="metric-hint">{hint}</div>}
      </div>
    </div>
  );
}

