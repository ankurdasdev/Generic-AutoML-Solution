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

// Wizard Steps Definition
const STEPS = [
  { id: 1, name: 'Problem Definition', desc: 'Draft statement & challenges' },
  { id: 2, name: 'Data Connection', desc: 'Connect org or upload' },
  { id: 3, name: 'Knowledge Mapping', desc: 'Reasoning & discovery' },
  { id: 4, name: 'Interactive EDA', desc: 'Feature engineering' },
  { id: 5, name: 'Final Template', desc: 'Download Excel' }
];

const ProgressBar = ({ currentStep }: { currentStep: number }) => (
  <div className="progress-container">
    <div className="progress-bar-bg">
      <div 
        className="progress-bar-fill" 
        style={{ width: `${(currentStep / STEPS.length) * 100}%` }}
      />
    </div>
    <div className="steps-labels">
      {STEPS.map(s => (
        <div key={s.id} className={`step-label ${currentStep >= s.id ? 'active' : ''}`}>
          <div className="step-number">{s.id}</div>
          <span>{s.name}</span>
        </div>
      ))}
    </div>
  </div>
);

const SystemConfig = () => (
  <div className="page-content">
    <div className="page-header">
      <h1 className="page-title">System Configuration</h1>
      <p className="page-subtitle">Manage your enterprise connections and OAuth handshakes.</p>
    </div>
    <div className="grid-2">
      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
          <div className="connector-icon sf">SF</div>
          <h2 className="label" style={{ margin: 0 }}>Salesforce Integration</h2>
        </div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
          Connect via OAuth 2.0 to fetch object metadata and training data directly from your Salesforce Org.
        </p>
        <button className="btn-primary" style={{ width: '100%' }}>
          <Database size={18} /> Connect Salesforce Org
        </button>
      </div>

      <div className="card">
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px', marginBottom: '20px' }}>
          <div className="connector-icon db">DB</div>
          <h2 className="label" style={{ margin: 0 }}>Databricks Compute</h2>
        </div>
        <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
          Configure your Databricks SQL Warehouse to handle high-scale analytical processing and model training.
        </p>
        <button className="btn-primary" style={{ width: '100%', background: '#334155' }}>
          <Settings size={18} /> Setup Databricks
        </button>
      </div>
    </div>
  </div>
);

