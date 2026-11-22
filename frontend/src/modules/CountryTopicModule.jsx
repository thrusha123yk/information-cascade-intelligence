import React, { useState, useEffect } from 'react';
import { Globe, MapPin, Building2, TrendingUp, AlertCircle, Layers } from 'lucide-react';
import { fetchSourceCountries, fetchEventCountries, fetchTopicsByCountry } from '../services/api';

export default function CountryTopicModule() {
  const [activeTab, setActiveTab] = useState('event'); // 'event' or 'source'
  const [sourceCountries, setSourceCountries] = useState([]);
  const [eventCountries, setEventCountries] = useState([]);
  const [selectedCountry, setSelectedCountry] = useState(null);
  const [countryTopics, setCountryTopics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [loadingTopics, setLoadingTopics] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [sc, ec] = await Promise.all([
          fetchSourceCountries(),
          fetchEventCountries()
        ]);
        setSourceCountries(sc);
        setEventCountries(ec);

        // Default selection
        const defaultList = activeTab === 'event' ? ec : sc;
        if (defaultList.length > 0) {
          setSelectedCountry(defaultList[0].country);
        }
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  useEffect(() => {
    async function loadTopics() {
      if (!selectedCountry) return;
      try {
        setLoadingTopics(true);
        const topics = await fetchTopicsByCountry(selectedCountry, activeTab);
        setCountryTopics(topics);
        setError(null);
      } catch (err) {
        setCountryTopics([]);
        setError(err.message);
        console.error(err);
      } finally {
        setLoadingTopics(false);
      }
    }
    loadTopics();
  }, [selectedCountry, activeTab]);

  const handleTabChange = (tab) => {
    setActiveTab(tab);
    const list = tab === 'event' ? eventCountries : sourceCountries;
    if (list.length > 0) {
      setSelectedCountry(list[0].country);
    } else {
      setSelectedCountry(null);
    }
  };

  const currentList = activeTab === 'event' ? eventCountries : sourceCountries;

  if (loading) {
    return <div style={{ padding: '40px', textAlign: 'center' }}>Loading geographical data from stored intelligence...</div>;
  }

  return (
    <div style={{ padding: '24px', maxWidth: '1200px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Globe size={24} color="#2563eb" />
            Country-wise Emerging Topics
          </h2>
          <p style={{ fontSize: '14px', color: '#64748b' }}>
            Separate analysis of Event Locations vs. News Source Publishing Countries based on stored records.
          </p>
        </div>

        {/* Toggle between Event Country and Source Country */}
        <div style={{ display: 'flex', background: '#e2e8f0', padding: '4px', borderRadius: '8px' }}>
          <button
            onClick={() => handleTabChange('event')}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              background: activeTab === 'event' ? '#ffffff' : 'transparent',
              fontWeight: activeTab === 'event' ? 'bold' : 'normal',
              cursor: 'pointer',
              boxShadow: activeTab === 'event' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            1. Event Country Analysis
          </button>
          <button
            onClick={() => handleTabChange('source')}
            style={{
              padding: '8px 16px',
              borderRadius: '6px',
              border: 'none',
              background: activeTab === 'source' ? '#ffffff' : 'transparent',
              fontWeight: activeTab === 'source' ? 'bold' : 'normal',
              cursor: 'pointer',
              boxShadow: activeTab === 'source' ? '0 1px 3px rgba(0,0,0,0.1)' : 'none'
            }}
          >
            2. Source Country Analysis
          </button>
        </div>
      </div>

      {error && (
        <div style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '12px', borderRadius: '6px', color: '#991b1b', marginBottom: '20px' }}>
          Error: {error}
        </div>
      )}

      {/* Main Grid: Country Selector & Details */}
      <div style={{ display: 'grid', gridTemplateColumns: '350px 1fr', gap: '24px' }}>

        {/* Country List Sidebar */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '16px', height: '600px', overflowY: 'auto' }}>
          <h3 style={{ fontSize: '15px', fontWeight: 'bold', marginBottom: '12px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            {activeTab === 'event' ? <MapPin size={16} color="#2563eb" /> : <Building2 size={16} color="#2563eb" />}
            {activeTab === 'event' ? 'Available Event Locations' : 'Publisher Countries (GDELT)'}
          </h3>

          {currentList.length === 0 ? (
            <div style={{ padding: '20px', textAlign: 'center', color: '#64748b', fontSize: '13px' }}>
              Insufficient data: No geographical breakdown available in stored records.
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {currentList.map((item, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedCountry(item.country)}
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                    padding: '10px 12px',
                    borderRadius: '6px',
                    border: '1px solid',
                    borderColor: selectedCountry === item.country ? '#2563eb' : '#e2e8f0',
                    background: selectedCountry === item.country ? '#eff6ff' : '#ffffff',
                    cursor: 'pointer',
                    textAlign: 'left'
                  }}
                >
                  <span style={{ fontWeight: '500', fontSize: '14px', color: '#1e293b' }}>{item.country}</span>
                  <span style={{ fontSize: '12px', background: '#e2e8f0', padding: '2px 8px', borderRadius: '10px', color: '#475569' }}>
                    {item.count} reports
                  </span>
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Selected Country Details */}
        <div style={{ background: '#ffffff', border: '1px solid #e2e8f0', borderRadius: '8px', padding: '20px', height: '600px', overflowY: 'auto' }}>
          <div style={{ borderBottom: '1px solid #e2e8f0', paddingBottom: '12px', marginBottom: '16px' }}>
            <h3 style={{ fontSize: '18px', fontWeight: 'bold', color: '#1e293b' }}>
              {selectedCountry ? `Analysis for: ${selectedCountry}` : 'Select a Country'}
            </h3>
            <p style={{ fontSize: '13px', color: '#64748b', marginTop: '4px' }}>
              {activeTab === 'event'
                ? 'Showing emerging topics where the event occurred in this region.'
                : 'Showing topics covered by publishers originating from this country metadata.'}
            </p>
          </div>

          {loadingTopics ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>Loading topics...</div>
          ) : countryTopics.length === 0 ? (
            <div style={{ padding: '40px', textAlign: 'center', color: '#64748b' }}>
              <AlertCircle size={32} style={{ margin: '0 auto 10px', color: '#cbd5e1' }} />
              <p style={{ fontWeight: '500' }}>Insufficient data for this region.</p>
              <p style={{ fontSize: '12px', marginTop: '4px' }}>No clustered emerging topics found directly linked to this country's articles.</p>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {countryTopics.map((topic) => (
                <div key={topic.id} style={{ border: '1px solid #e2e8f0', borderRadius: '6px', padding: '14px', background: '#f8fafc' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '6px' }}>
                    <h4 style={{ fontSize: '15px', fontWeight: 'bold', color: '#0f172a' }}>{topic.label}</h4>
                    <span style={{ fontSize: '11px', background: '#dbeafe', color: '#1d4ed8', padding: '2px 8px', borderRadius: '4px', fontWeight: '600' }}>
                      Cascade Score: {topic.cascade_score}
                    </span>
                  </div>
                  <p style={{ fontSize: '13px', color: '#475569', marginBottom: '10px' }}>{topic.description || 'No detailed description available.'}</p>

                  <div style={{ display: 'flex', gap: '16px', fontSize: '12px', color: '#64748b' }}>
                    <span>Articles: <strong>{topic.article_count}</strong></span>
                    <span>Sources: <strong>{topic.source_count}</strong></span>
                    <span>Status: <strong style={{ textTransform: 'capitalize' }}>{topic.status}</strong></span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

      </div>
    </div>
  );
}
