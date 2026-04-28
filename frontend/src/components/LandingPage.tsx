import { useNavigate } from 'react-router-dom';
import './LandingPage.css';
import FairGuardLogo from './common/FairGuardLogo';

/* ─── Hero Dashboard Terminal Preview ───────────────────────────── */
function HeroDashboard() {
  const decisions = [
    { id: 'DEC-8812', outcome: 'APPROVED', dpd: '0.01', status: 'compliant', delay: '0s' },
    { id: 'DEC-8813', outcome: 'CORRECTED', dpd: '0.09', status: 'corrected', delay: '0.4s' },
    { id: 'DEC-8814', outcome: 'APPROVED', dpd: '0.02', status: 'compliant', delay: '0.8s' },
    { id: 'DEC-8815', outcome: 'FLAGGED',  dpd: '0.18', status: 'flagged',   delay: '1.2s' },
    { id: 'DEC-8816', outcome: 'APPROVED', dpd: '0.03', status: 'compliant', delay: '1.6s' },
  ];

  return (
    <div className="lp-hero-dashboard">
      {/* ── Window chrome ──────────────────────────────────── */}
      <div className="lp-dash-chrome">
        <span className="lp-dash-dot red" />
        <span className="lp-dash-dot yellow" />
        <span className="lp-dash-dot green" />
        <span className="lp-dash-title">fairguard · live stream</span>
      </div>

      {/* ── Logo mark centred ─────────────────────────────── */}
      <div className="lp-dash-logo-zone">
        <FairGuardLogo size={72} glowIntensity="high" />
        <div className="lp-dash-logo-ring" />
        <div className="lp-dash-logo-ring lp-dash-logo-ring-2" />
      </div>

      {/* ── Metric row ────────────────────────────────────── */}
      <div className="lp-dash-metrics">
        <div className="lp-dash-metric">
          <span className="lp-dash-metric-val">0.02</span>
          <span className="lp-dash-metric-label">Avg DPD</span>
        </div>
        <div className="lp-dash-metric-sep" />
        <div className="lp-dash-metric">
          <span className="lp-dash-metric-val lime">98.4%</span>
          <span className="lp-dash-metric-label">Compliant</span>
        </div>
        <div className="lp-dash-metric-sep" />
        <div className="lp-dash-metric">
          <span className="lp-dash-metric-val">&lt;42ms</span>
          <span className="lp-dash-metric-label">Latency</span>
        </div>
      </div>

      {/* ── Decision feed ─────────────────────────────────── */}
      <div className="lp-dash-feed">
        {decisions.map((d) => (
          <div
            key={d.id}
            className={`lp-dash-row lp-dash-row-${d.status}`}
            style={{ animationDelay: d.delay }}
          >
            <span className="lp-dash-row-id">{d.id}</span>
            <span className="lp-dash-row-outcome">{d.outcome}</span>
            <span className="lp-dash-row-dpd">DPD {d.dpd}</span>
            <span className={`lp-dash-row-dot ${d.status}`} />
          </div>
        ))}
      </div>

      {/* ── Status bar ────────────────────────────────────── */}
      <div className="lp-dash-statusbar">
        <span className="lp-badge-dot green" />
        <span>LIVE · 2,847 decisions today</span>
        <span className="lp-dash-statusbar-right">v2.0.0</span>
      </div>

      {/* ── Floating badges (kept from original) ──────────── */}
      <div className="lp-scan-badge lp-scan-badge-1">
        <span className="lp-badge-dot green" />BIAS FREE
      </div>
      <div className="lp-scan-badge lp-scan-badge-2">
        <span className="lp-badge-dot yellow" />DPD: 0.02
      </div>
      <div className="lp-scan-badge lp-scan-badge-3">
        <span className="lp-badge-dot green" />COMPLIANT
      </div>
    </div>
  );
}