const TrainingWizard = ({ 
  step, 
  setStep, 
  onConfigRoute 
}: { 
  step: number, 
  setStep: (s: number) => void,
  onConfigRoute: () => void
}) => {
  const [isLocked, setIsLocked] = useState(false);
  const [problemDraft, setProblemDraft] = useState("");
  const [challenges, setChallenges] = useState<string[]>([]);
  const [isConnected, setIsConnected] = useState(false);
  const [dataContext, setDataContext] = useState("");
  
  const [messages, setMessages] = useState<Array<{role: 'ai' | 'user', text: string}>>([
    { role: 'ai', text: "Hello! I'm your AI partner. Please describe the business goal or problem you'd like to solve, and I'll help you break it down into actionable machine learning challenges." }
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isTyping) return;

    const userMsg = { role: 'user', text: inputValue };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages as any);
    setInputValue("");
    setIsTyping(true);

    try {
      const response = await fetch('http://localhost:8000/training/discuss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          history: messages.map(m => ({ role: m.role, text: m.text })),
          user_input: inputValue
        })
      });
      const data = await response.json();
      
      setMessages([...newMessages, { role: 'ai', text: data.ai_message }] as any);
      setProblemDraft(data.problem_statement);
      setChallenges(data.challenges);
    } catch (error) {
      console.error("Discussion Error:", error);
    } finally {
      setIsTyping(false);
    }
  };

  const handlePrev = () => step > 1 && setStep(step - 1);
  const handleNext = () => step < STEPS.length && setStep(step + 1);

  const renderStep = () => {
    switch(step) {
      case 1:
        return (
          <div className="wizard-split">
            {/* Left Panel: Collaboration */}
            <div className="wizard-panel left">
              <h2 className="label">Collaborative Drafter</h2>
              <p className="panel-desc">Discuss your goals with the AI to refine the challenges.</p>
              <div className="chat-container">
                 <div className="chat-scroll" style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', marginBottom: '20px', paddingRight: '8px' }}>
                    {messages.map((m, i) => (
                      <div key={i} className={`chat-bubble ${m.role}`}>
                        {m.role === 'ai' && (
                          <div className="chat-icon-box">
                             <BrainCircuit size={20} />
                          </div>
                        )}
                        <span>{m.text}</span>
                      </div>
                    ))}
                    {isTyping && <div className="chat-bubble ai"><i>Agent is thinking...</i></div>}
                 </div>
                 
                 <div className="command-box">
                    <textarea 
                      rows={2} 
                      disabled={isLocked || isTyping}
                      placeholder="Type to discuss..."
                      className="prompt-input"
                      value={inputValue}
                      onChange={(e) => setInputValue(e.target.value)}
                      onKeyDown={(e) => e.key === 'Enter' && !e.shiftKey && (e.preventDefault(), handleSendMessage())}
                    />
                    <div className="input-actions">
                       <button className="btn-send" onClick={handleSendMessage} disabled={isTyping}>
                          <Play size={18} />
                       </button>
                    </div>
                 </div>
              </div>
            </div>

            {/* Right Panel: Official Draft */}
            <div className="wizard-panel right">
              <h2 className="label">Official Draft Board</h2>
              <div className="draft-preview">
                 <h3>Problem Statement</h3>
                 <p>{problemDraft || "Awaiting your first description..."}</p>
                 <div className="challenge-pills">
                    {challenges.map(c => (
                      <span key={c} className="pill">{c}</span>
                    ))}
                 </div>
              </div>
              <div style={{ marginTop: 'auto', paddingTop: '24px' }}>
                <button 
                  className="btn-primary" 
                  style={{ width: '100%' }}
                  onClick={() => setIsLocked(true)}
                  disabled={isLocked}
                >
                  {isLocked ? 'Scope Locked' : 'Lock & Finalize Scope'}
                </button>
              </div>
            </div>
          </div>
        );
      case 2:
        return (
          <div className="wizard-step">
             <div className="card">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
                   <h2 className="label" style={{ margin: 0 }}>Step 2: Data Linker</h2>
                   <div className={`status-badge ${isConnected ? 'connected' : 'disconnected'}`}>
                      {isConnected ? 'Org Connected' : 'Not Connected'}
                   </div>
                </div>
                
                {!isConnected ? (
                  <div className="connection-prompt">
                    <Database size={48} color="var(--text-muted)" style={{ marginBottom: '16px' }} />
                    <p>No enterprise organization is linked to this workspace.</p>
                    <button className="btn-primary" onClick={onConfigRoute}>
                      Go to System Config <Settings size={18} />
                    </button>
                  </div>
                ) : (
                  <div className="context-form">
                    <h4 className="label" style={{ fontSize: '0.75rem' }}>Dataset Context & Instructions</h4>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '16px' }}>
                      Tell the AI which tables or timeframes to focus on.
                    </p>
                    <textarea 
                      rows={4}
                      placeholder="e.g., 'Focus only on the Opportunity and Account objects. Use data from the last 2 fiscal years...'"
                      className="prompt-input"
                      value={dataContext}
                      onChange={(e) => setDataContext(e.target.value)}
                    />
                  </div>
                )}
                
                <div className="grid-2" style={{ marginTop: '32px', opacity: isConnected ? 0.5 : 1 }}>
                  <div className="source-option" onClick={() => setIsConnected(true)}>
                    <Upload size={32} />
                    <h3>Manual Upload</h3>
                    <p>Process offline Excel files</p>
                  </div>
                </div>
             </div>
          </div>
        );
      case 3:
        return (
          <div className="wizard-step">
            <div className="card">
              <h2 className="label">Step 3: Intelligence Mapping</h2>
              <div className="discovery-header" style={{ marginBottom: '24px', background: 'var(--accent-soft)', padding: '24px', borderRadius: '20px' }}>
                 <BrainCircuit size={32} color="var(--primary)" />
                 <div style={{ flex: 1 }}>
                    <h4 style={{ margin: '0 0 8px 0', fontSize: '1.1rem' }}>Contextual Reasoning</h4>
                    <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: '1.6' }}>
                      Based on your context <strong>"{dataContext || 'General Org Scope'}"</strong>, I've prioritized the most relevant data elements to satisfy your drafted challenges.
                    </p>
                 </div>
              </div>
              <div className="mapping-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '20px' }}>
                 <div className="mapping-card">
                   <h5 className="label">Relevant Data Entities</h5>
                   <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                     {['Entity A', 'Entity B', 'Entity C'].map(o => <span key={o} className="pill">{o}</span>)}
                   </div>
                 </div>
                 <div className="mapping-card">
                   <h5 className="label">Identified Feature Clusters</h5>
                   <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                     {['Temporal Trends', 'Frequency Metrics', 'Historical State'].map(f => <span key={f} className="pill">{f}</span>)}
                   </div>
                 </div>
              </div>
            </div>
          </div>
        );
      case 4:
        return (
          <div className="wizard-step">
            <div className="card">
              <h2 className="label">Step 4: Collaborative EDA</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '24px' }}>
                Review the engineered feature plan. Our agent has prepared these based on your specific requirements.
              </p>
              
              <div className="feature-list" style={{ marginBottom: '32px' }}>
                 {[
                   { name: 'Feature A', desc: 'Calculated based on time intervals' },
                   { name: 'Feature B', desc: 'Normalized distribution mapping' },
                   { name: 'Feature C', desc: 'Aggregated historical values' }
                 ].map((f, i) => (
                   <div key={i} className="feature-item-refined">
                      <div className="checkbox-mock active"></div>
                      <div style={{ flex: 1 }}>
                        <strong style={{ display: 'block' }}>{f.name}</strong>
                        <span>{f.desc}</span>
                      </div>
                   </div>
                 ))}
              </div>

              <div className="discussion-box-refined">
                 <h4 className="label" style={{ fontSize: '0.7rem' }}>Refine Engineering Logic</h4>
                 <div style={{ display: 'flex', gap: '12px' }}>
                    <input placeholder="e.g., 'Also add a column for average deal size...'" />
                    <button className="btn-primary">Suggest</button>
                 </div>
              </div>
            </div>
          </div>
        );
      case 5:
        return (
          <div className="wizard-step">
            <div className="card" style={{ textAlign: 'center', padding: '60px 40px' }}>
              <div style={{ marginBottom: '32px' }}>
                <Download size={64} color="var(--primary)" />
              </div>
              <h2 className="page-title">Ready for Final Labeling</h2>
              <p style={{ color: 'var(--text-muted)', marginBottom: '40px', maxWidth: '500px', marginInline: 'auto' }}>
                The AI has finalized the engineering. Download your challenge sheets and provide the target values.
              </p>
              <button className="btn-primary" style={{ margin: '0 auto', padding: '16px 32px' }}>
                <Download size={20} /> Export Knowledge Sheets (.xlsx)
              </button>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="page-content">
      <ProgressBar currentStep={step} />
      <div className="wizard-container">
        <main className="wizard-main">
          {renderStep()}
          
          <div className="wizard-nav" style={{ display: 'flex', justifyContent: 'space-between', marginTop: '32px' }}>
             <button 
               className="btn-secondary" 
               onClick={handlePrev}
               disabled={step === 1}
             >
               Back
             </button>
             <button 
               className="btn-primary" 
               onClick={handleNext}
               disabled={step === 5 || (!isLocked && step === 1)}
             >
               Continue <ChevronRight size={18} />
             </button>
          </div>
        </main>
      </div>
    </div>
  );
};

function App() {
  const [activeTab, setActiveTab] = useState('training');
  const [trainingStep, setTrainingStep] = useState(1);

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
          <div 
            className={`nav-item ${activeTab === 'config' ? 'active' : ''}`}
            onClick={() => setActiveTab('config')}
          >
            <Settings size={20} />
            System Config
          </div>
        </nav>
      </aside>

      <main className="main-content">
        {activeTab === 'training' && (
          <TrainingWizard 
            step={trainingStep} 
            setStep={setTrainingStep} 
            onConfigRoute={() => setActiveTab('config')} 
          />
        )}
        {activeTab === 'production' && <ProductionPage />}
        {activeTab === 'config' && <SystemConfig />}
      </main>
    </div>
  );
}

export default App;
