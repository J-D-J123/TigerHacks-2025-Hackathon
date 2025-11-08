import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import 'react-native-reanimated';
import { useRouter } from 'expo-router';

import { useColorScheme } from '@/hooks/use-color-scheme';

export default function Index() {
  const colorScheme = useColorScheme();
  const router = useRouter();
  const isDark = colorScheme === 'dark';

  const menuItems = [
    { title: 'Play', onPress: () => router.push('/(tabs)') },
    { title: 'Settings', onPress: () => router.push('/settings') },
    { title: 'Credits', onPress: () => router.push('/credits') },
    // { title: 'Exit', onPress: () => console.log('Exit app') },
  ];

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
        <Text style={[styles.title, { color: isDark ? '#fff' : '#000' }]}>
          Main Menu
        </Text>
        {menuItems.map((item, index) => (
          <TouchableOpacity
            key={index}
            style={[styles.button, { borderColor: isDark ? '#fff' : '#000' }]}
            onPress={item.onPress}
          >
            <Text style={[styles.buttonText, { color: isDark ? '#fff' : '#000' }]}>
              {item.title}
            </Text>
          </TouchableOpacity>
        ))}
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
    fontSize: 48,
    fontWeight: 'bold',
    marginBottom: 60,
  },
  button: {
    width: 200,
    paddingVertical: 15,
    paddingHorizontal: 30,
    marginVertical: 10,
    borderWidth: 2,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 24,
    fontWeight: '600',
  },
});