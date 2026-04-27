
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
      
      <div className="graph-container" style={{ padding: '0', border: 'none' }}>
        <svg viewBox="0 0 500 200" style={{width: '100%', height: '100%', overflow: 'visible'}}>
          <defs>
            <marker id="arrow-highlight" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="var(--accent-red)" />
            </marker>
            <marker id="arrow-gray" viewBox="0 0 10 10" refX="28" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#4b5563" />
            </marker>
            <radialGradient id="nodeGrad" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(184, 242, 58, 0.08)" />
              <stop offset="100%" stopColor="rgba(11, 14, 20, 0.9)" />
            </radialGradient>
            <radialGradient id="nodeGradBiased" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="rgba(239, 68, 68, 0.1)" />
              <stop offset="100%" stopColor="rgba(11, 14, 20, 0.9)" />
            </radialGradient>
            <filter id="graphGlow">
              <feGaussianBlur stdDeviation="3" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          
          {/* Paths */}
          {/* Dynamic Path from Protected Attribute to Industry/Intermediate */}
          <path
            d="M 100,50 L 250,50"
            stroke={highlightColor}
            strokeWidth={strokeWidth}
            markerEnd={markerHighlight}
            className={isBiased ? "graph-path-animated" : ""}
            strokeDasharray={isBiased ? "10 5" : "none"}
            filter={isBiased ? "url(#graphGlow)" : undefined}
          />
          <path d="M 100,50 L 250,150" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" opacity={0.6} />
          
          <path d="M 100,150 L 250,150" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" opacity={0.6} />
          {/* Dynamic Path from Intermediate to Decision */}
          <path
            d="M 250,50 L 400,100"
            stroke={highlightColor}
            strokeWidth={strokeWidth}
            markerEnd={markerHighlight}
            className={isBiased ? "graph-path-animated" : ""}
            strokeDasharray={isBiased ? "10 5" : "none"}
            filter={isBiased ? "url(#graphGlow)" : undefined}
          />
          <path d="M 250,150 L 400,100" stroke="#4b5563" strokeWidth="2" markerEnd="url(#arrow-gray)" opacity={0.6} />

          {/* Nodes */}
          {/* Protected Attribute Node */}
          <g className="graph-node" transform="translate(100, 50)" style={{transition: 'all 0.5s'}}>
            <circle r="30" fill={isBiased ? "url(#nodeGradBiased)" : "url(#nodeGrad)"} stroke={nodeStroke} strokeWidth="2" />
            {isBiased && <circle r="30" fill="none" stroke="var(--accent-red)" strokeWidth="1" opacity="0.3" className="graph-node-pulse" />}
            <text fill="white" textAnchor="middle" dy="4" fontSize="11" fontWeight="bold" fontFamily="Inter">{featureName}</text>
          </g>
          
          <g className="graph-node" transform="translate(100, 150)">
            <circle r="30" fill="url(#nodeGrad)" stroke="rgba(42, 54, 74, 0.5)" strokeWidth="1" />
            <text fill="#9ca3af" textAnchor="middle" dy="4" fontSize="11" fontFamily="Inter">Age / Exp</text>
          </g>
          
          {/* Intermediate Node */}
          <g className="graph-node" transform="translate(250, 50)" style={{transition: 'all 0.5s'}}>
            <circle r="30" fill={isBiased ? "url(#nodeGradBiased)" : "url(#nodeGrad)"} stroke={nodeStroke} strokeWidth="1.5" />
            {isBiased && <circle r="30" fill="none" stroke="var(--accent-red)" strokeWidth="1" opacity="0.3" className="graph-node-pulse" />}
            <text fill="white" textAnchor="middle" dy="4" fontSize="11" fontFamily="Inter">Domain</text>
          </g>
          
          <g className="graph-node" transform="translate(250, 150)">
            <circle r="30" fill="url(#nodeGrad)" stroke="rgba(42, 54, 74, 0.5)" strokeWidth="1" />
            <text fill="#9ca3af" textAnchor="middle" dy="4" fontSize="11" fontFamily="Inter">Income</text>
          </g>
          
          {/* Target Node */}
          <g className="graph-node" transform="translate(400, 100)">
            <rect
              x="-35" y="-30" width="70" height="60" rx="12"
              fill={isBiased ? "url(#nodeGradBiased)" : "rgba(16, 185, 129, 0.15)"}
              stroke={isBiased ? "var(--accent-red)" : "var(--accent-green)"}
              strokeWidth="2"
              style={{transition: 'all 0.5s'}}
            />
            <text fill={isBiased ? "var(--text-main)" : "var(--accent-green)"} textAnchor="middle" dy="4" fontSize="12" fontWeight="bold" fontFamily="Syne">Decision</text>
          </g>
        </svg>
      </div>
      <p style={{color: 'var(--text-muted)', fontSize: '11px', textAlign: 'center', marginTop: '0.75rem', fontFamily: 'var(--font-mono)', letterSpacing: '0.3px'}}>
        {isBiased ? "Red paths highlight active intervention thresholds due to Causal Attribution limits." : "Gray paths indicate standard, unbiased causal mapping flowing normally."}
      </p>
    </div>
  );
};

export default CausalGraph;
