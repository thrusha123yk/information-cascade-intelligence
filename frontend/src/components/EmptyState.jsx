import React from 'react';
import { Database, RefreshCw } from 'lucide-react';

export default function EmptyState({ message, onCollect, isCollecting }) {
  return (
    <div className="card" style={{ textAlign: 'center', padding: '48px 24px' }}>
      <div style={{ width: 54, height: 54, borderRadius: 16, background: '#f1f5f9', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 16px', color: '#64748b' }}>
        <Database size={26} />
      </div>
      <h3 style={{ fontSize: 16, fontWeight: 700, color: '#0f172a', marginBottom: 6 }}>
        No Stored Observations Yet
      </h3>
      <p style={{ fontSize: 13, color: '#64748b', maxWidth: 440, margin: '0 auto 20px', lineHeight: 1.5 }}>
        {message || 'The research database is waiting for its first collection run. Connect to public feeds and indexed APIs to begin discovering information cascades.'}
      </p>
      {onCollect && (
        <button className="collect-btn" onClick={onCollect} disabled={isCollecting}>
          <RefreshCw size={15} className={isCollecting ? 'animate-spin' : ''} />
          {isCollecting ? 'Collecting Public Sources...' : 'Collect Public Sources Now'}
        </button>
      )}
    </div>
  );
}

