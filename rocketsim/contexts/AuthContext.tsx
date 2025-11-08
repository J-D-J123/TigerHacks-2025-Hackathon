
// auth context will use Auth0 to login and manage user sessions 
// and provide user info to the rest of the application 

import React, { createContext, useContext, useState, useEffect } from 'react';
import Auth0 from 'react-native-auth0';
import * as SecureStore from 'expo-secure-store';

const auth0 = new Auth0({
  domain: 'YOUR_AUTH0_DOMAIN', // e.g., 'dev-xxxxx.us.auth0.com'
  clientId: 'YOUR_CLIENT_ID',
});

interface User {
  name: string;
  email: string;
  picture: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: () => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const accessToken = await SecureStore.getItemAsync('accessToken');
      if (accessToken) {
        const userInfo = await auth0.auth.userInfo({ token: accessToken });
        setUser(userInfo);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async () => {
    try {
      const credentials = await auth0.webAuth.authorize({
        scope: 'openid profile email',
      });

      await SecureStore.setItemAsync('accessToken', credentials.accessToken);
      
      const userInfo = await auth0.auth.userInfo({ token: credentials.accessToken });
      setUser(userInfo);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const logout = async () => {
    try {
      await auth0.webAuth.clearSession();
      await SecureStore.deleteItemAsync('accessToken');
      setUser(null);
    } catch (error) {
      console.error('Logout failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider value={{ user, isLoading, login, logout }}>
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