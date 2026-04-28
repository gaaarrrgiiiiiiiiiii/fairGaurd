/**
 * AuthContext — stores the authenticated user's profile across the app.
 * On login, save user info here. Components (like DashboardLayout) read from it.
 */
import { createContext, useContext, useState, type ReactNode } from 'react';

export interface UserProfile {
  name: string;
  email: string;
  organization: string;
  role: string;
}

interface AuthContextValue {
  user: UserProfile | null;
  setUser: (u: UserProfile | null) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  setUser: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(() => {
    // Restore from sessionStorage on refresh
    try {
      const saved = sessionStorage.getItem('fg_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const handleSetUser = (u: UserProfile | null) => {
    setUser(u);
    if (u) {
      sessionStorage.setItem('fg_user', JSON.stringify(u));
    } else {
      sessionStorage.removeItem('fg_user');
    }
  };

  const logout = () => {
    handleSetUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, setUser: handleSetUser, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
