// app/index.tsx
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { View, Text, TouchableOpacity, StyleSheet, ActivityIndicator } from 'react-native';
import 'react-native-reanimated';
import { useRouter } from 'expo-router';
import { useState } from 'react';

import { useColorScheme } from '@/hooks/use-color-scheme';
import { useAuth } from '@/context/AuthContext';

export default function Index() {
  const colorScheme = useColorScheme();
  const router = useRouter();
  const isDark = colorScheme === 'dark';
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();

  const handleLogin = async () => {
    setIsLoading(true);
    try {
      await login();
      router.replace('/menu');
    } catch (error) {
      console.error('Login failed:', error);
      alert('Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGuestLogin = () => {
    // Skip authentication and go directly to menu
    router.replace('/menu');
  };

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
        <Text style={[styles.title, { color: isDark ? '#fff' : '#000' }]}>
          TigerHacks
        </Text>
        
        <Text style={[styles.subtitle, { color: isDark ? '#ccc' : '#666' }]}>
          Welcome! Please sign in to continue
        </Text>

        {isLoading ? (
          <ActivityIndicator 
            size="large" 
            color={isDark ? '#fff' : '#000'} 
            style={styles.loader}
          />
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
    marginBottom: 60,
    textAlign: 'center',
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