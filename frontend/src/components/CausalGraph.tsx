import React from 'react';

const CausalGraph = ({ decision }: { decision?: any }) => {
  // Determine if there is bias and which attribute is the cause
  const isBiased = decision?.bias_detected === true;
  
  // Safe extraction of the protected variable that caused the bias ( defaulting to Sex for visual demo )
  let featureName = "Sex";
  if (decision && decision.explanation && decision.explanation.toLowerCase().includes("race")) {
    featureName = "Race";
  }

  // Dynamic Styles
  const highlightColor = isBiased ? "var(--accent-red)" : "#4b5563"; // We use red/yellow based on threat level
  const strokeWidth = isBiased ? "4" : "2";
  const markerHighlight = isBiased ? "url(#arrow-highlight)" : "url(#arrow-gray)";
  const nodeStroke = isBiased ? "var(--accent-red)" : "transparent";

  return (
    <div className="card-wrapper" style={{height: '350px'}}>
      <h2 className="card-title">Causal Graph Map (DoWhy)</h2>
      
      <div className="graph-container" style={{ padding: '0', backgroundColor: 'transparent', border: 'none' }}>
        <svg viewBox="0 0 500 200" style={{width: '100%', height: '100%', overflow: 'visible'}}>
          <defs>
            <marker id="arrow-highlight" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-red)" />
            </marker>
            <marker id="arrow-gray" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563" />
            </marker>
          </defs>
          
          {/* Paths */}
          {/* Dynamic Path from Protected Attribute to Industry/Intermediate */}
          <path d="M 100,50 L 250,50" stroke={highlightColor} strokeWidth={strokeWidth} markerEnd={markerHighlight} className={isBiased ? "animated-path" : ""}/>
          <path d="M 100,50 L 250,150" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" />
          
          <path d="M 100,150 L 250,150" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" />
          {/* Dynamic Path from Intermediate to Decision */}
          <path d="M 250,50 L 400,100" stroke={highlightColor} strokeWidth={strokeWidth} markerEnd={markerHighlight} className={isBiased ? "animated-path" : ""}/>
          <path d="M 250,150 L 400,100" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" />

          {/* Nodes */}
          {/* Protected Attribute Node */}
          <g transform="translate(100, 50)" style={{transition: 'all 0.5s'}}>
            <circle r="30" fill="var(--bg-card-hover)" stroke={nodeStroke} strokeWidth="3" />
            <text fill="white" textAnchor="middle" dy="4" fontSize="12" fontWeight="bold">{featureName}</text>
          </g>
          
          <g transform="translate(100, 150)">
            <circle r="30" fill="var(--bg-card-hover)" />
            <text fill="white" textAnchor="middle" dy="4" fontSize="12">Age / Exp</text>
          </g>
          
          {/* Intermediate Node */}
          <g transform="translate(250, 50)" style={{transition: 'all 0.5s'}}>
            <circle r="30" fill="var(--bg-card-hover)" stroke={nodeStroke} strokeWidth="2" />
            <text fill="white" textAnchor="middle" dy="4" fontSize="12">Domain</text>
          </g>
          
          <g transform="translate(250, 150)">
            <circle r="30" fill="var(--bg-card-hover)" />
            <text fill="white" textAnchor="middle" dy="4" fontSize="12">Income</text>
          </g>
          
          {/* Target Node */}
          <g transform="translate(400, 100)">
            <rect x="-35" y="-30" width="70" height="60" rx="8" fill={isBiased ? "var(--bg-card-hover)" : "var(--accent-green)"} stroke={isBiased ? "var(--accent-green)" : "none"} strokeWidth="2" style={{transition: 'all 0.5s'}}/>
            <text fill={isBiased ? "var(--text-main)" : "black"} textAnchor="middle" dy="4" fontSize="12" fontWeight="bold">Decision</text>
          </g>
        </svg>
      </div>
      <p style={{color: 'var(--text-muted)', fontSize: '12px', textAlign: 'center', marginTop: '1rem'}}>
        {isBiased ? "Red paths highlight active intervention thresholds due to Causal Attribution limits." : "Gray paths indicate standard, unbiased causal mapping flowing normally."}
      </p>
    </div>
  );
};

export default CausalGraph;
