import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  Settings, 
  MessageSquare, 
  Database, 
  BrainCircuit, 
  History,
  Activity,
  ChevronRight,
  Download,
  Upload,
  Play
} from 'lucide-react';
import './App.css';

// Mock Pages (Will separate into files later)
const TrainingPage = () => {
  const [thinkingLogs, setThinkingLogs] = useState([
    { type: 'plan', text: 'Initialize Metadata Agent for analysis' },
    { type: 'act', text: 'Fetching JSON Schema from Salesforce connector' },
    { type: 'observe', text: 'Identified 4 core objects: Opportunity, Account, Lead, Task' }
  ]);

  return (
    <div className="page-content">
      <div className="page-header">
        <h1 className="page-title">AutoML Training Phase</h1>
        <p className="page-subtitle">Define challenges and generate labeled training sets.</p>
      </div>

      <div className="grid-2">
        <div className="card">
          <h2 className="label">Agent Input</h2>
          <div className="input-group">
            <textarea 
              rows={6} 
              placeholder="Describe your problem statement and challenges (C1, C2...)"
              className="prompt-input"
            />
          </div>
          <div style={{ display: 'flex', gap: '12px' }}>
            <button className="btn-primary"><Database size={18} /> Connect Org</button>
            <button className="btn-primary" style={{ background: '#334155' }}><Upload size={18} /> Upload Data</button>
          </div>
        </div>

        <div className="card">
          <h2 className="label">Thinking Logs</h2>
          <div className="thinking-logs">
            {thinkingLogs.map((log, i) => (
              <div key={i} className="log-entry">
                <span className="log-time">[{new Date().toLocaleTimeString()}]</span>
                <span className={`log-${log.type}`}>[{log.type.toUpperCase()}]</span>
                <span>{log.text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
          <h2 className="label" style={{ margin: 0 }}>Identified Challenge Mapping</h2>
          <button className="btn-primary"><Download size={18} /> Download Labeled Template</button>
        </div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border)', textAlign: 'left' }}>
              <th style={{ padding: '12px', color: 'var(--text-muted)' }}>Challenge</th>
              <th style={{ padding: '12px', color: 'var(--text-muted)' }}>Feature Columns</th>
              <th style={{ padding: '12px', color: 'var(--text-muted)' }}>Type</th>
              <th style={{ padding: '12px', color: 'var(--text-muted)' }}>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style={{ padding: '12px' }}>C1: Opp Likelihood</td>
              <td style={{ padding: '12px' }}>Amount, Stage, CloseDate, Rep_History...</td>
              <td style={{ padding: '12px' }}><span className="badge">Classification</span></td>
              <td style={{ padding: '12px' }}><Activity size={16} color="#4ade80" /> Ready</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  );
};

const ProductionPage = () => (
  <div className="page-content">
    <div className="page-header">
      <h1 className="page-title">Production Inference Agent</h1>
      <p className="page-subtitle">Ask questions to your micro-models in real-time.</p>
    </div>
    <div className="card" style={{ height: '500px', display: 'flex', flexDirection: 'column' }}>
       <div style={{ flex: 1, overflowY: 'auto', marginBottom: '20px' }}>
          <div className="log-entry" style={{ background: 'rgba(99, 102, 241, 0.1)', padding: '12px', borderRadius: '12px' }}>
             <BrainCircuit size={20} color="#818cf8" />
             <span>Hello! I am connected to your micro-models. How can I help you today?</span>
          </div>
       </div>
       <div className="input-group" style={{ marginBottom: 0 }}>
          <div style={{ position: 'relative' }}>
            <input placeholder="What's the risk on the Acme Corp deal?" style={{ paddingRight: '50px' }} />
            <Play size={18} style={{ position: 'absolute', right: '16px', top: '14px', cursor: 'pointer', color: 'var(--primary)' }} />
          </div>
       </div>
    </div>
  </div>
);

function App() {
  const [activeTab, setActiveTab] = useState('training');

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="logo">AutoML Engine</div>
        <nav>
          <div 
            className={`nav-item ${activeTab === 'training' ? 'active' : ''}`}
            onClick={() => setActiveTab('training')}
          >
            <BrainCircuit size={20} />
            Training Phase
          </div>
          <div 
            className={`nav-item ${activeTab === 'production' ? 'active' : ''}`}
            onClick={() => setActiveTab('production')}
          >
            <MessageSquare size={20} />
            Production Phase
          </div>
          <div className="nav-item">
            <History size={20} />
            MLFlow Logs
          </div>
          <div className="nav-item">
            <Settings size={20} />
            System Config
          </div>
        </nav>
      </aside>

      <main className="main-content">
        {activeTab === 'training' ? <TrainingPage /> : <ProductionPage />}
      </main>
    </div>
  );
}

export default App;
