import 'react-native-gesture-handler';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import React from 'react';
import DriverDashboard from './src/screens/DriverDashboard';

export default function App() {
  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <DriverDashboard />
    </GestureHandlerRootView>
  );
}
