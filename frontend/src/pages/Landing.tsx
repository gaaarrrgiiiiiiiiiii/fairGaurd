import { Link } from 'react-router-dom';
import Navbar from '../components/common/Navbar';
import Footer from '../components/common/Footer';
import Button from '../components/common/Button';
import FeatureCard from '../components/common/FeatureCard';
import './Landing.css';

export default function Landing() {
  return (
    <div className="landing-page">
      <Navbar />

      <main>
        {/* Hero Section */}
        <section className="hero">
          <div className="hero-content">
            <h1 className="hero-title">
              The AI Fairness <span className="logo-accent">Firewall</span>
            </h1>
            <p className="hero-subtitle">
              Intercept bias in real-time. FairGuard is the enterprise-grade platform for 
              detecting, auditing, and mitigating AI bias before it impacts your users.
            </p>
            <div className="hero-actions">
              <Link to="/auth">
                <Button variant="primary" size="large">Deploy FairGuard</Button>
              </Link>
              <a href="https://github.com/Ritinpaul/fairGaurd" target="_blank" rel="noreferrer">
                <Button variant="secondary" size="large">View GitHub</Button>
              </a>
            </div>
            
            <div className="trust-badges">
              <span>Powered by FastAPI</span>
              <span className="dot">•</span>
              <span>React</span>
              <span className="dot">•</span>
              <span>Server-Sent Events</span>
            </div>
          </div>
          
          <div className="hero-visual">
            {/* A simplified visual representation of the dashboard */}
            <div className="glass-panel mockup-panel">
              <div className="mockup-header">
                <div className="mockup-dots">
                  <span></span><span></span><span></span>
                </div>
                <div className="mockup-status">Live Stream Active</div>
              </div>
              <div className="mockup-body">
                <div className="mockup-bar" style={{ width: '80%' }}></div>
                <div className="mockup-bar" style={{ width: '60%' }}></div>
                <div className="mockup-bar accent" style={{ width: '95%' }}></div>
                <div className="mockup-bar" style={{ width: '40%' }}></div>
              </div>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="features" id="features">
          <div className="section-header">
            <h2>Enterprise-Grade Fairness</h2>
            <p>Built for production ML pipelines requiring low-latency bias intervention.</p>
          </div>
          
          <div className="feature-grid">
            <FeatureCard 
              icon="⚡"
              title="Real-Time Detection"
              description="Sub-10ms latency for streaming bias detection using optimized Rust/C++ backends under the hood."
            />
            <FeatureCard 
              icon="🧠"
              title="Causal Mitigation"
              description="Go beyond correlation. FairGuard uses causal inference to surgically remove bias without destroying model accuracy."
            />
            <FeatureCard 
              icon="🔒"
              title="Immutable Audit Logs"
              description="Every decision and intervention is cryptographically hashed for compliance and regulator auditing."
            />
          </div>
        </section>

        {/* Pipeline / How It Works */}
        <section className="pipeline" id="how-it-works">
          <div className="section-header">
            <h2>How It Works</h2>
            <p>Drop-in integration for any prediction endpoint.</p>
          </div>
          
          <div className="pipeline-steps">
            <div className="step">
              <div className="step-number">1</div>
              <h3>Connect API</h3>
              <p>Route your model predictions through FairGuard's proxy endpoint.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">2</div>
              <h3>Stream Decisions</h3>
              <p>Data flows via SSE to the fairness engine for real-time analysis.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">3</div>
              <h3>Intercept Bias</h3>
              <p>Causal algorithms correct unfair predictions on the fly.</p>
            </div>
            <div className="step-arrow">→</div>
            <div className="step">
              <div className="step-number">4</div>
              <h3>Audit & Report</h3>
              <p>Generate compliance reports for internal reviews or regulators.</p>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
