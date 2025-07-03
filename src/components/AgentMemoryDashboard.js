import React, { useState, useEffect } from 'react';

const AgentMemoryDashboard = () => {
  const [memoryData, setMemoryData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedAgent, setSelectedAgent] = useState('Zealot');

  useEffect(() => {
    const fetchMemoryData = async () => {
      try {
        const response = await fetch('/data/agent_memories.json');
        if (!response.ok) {
          throw new Error('Failed to fetch agent memory data');
        }
        const data = await response.json();
        setMemoryData(data);
        setLoading(false);
      } catch (err) {
        setError(err.message);
        setLoading(false);
      }
    };

    fetchMemoryData();
    
    // Refresh every 30 seconds
    const interval = setInterval(fetchMemoryData, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) return <div className="loading">Loading agent memories...</div>;
  if (error) return <div className="error">Error: {error}</div>;
  if (!memoryData || !memoryData.agents) return <div className="error">No memory data available</div>;

  const agent = memoryData.agents[selectedAgent];
  if (!agent) return <div className="error">Agent data not found</div>;

  const PersonalityChart = ({ traits }) => {
    if (!traits) return <div>No personality data</div>;
    
    return (
      <div className="personality-chart">
        <h4>🧠 Personality Evolution</h4>
        <div className="traits-grid">
          {Object.entries(traits).map(([traitName, traitData]) => (
            <div key={traitName} className="trait-item">
              <div className="trait-name">{traitName}</div>
              <div className="trait-bar">
                <div 
                  className="trait-fill"
                  style={{ 
                    width: `${traitData.strength * 100}%`,
                    backgroundColor: getTraitColor(traitData.strength)
                  }}
                />
              </div>
              <div className="trait-value">{traitData.strength.toFixed(2)}</div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const getTraitColor = (strength) => {
    if (strength > 0.8) return '#ff4444';
    if (strength > 0.6) return '#ff8844';
    if (strength > 0.4) return '#ffaa44';
    return '#44aa44';
  };

  const RelationshipNetwork = ({ relationships }) => {
    if (!relationships || !relationships.relationships) return <div>No relationship data</div>;

    return (
      <div className="relationship-network">
        <h4>🤝 Relationships</h4>
        <div className="network-stats">
          <div className="stat">
            <span className="stat-label">Average Trust:</span>
            <span className="stat-value">{relationships.average_trust}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Allies:</span>
            <span className="stat-value">{relationships.trusted_allies}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Enemies:</span>
            <span className="stat-value">{relationships.enemies}</span>
          </div>
        </div>
        
        <div className="relationships-list">
          {Object.entries(relationships.relationships).map(([agentName, rel]) => (
            <div key={agentName} className="relationship-item">
              <div className="relationship-agent">{agentName}</div>
              <div className="relationship-status" style={{
                color: getTrustColor(rel.trust_score)
              }}>
                {rel.relationship_status}
              </div>
              <div className="trust-score">
                Trust: {rel.trust_score}
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };

  const getTrustColor = (trustScore) => {
    if (trustScore > 0.5) return '#44aa44';
    if (trustScore > 0) return '#aaaa44';
    if (trustScore > -0.3) return '#aa4444';
    return '#ff4444';
  };

  const DebatePerformance = ({ performance }) => {
    if (!performance) return <div>No performance data</div>;

    return (
      <div className="debate-performance">
        <h4>📊 Debate Performance</h4>
        <div className="performance-stats">
          <div className="stat-row">
            <div className="stat">
              <span className="stat-label">Total Debates:</span>
              <span className="stat-value">{performance.total_debates}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Proposals:</span>
              <span className="stat-value">{performance.total_proposals}</span>
            </div>
          </div>
          <div className="stat-row">
            <div className="stat">
              <span className="stat-label">Success Rate:</span>
              <span className="stat-value">{(performance.proposal_success_rate * 100).toFixed(1)}%</span>
            </div>
            <div className="stat">
              <span className="stat-label">Satisfaction:</span>
              <span className="stat-value">{performance.average_satisfaction.toFixed(2)}</span>
            </div>
          </div>
        </div>

        {performance.recent_debates && performance.recent_debates.length > 0 && (
          <div className="recent-debates">
            <h5>Recent Debates</h5>
            {performance.recent_debates.map((debate, index) => (
              <div key={index} className="debate-item">
                <div className="debate-cycle">Cycle {debate.cycle}</div>
                <div className="debate-role">{debate.role}</div>
                <div className="debate-outcome" style={{
                  color: getOutcomeColor(debate.outcome)
                }}>
                  {debate.outcome}
                </div>
                <div className="debate-satisfaction">
                  😊 {debate.satisfaction.toFixed(2)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const getOutcomeColor = (outcome) => {
    switch (outcome.toLowerCase()) {
      case 'accept': return '#44aa44';
      case 'reject': return '#aa4444';
      case 'mutate': return '#aaaa44';
      default: return '#888888';
    }
  };

  const BeliefSystem = ({ beliefs }) => {
    if (!beliefs) return <div>No belief data</div>;

    return (
      <div className="belief-system">
        <h4>💭 Personal Beliefs</h4>
        <div className="belief-stats">
          <div className="stat">
            <span className="stat-label">Total Beliefs:</span>
            <span className="stat-value">{beliefs.total_beliefs}</span>
          </div>
          <div className="stat">
            <span className="stat-label">High Confidence:</span>
            <span className="stat-value">{beliefs.high_confidence_beliefs}</span>
          </div>
          <div className="stat">
            <span className="stat-label">Challenged:</span>
            <span className="stat-value">{beliefs.challenged_beliefs}</span>
          </div>
        </div>

        {beliefs.top_beliefs && beliefs.top_beliefs.length > 0 && (
          <div className="top-beliefs">
            <h5>Core Beliefs</h5>
            {beliefs.top_beliefs.map((belief, index) => (
              <div key={index} className="belief-item">
                <div className="belief-content">{belief.content}</div>
                <div className="belief-meta">
                  <span className="belief-type">{belief.type}</span>
                  <span className="belief-confidence">
                    Confidence: {belief.confidence.toFixed(2)}
                  </span>
                  <span className="belief-importance">
                    Importance: {belief.importance.toFixed(2)}
                  </span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  };

  const MemorySpecialization = ({ specialization }) => {
    if (!specialization) return <div>No specialization data</div>;

    return (
      <div className="memory-specialization">
        <h4>🎯 Specialization</h4>
        <div className="specialization-content">
          <div className="specialization-type">{specialization.specialization}</div>
          
          {Object.entries(specialization).map(([key, value]) => {
            if (key === 'specialization') return null;
            
            return (
              <div key={key} className="specialization-stat">
                <span className="spec-label">{key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}:</span>
                <span className="spec-value">
                  {typeof value === 'object' ? JSON.stringify(value) : value}
                </span>
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className="agent-memory-dashboard">
      <div className="dashboard-header">
        <h2>🧠 Agent Memory Dashboard</h2>
        <div className="last-updated">
          Last Updated: {new Date(memoryData.last_updated).toLocaleString()}
        </div>
      </div>

      <div className="agent-selector">
        {Object.keys(memoryData.agents).map(agentName => (
          <button
            key={agentName}
            className={`agent-button ${selectedAgent === agentName ? 'active' : ''}`}
            onClick={() => setSelectedAgent(agentName)}
          >
            {agentName}
          </button>
        ))}
      </div>

      <div className="agent-details">
        <h3>{selectedAgent} Memory Profile</h3>
        
        <div className="memory-grid">
          <div className="memory-section">
            <PersonalityChart traits={agent.personality_evolution?.traits} />
          </div>
          
          <div className="memory-section">
            <RelationshipNetwork relationships={agent.relationships} />
          </div>
          
          <div className="memory-section">
            <DebatePerformance performance={agent.debate_performance} />
          </div>
          
          <div className="memory-section">
            <BeliefSystem beliefs={agent.belief_system} />
          </div>
          
          <div className="memory-section">
            <MemorySpecialization specialization={agent.memory_specialization} />
          </div>
        </div>
      </div>

      {memoryData.relationship_network && (
        <div className="network-overview">
          <h3>🌐 Network Overview</h3>
          <div className="network-stats">
            <div className="stat">
              <span className="stat-label">Average Trust:</span>
              <span className="stat-value">{memoryData.relationship_network.average_network_trust}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Polarization:</span>
              <span className="stat-value">{memoryData.relationship_network.network_polarization}</span>
            </div>
            <div className="stat">
              <span className="stat-label">Total Relationships:</span>
              <span className="stat-value">{memoryData.relationship_network.total_relationships}</span>
            </div>
          </div>
        </div>
      )}

      <style jsx>{`
        .agent-memory-dashboard {
          background: #1a1a1a;
          color: #e0e0e0;
          padding: 20px;
          border-radius: 10px;
          margin: 20px 0;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 20px;
          border-bottom: 2px solid #333;
          padding-bottom: 10px;
        }

        .last-updated {
          font-size: 0.9em;
          color: #888;
        }

        .agent-selector {
          display: flex;
          gap: 10px;
          margin-bottom: 20px;
        }

        .agent-button {
          background: #333;
          color: #e0e0e0;
          border: none;
          padding: 10px 20px;
          border-radius: 5px;
          cursor: pointer;
          transition: all 0.3s;
        }

        .agent-button:hover {
          background: #444;
        }

        .agent-button.active {
          background: #0066cc;
          color: white;
        }

        .memory-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
          gap: 20px;
        }

        .memory-section {
          background: #2a2a2a;
          padding: 15px;
          border-radius: 8px;
          border: 1px solid #333;
        }

        .memory-section h4 {
          color: #4CAF50;
          margin: 0 0 15px 0;
          border-bottom: 1px solid #333;
          padding-bottom: 5px;
        }

        .traits-grid {
          display: grid;
          gap: 8px;
        }

        .trait-item {
          display: grid;
          grid-template-columns: 120px 1fr 60px;
          align-items: center;
          gap: 10px;
        }

        .trait-name {
          font-size: 0.9em;
          text-transform: capitalize;
        }

        .trait-bar {
          background: #444;
          height: 8px;
          border-radius: 4px;
          overflow: hidden;
        }

        .trait-fill {
          height: 100%;
          transition: width 0.5s ease;
        }

        .trait-value {
          text-align: right;
          font-size: 0.8em;
          color: #ccc;
        }

        .stat, .stat-row {
          display: flex;
          justify-content: space-between;
          margin: 5px 0;
        }

        .stat-row {
          gap: 20px;
        }

        .stat-label {
          color: #aaa;
        }

        .stat-value {
          color: #4CAF50;
          font-weight: bold;
        }

        .relationship-item, .debate-item, .belief-item {
          background: #333;
          padding: 10px;
          margin: 8px 0;
          border-radius: 5px;
          border-left: 3px solid #0066cc;
        }

        .relationship-item {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr;
          gap: 10px;
          align-items: center;
        }

        .debate-item {
          display: grid;
          grid-template-columns: 1fr 1fr 1fr 1fr;
          gap: 10px;
          align-items: center;
          font-size: 0.9em;
        }

        .belief-content {
          font-style: italic;
          margin-bottom: 5px;
        }

        .belief-meta {
          display: flex;
          gap: 15px;
          font-size: 0.8em;
          color: #aaa;
        }

        .network-overview {
          margin-top: 30px;
          padding: 20px;
          background: #2a2a2a;
          border-radius: 8px;
          border: 2px solid #0066cc;
        }

        .network-stats {
          display: flex;
          gap: 30px;
          justify-content: center;
        }

        .loading, .error {
          text-align: center;
          padding: 40px;
          font-size: 1.2em;
        }

        .error {
          color: #ff4444;
        }

        .loading {
          color: #4CAF50;
        }
      `}</style>
    </div>
  );
};

export default AgentMemoryDashboard;