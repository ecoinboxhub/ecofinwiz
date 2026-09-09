// Screenshot capture harness — renders each app screen with mocked API data
// and writes PNGs via golden files. Run with:
//   flutter test test/screenshots/screenshots_test.dart --update-goldens
@Tags(['screenshots'])
library;
import 'dart:convert';
import 'dart:io';
import 'package:test_api/test_api.dart' show Tags;

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:finwize/config/theme.dart';
import 'package:finwize/providers/auth_provider.dart';
import 'package:finwize/providers/connectivity_provider.dart';
import 'package:finwize/services/api_service.dart';
import 'package:finwize/services/local_db.dart';
import 'package:finwize/widgets/ad_banner.dart';

import 'package:finwize/screens/landing_screen.dart';
import 'package:finwize/screens/login_screen.dart';
import 'package:finwize/screens/register_screen.dart';
import 'package:finwize/screens/dashboard_screen.dart';
import 'package:finwize/screens/advisor_screen.dart';
import 'package:finwize/screens/mentor_screen.dart';
import 'package:finwize/screens/investment_screen.dart';
import 'package:finwize/screens/calculators_screen.dart';
import 'package:finwize/screens/budget_screen.dart';
import 'package:finwize/screens/transactions_screen.dart';
import 'package:finwize/screens/savings_screen.dart';
import 'package:finwize/screens/learning_screen.dart';
import 'package:finwize/screens/articles_screen.dart';
import 'package:finwize/screens/news_screen.dart';
import 'package:finwize/screens/forum_screen.dart';
import 'package:finwize/screens/invoices_screen.dart';
import 'package:finwize/screens/business_tasks_screen.dart';
import 'package:finwize/screens/business_plan_screen.dart';
import 'package:finwize/screens/profile_screen.dart';
import 'package:finwize/screens/notifications_screen.dart';
import 'package:finwize/screens/admin_screen.dart';

Map<String, dynamic> _user() => {
      'id': 'u1', 'full_name': 'Adaeze Okafor', 'email': 'adaeze@finwize.app',
      'is_admin': true, 'is_active': true,
    };

