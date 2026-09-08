import 'dart:convert';

import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:finwize/config/app_config.dart';
import 'package:finwize/providers/auth_provider.dart';
import 'package:finwize/services/api_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    await initializeAppConfig();
  });

  tearDown(() => ApiService.debugClient = null);

  test('login parses the nested {user, tokens} response and resolves the plan', () async {
    ApiService.debugClient = MockClient((request) async {
      final path = request.url.path.replaceFirst('/api/v1', '');
      if (path == '/auth/login') {
        return http.Response(jsonEncode({
          'user': {'id': 'u1', 'email': 'adaeze@finwize.app', 'full_name': 'Adaeze Okafor', 'is_admin': false},
          'tokens': {'access_token': 'at1', 'refresh_token': 'rt1', 'token_type': 'bearer'},
        }), 200);
      }
      if (path == '/users/me') {
        return http.Response(jsonEncode({'id': 'u1', 'email': 'adaeze@finwize.app', 'full_name': 'Adaeze Okafor', 'is_admin': false}), 200);
      }
      if (path == '/subscriptions/my') {
        return http.Response(jsonEncode({'id': 's1', 'user_id': 'u1', 'plan': 'pro', 'status': 'active'}), 200);
      }
      return http.Response('{}', 404);
    });

    final provider = AuthProvider();
    await provider.login('adaeze@finwize.app', 'password123');

    expect(provider.isLoggedIn, isTrue);
    expect(provider.user?['full_name'], 'Adaeze Okafor');
    expect(provider.plan, 'pro');

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('access_token'), 'at1');
    expect(prefs.getString('refresh_token'), 'rt1');

    await provider.logout();
    expect(provider.isLoggedIn, isFalse);
  });

  test('register parses the nested response and stores tokens', () async {
    ApiService.debugClient = MockClient((request) async {
      final path = request.url.path.replaceFirst('/api/v1', '');
      if (path == '/auth/register') {
        return http.Response(jsonEncode({
          'user': {'id': 'u2', 'email': 'chidi@finwize.app', 'full_name': 'Chidi Obi', 'is_admin': false},
          'tokens': {'access_token': 'at2', 'refresh_token': 'rt2', 'token_type': 'bearer'},
        }), 200);
      }
      if (path == '/subscriptions/my') {
        return http.Response(jsonEncode({'id': 's1', 'user_id': 'u2', 'plan': 'free', 'status': 'active'}), 200);
      }
      return http.Response('{}', 404);
    });

    final provider = AuthProvider();
    await provider.register('chidi@finwize.app', 'password123', 'Chidi Obi');

    expect(provider.isLoggedIn, isTrue);
    expect(provider.user?['full_name'], 'Chidi Obi');
    expect(provider.user?['email'], 'chidi@finwize.app');
    expect(provider.plan, 'free');

    final prefs = await SharedPreferences.getInstance();
    expect(prefs.getString('access_token'), 'at2');
    expect(prefs.getString('refresh_token'), 'rt2');
  });
}