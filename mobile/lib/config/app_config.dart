import 'package:flutter/foundation.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

enum AppFlavor { development, staging, production }

/// Centralized app configuration driven by build flavor and dart-defines.
/// All values are resolved at startup; no runtime mutation.
class AppConfig {
  static const String _defaultDevUrl = 'http://10.0.2.2:8100/api/v1';
  static const String _defaultStagingUrl = 'https://ecofinwiz-api.onrender.com/api/v1';
  static const String _defaultProductionUrl = 'https://ecofinwiz-api.onrender.com/api/v1';

  /// Current build flavor (injected via `--flavor` → `FLUTTER_APP_FLAVOR` dart-define).
  final AppFlavor flavor;

  /// API base URL (can be overridden via `--dart-define=API_BASE_URL=...`).
  final String apiBaseUrl;

  /// Human-readable app name per flavor.
  final String appName;

  /// Bundle ID / Application ID per flavor.
  final String bundleId;

  /// Whether this is a production build (affects logging, crash reporting, etc.).
  final bool isProduction;

  /// Whether this is a staging build.
  final bool isStaging;

  /// Whether this is a development build.
  final bool isDevelopment;

  const AppConfig._({
    required this.flavor,
    required this.apiBaseUrl,
    required this.appName,
    required this.bundleId,
    required this.isProduction,
    required this.isStaging,
    required this.isDevelopment,
  });

  /// Initialize configuration from environment.
  /// Call once at app startup before [runApp].
  static Future<AppConfig> initialize() async {
    // Load .env file if present (non-secret config only)
    await dotenv.load(fileName: '.env').catchError((_) {});
    return fromEnvironment();
  }

  /// Build configuration synchronously from compile-time dart-defines.
  /// Used by [initializeAppConfig] and as a safe lazy fallback so the app
  /// never crashes on an uninitialized config in tests.
  static AppConfig fromEnvironment() {
    const flavorString = String.fromEnvironment('FLUTTER_APP_FLAVOR');
    final flavor = _parseFlavor(flavorString);

    // Explicit override via dart-define takes highest priority
    const overrideUrl = String.fromEnvironment('API_BASE_URL');
    final apiBaseUrl = overrideUrl.isNotEmpty
        ? overrideUrl
        : _defaultBaseUrlForFlavor(flavor);

    return AppConfig._(
      flavor: flavor,
      apiBaseUrl: apiBaseUrl,
      appName: _appNameForFlavor(flavor),
      bundleId: _bundleIdForFlavor(flavor),
      isProduction: flavor == AppFlavor.production,
      isStaging: flavor == AppFlavor.staging,
      isDevelopment: flavor == AppFlavor.development,
    );
  }

  static AppFlavor _parseFlavor(String value) {
    switch (value.toLowerCase()) {
      case 'staging':
        return AppFlavor.staging;
      case 'production':
        return AppFlavor.production;
      case 'development':
      case 'dev':
      default:
        return AppFlavor.development;
    }
  }

  static String _defaultBaseUrlForFlavor(AppFlavor flavor) {
    switch (flavor) {
      case AppFlavor.staging:
        return _defaultStagingUrl;
      case AppFlavor.production:
        return _defaultProductionUrl;
      case AppFlavor.development:
        return _defaultDevUrl;
    }
  }

  /// Test-only accessor so flavor→URL resolution can be asserted.
  @visibleForTesting
  static String defaultBaseUrlForFlavor(AppFlavor flavor) => _defaultBaseUrlForFlavor(flavor);

  static String _appNameForFlavor(AppFlavor flavor) {
    switch (flavor) {
      case AppFlavor.staging:
        return 'EcoFinwize Staging';
      case AppFlavor.production:
        return 'EcoFinwize';
      case AppFlavor.development:
        return 'EcoFinwize Dev';
    }
  }

  static String _bundleIdForFlavor(AppFlavor flavor) {
    switch (flavor) {
      case AppFlavor.staging:
        return 'com.finwize.finwize.staging';
      case AppFlavor.production:
        return 'com.finwize.finwize';
      case AppFlavor.development:
        return 'com.finwize.finwize.dev';
    }
  }

  /// Convenience getter for API config used by [ApiService].
  String get apiConfigBaseUrl => apiBaseUrl;

  @override
  String toString() {
    return 'AppConfig(flavor: $flavor, apiBaseUrl: $apiBaseUrl, appName: $appName, bundleId: $bundleId)';
  }
}

/// Global accessor initialized at startup. Lazily falls back to a synchronous
/// build from dart-defines so tests never crash on an uninitialized config.
AppConfig? _appConfig;

AppConfig get appConfig {
  final resolved = _appConfig;
  if (resolved != null) return resolved;
  final fallback = AppConfig.fromEnvironment();
  _appConfig = fallback;
  return fallback;
}

/// Initialize [appConfig] globally. Call once before [runApp] to also load an
/// optional `.env` file (dotenv). Re-runnable so tests can re-init per case.
Future<void> initializeAppConfig() async {
  await dotenv.load(fileName: '.env').catchError((_) {});
  _appConfig = AppConfig.fromEnvironment();
  debugPrint('AppConfig initialized: $appConfig');
}