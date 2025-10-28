class AppConfig {
  // API configuration
  static const String apiBaseUrl = 'http://localhost:8000/api/v1';

  // App metadata
  static const String appName = 'BUBBLE';
  static const String appVersion = '1.0.0';

  // Location settings (must match backend config)
  static const int homeRadiusMeters = 200;
  static const int workRadiusMeters = 500;
  static const int locationChangeLockDays = 90;

  // Near-miss detection settings
  static const int nearMissRadiusMeters = 50;
  static const int nearMissTimeDiffMinutes = 30;
  static const int locationHistoryRetentionDays = 7;
}