MockClient _mockClient() {
  return MockClient((request) async {
    final path = request.url.path.replaceFirst('/api/v1', '');
    if (request.url.pathSegments.isNotEmpty && request.url.pathSegments.first == 'ads') {
      return http.Response(jsonEncode([]), 200);
    }
    if (path == '/users/me') return http.Response(jsonEncode(_user()), 200);
    if (path == '/subscriptions/my') {
      return http.Response(jsonEncode({
        'id': 's1', 'user_id': 'u1', 'plan': 'free', 'status': 'active',
        'provider': 'internal', 'provider_ref': null,
        'current_period_start': '2026-08-01T00:00:00Z', 'current_period_end': null,
        'auto_renew': false, 'created_at': '2026-08-01T00:00:00Z',
      }), 200);
    }
    if (path == '/users/me/progress') {
      return http.Response(jsonEncode({'lessons_completed': 12, 'badges': ['b1', 'b2', 'b3', 'b4', 'b5'], 'active_goals': 3}), 200);
    }
    if (path == '/users/me/notifications') {
      return http.Response(jsonEncode({
        'items': [
          {'id': 'n1', 'title': 'Budget alert', 'message': 'You spent 80% of your Food budget.', 'created_at': '2026-08-16', 'is_read': false},
          {'id': 'n2', 'title': 'Goal reached', 'message': 'Emergency fund goal is 50% funded.', 'created_at': '2026-08-15', 'is_read': true},
        ],
        'page': 1, 'per_page': 20,
      }), 200);
    }
    if (path == '/finance/budgets') {
      return http.Response(jsonEncode({'budgets': [
        {'id': 'b1', 'name': 'Food', 'category': 'Food', 'monthly_limit': 120000, 'spent': 96000, 'remaining': 24000},
        {'id': 'b2', 'name': 'Transport', 'category': 'Transport', 'monthly_limit': 60000, 'spent': 21000, 'remaining': 39000},
        {'id': 'b3', 'name': 'Rent', 'category': 'Housing', 'monthly_limit': 300000, 'spent': 300000, 'remaining': 0},
      ]}), 200);
    }
    if (path == '/finance/transactions') {
      return http.Response(jsonEncode({'transactions': [
        {'id': 't1', 'description': 'Salary', 'category': 'Income', 'type': 'income', 'amount': 350000, 'date': '2026-08-14'},
        {'id': 't2', 'description': 'Groceries', 'category': 'Food', 'type': 'expense', 'amount': 42000, 'date': '2026-08-13'},
        {'id': 't3', 'description': 'Fuel', 'category': 'Transport', 'type': 'expense', 'amount': 18000, 'date': '2026-08-12'},
        {'id': 't4', 'description': 'Freelance gig', 'category': 'Income', 'type': 'income', 'amount': 85000, 'date': '2026-08-11'},
      ]}), 200);
    }
    if (path == '/finance/savings-goals') {
      return http.Response(jsonEncode({'goals': [
        {'id': 'g1', 'name': 'Emergency Fund', 'target_amount': 500000, 'current_amount': 250000},
        {'id': 'g2', 'name': 'New Laptop', 'target_amount': 800000, 'current_amount': 320000},
      ]}), 200);
    }
    if (path == '/intelligence/tips/daily') {
      return http.Response(jsonEncode({'tip': 'Set aside at least 20% of your income before spending it.'}), 200);
    }
    if (path == '/content/articles') {
      return http.Response(jsonEncode([
        {'id': 'a1', 'title': 'The 50-30-20 Budgeting Rule', 'summary': 'A simple way to split your income into needs, wants and savings.', 'content': 'body'},
        {'id': 'a2', 'title': 'Understanding Compound Interest', 'summary': 'Why time in the market beats timing the market.', 'content': 'body'},
        {'id': 'a3', 'title': 'Getting Your First Loan', 'summary': 'What lenders look for and how to qualify.', 'content': 'body'},
      ]), 200);
    }
    if (path == '/content/news') {
      return http.Response(jsonEncode([
        {'id': 'nw1', 'title': 'CBN holds benchmark rate at 27.5%', 'summary': 'Inflation pressures ease as economy stabilises.', 'is_breaking': true},
        {'id': 'nw2', 'title': 'NGX All-Share Index crosses 150k', 'summary': 'Investors eye banking and telecom stocks.', 'is_breaking': false},
      ]), 200);
    }
    if (path == '/content/forum/topics') {
      return http.Response(jsonEncode([
        {'id': 'f1', 'title': 'Best apps for budgeting in Nigeria?', 'content': 'Looking for recommendations...', 'reply_count': 14, 'is_pinned': true, 'is_locked': false},
        {'id': 'f2', 'title': 'Where to start investing with NGN 50k', 'content': 'Mutual funds or T-bills?', 'reply_count': 8, 'is_pinned': false, 'is_locked': false},
      ]), 200);
    }
    if (path == '/invoices') {
      return http.Response(jsonEncode([
        {'id': 'i1', 'number': 'INV-001', 'client_name': 'Babs Ltd', 'total': 250000, 'currency': 'NGN', 'status': 'paid'},
        {'id': 'i2', 'number': 'INV-002', 'client_name': 'Ada Traders', 'total': 120000, 'currency': 'NGN', 'status': 'sent'},
      ]), 200);
    }
    if (path == '/tasks') {
      return http.Response(jsonEncode([
        {'id': 't1', 'title': 'Send proposal to client', 'priority': 'high', 'status': 'pending'},
        {'id': 't2', 'title': 'Update cash flow sheet', 'priority': 'medium', 'status': 'in_progress'},
      ]), 200);
    }
    if (path == '/admin/stats') {
      return http.Response(jsonEncode({'total_users': 2480, 'total_transactions': 15642}), 200);
    }
    if (path == '/admin/users') {
      return http.Response(jsonEncode({
        'items': [
          {'id': 'u1', 'full_name': 'Adaeze Okafor', 'email': 'adaeze@finwize.app', 'is_admin': true, 'is_active': true},
          {'id': 'u2', 'full_name': 'Chidi Obi', 'email': 'chidi@finwize.app', 'is_admin': false, 'is_active': true},
        ],
        'total': 2,
      }), 200);
    }
    if (path == '/subscriptions/plans') {
      return http.Response(jsonEncode([
        {'key': 'free', 'name': 'Free', 'price_monthly': 0, 'ai_chats_per_month': null, 'max_savings_goals': 3, 'max_invoices_per_month': 0, 'ad_free': false},
        {'key': 'pro', 'name': 'Pro', 'price_monthly': 4000, 'ai_chats_per_month': null, 'max_savings_goals': null, 'max_invoices_per_month': null, 'ad_free': true},
      ]), 200);
    }
    return http.Response(jsonEncode([]), 200);
  });
}

