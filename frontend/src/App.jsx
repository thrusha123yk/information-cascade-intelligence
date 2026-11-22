import React, { useState, useEffect } from 'react';
import {
  LayoutDashboard,
  Layers,
  GitBranch,
  Clock,
  TrendingUp,
  ShieldCheck,
  HeartPulse,
  LineChart,
  Grid,
  Search,
  RefreshCw,
  AlertCircle,
  CheckCircle2,
  Activity,
  Bot,
  Globe
} from 'lucide-react';
import { fetchOverview, fetchTopics, triggerCollection } from './services/api';

import OverviewModule from './modules/OverviewModule';
import TopicDiscoveryModule from './modules/TopicDiscoveryModule';
import NarrativeTreeModule from './modules/NarrativeTreeModule';
import EvolutionAnalysisModule from './modules/EvolutionAnalysisModule';
import CascadeAnalysisModule from './modules/CascadeAnalysisModule';
import EvidenceAnalysisModule from './modules/EvidenceAnalysisModule';
import SocialImpactModule from './modules/SocialImpactModule';
import GrowthPredictionModule from './modules/GrowthPredictionModule';
import ClassificationMatrixModule from './modules/ClassificationMatrixModule';
import SearchExplorationModule from './modules/SearchExplorationModule';
import AgentModule from './modules/AgentModule';
import CountryTopicModule from './modules/CountryTopicModule';

const NAV_ITEMS = [
  { id: 'overview', label: '1. Overview Dashboard', icon: LayoutDashboard },
  { id: 'discovery', label: '2. Emerging Topic Discovery', icon: Layers },
  { id: 'narratives', label: '3. Narrative Tree Graph', icon: GitBranch },
  { id: 'evolution', label: '4. Information Evolution', icon: Clock },
  { id: 'cascades', label: '5. Cascade Activity Analysis', icon: TrendingUp },
  { id: 'evidence', label: '6. Credibility & Evidence', icon: ShieldCheck },
  { id: 'impact', label: '7. Social Impact Analysis', icon: HeartPulse },
  { id: 'predictions', label: '8. 24h–72h Growth Prediction', icon: LineChart },
  { id: 'matrix', label: '9. Classification Matrix (2×2)', icon: Grid },
  { id: 'search', label: '10. Search & Exploration', icon: Search },
  { id: 'agent', label: '11. AI Research Analyst', icon: Bot },
  { id: 'countries', label: '12. Country-wise Emerging Topics', icon: Globe },
];

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overview, setOverview] = useState(null);
  const [topics, setTopics] = useState([]);
  const [activeTopicId, setActiveTopicId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [isCollecting, setIsCollecting] = useState(false);
  const [statusMessage, setStatusMessage] = useState('Connecting to intelligence backend...');
  const [errorMessage, setErrorMessage] = useState(null);

  const loadData = async () => {
    try {
      setLoading(true);
      const [ovData, topData] = await Promise.all([
        fetchOverview(),
        fetchTopics(50)
      ]);
      setOverview(ovData);
      setTopics(topData);
      if (topData && topData.length > 0 && !activeTopicId) {
        setActiveTopicId(topData[0].id);
      }
      setStatusMessage('Connected • Serving research observations from configured public APIs & feeds');
      setErrorMessage(null);
    } catch (err) {
      console.error('Data loading error:', err);
      setStatusMessage('Backend offline. Please start the FastAPI backend server on port 8000.');
      setErrorMessage(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCollect = async () => {
    setIsCollecting(true);
    setStatusMessage('Querying GDELT DOC API, RSS feeds (BBC, Guardian, UN, WHO), Open-Meteo & NASA...');
    setErrorMessage(null);
    try {
      const res = await triggerCollection();
      setStatusMessage(`Collection complete: ${res.saved_records} articles processed, ${res.topics_discovered} topics clustered.`);
      await loadData();
    } catch (err) {
      console.error('Collection error:', err);
      setStatusMessage('Data collection encountered an error.');
      setErrorMessage(err.message);
    } finally {
      setIsCollecting(false);
    }
  };

  const handleSelectTopicAndNavigate = (topicId) => {
    setActiveTopicId(topicId);
    setActiveTab('narratives');
  };

  return (
    <div className="app-shell">
      {/* Research Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="brand-badge">Academic Research AI</div>
          <h1 className="brand-title">Information Cascade Intelligence</h1>
          <p className="brand-tagline">"We don't just detect information. We understand its journey."</p>
        </div>

        <div className="nav-section">
          <div className="nav-label">Research Modules</div>
          {NAV_ITEMS.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                className={`nav-btn ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(item.id)}
              >
                <Icon className="icon" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>

        <div className="sidebar-footer">
          <div className="research-disclaimer">
            <strong>Research Boundary:</strong> Not a binary fake news detector. Focuses on information emergence, multi-source corroboration, and societal impact modeling.
          </div>
          <div style={{ fontSize: 10, color: '#94a3b8', marginTop: 10, textAlign: 'center' }}>
            ACADEMIC RESEARCH PLATFORM • v2.0
          </div>
        </div>
      </aside>

      {/* Main Workspace */}
      <main className="main-content">
        {/* Top Header Bar */}
        <header className="top-bar">
          <div className="top-bar-left">
            <h1>{NAV_ITEMS.find((n) => n.id === activeTab)?.label}</h1>
            <p>Information Cascade Intelligence Platform</p>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button
              className="collect-btn"
              onClick={handleCollect}
              disabled={isCollecting}
            >
              <RefreshCw size={15} className={isCollecting ? 'animate-spin' : ''} />
              <span>{isCollecting ? 'Collecting Public Feeds...' : 'Collect Latest Data'}</span>
            </button>
          </div>
        </header>

        {/* Global Connection / Status Notification Banner */}
        <div style={{
          padding: '10px 32px',
          background: errorMessage ? '#fef2f2' : '#f0fdf4',
          borderBottom: `1px solid ${errorMessage ? '#fecaca' : '#bbf7d0'}`,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          fontSize: 12,
          color: errorMessage ? '#991b1b' : '#166534'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            {errorMessage ? <AlertCircle size={15} /> : <CheckCircle2 size={15} />}
            <span>{errorMessage ? `Error: ${errorMessage}` : statusMessage}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11 }}>
            <Activity size={13} />
            <span>GDELT • BBC • Guardian • UN • WHO • NASA • Open-Meteo</span>
          </div>
        </div>

        {/* Dynamic Body Render based on activeTab */}
        <div className="content-body">
          {activeTab === 'overview' && (
            <OverviewModule
              overview={overview}
              topics={topics}
              onSelectTopic={handleSelectTopicAndNavigate}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'discovery' && (
            <TopicDiscoveryModule
              topics={topics}
              onNavigateToNarrative={handleSelectTopicAndNavigate}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'narratives' && (
            <NarrativeTreeModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'evolution' && (
            <EvolutionAnalysisModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'cascades' && (
            <CascadeAnalysisModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'evidence' && (
            <EvidenceAnalysisModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'impact' && (
            <SocialImpactModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'predictions' && (
            <GrowthPredictionModule
              topics={topics}
              activeTopicId={activeTopicId}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'matrix' && (
            <ClassificationMatrixModule
              topics={topics}
              onSelectTopic={handleSelectTopicAndNavigate}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'search' && (
            <SearchExplorationModule
              topics={topics}
              onCollect={handleCollect}
              isCollecting={isCollecting}
            />
          )}

          {activeTab === 'agent' && (
            <AgentModule />
          )}

          {activeTab === 'countries' && (
            <CountryTopicModule />
          )}
        </div>
      </main>
    </div>
  );
}

