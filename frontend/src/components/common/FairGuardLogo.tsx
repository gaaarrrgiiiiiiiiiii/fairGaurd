import React from 'react';

interface FairGuardLogoProps {
  size?: number;          // px – overall bounding box
  showText?: boolean;     // render "FAIR GUARD" wordmark next to icon
  glowIntensity?: 'none' | 'low' | 'high';
  className?: string;
}

/**
 * FairGuardLogo – compact extraction of the hero face-scan animation.
 *
 * The mark is built from three visual "layers":
 *   1. Corner target brackets  (the scanner framing)
 *   2. Minimalist face outline (head + eyes)
 *   3. Scan cross-hair line    (the horizontal beam across the face)
 *
 * All three are rendered in #CCFF00 (Electric Lime) with a soft green glow.
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
          {/* Subtle radial glow behind face */}
          <radialGradient id="fgLogoOrb" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(204,255,0,0.10)" />
            <stop offset="100%" stopColor="transparent" />
          </radialGradient>

          {/* Scan-beam gradient */}
          <linearGradient id="fgScanGrad" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%"   stopColor="rgba(204,255,0,0)" />
            <stop offset="40%"  stopColor="rgba(204,255,0,0.45)" />
            <stop offset="60%"  stopColor="rgba(204,255,0,0.45)" />
            <stop offset="100%" stopColor="rgba(204,255,0,0)" />
          </linearGradient>
        </defs>

        {/* Orb background */}
        <circle cx="32" cy="32" r="30" fill="url(#fgLogoOrb)" />

        {/* ── Corner target brackets ──────────────────────────── */}
        <g stroke="#CCFF00" strokeWidth="3" strokeLinecap="round" fill="none" opacity="0.95">
          {/* Top-left */}
          <line x1="8"  y1="14" x2="8"  y2="24" />
          <line x1="8"  y1="14" x2="18" y2="14" />
          {/* Top-right */}
          <line x1="56" y1="14" x2="56" y2="24" />
          <line x1="56" y1="14" x2="46" y2="14" />
          {/* Bottom-left */}
          <line x1="8"  y1="50" x2="8"  y2="40" />
          <line x1="8"  y1="50" x2="18" y2="50" />
          {/* Bottom-right */}
          <line x1="56" y1="50" x2="56" y2="40" />
          <line x1="56" y1="50" x2="46" y2="50" />
        </g>

        {/* ── Face outline ───────────────────────────────────── */}
        <g fill="none" stroke="#CCFF00" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" opacity="0.8">
          {/* Head */}
          <ellipse cx="32" cy="30" rx="11" ry="14" />
          {/* Left eye socket */}
          <ellipse cx="27" cy="26" rx="2.5" ry="1.6" />
          {/* Right eye socket */}
          <ellipse cx="37" cy="26" rx="2.5" ry="1.6" />
          {/* Nose bridge */}
          <line x1="32" y1="29" x2="32" y2="33" />
          {/* Mouth curve */}
          <path d="M 27 37 Q 32 41 37 37" />
          {/* Chin/jaw connector */}
          <path d="M 21 43 Q 21 47 27 50 L 32 52 L 37 50 Q 43 47 43 43" opacity="0.5" />
        </g>

        {/* ── Horizontal scan cross-hair (the signature element) ─ */}
        <rect
          x="16" y="29" width="32" height="4" rx="2"
          fill="url(#fgScanGrad)"
          opacity="0.85"
        />

        {/* Eye dot fills */}
        <circle cx="27" cy="26" r="1" fill="#CCFF00" opacity="0.6" />
        <circle cx="37" cy="26" r="1" fill="#CCFF00" opacity="0.6" />

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
