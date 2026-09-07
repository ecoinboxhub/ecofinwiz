# EcoFinwize Mobile App

Flutter application for EcoFinwize — Financial & Business Guidance for Africa.

## Build Flavors

The app supports three build flavors, each with its own API endpoint, bundle ID, and app name:

| Flavor | API Base URL | Bundle ID | App Name |
|--------|--------------|-----------|----------|
| `development` | `http://10.0.2.2:8100/api/v1` (emulator) | `com.finwize.finwize.dev` | EcoFinwize Dev |
| `staging` | `https://staging-api.finwize.app/api/v1` | `com.finwize.finwize.staging` | EcoFinwize Staging |
| `production` | `https://api.finwize.app/api/v1` | `com.finwize.finwize` | EcoFinwize |

## Quick Start

### Prerequisites
- Flutter SDK 3.22.0+
- Dart 3.4+
- Android Studio / VS Code with Flutter plugin
- Android SDK (API 24+)

### Local Development

```bash
# 1. Install dependencies
cd mobile
flutter pub get

# 2. Run on emulator (development flavor)
flutter run --flavor development

# 3. Run on physical device (development flavor)
# Update lib/services/api_service.dart physicalBaseUrl if needed
flutter run --flavor development
```

### Build APKs

```bash
# Development (emulator default)
flutter build apk --flavor development --dart-define=FLUTTER_APP_FLAVOR=development

# Staging
flutter build apk --flavor staging --dart-define=FLUTTER_APP_FLAVOR=staging

# Production
flutter build apk --flavor production --dart-define=FLUTTER_APP_FLAVOR=production

# Override API URL at build time (e.g., point dev build at staging)
flutter build apk --flavor development --dart-define=FLUTTER_APP_FLAVOR=development --dart-define=API_BASE_URL=https://staging-api.finwize.app/api/v1
```

### Output Locations
- Development: `build/app/outputs/flutter-apk/app-development-release.apk`
- Staging: `build/app/outputs/flutter-apk/app-staging-release.apk`
- Production: `build/app/outputs/flutter-apk/app-production-release.apk`

## Configuration

### Environment Files
Non-secret configuration via `.env` files (loaded by `flutter_dotenv`):
- `.env.development` — Local development defaults
- `.env.staging` — Staging defaults
- `.env.production` — Production defaults
- `.env` — Active config (copy from flavor file or use CI `--dart-define`)

### Dart Defines (CI/CD)
All configuration injected at build time via `--dart-define`:
- `FLUTTER_APP_FLAVOR` — `development`, `staging`, or `production`
- `API_BASE_URL` — Override API endpoint (highest priority)

### GitHub Actions
Automated builds on push to `main`:
```yaml
# .github/workflows/ci.yml
flutter-build:
  strategy:
    matrix:
      flavor: [development, staging, production]
  steps:
    - flutter build apk --flavor ${{ matrix.flavor }} --dart-define=FLUTTER_APP_FLAVOR=${{ matrix.flavor }}
```

Artifacts uploaded as `finwize-apk-<flavor>`.

## Architecture

### Key Files
- `lib/config/app_config.dart` — Centralized configuration (flavor, API URL, bundle ID)
- `lib/services/api_service.dart` — HTTP client with offline-first support
- `lib/main.dart` — App entry point, initializes config before runApp
- `android/app/build.gradle` — Android flavor definitions

### Offline-First Support
- `LocalDb` (sqflite) caches GET responses
- Failed POST requests queued in `pending_ops` for background sync
- `ConnectivityProvider` detects online/offline state
- `SyncService` replays queued operations when connectivity restored

## Testing

```bash
# Unit tests
flutter test

# Integration tests (requires device/emulator)
flutter drive --target=test_driver/app.dart --flavor development
```

## Code Generation
None required — configuration is pure Dart with compile-time constants.

## Troubleshooting

### "Unable to load asset: .env"
Ensure `.env` is listed in `pubspec.yaml` assets and run `flutter pub get`.

### Wrong API URL in production build
Verify `--dart-define=FLUTTER_APP_FLAVOR=production` is passed and `API_BASE_URL` not overridden incorrectly.

### Emulator can't reach localhost
Use `10.0.2.2` (Android emulator alias for host machine) not `localhost`.

### Flavor not recognized
Clean and rebuild: `flutter clean && flutter pub get && flutter build apk --flavor <flavor>`