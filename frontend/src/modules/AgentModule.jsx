import React, { useState } from 'react';
import { Bot, Send, User, Sparkles } from 'lucide-react';
import { sendAgentMessage } from '../services/api';

export default function AgentModule() {
  const [messages, setMessages] = useState([
    {
      sender: 'agent',
      text: 'Hello! I am your AI Research Analyst. Ask me anything about current information cascades, emerging topics, or narrative evolutions.'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = { sender: 'user', text: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await sendAgentMessage(input);
      const agentMsg = { sender: 'agent', text: res.response };
      setMessages((prev) => [...prev, agentMsg]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { sender: 'agent', text: `Error: ${err.message}. Check the backend server and Google Gemini API configuration.` }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: '900px', margin: '0 auto' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '20px' }}>
        <Bot size={28} color="#2563eb" />
        <div>
          <h2 style={{ fontSize: '20px', fontWeight: 'bold' }}>AI Research Analyst Agent</h2>
        </div>
      </div>

      {/* Chat Area */}
      <div style={{
        background: '#ffffff',
        border: '1px solid #e2e8f0',
        borderRadius: '8px',
        height: '450px',
        display: 'flex',
        flexDirection: 'column',
        justify: 'space-between',
        boxShadow: '0 1px 3px rgba(0,0,0,0.05)'
      }}>
        {/* Messages */}
        <div style={{ padding: '16px', overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {messages.map((m, idx) => (
            <div key={idx} style={{
              display: 'flex',
              gap: '10px',
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '80%'
            }}>
              {m.sender === 'agent' && <Sparkles size={20} color="#2563eb" style={{ marginTop: '2px' }} />}
              <div style={{
                padding: '10px 14px',
                borderRadius: '8px',
                background: m.sender === 'user' ? '#2563eb' : '#f1f5f9',
                color: m.sender === 'user' ? '#ffffff' : '#1e293b',
                fontSize: '14px',
                lineHeight: '1.4'
              }}>
                {m.text}
              </div>
              {m.sender === 'user' && <User size={20} color="#64748b" style={{ marginTop: '2px' }} />}
            </div>
          ))}
          {loading && (
            <div style={{ fontSize: '13px', color: '#94a3b8', fontStyle: 'italic' }}>
              AI Analyst is preparing a concise response...
            </div>
          )}
        </div>

        {/* Input */}
        <form onSubmit={handleSend} style={{ borderTop: '1px solid #e2e8f0', padding: '12px', display: 'flex', gap: '8px' }}>
          <input
            type="text"
            placeholder="Ask a research question..."
            value={input}
            onChange={(e) => setInput(e.target.value)}
            style={{
              flex: 1,
              padding: '8px 12px',
              border: '1px solid #cbd5e1',
              borderRadius: '6px',
              outline: 'none',
              fontSize: '14px'
            }}
          />
          <button type="submit" disabled={loading} style={{
            background: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '6px',
            padding: '8px 16px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '6px'
          }}>
            <Send size={14} />
            <span>Send</span>
          </button>
        </form>
      </div>
    </div>
  );
}
