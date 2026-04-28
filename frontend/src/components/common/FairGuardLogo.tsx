import React from 'react';

interface FairGuardLogoProps {
  size?: number;          // px – overall bounding box
  showText?: boolean;     // render "FAIR GUARD" wordmark next to icon
  glowIntensity?: 'none' | 'low' | 'high';
  className?: string;
}

/**
 * FairGuardLogo – compact geometric shield motif.
 */
const FairGuardLogo: React.FC<FairGuardLogoProps> = ({
  size = 32,
  showText = false,
  glowIntensity = 'low',
  className = '',
}) => {
  const glowFilter =
    glowIntensity === 'none'
      ? undefined
      : glowIntensity === 'high'
      ? 'drop-shadow(0 0 6px #CCFF00) drop-shadow(0 0 12px rgba(204,255,0,0.5))'
      : 'drop-shadow(0 0 3px rgba(204,255,0,0.7))';

  return (
    <span
      className={`fg-logo-root ${className}`}
      style={{ display: 'inline-flex', alignItems: 'center', gap: '0.5rem' }}
    >
      {/* ── Icon mark ─────────────────────────────────────────── */}
      <svg
        viewBox="0 0 64 64"
        xmlns="http://www.w3.org/2000/svg"
        width={size}
        height={size}
        style={{ filter: glowFilter, flexShrink: 0 }}
        aria-label="FairGuard logo mark"
      >
        <defs>
          {/* Subtle radial glow behind shield */}
          <radialGradient id="fgLogoOrb" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(204,255,0,0.15)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>
        </defs>

        {/* Orb background */}
        <circle cx="32" cy="32" r="30" fill="url(#fgLogoOrb)" />

        {/* ── Geometric Shield / Guard Motif ──────────────────────────── */}
        <g stroke="#CCFF00" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none">
          {/* Outer Shield Hexagon */}
          <polygon points="32,10 52,20 52,42 32,56 12,42 12,20" opacity="0.9" />
          {/* Inner geometry - Firewall grid lines */}
          <line x1="32" y1="10" x2="32" y2="56" opacity="0.6" />
          <line x1="12" y1="31" x2="52" y2="31" opacity="0.6" />
          
          {/* Central data node */}
          <rect x="26" y="25" width="12" height="12" rx="2" fill="#CCFF00" opacity="0.8" />
        </g>

        {/* Corner data pips */}
        <circle cx="32" cy="4"  r="1.5" fill="#CCFF00" opacity="0.5" />
        <circle cx="60" cy="32" r="1.5" fill="#CCFF00" opacity="0.5" />
        <circle cx="32" cy="60" r="1.5" fill="#CCFF00" opacity="0.5" />
        <circle cx="4"  cy="32" r="1.5" fill="#CCFF00" opacity="0.5" />
      </svg>

      {/* ── Optional wordmark ──────────────────────────────────── */}
      {showText && (
        <span
          style={{
            fontFamily: 'var(--font-display, "Space Grotesk", sans-serif)',
            fontWeight: 700,
            fontSize: size * 0.5,
            letterSpacing: '-0.5px',
            color: 'var(--text-main, #fff)',
            lineHeight: 1,
            userSelect: 'none',
          }}
        >
          FAIR<span style={{ color: '#CCFF00' }}>GUARD</span>
        </span>
      )}
    </span>
  );
};

export default FairGuardLogo;