Future<void> _loadFonts() async {
  const fontDir = 'C:/src/flutter/bin/cache/artifacts/material_fonts';
  if (!File('$fontDir/roboto-regular.ttf').existsSync()) {
    return;
  }
  final loader = FontLoader('Roboto');
  for (final name in ['roboto-regular.ttf', 'roboto-medium.ttf', 'roboto-bold.ttf']) {
    final bytes = await File('$fontDir/$name').readAsBytes();
    loader.addFont(Future.value(ByteData.view(bytes.buffer)));
  }
  await loader.load();
}

Future<void> _pump(WidgetTester tester, Widget home) async {
  tester.view.physicalSize = const Size(824, 1784); // ~412x892 logical @2x phone
  tester.view.devicePixelRatio = 2.0;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    MultiProvider(
      providers: [
        ChangeNotifierProvider<AuthProvider>(create: (_) => AuthProvider()),
        ChangeNotifierProvider<ConnectivityProvider>(create: (_) => ConnectivityProvider()),
      ],
      child: MaterialApp(theme: AppTheme.lightTheme, home: home),
    ),
  );
  await tester.pumpAndSettle();
  tester.takeException(); // swallow layout overflow so goldens still render
}

Future<void> _shot(WidgetTester tester, String name) async {
  await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/$name.png'));
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUpAll(() async {
    SharedPreferences.setMockInitialValues({});
    ApiService.debugClient = _mockClient();
    await _loadFonts();
    LocalDb.instance.reset();
    final db = await databaseFactoryFfiNoIsolate.openDatabase(
      inMemoryDatabasePath,
      options: OpenDatabaseOptions(version: 1, onCreate: LocalDb.createSchema),
    );
    LocalDb.instance.attach(db);
  });

  setUp(() {
    ApiService.debugClient = _mockClient();
  });

  tearDown(() => ApiService.debugClient = null);

  final shots = <String, Widget>{
    'landing': const LandingScreen(),
    'login': const LoginScreen(),
    'register': const RegisterScreen(),
    'dashboard': const DashboardScreen(),
    'advisor': const AdvisorScreen(),
    'mentor': const MentorScreen(),
    'investment': const InvestmentScreen(),
    'calculators': const CalculatorsScreen(),
    'budget': const BudgetScreen(),
    'transactions': const TransactionsScreen(),
    'savings': const SavingsScreen(),
    'learning': const LearningScreen(),
    'articles': const ArticlesScreen(),
    'news': const NewsScreen(),
    'forum': const ForumScreen(),
    'invoices': const InvoicesScreen(),
    'business_tasks': const BusinessTasksScreen(),
    'business_plan': const BusinessPlanScreen(),
    'profile': const ProfileScreen(),
    'notifications': const NotificationsScreen(),
    'admin': const AdminScreen(),
    'pricing': const PricingScreen(),
  };

  for (final entry in shots.entries) {
    testWidgets('screenshot: ${entry.key}', (tester) async {
      await _pump(tester, entry.value);
      await _shot(tester, entry.key);
    });
  }
}