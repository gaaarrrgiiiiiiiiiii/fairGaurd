import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import '../components/LandingPage.css';
import './Auth.css';

const ROLES = [
  { value: 'admin',     label: 'Admin',        icon: '🛡️', desc: 'Full system access' },
  { value: 'developer', label: 'Developer',     icon: '⚡', desc: 'API & SDK access' },
  { value: 'analyst',   label: 'Data Analyst',  icon: '📊', desc: 'Reports & insights' },
  { value: 'manager',   label: 'Manager',       icon: '👔', desc: 'Oversight & review' },
];

export default function Auth() {
  const [isLogin, setIsLogin] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [nameVal, setNameVal] = useState('');
  const [orgVal, setOrgVal] = useState('');
  const [roleVal, setRoleVal] = useState('');
  const [emailVal, setEmailVal] = useState('');
  const { setUser } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const name = nameVal.trim() || emailVal.split('@')[0] || 'User';
    setUser({
      name,
      email: emailVal,
      organization: orgVal.trim() || 'Enterprise',
      role: roleVal || 'admin',
    });
    navigate('/dashboard');
  };

  return (
    <div className="auth-page lp-root">
      {/* ─── NAVBAR (Dynamic based on login/signup state) ────────────────────── */}
      <nav className="lp-nav">
        <div className="lp-nav-inner" style={{ justifyContent: 'space-between' }}>
          <div className="lp-nav-logo" onClick={() => navigate('/')} style={{ cursor: 'pointer' }}>
            <div className="lp-nav-logo-icon">
              <svg viewBox="0 0 64 64" xmlns="http://www.w3.org/2000/svg" width="20" height="20" aria-label="FairGuard logo mark">
                <circle cx="32" cy="32" r="30" fill="rgba(204,255,0,0.07)" />
                <g stroke="#CCFF00" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" fill="none">
                  <polygon points="32,10 52,20 52,42 32,56 12,42 12,20" opacity="0.9" />
                  <line x1="32" y1="10" x2="32" y2="56" opacity="0.5" />
                  <line x1="12" y1="31" x2="52" y2="31" opacity="0.5" />
                  <rect x="26" y="25" width="12" height="12" rx="2" fill="#CCFF00" opacity="0.85" />
                </g>
              </svg>
            </div>
            FAIR<span className="lp-nav-logo-accent">GUARD</span>
          </div>
          
          <div className="lp-nav-actions">
            <button className="lp-btn-ghost" onClick={() => navigate('/')}>Home</button>
            {!isLogin ? (
              <button className="lp-btn-primary" onClick={() => setIsLogin(true)}>
                Log in <span className="lp-btn-arrow">↗</span>
              </button>
            ) : (
              <button className="lp-btn-primary" onClick={() => setIsLogin(false)}>
                Sign up <span className="lp-btn-arrow">↗</span>
              </button>
            )}
          </div>
        </div>
      </nav>
      
      <div className="auth-container">
        <div className="auth-card glass-panel" style={{ background: 'rgba(20, 21, 26, 0.75)', border: '1px solid rgba(255, 255, 255, 0.08)', borderRadius: '20px', padding: '3rem 2.5rem', boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.5)' }}>
          <div className="auth-header" style={{ marginBottom: '1.5rem' }}>
            <h2 style={{ color: '#fff', fontSize: '2rem', fontWeight: '700', marginBottom: '0.5rem' }}>{isLogin ? 'Welcome Back' : 'Create an Account'}</h2>
            <p style={{ color: '#8b949e', fontSize: '1.1rem' }}>{isLogin ? 'Sign in to access your dashboard' : 'Start mitigating AI bias today'}</p>
          </div>
          
          <form className="auth-form" onSubmit={handleSubmit}>
            {!isLogin && (
              <>
                <div className="form-group">
                  <label htmlFor="name" style={{ color: '#8b949e', fontWeight: '500' }}>Full Name</label>
                  <input type="text" id="name" placeholder="Jane Smith" required value={nameVal} onChange={e => setNameVal(e.target.value)} style={{ backgroundColor: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', padding: '1rem', borderRadius: '8px', fontSize: '1rem' }} />
                </div>
                <div className="form-group">
                  <label htmlFor="org" style={{ color: '#8b949e', fontWeight: '500' }}>Organization</label>
                  <input type="text" id="org" placeholder="Enterprise Inc." required value={orgVal} onChange={e => setOrgVal(e.target.value)} style={{ backgroundColor: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', padding: '1rem', borderRadius: '8px', fontSize: '1rem' }} />
                </div>
                <div className="form-group">
                  <label style={{ color: '#8b949e', fontWeight: '500' }}>Role</label>
                  <div className="role-picker">
                    {ROLES.map(r => (
                      <button
                        key={r.value}
                        type="button"
                        className={`role-card ${roleVal === r.value ? 'selected' : ''}`}
                        onClick={() => setRoleVal(r.value)}
                      >
                        <span className="role-card-icon">{r.icon}</span>
                        <span className="role-card-label">{r.label}</span>
                        <span className="role-card-desc">{r.desc}</span>
                      </button>
                    ))}
                  </div>
                  {/* Hidden input to satisfy form required validation */}
                  <input type="text" required value={roleVal} onChange={() => {}} style={{ opacity: 0, height: 0, position: 'absolute', pointerEvents: 'none' }} />
                </div>
              </>
            )}
            
            <div className="form-group">
              <label htmlFor="email" style={{ color: '#8b949e', fontWeight: '500' }}>Work Email</label>
              <input type="email" id="email" placeholder="jane@company.com" required value={emailVal} onChange={e => setEmailVal(e.target.value)} style={{ backgroundColor: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', padding: '1rem', borderRadius: '8px', fontSize: '1rem' }} />
            </div>
            
            <div className="form-group">
              <label htmlFor="password" style={{ color: '#8b949e', fontWeight: '500' }}>Password</label>
              <div className="password-input-wrapper" style={{ position: 'relative' }}>
                <input 
                  type={showPassword ? "text" : "password"} 
                  id="password" 
                  placeholder="••••••••" 
                  required 
                  style={{ width: '100%', paddingRight: '40px', backgroundColor: 'rgba(255,255,255,0.03)', borderColor: 'rgba(255,255,255,0.1)', color: '#fff', padding: '1rem', borderRadius: '8px', fontSize: '1rem' }}
                />
                <button 
                  type="button" 
                  onClick={() => setShowPassword(!showPassword)}
                  style={{ 
                    position: 'absolute', 
                    right: '10px', 
                    top: '50%', 
                    transform: 'translateY(-50%)', 
                    background: 'none', 
                    border: 'none', 
                    cursor: 'pointer',
                    color: '#8b949e',
                    padding: '8px',
                    display: 'flex',
                    alignItems: 'center'
                  }}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path><line x1="1" y1="1" x2="23" y2="23"></line></svg>
                  ) : (
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>
                  )}
                </button>
              </div>
            </div>
            
            <button className="lp-btn-primary lp-btn-lg auth-submit" type="submit" style={{ width: '100%', marginTop: '1.5rem', justifyContent: 'center', padding: '1rem', fontSize: '1.1rem' }}>
              {isLogin ? 'Sign In' : 'Sign Up'}
            </button>
          </form>
          
          <div className="auth-footer" style={{ marginTop: '2rem', color: '#8b949e', fontSize: '1rem' }}>
            <p>
              {isLogin ? "Don't have an account? " : "Already have an account? "}
              <button 
                className="text-btn" 
                onClick={() => setIsLogin(!isLogin)}
                style={{ color: '#CCFF00', fontWeight: 'bold', fontSize: '1rem' }}
              >
                {isLogin ? 'Sign up' : 'Sign in'}
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
