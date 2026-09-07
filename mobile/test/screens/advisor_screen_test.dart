import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:finwize/screens/advisor_screen.dart';
import 'package:finwize/services/api_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    ApiService.debugClient = null;
  });

  tearDown(() => ApiService.debugClient = null);

  Widget wrap() => const MaterialApp(home: AdvisorScreen());

  Future<void> pumpAdvisor(WidgetTester tester) async {
    await tester.pumpWidget(wrap());
    await tester.pump();
  }

  testWidgets('shows greeting and suggestion chips when empty', (tester) async {
    await pumpAdvisor(tester);

    expect(find.text("Hi! I'm Kemi"), findsOneWidget);
    expect(find.text('Your personal finance coach.'), findsOneWidget);
    expect(find.text('How do I start budgeting?'), findsOneWidget);
  });

  testWidgets('sends a message and streams the assistant reply', (tester) async {
    ApiService.debugClient = MockClient((request) async {
      expect(request.method, 'POST');
      expect(request.url.path, endsWith('/ai/advisor/chat'));
      return http.Response(
        'data: {"event": "started", "conversation_id": "c1"}\n\n'
        'data: {"event": "token", "token": "Try a 50-30-20 split"}\n\n'
        'data: {"event": "done", "message_id": "m1", "conversation_id": "c1"}\n\n',
        200,
        headers: {'content-type': 'text/event-stream'},
      );
    });

    await pumpAdvisor(tester);

    await tester.enterText(find.byType(TextField), 'Help me budget');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pump();

    expect(find.text('Help me budget'), findsOneWidget);

    await tester.pump(const Duration(milliseconds: 50));
    expect(find.text('Try a 50-30-20 split'), findsOneWidget);
  });

  testWidgets('shows fallback error message when the request fails', (tester) async {
    ApiService.debugClient = MockClient((request) async {
      return http.Response('{"detail":"Forbidden"}', 403);
    });

    await pumpAdvisor(tester);

    await tester.enterText(find.byType(TextField), 'Hello');
    await tester.tap(find.byIcon(Icons.send));
    await tester.pump();
    await tester.pump(const Duration(milliseconds: 50));

    expect(find.text("Sorry, I couldn't process that."), findsOneWidget);
  });
}