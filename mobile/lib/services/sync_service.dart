import 'dart:async';
import 'dart:convert';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import 'api_service.dart';
import 'local_db.dart';

/// Flushes queued offline writes when connectivity returns. Uses
/// `connectivity_plus` as a trigger only; a real reachability probe against
/// `/api/v1/health` confirms the server is actually reachable before any op is
/// replayed (AGENTS.md Principle 3).
class SyncService {
  SyncService._();
  static final SyncService instance = SyncService._();

  final ApiService _api = ApiService();
  final LocalDb _db = LocalDb.instance;

  StreamSubscription<List<ConnectivityResult>>? _sub;
  bool _listening = false;
  bool _flushing = false;

  /// Test-only reachability probe, so tests can simulate offline/online.
  @visibleForTesting
  Future<bool> Function()? reachabilityProbe;

  /// Test-only flag to suppress the health probe entirely.
  @visibleForTesting
  bool skipReachabilityProbe = false;

  Future<bool> _isReachable() async {
    if (skipReachabilityProbe) return true;
    final probe = reachabilityProbe;
    if (probe != null) return probe();
    try {
      final client = ApiService.activeClient ?? http.Client();
      final res = await client.get(Uri.parse('${_api.baseUrl}/health'));
      if (client != ApiService.activeClient) client.close();
      return res.statusCode >= 200 && res.statusCode < 300;
    } catch (_) {
      return false;
    }
  }

  /// Starts listening for connectivity changes and flushes on reconnect.
  void start() {
    if (_listening) return;
    _listening = true;
    _sub = Connectivity().onConnectivityChanged.listen((results) {
      final online = results.any((r) => r != ConnectivityResult.none);
      if (online) flush();
    });
  }

  void stop() {
    _sub?.cancel();
    _sub = null;
    _listening = false;
  }

  /// Replays queued ops in FIFO order. Stops at the first failure (the op that
  /// failed keeps its 'pending' status so it retries next time). Ops that fail
  /// with a permanent client error are dropped.
  Future<void> flush() async {
    if (_flushing) return;
    _flushing = true;
    try {
      if (!await _isReachable()) return;
      final ops = await _db.pendingOps();
      for (final op in ops) {
        final id = op['id'] as int;
        final method = op['method'] as String;
        final url = op['url'] as String;
        final rawBody = op['body'] as String?;
        try {
          final decoded = rawBody != null ? _parseJson(rawBody) : null;
          if (method == 'POST') {
            await _api.post(url, body: decoded);
          } else if (method == 'PUT') {
            await _api.put(url, body: decoded);
          } else if (method == 'PATCH') {
            await _api.patch(url, body: decoded);
          } else if (method == 'DELETE') {
            await _api.delete(url);
          }
          await _db.markOpDone(id);
        } on ApiException catch (e) {
          if (e.statusCode >= 400 && e.statusCode < 500) {
            // Permanent client error - drop the op so it never retries forever.
            await _db.markOpDone(id);
          } else {
            // Server error / network failure - stop, retry next flush.
            return;
          }
        } catch (_) {
          return;
        }
      }
    } finally {
      _flushing = false;
    }
  }

  Map<String, dynamic> _parseJson(String raw) {
    try {
      return (jsonDecode(raw) as Map).cast<String, dynamic>();
    } catch (_) {
      return {};
    }
  }
}