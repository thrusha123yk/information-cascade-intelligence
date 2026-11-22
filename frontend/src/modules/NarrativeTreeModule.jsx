import React, { useState, useEffect, useCallback, useMemo } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  Handle,
  Position
} from '@xyflow/react';
import {
  GitBranch, ExternalLink, Calendar, ShieldCheck, Tag, Info, CheckCircle2, AlertTriangle, Layers
} from 'lucide-react';
import { fetchNarrativeGraph } from '../services/api';
import ResearchCaveat from '../components/ResearchCaveat';
import EmptyState from '../components/EmptyState';

// Custom Node Component for React Flow
function CustomNarrativeNode({ data, selected }) {
  const nodeType = data.node_type || 'corroboration';
  const badgeColors = {
    initial_report: 'badge-blue',
    corroboration: 'badge-green',
    expansion: 'badge-lavender',
    update: 'badge-yellow',
    variant: 'badge-pink'
  };

  return (
    <div className={`narrative-node ${nodeType}`} style={{
      boxShadow: selected ? '0 0 0 2px #0284c7, var(--shadow-md)' : 'var(--shadow-sm)',
      cursor: 'pointer'
    }}>
      <Handle type="target" position={Position.Top} style={{ background: '#64748b', width: 8, height: 8 }} />
      
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 6 }}>
        <span className={`badge ${badgeColors[nodeType] || 'badge-blue'}`}>
          {data.badge || 'Report Node'}
        </span>
        <span style={{ fontSize: 10, color: '#94a3b8' }}>
          {data.published_at ? new Date(data.published_at).toLocaleDateString() : 'N/A'}
        </span>
      </div>

      <div className="node-title" title={data.title}>
        {data.title.length > 70 ? data.title.substring(0, 70) + '...' : data.title}
      </div>

      <div className="node-publisher">
        <strong>{data.publisher}</strong>
        <span className="badge badge-gray">{data.origin || 'RSS'}</span>
      </div>

      {data.entities && data.entities.length > 0 && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 3, marginTop: 6 }}>
          {data.entities.slice(0, 3).map((ent, idx) => (
            <span key={idx} style={{ fontSize: 9, background: '#f1f5f9', color: '#475569', padding: '1px 5px', borderRadius: 3 }}>
              {ent}
            </span>
          ))}
        </div>
      )}

      <Handle type="source" position={Position.Bottom} style={{ background: '#64748b', width: 8, height: 8 }} />
    </div>
  );
}

