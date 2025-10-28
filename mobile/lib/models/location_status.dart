enum LocationStatusType {
  home,
  work,
  moving,
  custom,
  unknown,
}

class LocationStatus {
  final LocationStatusType type;
  final String displayName;
  final double? latitude;
  final double? longitude;
  final DateTime timestamp;

  LocationStatus({
    required this.type,
    required this.displayName,
    this.latitude,
    this.longitude,
    required this.timestamp,
  });

  String get statusText {
    switch (type) {
      case LocationStatusType.home:
        return '自宅';
      case LocationStatusType.work:
        return '職場';
      case LocationStatusType.moving:
        return '移動中';
      case LocationStatusType.custom:
        return displayName;
      case LocationStatusType.unknown:
        return '不明';
    }
  }

  factory LocationStatus.fromJson(Map<String, dynamic> json) {
    return LocationStatus(
      type: LocationStatusType.values.byName(json['type']),
      displayName: json['displayName'],
      latitude: json['latitude'],
      longitude: json['longitude'],
      timestamp: DateTime.parse(json['timestamp']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'type': type.name,
      'displayName': displayName,
      'latitude': latitude,
      'longitude': longitude,
      'timestamp': timestamp.toIso8601String(),
    };
  }
}

class RegisteredAddress {
  final String id;
  final String name;
  final double latitude;
  final double longitude;
  final String address;
  final double radiusMeters;
  final DateTime registeredAt;
  final DateTime? canChangeAt;

  RegisteredAddress({
    required this.id,
    required this.name,
    required this.latitude,
    required this.longitude,
    required this.address,
    required this.radiusMeters,
    required this.registeredAt,
    this.canChangeAt,
  });

  bool get canChange {
    if (canChangeAt == null) return true;
    return DateTime.now().isAfter(canChangeAt!);
  }

  int get daysUntilCanChange {
    if (canChangeAt == null) return 0;
    final diff = canChangeAt!.difference(DateTime.now());
    return diff.inDays;
  }

  factory RegisteredAddress.fromJson(Map<String, dynamic> json) {
    return RegisteredAddress(
      id: json['id'],
      name: json['name'],
      latitude: json['latitude'],
      longitude: json['longitude'],
      address: json['address'],
      radiusMeters: json['radiusMeters'],
      registeredAt: DateTime.parse(json['registeredAt']),
      canChangeAt: json['canChangeAt'] != null
          ? DateTime.parse(json['canChangeAt'])
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'latitude': latitude,
      'longitude': longitude,
      'address': address,
      'radiusMeters': radiusMeters,
      'registeredAt': registeredAt.toIso8601String(),
      'canChangeAt': canChangeAt?.toIso8601String(),
    };
  }
}