/* ─── Feature Bento Card with Color Variants ─────────────────────── */
function FeatureCard({ icon, title, desc, color = 'solid-lime', arrow = false, featured = false }: {
  icon: string; title: string; desc: string;
  color?: 'solid-lime' | 'solid-purple' | 'solid-dark' | 'solid-white' | 'solid-emerald' | 'solid-indigo' | 'green' | 'violet' | 'cyan' | 'amber' | 'pink' | 'lime';
  arrow?: boolean; featured?: boolean;
}) {
  return (
    <div className={`lp-feature-card lp-color-${color} ${featured ? 'lp-feature-featured' : ''}`}>
      <div className="lp-feature-icon-wrap">{icon}</div>
      <h3 className="lp-feature-title">{title}</h3>
      <p className="lp-feature-desc">{desc}</p>
      {arrow && <div className="lp-feature-arrow">↗</div>}
    </div>
  );
}

/* ─── Step Card ───────────────────────────────────────────────────── */
function StepCard({ num, title, desc, color = 'solid-emerald' }: {
  num: string; title: string; desc: string;
  color?: 'solid-lime' | 'solid-purple' | 'solid-dark' | 'solid-white' | 'solid-emerald' | 'solid-indigo';
}) {
  return (
    <div className={`lp-step-card lp-step-${color}`}>
      <div className="lp-step-num">{num}</div>
      <h3 className="lp-step-title">{title}</h3>
      <p className="lp-step-desc">{desc}</p>
    </div>
  );
}

/* ═══════════════════════════════════════════════════════════════════
   LANDING PAGE COMPONENT
   ═══════════════════════════════════════════════════════════════════ */
