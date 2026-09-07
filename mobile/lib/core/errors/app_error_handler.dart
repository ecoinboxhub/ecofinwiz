import 'dart:async';
import 'dart:io';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:package_info_plus/package_info_plus.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:device_info_plus/device_info_plus.dart';
import 'package:sentry_flutter/sentry_flutter.dart';
import '../../config/app_config.dart';

/// Global error handler for Flutter app.
/// Initializes in main.dart before runApp.
class AppErrorHandler {
  static bool _initialized = false;
  static String? _userId;
  static String? _currentRoute;
  static final _localErrorLog = <Map<String, dynamic>>[];
  static const _maxLocalLogs = 100;

  static Future<void> init() async {
    if (_initialized) return;
    _initialized = true;

    // Initialize Sentry if DSN is configured
    final sentryDsn = const String.fromEnvironment('SENTRY_DSN');
    if (sentryDsn.isNotEmpty) {
      await SentryFlutter.init(
        (options) {
          options.dsn = sentryDsn;
          options.environment = appConfig.flavor.name;
          options.release = 'finwize@${appConfig.appName}'; // Will be updated from package info
          options.tracesSampleRate = 0.25;
          options.profilesSampleRate = 0.10;
          options.enableAutoSessionTracking = true;
          options.attachStacktrace = true;
          options.debug = kDebugMode;
        },
        appRunner: () => runApp(const _SentryAppWrapper()),
      );
    }

    // Capture Flutter framework errors
    FlutterError.onError = _onFlutterError;

    // Capture Dart async errors (outside Flutter framework)
    PlatformDispatcher.instance.onError = _onPlatformError;

    // Get package info for context
    final packageInfo = await PackageInfo.fromPlatform();
    debugPrint('AppErrorHandler initialized: ${packageInfo.packageName} v${packageInfo.version}');
  }

  static void setUserId(String? userId) {
    _userId = userId;
    if (_userId != null) {
      Sentry.configureScope((scope) => scope.setUser(SentryUser(id: _userId)));
    } else {
      Sentry.configureScope((scope) => scope.setUser(null));
    }
  }

  static void setCurrentRoute(String? route) {
    _currentRoute = route;
    if (_currentRoute != null) {
      Sentry.configureScope((scope) => scope.setTag('route', _currentRoute!));
    }
  }

  static void setUserContext({String? email, String? username, Map<String, String>? extra}) {
    Sentry.configureScope((scope) {
      if (email != null) scope.setUser(SentryUser(id: _userId, email: email));
      if (username != null) scope.setTag('username', username);
      if (extra != null) {
        for (final entry in extra.entries) {
          scope.setExtra(entry.key, entry.value);
        }
      }
    });
  }

  static bool _onPlatformError(Object error, StackTrace stack) {
    _handleError(error, stack, 'PlatformDispatcher');
    return true; // Prevent default handler
  }

  static void _onFlutterError(FlutterErrorDetails details) {
    _handleError(details.exception, details.stack, 'FlutterError', {'context': details.context?.toString()});
  }

  static void _handleError(
    Object error,
    StackTrace? stack, [
    String? source,
    Map<String, dynamic>? context,
  ]) {
    final errorEntry = _buildErrorEntry(error, stack, source, context);
    _localErrorLog.add(errorEntry);

    // Keep only recent logs
    if (_localErrorLog.length > _maxLocalLogs) {
      _localErrorLog.removeAt(0);
    }

    // Log to console
    debugPrint('=== AppErrorHandler ===');
    debugPrint('Source: $source');
    debugPrint('Route: $_currentRoute');
    debugPrint('User: ${_userId ?? 'anonymous'}');
    debugPrint('Error: $error');
    if (stack != null) debugPrint('Stack: $stack');
    debugPrint('========================');

    // Send to Sentry if configured
    if (appConfig.isProduction || appConfig.isStaging) {
      _sendToSentry(error, stack, source, context);
    }
  }

  static Map<String, dynamic> _buildErrorEntry(
    Object error,
    StackTrace? stack,
    String? source,
    Map<String, dynamic>? context,
  ) {
    return {
      'timestamp': DateTime.now().toIso8601String(),
      'error': error.toString(),
      'stack': stack?.toString(),
      'source': source,
      'route': _currentRoute,
      'userId': _userId,
      'flavor': appConfig.flavor.name,
      'appVersion': '1.0.0', // Will be updated from package info
      'context': context ?? {},
    };
  }

  static Future<void> _sendToSentry(
    Object error,
    StackTrace? stack,
    String? source,
    Map<String, dynamic>? context,
  ) async {
    try {
      await Sentry.captureException(
        error,
        stackTrace: stack,
        withScope: (scope) {
          scope.setTag('source', source ?? 'unknown');
          scope.setTag('flavor', appConfig.flavor.name);
          if (_userId != null) scope.setUser(SentryUser(id: _userId));
          if (_currentRoute != null) scope.setTag('route', _currentRoute!);
          if (context != null) {
            for (final entry in context.entries) {
              scope.setExtra(entry.key, entry.value);
            }
          }
        },
      );
    } catch (e) {
      debugPrint('[Sentry] Failed to send error: $e');
    }
  }

  /// Get locally stored error logs for debugging/support.
  static List<Map<String, dynamic>> getLocalLogs() => List.unmodifiable(_localErrorLog);

  /// Clear local error logs.
  static void clearLocalLogs() => _localErrorLog.clear();

  /// Report a non-fatal error manually (e.g., from try-catch).
  static void reportError(
    Object error,
    StackTrace? stack, {
    String? source,
    Map<String, dynamic>? context,
  }) {
    _handleError(error, stack, source ?? 'ManualReport', context);
  }

  /// Add breadcrumb for debugging trail
  static void addBreadcrumb(String message, {String? category, Map<String, dynamic>? data}) {
    Sentry.addBreadcrumb(
      Breadcrumb(
        message: message,
        category: category ?? 'app',
        data: data,
        level: SentryLevel.info,
      ),
    );
  }
}

/// Wrapper app for Sentry initialization
class _SentryAppWrapper extends StatelessWidget {
  const _SentryAppWrapper();

  @override
  Widget build(BuildContext context) {
    return const _SentryApp();
  }
}

class _SentryApp extends StatelessWidget {
  const _SentryApp({super.key});

  @override
  Widget build(BuildContext context) {
    // This will be replaced by the actual app in main.dart
    return Container();
  }
}