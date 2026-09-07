import 'dart:async';

import 'package:connectivity_plus/connectivity_plus.dart';
import 'package:flutter/foundation.dart';

import '../services/sync_service.dart';

/// Tracks connectivity state for the offline banner and triggers the pending-op
/// queue flush when the device comes back online.
class ConnectivityProvider extends ChangeNotifier {
  ConnectivityProvider({SyncService? sync}) : _sync = sync ?? SyncService.instance;

  final SyncService _sync;
  bool _isOnline = true;
  StreamSubscription<List<ConnectivityResult>>? _sub;

  bool get isOnline => _isOnline;

  /// Test-only override so widget tests can simulate offline without plugins.
  @visibleForTesting
  bool overrideOnline = true;

  Future<void> start() async {
    if (_sub != null) return;
    _sub = Connectivity().onConnectivityChanged.listen((results) {
      final online = results.any((r) => r != ConnectivityResult.none);
      if (online != _isOnline) {
        _isOnline = online;
        notifyListeners();
        if (online) _sync.flush();
      }
    });
    try {
      final results = await Connectivity().checkConnectivity();
      _isOnline = results.any((r) => r != ConnectivityResult.none);
    } catch (_) {}
    notifyListeners();
  }

  void disposeSync() {
    _sub?.cancel();
    _sub = null;
    super.dispose();
  }
}