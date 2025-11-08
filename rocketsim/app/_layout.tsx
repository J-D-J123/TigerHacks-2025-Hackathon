// app/_layout.tsx
import { Stack } from 'expo-router';
import { Auth0Provider } from '@auth0/auth0-react';
import { AuthProvider } from '@/context/AuthContext';

export default function RootLayout() {
  return (
    <Auth0Provider
      domain="dev-h3bhzbotlkitguzp.us.auth0.com"
      clientId="EzzXPmewAewUEuZQdHnl8vyePdkAShze"
      authorizationParams={{
        redirect_uri: typeof window !== 'undefined' ? window.location.origin : 'http://localhost:8081'
      }}
    >
      <AuthProvider>
        <Stack screenOptions={{ headerShown: false }}>
          <Stack.Screen name="index" />
          <Stack.Screen name="menu" />
          <Stack.Screen name="(tabs)" />
          <Stack.Screen name="settings" />
          <Stack.Screen name="credits" />
        </Stack>
      </AuthProvider>
    </Auth0Provider>
  );
}