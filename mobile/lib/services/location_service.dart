import 'package:geolocator/geolocator.dart';
import 'package:permission_handler/permission_handler.dart';
import 'package:geocoding/geocoding.dart';
import 'dart:math' show cos, sqrt, asin;
import '../models/location_status.dart';

class LocationService {
  static const double HOME_RADIUS_METERS = 200;
  static const double WORK_RADIUS_METERS = 500;
  static const double MOVING_SPEED_THRESHOLD = 5.0; // km/h

  // Request location permissions
  Future<bool> requestLocationPermission() async {
    final status = await Permission.locationWhenInUse.request();
    return status.isGranted;
  }

  // Request always location permission (for background tracking)
  Future<bool> requestAlwaysLocationPermission() async {
    final status = await Permission.locationAlways.request();
    return status.isGranted;
  }

  // Check if location permission is granted
  Future<bool> hasLocationPermission() async {
    final status = await Permission.locationWhenInUse.status;
    return status.isGranted;
  }

  // Check if always location permission is granted
  Future<bool> hasAlwaysLocationPermission() async {
    final status = await Permission.locationAlways.status;
    return status.isGranted;
  }

  // Get current location
  Future<Position?> getCurrentLocation() async {
    try {
      final hasPermission = await hasLocationPermission();
      if (!hasPermission) {
        final granted = await requestLocationPermission();
        if (!granted) return null;
      }

      final position = await Geolocator.getCurrentPosition(
        locationSettings: const LocationSettings(
          accuracy: LocationAccuracy.high,
          distanceFilter: 10,
        ),
      );

      return position;
    } catch (e) {
      print('Error getting current location: $e');
      return null;
    }
  }

  // Calculate distance between two coordinates (Haversine formula)
  double calculateDistance(
    double lat1,
    double lon1,
    double lat2,
    double lon2,
  ) {
    const p = 0.017453292519943295; // Math.PI / 180
    final a = 0.5 -
        cos((lat2 - lat1) * p) / 2 +
        cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2;
    return 12742000 * asin(sqrt(a)); // 2 * R; R = 6371 km, returns meters
  }

  // Calculate location status based on registered addresses
  LocationStatus calculateLocationStatus({
    required Position currentPosition,
    RegisteredAddress? homeAddress,
    RegisteredAddress? workAddress,
    List<RegisteredAddress>? customAddresses,
  }) {
    final lat = currentPosition.latitude;
    final lon = currentPosition.longitude;

    // Check home
    if (homeAddress != null) {
      final distance = calculateDistance(
        lat,
        lon,
        homeAddress.latitude,
        homeAddress.longitude,
      );
      if (distance <= homeAddress.radiusMeters) {
        return LocationStatus(
          type: LocationStatusType.home,
          displayName: '自宅',
          latitude: lat,
          longitude: lon,
          timestamp: DateTime.now(),
        );
      }
    }

    // Check work
    if (workAddress != null) {
      final distance = calculateDistance(
        lat,
        lon,
        workAddress.latitude,
        workAddress.longitude,
      );
      if (distance <= workAddress.radiusMeters) {
        return LocationStatus(
          type: LocationStatusType.work,
          displayName: '職場',
          latitude: lat,
          longitude: lon,
          timestamp: DateTime.now(),
        );
      }
    }

    // Check custom addresses
    if (customAddresses != null) {
      for (final customAddress in customAddresses) {
        final distance = calculateDistance(
          lat,
          lon,
          customAddress.latitude,
          customAddress.longitude,
        );
        if (distance <= customAddress.radiusMeters) {
          return LocationStatus(
            type: LocationStatusType.custom,
            displayName: customAddress.name,
            latitude: lat,
            longitude: lon,
            timestamp: DateTime.now(),
          );
        }
      }
    }

    // Check if moving (based on speed)
    final speedKmH = (currentPosition.speed * 3.6); // m/s to km/h
    if (speedKmH > MOVING_SPEED_THRESHOLD) {
      return LocationStatus(
        type: LocationStatusType.moving,
        displayName: '移動中',
        latitude: lat,
        longitude: lon,
        timestamp: DateTime.now(),
      );
    }

    // Unknown
    return LocationStatus(
      type: LocationStatusType.unknown,
      displayName: '不明',
      latitude: lat,
      longitude: lon,
      timestamp: DateTime.now(),
    );
  }

  // Get address from coordinates
  Future<String?> getAddressFromCoordinates(
    double latitude,
    double longitude,
  ) async {
    try {
      final placemarks = await placemarkFromCoordinates(latitude, longitude);
      if (placemarks.isNotEmpty) {
        final place = placemarks.first;
        return '${place.country ?? ''}${place.administrativeArea ?? ''}${place.locality ?? ''}${place.subLocality ?? ''}${place.thoroughfare ?? ''}${place.subThoroughfare ?? ''}';
      }
      return null;
    } catch (e) {
      print('Error getting address from coordinates: $e');
      return null;
    }
  }

  // Get coordinates from address
  Future<List<Location>?> getCoordinatesFromAddress(String address) async {
    try {
      final locations = await locationFromAddress(address);
      return locations;
    } catch (e) {
      print('Error getting coordinates from address: $e');
      return null;
    }
  }

  // Start location updates stream
  Stream<Position> getLocationStream() {
    return Geolocator.getPositionStream(
      locationSettings: const LocationSettings(
        accuracy: LocationAccuracy.high,
        distanceFilter: 10,
        timeLimit: Duration(minutes: 5),
      ),
    );
  }
}
