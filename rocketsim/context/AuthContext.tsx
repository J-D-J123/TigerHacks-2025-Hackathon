// context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import Auth0 from 'react-native-auth0';
import { Platform } from 'react-native';

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

  console.log('🔐 AuthProvider state:', {
    user: user ? 'exists' : 'null',
    isLoading,
    isAuthenticated: !!user,
    platform: Platform.OS,
    timestamp: new Date().toISOString()
  });

  useEffect(() => {
    console.log('🔄 AuthProvider useEffect - checking auth on platform:', Platform.OS);
    
    // For web development, just set loading to false without auto-login
    if (Platform.OS === 'web') {
      console.log('🌐 Running on web - setting isLoading to false (no auto-login)');
      setIsLoading(false);
      setUser(null); // Explicitly set user to null
      return;
    }
    
    checkAuth().catch(err => {
      console.error('❌ checkAuth failed in useEffect:', err);
      setIsLoading(false);
    });
  }, []);

  const checkAuth = async () => {
    console.log('🔍 checkAuth called - START');
    setIsLoading(true);
    console.log('⏳ isLoading explicitly set to true');
    
    try {
      // Check if user has valid credentials stored
      console.log('📞 About to call credentialsManager.getCredentials()');
      const credentials = await auth0.credentialsManager.getCredentials();
      console.log('📞 credentialsManager.getCredentials() returned');
      
      if (credentials) {
        console.log('✅ Credentials found:', {
          hasIdToken: !!credentials.idToken,
          hasAccessToken: !!credentials.accessToken
        });
        setUser(credentials.idToken);
        console.log('✅ User state set to credentials.idToken');
      } else {
        console.log('⚠️ No credentials found (credentials is null/undefined)');
        setUser(null);
      }
    } catch (error) {
      console.log('❌ checkAuth caught error:', error);
      if (error instanceof Error) {
        console.log('❌ Error message:', error.message);
        console.log('❌ Error stack:', error.stack);
      }
      setUser(null);
    } finally {
      console.log('🏁 checkAuth FINALLY block - setting isLoading to false');
      setIsLoading(false);
      console.log('✅ isLoading set to false');
    }
    
    console.log('🔍 checkAuth called - END');
  };

  const login = async () => {
    console.log('🔐 login() called on platform:', Platform.OS);
    
    // For web development, simulate login
    if (Platform.OS === 'web') {
      console.log('🌐 Web platform detected - simulating login');
      setIsLoading(true);
      
      // Simulate async auth
      await new Promise(resolve => setTimeout(resolve, 500));
      
      // Set a dummy user for web testing
      setUser({ platform: 'web', timestamp: Date.now() });
      console.log('✅ Web user set (simulated)');
      setIsLoading(false);
      return;
    }
    
    try {
      setIsLoading(true);
      console.log('⏳ isLoading set to true');
      
      console.log('📞 Calling auth0.webAuth.authorize()');
      const credentials = await auth0.webAuth.authorize({
        scope: 'openid profile email',
      });
      
      console.log('✅ Authorization successful:', {
        hasIdToken: !!credentials.idToken,
        hasAccessToken: !!credentials.accessToken
      });
      
      console.log('💾 Saving credentials...');
      await auth0.credentialsManager.saveCredentials(credentials);
      console.log('✅ Credentials saved');
      
      console.log('👤 Setting user state...');
      setUser(credentials.idToken);
      console.log('✅ User state set');
      
      // Give React time to update state
      await new Promise(resolve => setTimeout(resolve, 100));
      console.log('✅ State update delay complete');
      
    } catch (error) {
      console.error('❌ Login error:', error);
      console.error('❌ Error type:', typeof error);
      console.error('❌ Error details:', JSON.stringify(error, null, 2));
      throw error;
    } finally {
      console.log('🏁 login() finally block, setting isLoading to false');
      setIsLoading(false);
    }
  };

  const logout = async () => {
    console.log('🚪 logout() called');
    
    if (Platform.OS === 'web') {
      console.log('🌐 Web platform - clearing simulated user');
      setUser(null);
      return;
    }
    
    try {
      setIsLoading(true);
      console.log('📞 Calling auth0.webAuth.clearSession()');
      await auth0.webAuth.clearSession();
      console.log('✅ Session cleared');
      
      console.log('🗑️ Clearing credentials...');
      await auth0.credentialsManager.clearCredentials();
      console.log('✅ Credentials cleared');
      
      setUser(null);
      console.log('✅ User state set to null');
    } catch (error) {
      console.error('❌ Logout error:', error);
    } finally {
      console.log('🏁 logout() complete');
      setIsLoading(false);
    }
  };

  const contextValue = {
    user,
    isLoading,
    login,
    logout,
    isAuthenticated: !!user,
  };

  console.log('🎁 AuthContext providing value:', {
    hasUser: !!user,
    isLoading,
    isAuthenticated: !!user,
    platform: Platform.OS
  });

  return (
    <AuthContext.Provider value={contextValue}>
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