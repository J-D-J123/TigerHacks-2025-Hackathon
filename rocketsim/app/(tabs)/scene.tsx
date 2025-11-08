// app/scene.tsx
import { DarkTheme, DefaultTheme, ThemeProvider } from '@react-navigation/native';
import { StatusBar } from 'expo-status-bar';
import { View, Text, StyleSheet, TouchableOpacity } from 'react-native';
import 'react-native-reanimated';
import { useRouter } from 'expo-router';
import { useColorScheme } from '@/hooks/use-color-scheme';

export default function Scene() {
  const colorScheme = useColorScheme();
  const router = useRouter();
  const isDark = colorScheme === 'dark';

  return (
    <ThemeProvider value={colorScheme === 'dark' ? DarkTheme : DefaultTheme}>
      <View style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
        {/* Scene/Game View */}
        <View style={[styles.sceneView, { 
          borderColor: isDark ? '#fff' : '#000' 
        }]}>
          <Text style={[styles.sceneText, { color: isDark ? '#fff' : '#000' }]}>
            🚀 Scene Window
          </Text>
          <Text style={[styles.subtitle, { color: isDark ? '#ccc' : '#666' }]}>
            Your game/simulation renders here
          </Text>
        </View>

        {/* Controls */}
        <View style={styles.controls}>
          <TouchableOpacity
            style={[styles.button, { 
              backgroundColor: isDark ? '#fff' : '#000' 
            }]}
            onPress={() => router.push('/menu')}
          >
            <Text style={[styles.buttonText, { 
              color: isDark ? '#000' : '#fff' 
            }]}>
              Menu
            </Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[styles.button, { 
              backgroundColor: isDark ? '#fff' : '#000' 
            }]}
            onPress={() => router.push('/(tabs)')}
          >
            <Text style={[styles.buttonText, { 
              color: isDark ? '#000' : '#fff' 
            }]}>
              Play
            </Text>
          </TouchableOpacity>
        </View>
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
  sceneView: {
    width: '90%',
    height: '70%',
    borderWidth: 3,
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 30,
  },
  sceneText: {
    fontSize: 48,
    fontWeight: 'bold',
    marginBottom: 10,
  },
  subtitle: {
    fontSize: 18,
    textAlign: 'center',
  },
  controls: {
    flexDirection: 'row',
    gap: 20,
  },
  button: {
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 8,
    minWidth: 120,
    alignItems: 'center',
  },
  buttonText: {
    fontSize: 20,
    fontWeight: '600',
  },
});