import React, { useEffect, useState, useMemo, useRef } from 'react';
import { StyleSheet, View, Text, TouchableOpacity, FlatList } from 'react-native';
import MapView, { Marker, PROVIDER_DEFAULT } from 'react-native-maps';
import * as Location from 'expo-location';
import Animated, { useSharedValue, withTiming, useAnimatedProps, Easing } from 'react-native-reanimated';
import BottomSheet, { BottomSheetView } from '@gorhom/bottom-sheet';

// Wrap the MapView Marker to allow Reanimated to control its props smoothly
const AnimatedMarker = Animated.createAnimatedComponent(Marker);

// Standerton, South Africa Default Coordinates
const DEFAULT_LAT = -26.9602;
const DEFAULT_LNG = 29.2415;

const dummyOrder = {
  id: "ORD-9482",
  customerName: "Thabo M.",
  phone: "071 234 5678",
  address: "123 Nelson Mandela Dr, Standerton",
  items: [
    { id: '1', name: "Albany Brown Bread", qty: 2, price: 18.50 },
    { id: '2', name: "Coca-Cola 2L", qty: 1, price: 24.00 },
    { id: '3', name: "Amathole Maize Meal 10kg", qty: 1, price: 85.00 }
  ],
  total: 146.00,
};

export default function DriverDashboard() {
  const mapRef = useRef(null);
  const bottomSheetRef = useRef(null);
  
  // Reanimated shared values for buttery smooth coordinate interpolation
  const markerLat = useSharedValue(DEFAULT_LAT);
  const markerLng = useSharedValue(DEFAULT_LNG);
  const [hasLocation, setHasLocation] = useState(false);

  // Bottom sheet snap points: 15% (Collapsed) to 50% (Expanded)
  const snapPoints = useMemo(() => ['15%', '50%'], []);

  useEffect(() => {
    let locationSubscription;

    (async () => {
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status !== 'granted') return;

      const initialLocation = await Location.getCurrentPositionAsync({});
      markerLat.value = initialLocation.coords.latitude;
      markerLng.value = initialLocation.coords.longitude;
      setHasLocation(true);

      mapRef.current?.animateToRegion({
        latitude: initialLocation.coords.latitude,
        longitude: initialLocation.coords.longitude,
        latitudeDelta: 0.015,
        longitudeDelta: 0.015,
      });

      locationSubscription = await Location.watchPositionAsync(
        { accuracy: Location.Accuracy.High, timeInterval: 3000, distanceInterval: 2 },
        (loc) => {
          markerLat.value = withTiming(loc.coords.latitude, { duration: 1000, easing: Easing.inOut(Easing.ease) });
          markerLng.value = withTiming(loc.coords.longitude, { duration: 1000, easing: Easing.inOut(Easing.ease) });
        }
      );
    })();

    return () => locationSubscription?.remove();
  }, []);

  const animatedMarkerProps = useAnimatedProps(() => {
    return {
      coordinate: { latitude: markerLat.value, longitude: markerLng.value },
    };
  });

  const handleUpdateStatus = () => console.log("Updating order status to 'On The Way'...");
  const handleCallCustomer = () => console.log(`Dialing ${dummyOrder.phone}...`);

  return (
    <View style={styles.container}>
      <MapView
        ref={mapRef}
        style={styles.map}
        provider={PROVIDER_DEFAULT}
        customMapStyle={cartoDbDarkStyle}
        showsUserLocation={false}
        showsCompass={false}
        showsMyLocationButton={false}
      >
        {hasLocation && (
          <AnimatedMarker animatedProps={animatedMarkerProps}>
            <View style={styles.markerContainer}>
              <View style={styles.markerCore} />
              <View style={styles.markerPulse} />
            </View>
          </AnimatedMarker>
        )}
      </MapView>

      <BottomSheet
        ref={bottomSheetRef}
        index={0}
        snapPoints={snapPoints}
        backgroundStyle={styles.sheetBackground}
        handleIndicatorStyle={styles.sheetHandle}
      >
        <BottomSheetView style={styles.sheetContent}>
          <View style={styles.headerRow}>
            <View>
              <Text style={styles.activeDeliveryText}>1 Active Delivery</Text>
              <Text style={styles.orderIdText}>{dummyOrder.id}</Text>
            </View>
            <TouchableOpacity style={styles.primaryButton} onPress={handleUpdateStatus}>
              <Text style={styles.primaryButtonText}>Start Delivery</Text>
            </TouchableOpacity>
          </View>

          <View style={styles.detailsContainer}>
            <View style={styles.customerRow}>
              <View>
                <Text style={styles.customerName}>{dummyOrder.customerName}</Text>
                <Text style={styles.addressText}>{dummyOrder.address}</Text>
              </View>
              <TouchableOpacity style={styles.callButton} onPress={handleCallCustomer}>
                <Text style={styles.callButtonText}>Call</Text>
              </TouchableOpacity>
            </View>

            <View style={styles.divider} />

            <FlatList
              data={dummyOrder.items}
              keyExtractor={(item) => item.id}
              renderItem={({ item }) => (
                <View style={styles.itemRow}>
                  <Text style={styles.itemText}>{item.qty}x {item.name}</Text>
                  <Text style={styles.itemPrice}>R {item.price.toFixed(2)}</Text>
                </View>
              )}
            />

            <View style={styles.totalRow}>
              <Text style={styles.totalLabel}>Total to Collect</Text>
              <Text style={styles.totalValue}>R {dummyOrder.total.toFixed(2)}</Text>
            </View>
          </View>
        </BottomSheetView>
      </BottomSheet>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#111' },
  map: { flex: 1 },
  markerContainer: { alignItems: 'center', justifyContent: 'center' },
  markerCore: { width: 16, height: 16, borderRadius: 8, backgroundColor: '#FF9800', zIndex: 2 },
  markerPulse: { position: 'absolute', width: 32, height: 32, borderRadius: 16, backgroundColor: 'rgba(255, 152, 0, 0.3)', zIndex: 1 },
  sheetBackground: { backgroundColor: '#1a1a1a', borderTopLeftRadius: 24, borderTopRightRadius: 24, borderWidth: 1, borderColor: 'rgba(255,255,255,0.1)' },
  sheetHandle: { backgroundColor: 'rgba(255,255,255,0.3)', width: 40 },
  sheetContent: { flex: 1, paddingHorizontal: 20, paddingTop: 10 },
  headerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  activeDeliveryText: { color: '#FF9800', fontSize: 12, fontWeight: '700', textTransform: 'uppercase', marginBottom: 4 },
  orderIdText: { color: '#FFF', fontSize: 18, fontWeight: '600' },
  primaryButton: { backgroundColor: '#FF9800', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 12 },
  primaryButtonText: { color: '#111', fontWeight: '700', fontSize: 14 },
  detailsContainer: { flex: 1 },
  customerRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', marginBottom: 20 },
  customerName: { color: '#FFF', fontSize: 16, fontWeight: '600', marginBottom: 4 },
  addressText: { color: 'rgba(255,255,255,0.6)', fontSize: 13, maxWidth: 220 },
  callButton: { backgroundColor: 'rgba(255,255,255,0.1)', paddingVertical: 8, paddingHorizontal: 16, borderRadius: 8 },
  callButtonText: { color: '#FFF', fontWeight: '600', fontSize: 13 },
  divider: { height: 1, backgroundColor: 'rgba(255,255,255,0.1)', marginBottom: 20 },
  itemRow: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 12 },
  itemText: { color: 'rgba(255,255,255,0.8)', fontSize: 14 },
  itemPrice: { color: '#FFF', fontSize: 14, fontWeight: '500' },
  totalRow: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 20, paddingTop: 20, borderTopWidth: 1, borderTopColor: 'rgba(255,255,255,0.1)' },
  totalLabel: { color: 'rgba(255,255,255,0.6)', fontSize: 16 },
  totalValue: { color: '#FF9800', fontSize: 20, fontWeight: '700' },
});

