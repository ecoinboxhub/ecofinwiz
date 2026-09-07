import 'package:flutter/foundation.dart';
import '../services/api_service.dart';

class AuthProvider extends ChangeNotifier {
  final ApiService _api = ApiService();
  Map<String, dynamic>? _user;
  String? _plan;
  bool _loading = true;

  Map<String, dynamic>? get user => _user;
  bool get loading => _loading;
  bool get isLoggedIn => _user != null;
  bool get isAdmin => _user?['is_admin'] == true;

  /// The user's plan, resolved from `/subscriptions/my`. Defaults to 'free' so
  /// the upgrade banner and ads still behave sensibly when the call is not
  /// available yet (for example, on first launch while offline).
  String get plan => _plan ?? 'free';

  AuthProvider() { _checkAuth(); }

  Future<void> _checkAuth() async {
    try { _user = await _api.get('/users/me'); } catch (_) { _user = null; }
    _loading = false;
    await _refreshPlan();
    notifyListeners();
  }

  Future<void> _refreshPlan() async {
    if (_user == null) return;
    try {
      final sub = await _api.get('/subscriptions/my');
      if (sub is Map) {
        final value = sub['plan'];
        if (value is String) _plan = value;
      }
    } catch (_) {
      // Keep the last known plan; default remains 'free'.
    }
  }

  Future<void> login(String email, String password) async {
    final data = await _api.post('/auth/login', body: {'email': email, 'password': password});
    await _applyAuth(data);
    _user = await _api.get('/users/me');
    await _refreshPlan();
    notifyListeners();
  }

  Future<void> register(String email, String password, String fullName) async {
    final data = await _api.post('/auth/register', body: {'email': email, 'password': password, 'full_name': fullName});
    await _applyAuth(data);
    _user = data is Map && data['user'] is Map ? data['user'] as Map<String, dynamic> : null;
    await _refreshPlan();
    notifyListeners();
  }

  /// Backend auth responses nest tokens under `tokens`:
  /// `{user: {...}, tokens: {access_token, refresh_token}}`.
  Future<void> _applyAuth(dynamic data) async {
    if (data is! Map) return;
    final tokens = data['tokens'] is Map ? data['tokens'] as Map : null;
    final access = (tokens?['access_token'] ?? data['access_token']) as String?;
    final refresh = (tokens?['refresh_token'] ?? data['refresh_token']) as String?;
    if (access != null && refresh != null) {
      await _api.setTokens(access, refresh);
    }
  }

  Future<void> logout() async {
    await _api.clearTokens();
    _user = null;
    _plan = null;
    notifyListeners();
  }
}
