import React from 'react';
import { AlertCircle } from 'lucide-react';

export default function ResearchCaveat({ text }) {
  return (
    <div style={{
      display: 'flex',
      alignItems: 'flex-start',
      gap: 10,
      background: 'var(--yellow-subtle)',
      border: '1px solid var(--yellow-border)',
      padding: '12px 14px',
      borderRadius: 10,
      fontSize: 12,
      color: '#713f12',
      lineHeight: 1.5,
      marginTop: 16
    }}>
      <AlertCircle size={17} style={{ flexShrink: 0, marginTop: 1, color: '#ca8a04' }} />
      <div>
        <strong>Academic Research Boundary: </strong>
        {text || 'All metrics represent observed public journalistic coverage and publisher diversity. They are not truth verdicts or measured private social media impressions.'}
      </div>
    </div>
  );
}