const cartoDbDarkStyle = [
  { elementType: "geometry", stylers: [{ color: "#242f3e" }] },
  { elementType: "labels.text.fill", stylers: [{ color: "#746855" }] },
  { elementType: "labels.text.stroke", stylers: [{ color: "#242f3e" }] },
  { featureType: "administrative.locality", elementType: "labels.text.fill", stylers: [{ color: "#d59563" }] },
  { featureType: "poi", elementType: "labels.text.fill", stylers: [{ color: "#d59563" }] },
  { featureType: "poi.park", elementType: "geometry", stylers: [{ color: "#263c3f" }] },
  { featureType: "poi.park", elementType: "labels.text.fill", stylers: [{ color: "#6b9a76" }] },
  { featureType: "road", elementType: "geometry", stylers: [{ color: "#38414e" }] },
  { featureType: "road", elementType: "geometry.stroke", stylers: [{ color: "#212a37" }] },
  { featureType: "road", elementType: "labels.text.fill", stylers: [{ color: "#9ca5b3" }] },
  { featureType: "road.highway", elementType: "geometry", stylers: [{ color: "#746855" }] },
  { featureType: "road.highway", elementType: "geometry.stroke", stylers: [{ color: "#1f2835" }] },
  { featureType: "road.highway", elementType: "labels.text.fill", stylers: [{ color: "#f3d19c" }] },
  { featureType: "water", elementType: "geometry", stylers: [{ color: "#17263c" }] },
  { featureType: "water", elementType: "labels.text.fill", stylers: [{ color: "#515c6d" }] },
  { featureType: "water", elementType: "labels.text.stroke", stylers: [{ color: "#17263c" }] }
];
