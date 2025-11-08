// app/index.tsx
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import 'react-native-reanimated';
import { useRouter } from 'expo-router';
import { useState, useEffect } from 'react';

import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/context/AuthContext';

export default function Index() {
  const colorScheme = useColorScheme();
  const router = useRouter();
  const isDark = colorScheme === 'dark';
  const [isLoading, setIsLoading] = useState(false);
  const { login, isAuthenticated, isLoading: authLoading } = useAuth();

  console.log('🔍 Index Component Render:', {
    isAuthenticated,
    authLoading,
    isLoading,
    timestamp: new Date().toISOString()
  });

  // Auto-redirect if already logged in
  useEffect(() => {
    console.log('🎯 useEffect triggered:', {
      isAuthenticated,
      authLoading,
      willRedirect: isAuthenticated && !authLoading
    });

    if (isAuthenticated && !authLoading) {
      console.log('✅ Attempting redirect to /(tabs)/scene');
      try {
        router.replace('/(tabs)/scene');
        console.log('✅ Router.replace called successfully');
      } catch (error) {
        console.error('❌ Router.replace failed:', error);
      }
    }
  }, [isAuthenticated, authLoading, router]);

  const handleLogin = async () => {
    console.log('🔐 handleLogin called');
    setIsLoading(true);
    try {
      console.log('📞 Calling login()...');
      await login();
      console.log('✅ login() completed successfully');
      console.log('🔍 Auth state after login:', { isAuthenticated, authLoading });
      
      console.log('🚀 Attempting manual redirect to /(tabs)/scene');
      router.replace('/(tabs)/scene');
      console.log('✅ Manual redirect called');
    } catch (error) {
      console.error('❌ Login failed:', error);
      console.error('❌ Error details:', JSON.stringify(error, null, 2));
      alert('Login failed. Please try again.');
    } finally {
      console.log('🏁 handleLogin finally block');
      setIsLoading(false);
    }
  };

  const handleGuestLogin = () => {
    console.log('👤 Guest login - redirecting to /(tabs)/scene');
    try {
      router.replace('/(tabs)/scene');
      console.log('✅ Guest redirect successful');
    } catch (error) {
      console.error('❌ Guest redirect failed:', error);
    }
  };

  // Show loading while checking auth status
  if (authLoading) {
    console.log('⏳ Showing auth loading screen');
    return (
      <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
        <ActivityIndicator 
          size="large" 
          color={isDark ? '#fff' : '#000'} 
        />
        <Text style={[styles.debugText, { color: isDark ? '#fff' : '#000' }]}>
          Checking authentication...
        </Text>
      </View>
    );
  }

  console.log('📱 Rendering login screen');

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
        <Text style={[styles.title, { color: isDark ? '#fff' : '#000' }]}>
          TigerHacks
        </Text>
        
        <Text style={[styles.subtitle, { color: isDark ? '#ccc' : '#666' }]}>
          Welcome! Please sign in to continue
        </Text>

        {/* Debug Info */}
        <View style={styles.debugContainer}>
          <Text style={[styles.debugText, { color: isDark ? '#888' : '#666' }]}>
            Debug: Auth={isAuthenticated ? 'Yes' : 'No'} | Loading={authLoading ? 'Yes' : 'No'}
          </Text>
        </View>

        {isLoading ? (
          <>
            <ActivityIndicator 
              size="large" 
              color={isDark ? '#fff' : '#000'} 
              style={styles.loader}
            />
            <Text style={[styles.debugText, { color: isDark ? '#fff' : '#000' }]}>
              Logging in...
            </Text>
          </>
        ) : (
          <>
            <TouchableOpacity
              style={[styles.loginButton, { 
                backgroundColor: isDark ? '#fff' : '#000',
              }]}
              onPress={handleLogin}
            >
              <Text style={[styles.loginButtonText, { 
                color: isDark ? '#000' : '#fff' 
              }]}>
                Login with Auth0
              </Text>
            </TouchableOpacity>

            <TouchableOpacity
              style={[styles.guestButton, { 
                borderColor: isDark ? '#fff' : '#000',
              }]}
              onPress={handleGuestLogin}
            >
              <Text style={[styles.guestButtonText, { 
                color: isDark ? '#fff' : '#000' 
              }]}>
                Continue as Guest
              </Text>
            </TouchableOpacity>
          </>
        )}
      </View>
      <StatusBar style={colorScheme === 'dark' ? 'light' : 'dark'} />
    </ThemeProvider>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20,
  },
  title: {
    fontSize: 56,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  subtitle: {
    fontSize: 18,
    marginBottom: 40,
    textAlign: 'center',
  },
  debugContainer: {
    marginBottom: 20,
    padding: 10,
    borderRadius: 5,
  },
  debugText: {
    fontSize: 12,
    textAlign: 'center',
    marginTop: 10,
  },
  loginButton: {
    width: 280,
    paddingVertical: 18,
    paddingHorizontal: 30,
    marginVertical: 10,
    borderRadius: 12,
    alignItems: 'center',
    elevation: 3,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
  },
  loginButtonText: {
    fontSize: 22,
    fontWeight: '700',
  },
  guestButton: {
    width: 280,
    paddingVertical: 18,
    paddingHorizontal: 30,
    marginVertical: 10,
    borderWidth: 2,
    borderRadius: 12,
    alignItems: 'center',
  },
  guestButtonText: {
    fontSize: 22,
    fontWeight: '600',
  },
  loader: {
    marginTop: 40,
  },
});