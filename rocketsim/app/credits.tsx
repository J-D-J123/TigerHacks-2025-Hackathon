import { View, Text, StyleSheet, ScrollView, Linking } from 'react-native';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { StatusBar } from 'expo-status-bar';

export default function Credits() {
  const colorScheme = useColorScheme();
  const isDark = colorScheme === 'dark';

  const creditsData = [
    {
      title: 'Development Team',
      items: [
        { name: 'Joey Johnson', role: 'Lead Developer' },
        { name: 'devtw', role: 'UI/UX Designer' },
        { name: 'Amit Singh', role: 'Backend Engineer' },
      ]
    },
    {
      title: 'Technologies Used',
      items: [
        'React Native',
        'Expo',
        'TypeScript',
      ]
    },
    {
      title: 'Assets & Libraries',
      items: [
        'React Native Vector Icons',
        'React Navigation',
        'React Native Reanimated',
      ]
    }
  ];

  const openLink = (url: string) => {
    Linking.openURL(url).catch(err => console.error('Failed to open URL:', err));
  };

  return (
    <ScrollView style={[styles.container, { backgroundColor: isDark ? '#000' : '#fff' }]}>
      <View style={styles.header}>
        <Text style={[styles.title, { color: isDark ? '#fff' : '#000' }]}>
          Credits
        </Text>
        <Text style={[styles.subtitle, { color: isDark ? '#ccc' : '#666' }]}>
          Meet the team behind the app
        </Text>
      </View>

      {creditsData.map((section, sectionIndex) => (
        <View key={sectionIndex} style={styles.section}>
          <Text style={[styles.sectionTitle, { color: isDark ? '#fff' : '#000' }]}>
            {section.title}
          </Text>
          <View style={[styles.sectionContent, { backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5' }]}>
            {section.items.map((item, itemIndex) => (
              <View 
                key={itemIndex} 
                style={[
                  styles.listItem,
                  itemIndex === section.items.length - 1 && styles.listItemLast
                ]}
              >
                {section.title === 'Development Team' ? (
                  <View style={styles.teamItem}>
                    <Text style={[styles.teamName, { color: isDark ? '#fff' : '#000' }]}>
                      {item.name}
                    </Text>
                    <Text style={[styles.teamRole, { color: isDark ? '#ccc' : '#666' }]}>
                      {item.role}
                    </Text>
                  </View>
                ) : (
                  <Text style={[styles.techItem, { color: isDark ? '#fff' : '#000' }]}>
                    {item}
                  </Text>
                )}
              </View>
            ))}
          </View>
        </View>
      ))}

      <View style={styles.footer}>
        <Text style={[styles.footerText, { color: isDark ? '#ccc' : '#666' }]}>
          Crafted with excellence by our dedicated team
        </Text>
        <Text 
          style={[styles.version, { color: isDark ? '#888' : '#999' }]}
          onPress={() => openLink('https://yourapp.com')}
        >
          Version 1.0.0
        </Text>
      </View>

      <StatusBar style={isDark ? 'light' : 'dark'} />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  header: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  title: {
    fontSize: 36,
    fontWeight: 'bold',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    textAlign: 'center',
    lineHeight: 22,
  },
  section: {
    marginBottom: 24,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: '600',
    marginBottom: 12,
    marginLeft: 4,
    textAlign: 'center',
  },
  sectionContent: {
    borderRadius: 12,
    padding: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  listItem: {
    paddingVertical: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(128,128,128,0.2)',
  },
  listItemLast: {
    borderBottomWidth: 0,
  },
  teamItem: {
    alignItems: 'center',
  },
  teamName: {
    fontSize: 16,
    fontWeight: '600',
    marginBottom: 4,
    textAlign: 'center',
  },
  teamRole: {
    fontSize: 14,
    fontStyle: 'italic',
    textAlign: 'center',
  },
  techItem: {
    fontSize: 16,
    fontWeight: '500',
    textAlign: 'center',
    paddingVertical: 8,
  },
  footer: {
    alignItems: 'center',
    paddingVertical: 40,
    paddingHorizontal: 20,
  },
  footerText: {
    fontSize: 16,
    marginBottom: 8,
    textAlign: 'center',
  },
  version: {
    fontSize: 14,
    textDecorationLine: 'underline',
  },
});