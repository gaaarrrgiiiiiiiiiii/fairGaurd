import React, { Component, ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

/**
 * ErrorBoundary — catches render-time errors in any child component tree
 * and displays a graceful fallback instead of a blank white screen.
 */
class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[FairGuard ErrorBoundary]', error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;

      return (
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: '100vh',
            background: 'var(--bg-main, #050608)',
            color: 'white',
            fontFamily: 'var(--font-sans, Inter, sans-serif)',
            padding: '2rem',
            textAlign: 'center',
          }}
        >
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
          <h1
            style={{
              fontFamily: 'var(--font-display, Syne, sans-serif)',
              fontSize: '1.8rem',
              marginBottom: '0.5rem',
            }}
          >
            Dashboard Error
          </h1>
          <p style={{ color: '#9ca3af', maxWidth: '480px', marginBottom: '1.5rem' }}>
            {this.state.error?.message ?? 'An unexpected error occurred.'}
          </p>
          <button
            onClick={this.handleReset}
            style={{
              background: '#b8f23a',
              color: 'black',
              border: 'none',
              padding: '0.75rem 1.5rem',
              borderRadius: '8px',
              fontWeight: 700,
              cursor: 'pointer',
            }}
          >
            Reload Dashboard
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
