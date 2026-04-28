export default function Footer() {
  return (
    <footer className="footer">
      <div className="footer-container">
        <div className="footer-brand">
          <h3>FAIR<span className="logo-accent">GUARD</span></h3>
          <p>Building a fairer future for Artificial Intelligence.</p>
        </div>
        
        <div className="footer-links">
          <div className="footer-col">
            <h4>Product</h4>
            <a href="#features">Features</a>
            <a href="/dashboard">Dashboard</a>
            <a href="#how-it-works">Integration</a>
          </div>
          <div className="footer-col">
            <h4>Resources</h4>
            <a href="https://github.com/Ritinpaul/fairGaurd">Documentation</a>
            <a href="https://github.com/Ritinpaul/fairGaurd/tree/main/sdk">Python SDK</a>
            <a href="https://github.com/Ritinpaul/fairGaurd/blob/main/README.md">API Reference</a>
          </div>
        </div>
      </div>
      <div className="footer-bottom">
        <p>&copy; {new Date().getFullYear()} FairGuard Project. Open Source.</p>
      </div>
    </footer>
  );
}
