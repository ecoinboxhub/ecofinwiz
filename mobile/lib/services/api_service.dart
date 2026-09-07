import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

import 'local_db.dart';
import '../../config/app_config.dart';

typedef StreamEventHandler = void Function(Map<String, dynamic> event);

class ApiService {
  static final ApiService _instance = ApiService._();
  factory ApiService() => _instance;
  ApiService._();

  /// Test-only override so widget/unit tests can inject a mock HTTP client.
  @visibleForTesting
  static http.Client? debugClient;

  /// The active HTTP client (mock in tests, real otherwise). Public so internal
  /// services like [SyncService] can share the same injected client.
  static http.Client? get activeClient => debugClient;

  String get baseUrl => appConfig.apiConfigBaseUrl;

  /// Allow runtime override for deep links, testing, or dynamic config.
  static void configureBaseUrl(String url) {
    // This is a no-op since baseUrl now reads from appConfig.
    // Kept for API compatibility with existing callers.
    debugPrint('ApiService.configureBaseUrl called but ignored; use AppConfig.initialize()');
  }

  Future<Map<String, String>> _headers() async {
    final prefs = await SharedPreferences.getInstance();
    final token = prefs.getString('access_token');
    return {'Content-Type': 'application/json', if (token != null) 'Authorization': 'Bearer $token'};
  }

  Future<dynamic> get(String path, {Map<String, String>? params}) async {
    final uri = Uri.parse('$baseUrl$path').replace(queryParameters: params);
    final client = debugClient ?? http.Client();
    final res = await client.get(uri, headers: await _headers());
    if (client != debugClient) client.close();
    return _handle(res);
  }

  Future<dynamic> post(String path, {Map<String, dynamic>? body}) async {
    final client = debugClient ?? http.Client();
    final res = await client.post(Uri.parse('$baseUrl$path'), headers: await _headers(), body: body != null ? jsonEncode(body) : null);
    if (client != debugClient) client.close();
    return _handle(res);
  }

  Future<dynamic> put(String path, {Map<String, dynamic>? body}) async {
    final client = debugClient ?? http.Client();
    final res = await client.put(Uri.parse('$baseUrl$path'), headers: await _headers(), body: body != null ? jsonEncode(body) : null);
    if (client != debugClient) client.close();
    return _handle(res);
  }

  Future<dynamic> patch(String path, {Map<String, dynamic>? body}) async {
    final client = debugClient ?? http.Client();
    final res = await client.patch(Uri.parse('$baseUrl$path'), headers: await _headers(), body: body != null ? jsonEncode(body) : null);
    if (client != debugClient) client.close();
    return _handle(res);
  }

  Future<dynamic> delete(String path) async {
    final client = debugClient ?? http.Client();
    final res = await client.delete(Uri.parse('$baseUrl$path'), headers: await _headers());
    if (client != debugClient) client.close();
    return _handle(res);
  }

  /// Streams an SSE POST response, invoking [onEvent] for each `data:` payload.
  Future<void> stream(String path, {Map<String, dynamic>? body, required StreamEventHandler onEvent, http.Client? client}) async {
    final uri = Uri.parse('$baseUrl$path');
    final request = http.Request('POST', uri)
      ..headers.addAll(await _headers())
      ..body = body != null ? jsonEncode(body) : '';
    if (body != null) request.headers['Content-Type'] = 'application/json';
    final activeClient = client ?? debugClient ?? http.Client();
    final response = await activeClient.send(request);
    try {
      if (response.statusCode < 200 || response.statusCode >= 300) {
        throw ApiException(response.statusCode, await response.stream.bytesToString());
      }
      var buffer = '';
      await for (final chunk in response.stream.transform(utf8.decoder)) {
        buffer += chunk;
        var boundary = buffer.indexOf('\n');
        while (boundary != -1) {
          final line = buffer.substring(0, boundary).trim();
          buffer = buffer.substring(boundary + 1);
          if (line.startsWith('data: ')) {
            try {
              final data = jsonDecode(line.substring(6));
              if (data is Map<String, dynamic>) onEvent(data);
            } catch (_) {
              // skip malformed JSON
            }
          }
          boundary = buffer.indexOf('\n');
        }
      }
    } finally {
      if (activeClient != debugClient && activeClient != client) activeClient.close();
    }
  }

  dynamic _handle(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return response.body.isNotEmpty ? jsonDecode(response.body) : null;
    }
    throw ApiException(response.statusCode, response.body);
  }

  // ----------------------------------------------------------- offline ------

  static final LocalDb _offline = LocalDb.instance;

  /// Offline-first GET: hits the network and caches the response; on any
  /// failure (offline, timeout, server error) falls back to the cached copy.
  /// Returns `null` only when there is neither a live response nor a cache.
  Future<dynamic> getOffline(String path, {Map<String, String>? params}) async {
    final key = '$path?${params?.entries.map((e) => '${e.key}=${e.value}').join('&') ?? ''}';
    try {
      final data = await get(path, params: params);
      await _offline.cacheResponse(key, data);
      return data;
    } catch (_) {
      return _offline.readCache(key);
    }
  }

  /// Offline-first POST: replays the request immediately when online; when
  /// offline it queues the write in `pending_ops` for later background sync.
  /// Returns the live response, or `true` when the op was queued.
  Future<dynamic> postOffline(String path, {Map<String, dynamic>? body}) async {
    try {
      return await post(path, body: body);
    } catch (_) {
      await _offline.enqueueOp('POST', path, body: body);
      return true;
    }
  }

  Future<void> setTokens(String access, String refresh) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('access_token', access);
    await prefs.setString('refresh_token', refresh);
  }

  Future<void> clearTokens() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('access_token');
    await prefs.remove('refresh_token');
  }
}

class ApiException implements Exception {
  final int statusCode;
  final String body;
  ApiException(this.statusCode, this.body);
  @override
  String toString() => 'ApiException($statusCode): $body';
}