export default function NarrativeTreeModule({ topics, activeTopicId, onCollect, isCollecting }) {
  const [selectedTopicId, setSelectedTopicId] = useState(
    activeTopicId || (topics && topics.length > 0 ? topics[0].id : null)
  );
  const [graphData, setGraphData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedNodeData, setSelectedNodeData] = useState(null);

  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  const nodeTypes = useMemo(() => ({ customNarrativeNode: CustomNarrativeNode }), []);

  useEffect(() => {
    if (activeTopicId) {
      setSelectedTopicId(activeTopicId);
    }
  }, [activeTopicId]);

  const loadGraph = useCallback(async (tId) => {
    if (!tId) return;
    setLoading(true);
    setSelectedNodeData(null);
    try {
      const data = await fetchNarrativeGraph(tId);
      setGraphData(data);
      setNodes(data.nodes || []);
      setEdges(data.edges || []);
      if (data.nodes && data.nodes.length > 0) {
        setSelectedNodeData(data.nodes[0].data);
      }
    } catch (err) {
      console.error('Failed to load narrative graph:', err);
    } finally {
      setLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    if (selectedTopicId) {
      loadGraph(selectedTopicId);
    }
  }, [selectedTopicId, loadGraph]);

  const onNodeClick = useCallback((event, node) => {
    setSelectedNodeData(node.data);
  }, []);

  if (!topics || topics.length === 0) {
    return (
      <EmptyState
        message="No topics discovered for narrative graph construction. Collect public news streams to map information evolution."
        onCollect={onCollect}
        isCollecting={isCollecting}
      />
    );
  }

  return (
    <div>
      {/* Top Topic Switcher */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: 16,
        background: 'white',
        border: '1px solid #e2e8f0',
        borderRadius: 12,
        padding: '12px 18px',
        marginBottom: 16,
        flexWrap: 'wrap'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
          <GitBranch size={18} style={{ color: '#7c3aed' }} />
          <span style={{ fontSize: 13, fontWeight: 700, color: '#0f172a' }}>Active Cascade Topic:</span>
          <select
            value={selectedTopicId || ''}
            onChange={(e) => setSelectedTopicId(e.target.value)}
            style={{
              padding: '7px 12px',
              borderRadius: 8,
              border: '1px solid #cbd5e1',
              fontSize: 12,
              fontFamily: 'inherit',
              maxWidth: 400
            }}
          >
            {topics.map((t) => (
              <option key={t.id} value={t.id}>
                {t.label.length > 60 ? t.label.substring(0, 60) + '...' : t.label} ({t.article_count} reports)
              </option>
            ))}
          </select>
        </div>

        {graphData && (
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, fontSize: 12, color: '#64748b' }}>
            <span><strong>{graphData.total_nodes}</strong> Narrative Nodes</span>
            <span>•</span>
            <span><strong>{graphData.total_edges}</strong> Evidentiary Edges</span>
          </div>
        )}
      </div>

      {/* Narrative Canvas + Node Inspector Split */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: 16 }}>
        {/* React Flow Interactive Graph */}
        <div className="card" style={{ padding: 0, overflow: 'hidden', height: 600, position: 'relative' }}>
          {loading ? (
            <div style={{ display: 'grid', placeItems: 'center', height: '100%', color: '#64748b', fontSize: 13 }}>
              Synthesizing React Flow Narrative Graph...
            </div>
          ) : nodes.length === 0 ? (
            <div style={{ display: 'grid', placeItems: 'center', height: '100%', color: '#94a3b8', fontSize: 13 }}>
              No graph data available for this topic.
            </div>
          ) : (
            <ReactFlow
              nodes={nodes}
              edges={edges}
              onNodesChange={onNodesChange}
              onEdgesChange={onEdgesChange}
              onNodeClick={onNodeClick}
              nodeTypes={nodeTypes}
              fitView
              attributionPosition="bottom-left"
            >
              <Background color="#cbd5e1" gap={16} size={1} />
              <Controls />
              <MiniMap
                nodeColor={(n) => {
                  if (n.data?.node_type === 'initial_report') return '#0284c7';
                  if (n.data?.node_type === 'corroboration') return '#10b981';
                  if (n.data?.node_type === 'update') return '#f59e0b';
                  return '#8b5cf6';
                }}
                style={{ height: 100, width: 140 }}
              />
            </ReactFlow>
          )}
        </div>

        {/* Node Inspector Panel */}
        <div className="card" style={{ height: 600, overflowY: 'auto' }}>
          <div className="card-header" style={{ marginBottom: 12 }}>
            <div>
              <h3 className="card-title">Narrative Node Inspector</h3>
              <p className="card-subtitle">Click any node in the graph to inspect evidence</p>
            </div>
          </div>

          {selectedNodeData ? (
            <div>
              <div style={{ marginBottom: 12 }}>
                <span className="badge badge-blue">{selectedNodeData.badge}</span>
                <h4 style={{ fontSize: 14, fontWeight: 700, color: '#0f172a', margin: '8px 0 4px', lineHeight: 1.4 }}>
                  {selectedNodeData.title}
                </h4>
              </div>

              <div style={{ background: '#f8fafc', padding: '10px 12px', borderRadius: 8, fontSize: 11, marginBottom: 14 }}>
                <div style={{ marginBottom: 4 }}><strong>Publisher:</strong> {selectedNodeData.publisher}</div>
                <div style={{ marginBottom: 4 }}><strong>Published:</strong> {selectedNodeData.published_at ? new Date(selectedNodeData.published_at).toLocaleString() : 'N/A'}</div>
                <div><strong>Source Type:</strong> {selectedNodeData.origin} Feed</div>
              </div>

              {/* Extracted Entities */}
              <div style={{ marginBottom: 16 }}>
                <h5 style={{ fontSize: 12, fontWeight: 700, color: '#334155', marginBottom: 6, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Tag size={13} />
                  <span>Identified Entities ({selectedNodeData.entities ? selectedNodeData.entities.length : 0})</span>
                </h5>
                <div style={{ display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {selectedNodeData.entities && selectedNodeData.entities.length > 0 ? (
                    selectedNodeData.entities.map((e, idx) => (
                      <span key={idx} className="badge badge-lavender">
                        {e}
                      </span>
                    ))
                  ) : (
                    <span style={{ fontSize: 11, color: '#94a3b8' }}>No salient entities extracted.</span>
                  )}
                </div>
              </div>

              {/* Description Preview */}
              {selectedNodeData.description && (
                <div style={{ marginBottom: 16 }}>
                  <h5 style={{ fontSize: 12, fontWeight: 700, color: '#334155', marginBottom: 6 }}>
                    Text Snippet / Lead Summary
                  </h5>
                  <p style={{ fontSize: 12, color: '#475569', lineHeight: 1.5, background: '#fafaf9', padding: '10px', borderRadius: 8, border: '1px solid #f1f5f9' }}>
                    {selectedNodeData.description}
                  </p>
                </div>
              )}

              {/* Original Article Link */}
              {selectedNodeData.url && (
                <a
                  href={selectedNodeData.url}
                  target="_blank"
                  rel="noreferrer"
                  className="collect-btn"
                  style={{ width: '100%', justifyContent: 'center', textDecoration: 'none', marginTop: 10 }}
                >
                  <span>Open Primary Source Article</span>
                  <ExternalLink size={14} />
                </a>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#94a3b8', fontSize: 12, marginTop: 80 }}>
              Select a node on the canvas to inspect its source details, publishing timeline, and verified entities.
            </div>
          )}
        </div>
      </div>

      <ResearchCaveat text="Narrative graph edges denote temporal ordering and lexical/entity co-occurrence between public reports. Directed edges do not prove direct copying, syndication agreement, or shared causality unless explicitly established." />
    </div>
  );
}