export default function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="lp-root">

      {/* ─── NAVBAR ────────────────────────────────────────────── */}
      <nav className="lp-nav">
        <div className="lp-nav-inner">
          <div className="lp-nav-logo">
            <FairGuardLogo size={30} glowIntensity="low" />
            FAIR<span className="lp-nav-logo-accent">GUARD</span>
          </div>
          <div className="lp-nav-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#capabilities">Capabilities</a>
            <a href="#stats">Enterprise</a>
          </div>
          <div className="lp-nav-actions">
            <button className="lp-btn-ghost" onClick={() => navigate('/auth')}>Log in</button>
            <button className="lp-btn-primary" onClick={() => navigate('/auth')}>
              Try for free <span className="lp-btn-arrow">↗</span>
            </button>
          </div>
        </div>
      </nav>

      {/* ─── HERO SECTION ──────────────────────────────────────── */}
      <section className="lp-hero">
        <div className="lp-hero-content">
          <div className="lp-hero-text">
            <div className="lp-hero-badge">
              <span className="lp-badge-dot green" />
              AI Fairness Firewall — Now in v2.0
            </div>
            <h1 className="lp-hero-heading">
              Intercept Bias.<br />
              Protect <span className="lp-text-lime">Fairness</span>.<br />
              Ship Confidently.
            </h1>
            <p className="lp-hero-sub">
              FairGuard sits between your AI model and production, automatically detecting and correcting
              algorithmic bias in real-time before unfair decisions reach your users.
            </p>
            <div className="lp-hero-btns">
              <button className="lp-btn-primary lp-btn-lg" onClick={() => navigate('/auth')}>
                Try for free <span className="lp-btn-arrow">↗</span>
              </button>
              <button className="lp-btn-outline lp-btn-lg" onClick={() => {
                document.getElementById('features')?.scrollIntoView({ behavior: 'smooth' });
              }}>
                More about FairGuard
              </button>
            </div>
          </div>
          <HeroDashboard />
        </div>

        {/* Stats strip below hero */}
        <div className="lp-stats-strip">
          <div className="lp-stat-item">
            <div className="lp-stat-avatars">
              <div className="lp-avatar">🟢</div>
              <div className="lp-avatar">🔵</div>
              <div className="lp-avatar">🟣</div>
            </div>
            <div>
              <div className="lp-stat-big">10,000+</div>
              <div className="lp-stat-label">decisions audited daily</div>
            </div>
          </div>
          <div className="lp-stat-item lp-stat-dark lp-stat-purple">
            <p className="lp-stat-quote">
              Bias is intercepted before it impacts users. Real-time causal analysis ensures every
              decision meets fairness thresholds.
            </p>
            <div className="lp-stat-meta">
              <span>FairGuard Engine</span>
              <span className="lp-stat-date">v2.0</span>
            </div>
          </div>
          <div className="lp-stat-item lp-stat-accent">
            <div className="lp-stat-big" style={{ color: '#050608' }}>Get 14 days free</div>
            <div className="lp-stat-label" style={{ color: '#050608', opacity: 0.7 }}>
              Just deploy our SDK or message us in the chat.
            </div>
          </div>
        </div>
      </section>

      {/* ─── FEATURES — BENTO GRID ─────────────────────────────── */}
      <section className="lp-section" id="features">
        <div className="lp-section-header">
          <span className="lp-pill-tag">Features</span>
          <h2 className="lp-section-title">
            Designed for <span className="lp-text-lime">secure</span>,<br />
            compliant, scalable<br />
            enterprise use
          </h2>
        </div>

        <div className="lp-bento-grid">
          <FeatureCard
            icon="🛡️"
            title="Real-time Bias Detection"
            desc="Every AI decision is scanned in < 50ms using 4 parallel fairness metrics: DPD, EOD, ICD, and CAS."
            color="solid-lime"
            arrow
          />
          <FeatureCard
            icon="🔬"
            title="Causal Analysis (DoWhy)"
            desc="Goes beyond correlation — uses counterfactual reasoning to identify the root cause of bias."
            color="solid-purple"
            arrow
          />
          <FeatureCard
            icon="⚡"
            title="Auto-Correction Engine"
            desc="Biased decisions are automatically corrected before reaching production, with full audit trails."
            color="solid-dark"
            arrow
          />
          <FeatureCard
            icon="📊"
            title="Compliance Reports"
            desc="One-click PDF reports for SOC 2, GDPR, and EEOC compliance audits."
            color="solid-white"
            arrow
          />
          <FeatureCard
            icon="🔒"
            title="Robust Security"
            desc="256-bit encryption, RBAC, audit logs, and vaulting. Cloud, on-premise, or hybrid deployments."
            color="solid-emerald"
            arrow
          />
          <FeatureCard
            icon="📡"
            title="Live Decision Stream"
            desc="Server-sent events provide a real-time feed of every decision flowing through the firewall."
            color="solid-indigo"
            arrow
          />
        </div>
      </section>

      {/* ─── HOW IT WORKS ───────────────────────────────────────── */}
      <section className="lp-section lp-section-dark" id="how-it-works">
        <div className="lp-section-header">
          <span className="lp-pill-tag">How it works</span>
          <h2 className="lp-section-title">
            Let's build your <span className="lp-text-lime">AI</span><br />
            fairness firewall —<br />
            <span className="lp-text-underline">together</span>
          </h2>
        </div>

        <div className="lp-steps-grid">
          <StepCard
            num="01"
            title="Integrate the SDK"
            desc="Start with one API call. Our Python/JS SDK wraps your model output and sends it through the firewall."
            color="solid-emerald"
          />
          <StepCard
            num="02"
            title="Configure Fairness Policies"
            desc="Set thresholds for demographic parity, equalized odds, and counterfactual fairness — tailored to your domain."
            color="solid-purple"
          />
          <StepCard
            num="03"
            title="Ship with Confidence"
            desc="FairGuard runs in production, catching bias in real-time. Monitor everything from the live dashboard."
            color="solid-white"
          />
        </div>
      </section>

      {/* ─── CAPABILITIES — BENTO GRID ──────────────────────────── */}
      <section className="lp-section" id="capabilities">
        <div className="lp-section-header">
          <span className="lp-pill-tag">Capabilities</span>
          <h2 className="lp-section-title">
            Everything you need<br />
            for <span className="lp-text-lime">fair AI</span>
          </h2>
        </div>

        <div className="lp-cap-grid">
          <div className="lp-cap-card lp-cap-wide lp-cap-solid-dark">
            <div className="lp-cap-icon">✳️</div>
            <div>
              <div className="lp-cap-title">Professional-grade fairness metrics</div>
              <div className="lp-cap-desc">4 parallel metrics with at least 5 years of research backing.</div>
            </div>
          </div>
          <div className="lp-cap-card lp-cap-solid-indigo">
            <div className="lp-cap-icon">📶</div>
            <div className="lp-cap-title">Real-time SSE Stream</div>
          </div>
          <div className="lp-cap-card lp-cap-solid-white">
            <div className="lp-cap-icon">🔐</div>
            <div className="lp-cap-title">SOC 2 Certified</div>
          </div>
          <div className="lp-cap-card lp-cap-solid-purple">
            <div className="lp-cap-icon">🏥</div>
            <div>
              <div className="lp-cap-title">Counterfactual Analysis</div>
              <div className="lp-cap-desc">DoWhy-powered causal inference engine.</div>
            </div>
          </div>
          <div className="lp-cap-card lp-cap-center lp-cap-solid-emerald">
            <div className="lp-cap-big-num">4</div>
            <div className="lp-cap-desc">fairness metrics</div>
          </div>
          <div className="lp-cap-card lp-cap-solid-dark">
            <div>
              <div className="lp-cap-title">Auto-correction with audit trail</div>
              <div className="lp-cap-desc">Every correction is logged and explainable.</div>
            </div>
          </div>
          <div className="lp-cap-card lp-cap-solid-lime">
            <div className="lp-cap-title">Model Drift Detection</div>
            <div className="lp-cap-desc">KS-statistic monitoring.</div>
          </div>
          <div className="lp-cap-card lp-cap-big-stat lp-cap-solid-indigo">
            <div className="lp-cap-big-num">&lt;50<span style={{ fontSize: '1.2rem' }}>ms</span></div>
            <div className="lp-cap-desc">average latency</div>
          </div>
        </div>
      </section>

      {/* ─── ENTERPRISE STATS ────────────────────────────────── */}
      <section className="lp-section lp-section-dark" id="stats">
        <div className="lp-enterprise-grid">
          <div className="lp-ent-card lp-ent-solid-emerald">
            <div className="lp-ent-num">100%</div>
            <div className="lp-ent-label">decision validation accuracy</div>
          </div>
          <div className="lp-ent-card lp-ent-solid-indigo">
            <div className="lp-ent-num">70%</div>
            <div className="lp-ent-label">faster compliance cycles</div>
          </div>
          <div className="lp-ent-card lp-ent-solid-purple">
            <div className="lp-ent-num">80%+</div>
            <div className="lp-ent-label">bias interventions automated</div>
          </div>
          <div className="lp-ent-card lp-ent-solid-lime">
            <div className="lp-ent-num lp-ent-highlight">4 <span>weeks</span></div>
            <div className="lp-ent-label">average deployment per domain</div>
          </div>
        </div>
      </section>

      {/* ─── FINAL CTA ─────────────────────────────────────────── */}
      <section className="lp-cta">
        <div className="lp-cta-inner">
          <h2 className="lp-cta-heading">
            Ready to ship <span className="lp-text-lime">fair AI</span>?
          </h2>
          <p className="lp-cta-sub">
            Deploy FairGuard in minutes. No infrastructure changes needed.
          </p>
          <div className="lp-hero-btns">
            <button className="lp-btn-primary lp-btn-lg" onClick={() => navigate('/auth')}>
              Open Dashboard <span className="lp-btn-arrow">↗</span>
            </button>
            <button className="lp-btn-outline lp-btn-lg">
              Read Documentation
            </button>
          </div>
        </div>
      </section>

      {/* ─── FOOTER ────────────────────────────────────────────── */}
      <footer className="lp-footer">
        <div className="lp-footer-inner">
          <div className="lp-footer-brand">
            FAIR<span className="lp-nav-logo-accent">GUARD</span>
            <span className="lp-footer-copy">© 2026 FairGuard. All rights reserved.</span>
          </div>
          <div className="lp-footer-links">
            <a href="#features">Features</a>
            <a href="#how-it-works">How It Works</a>
            <a href="#capabilities">Capabilities</a>
            <a href="#stats">Enterprise</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
