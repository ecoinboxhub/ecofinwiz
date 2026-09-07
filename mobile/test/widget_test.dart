import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:finwize/main.dart';
import 'package:finwize/providers/auth_provider.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('app boots to the landing screen when logged out', (tester) async {
    tester.view.physicalSize = const Size(2560, 1600);
    tester.view.devicePixelRatio = 1.0;
    addTearDown(tester.view.reset);

    await tester.pumpWidget(
      MultiProvider(
        providers: [ChangeNotifierProvider(create: (_) => AuthProvider())],
        child: const EcoFinwizeApp(),
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('EcoFinwize'), findsOneWidget);
    expect(find.text('Get Started'), findsOneWidget);
    expect(find.text('Log In'), findsOneWidget);
  });
}