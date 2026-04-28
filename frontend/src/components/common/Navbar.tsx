import { Link } from 'react-router-dom';
import Button from './Button';

export default function Navbar() {
  return (
    <nav className="navbar">
      <div className="navbar-container">
        <Link to="/" className="navbar-logo">
          FAIR<span className="logo-accent">GUARD</span>
        </Link>
        
        <div className="navbar-links">
          <a href="#features" className="nav-link">Features</a>
          <a href="#how-it-works" className="nav-link">How it Works</a>
          <a href="https://github.com/Ritinpaul/fairGaurd" target="_blank" rel="noreferrer" className="nav-link">Docs</a>
        </div>
        
        <div className="navbar-actions">
          <Link to="/auth">
            <Button variant="primary" size="small">Get Started</Button>
          </Link>
        </div>
      </div>
    </nav>
  );
}
