import 'dart:async';
import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../../services/location_service.dart';
import '../../models/location_status.dart';

class LocationTestScreen extends StatefulWidget {
  const LocationTestScreen({super.key});

  @override
  State<LocationTestScreen> createState() => _LocationTestScreenState();
}

class _LocationTestScreenState extends State<LocationTestScreen> {
  final LocationService _locationService = LocationService();
  Position? _currentPosition;
  LocationStatus? _locationStatus;
  String? _address;
  bool _isLoading = false;
  String? _errorMessage;

  // Test addresses for demonstration
  RegisteredAddress? _homeAddress;
  RegisteredAddress? _workAddress;

  @override
  void initState() {
    super.initState();
    _checkPermissions();
  }

  Future<void> _checkPermissions() async {
    final hasPermission = await _locationService.hasLocationPermission();
    if (!hasPermission) {
      setState(() {
        _errorMessage = '位置情報の権限が必要です';
      });
    }
  }

  Future<void> _requestPermission() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      print('Requesting location permission...');
      final granted = await _locationService.requestLocationPermission();
      print('Permission granted: $granted');

      setState(() {
        _isLoading = false;
        if (granted) {
          _errorMessage = null;
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('位置情報の権限が許可されました'),
              backgroundColor: Colors.green,
            ),
          );
        } else {
          _errorMessage = '位置情報の権限が拒否されました。設定アプリから手動で許可してください。';
        }
      });
    } catch (e) {
      print('Error requesting permission: $e');
      setState(() {
        _isLoading = false;
        _errorMessage = '権限リクエストエラー: $e';
      });
    }
  }

  Future<void> _getCurrentLocation({bool skipPermissionCheck = false}) async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      Position? position;

      if (skipPermissionCheck) {
        // For simulator: directly use mock data
        print('Using mock data for simulator (permission issues)');
        // Use mock data for simulator (Cupertino, CA)
        position = Position(
          latitude: 37.3317,
          longitude: -122.0307,
          timestamp: DateTime.now(),
          accuracy: 5.0,
          altitude: 0.0,
          altitudeAccuracy: 0.0,
          heading: 0.0,
          headingAccuracy: 0.0,
          speed: 0.0,
          speedAccuracy: 0.0,
        );
        print('Mock position: ${position.latitude}, ${position.longitude}');

        // Add a small delay to simulate API call
        await Future.delayed(const Duration(milliseconds: 500));
      } else {
        position = await _locationService.getCurrentLocation();
      }

      if (position != null) {
        print('Got position: ${position.latitude}, ${position.longitude}');

        // Get address
        final address = await _locationService.getAddressFromCoordinates(
          position.latitude,
          position.longitude,
        );
        print('Got address: $address');

        // Calculate status
        final status = _locationService.calculateLocationStatus(
          currentPosition: position,
          homeAddress: _homeAddress,
          workAddress: _workAddress,
        );
        print('Calculated status: ${status.statusText}');

        setState(() {
          _currentPosition = position;
          _address = address;
          _locationStatus = status;
        });
      } else {
        setState(() {
          _errorMessage = '位置情報を取得できませんでした';
        });
      }
    } catch (e) {
      print('Error getting location: $e');
      setState(() {
        _errorMessage = 'エラー: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _setTestHomeAddress() {
    if (_currentPosition != null) {
      setState(() {
        _homeAddress = RegisteredAddress(
          id: 'home_test',
          name: '自宅（テスト）',
          latitude: _currentPosition!.latitude,
          longitude: _currentPosition!.longitude,
          address: _address ?? '不明',
          radiusMeters: 200,
          registeredAt: DateTime.now(),
        );
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('現在地をテスト自宅住所として設定しました')),
      );
    }
  }

  void _setTestWorkAddress() {
    if (_currentPosition != null) {
      setState(() {
        _workAddress = RegisteredAddress(
          id: 'work_test',
          name: '職場（テスト）',
          latitude: _currentPosition!.latitude,
          longitude: _currentPosition!.longitude,
          address: _address ?? '不明',
          radiusMeters: 500,
          registeredAt: DateTime.now(),
        );
      });
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('現在地をテスト職場住所として設定しました')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('位置情報テスト'),
        backgroundColor: Colors.blue,
        foregroundColor: Colors.white,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: [
          // Permission status
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    '権限ステータス',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 12),
                  ElevatedButton(
                    onPressed: _isLoading ? null : _requestPermission,
                    child: const Text('位置情報権限をリクエスト'),
                  ),
                  const SizedBox(height: 8),
                  OutlinedButton(
                    onPressed: _isLoading
                        ? null
                        : () async {
                            final hasPermission =
                                await _locationService.hasLocationPermission();
                            if (!mounted) return;
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  hasPermission
                                      ? '位置情報権限: 許可されています'
                                      : '位置情報権限: 拒否されています',
                                ),
                                backgroundColor:
                                    hasPermission ? Colors.green : Colors.red,
                              ),
                            );
                          },
                    child: const Text('現在の権限ステータスを確認'),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Get location button
          ElevatedButton.icon(
            onPressed: _isLoading ? null : _getCurrentLocation,
            icon: _isLoading
                ? const SizedBox(
                    width: 20,
                    height: 20,
                    child: CircularProgressIndicator(strokeWidth: 2),
                  )
                : const Icon(Icons.my_location),
            label: const Text('現在地を取得'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
            ),
          ),
          const SizedBox(height: 8),

          // Simulator test button
          OutlinedButton.icon(
            onPressed: _isLoading
                ? null
                : () => _getCurrentLocation(skipPermissionCheck: true),
            icon: const Icon(Icons.bug_report),
            label: const Text('モックデータを使用（シミュレータ用）'),
            style: OutlinedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 16),
              foregroundColor: Colors.orange,
            ),
          ),
          const SizedBox(height: 8),
          const Text(
            '※ シミュレータでは位置情報が取得できないため、\nCupertino, CAのモックデータを使用します',
            style: TextStyle(fontSize: 12, color: Colors.grey),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),

          // Error message
          if (_errorMessage != null)
            Card(
              color: Colors.red.shade50,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    Icon(Icons.error_outline, color: Colors.red.shade700),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Text(
                        _errorMessage!,
                        style: TextStyle(color: Colors.red.shade900),
                      ),
                    ),
                  ],
                ),
              ),
            ),

          // Current location info
          if (_currentPosition != null) ...[
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text(
                      '現在の位置情報',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    _buildInfoRow('緯度', _currentPosition!.latitude.toString()),
                    _buildInfoRow('経度', _currentPosition!.longitude.toString()),
                    _buildInfoRow(
                      '速度',
                      '${(_currentPosition!.speed * 3.6).toStringAsFixed(1)} km/h',
                    ),
                    _buildInfoRow(
                      '精度',
                      '${_currentPosition!.accuracy.toStringAsFixed(1)} m',
                    ),
                    if (_address != null) _buildInfoRow('住所', _address!),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Location status
            if (_locationStatus != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        '位置情報ステータス',
                        style: TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Container(
                        padding: const EdgeInsets.all(16),
                        decoration: BoxDecoration(
                          color: _getStatusColor(_locationStatus!.type),
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Row(
                          children: [
                            Icon(
                              _getStatusIcon(_locationStatus!.type),
                              size: 32,
                              color: Colors.white,
                            ),
                            const SizedBox(width: 16),
                            Text(
                              _locationStatus!.statusText,
                              style: const TextStyle(
                                fontSize: 24,
                                fontWeight: FontWeight.bold,
                                color: Colors.white,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 16),

            // Test address buttons
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Text(
                      'テスト用住所設定',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 12),
                    ElevatedButton(
                      onPressed: _setTestHomeAddress,
                      child: const Text('現在地を自宅住所に設定'),
                    ),
                    const SizedBox(height: 8),
                    ElevatedButton(
                      onPressed: _setTestWorkAddress,
                      child: const Text('現在地を職場住所に設定'),
                    ),
                    if (_homeAddress != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        '自宅: ${_homeAddress!.address}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ],
                    if (_workAddress != null) ...[
                      const SizedBox(height: 4),
                      Text(
                        '職場: ${_workAddress!.address}',
                        style: const TextStyle(fontSize: 12),
                      ),
                    ],
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 60,
            child: Text(
              label,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                color: Colors.grey[600],
              ),
            ),
          ),
          Expanded(
            child: Text(value),
          ),
        ],
      ),
    );
  }

  Color _getStatusColor(LocationStatusType type) {
    switch (type) {
      case LocationStatusType.home:
        return Colors.green;
      case LocationStatusType.work:
        return Colors.blue;
      case LocationStatusType.moving:
        return Colors.orange;
      case LocationStatusType.custom:
        return Colors.purple;
      case LocationStatusType.unknown:
        return Colors.grey;
    }
  }

  IconData _getStatusIcon(LocationStatusType type) {
    switch (type) {
      case LocationStatusType.home:
        return Icons.home;
      case LocationStatusType.work:
        return Icons.work;
      case LocationStatusType.moving:
        return Icons.directions_walk;
      case LocationStatusType.custom:
        return Icons.location_on;
      case LocationStatusType.unknown:
        return Icons.help_outline;
    }
  }
}
