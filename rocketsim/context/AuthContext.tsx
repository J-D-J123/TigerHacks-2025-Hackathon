// AuthContext.tsx
// Install: npm install react-native-auth0
import React, { createContext, useContext, useState, useEffect } from 'react';
import Auth0 from 'react-native-auth0';

const auth0 = new Auth0({
  domain: 'dev-h3bhzbotlkitguzp.us.auth0.com',
  clientId: 'EzzXPmewAewUEuZQdHnl8vyePdkAShze',
});

interface AuthContextType {
  user: any | null;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<any | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      // Check if user has valid credentials stored
      const credentials = await auth0.credentialsManager.getCredentials();
      if (credentials) {
        setUser(credentials.idToken);
      }
    } catch (error) {
      console.log('No valid session', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      setIsLoading(true);
      const credentials = await auth0.webAuth.authorize({
        scope: 'openid profile email',
      });
      
      await auth0.credentialsManager.saveCredentials(credentials);
      setUser(credentials.idToken);
    } catch (error) {
      console.error('Login error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      setIsLoading(true);
      await auth0.webAuth.clearSession();
      await auth0.credentialsManager.clearCredentials();
      setUser(null);
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        logout,
        isAuthenticated: !!user,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};