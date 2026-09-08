import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:finwize/config/app_config.dart';
import 'package:finwize/config/app_config.dart';
import 'package:finwize/services/api_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    ApiService.debugClient = null;
    await initializeAppConfig();
  });

  tearDown(() => ApiService.debugClient = null);

  group('ApiService.stream', () {
    test('parses SSE data events into onEvent callbacks', () async {
      ApiService.debugClient = MockClient((request) async {
        expect(request.method, 'POST');
        expect(request.url.path, endsWith('/ai/advisor/chat'));
        expect(request.headers['Content-Type'], 'application/json');
        expect(request.body, contains('"message":"hello"'));
        return http.Response(
          'data: {"event": "started", "conversation_id": "c1"}\n\n'
          'data: {"event": "token", "token": "Hi"}\n\n'
          'data: {"event": "token", "token": " there"}\n\n'
          'data: {"event": "done", "message_id": "m1", "conversation_id": "c1"}\n\n',
          200,
          headers: {'content-type': 'text/event-stream'},
        );
      });

      final events = <Map<String, dynamic>>[];
      await ApiService().stream(
        '/ai/advisor/chat',
        body: {'message': 'hello'},
        onEvent: events.add,
      );

      expect(events.length, 4);
      expect(events[0]['event'], 'started');
      expect(events[0]['conversation_id'], 'c1');
      expect(events[1]['event'], 'token');
      expect(events[1]['token'], 'Hi');
      expect(events[2]['token'], ' there');
      expect(events[3]['event'], 'done');
    });

    test('ignores malformed JSON lines', () async {
      ApiService.debugClient = MockClient((request) async {
        return http.Response(
          'data: not-json\n\n'
          'data: {"event": "done", "message_id": "m1"}\n\n',
          200,
          headers: {'content-type': 'text/event-stream'},
        );
      });

      final events = <Map<String, dynamic>>[];
      await ApiService().stream('/ai/advisor/chat', onEvent: events.add);

      expect(events.length, 1);
      expect(events[0]['event'], 'done');
    });

    test('throws ApiException on non-2xx response', () async {
      ApiService.debugClient = MockClient((request) async {
        return http.Response('{"detail":"Forbidden"}', 403);
      });

      expect(
        () => ApiService().stream('/ai/advisor/chat', onEvent: (_) {}),
        throwsA(isA<ApiException>()
            .having((e) => e.statusCode, 'statusCode', 403)),
      );
    });
  });

  group('AppConfig flavor→URL resolution', () {
    test('defaults to emulator base URL in tests', () async {
      final config = await AppConfig.initialize();
      expect(config.apiBaseUrl, 'http://10.0.2.2:8100/api/v1');
    });

    test('staging flavor resolves to staging base URL', () {
      expect(
        AppConfig.defaultBaseUrlForFlavor(AppFlavor.staging),
        'https://ecofinwiz-api.onrender.com/api/v1',
      );
    });

    test('production flavor resolves to production base URL', () {
      expect(
        AppConfig.defaultBaseUrlForFlavor(AppFlavor.production),
        'https://ecofinwiz-api.onrender.com/api/v1',
      );
    });
  });
}