import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'config/theme.dart';
import 'config/app_config.dart';
import 'core/errors/app_error_handler.dart';
import 'providers/auth_provider.dart';
import 'providers/connectivity_provider.dart';
import 'screens/landing_screen.dart';
import 'screens/dashboard_screen.dart';
import 'screens/budget_screen.dart';
import 'screens/advisor_screen.dart';
import 'screens/mentor_screen.dart';
import 'screens/investment_screen.dart';
import 'screens/learning_screen.dart';
import 'services/sync_service.dart';
import 'widgets/ad_banner.dart';
import 'widgets/offline_banner.dart';
import 'widgets/error_fallback.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await initializeAppConfig();

  final sentryDsn = const String.fromEnvironment('SENTRY_DSN');
  if (sentryDsn.isNotEmpty) {
    await SentryFlutter.init(
      (options) {
        options.dsn = sentryDsn;
        options.environment = appConfig.flavor.name;
        options.release = 'finwize@1.0.0';
        options.tracesSampleRate = 0.25;
        options.profilesSampleRate = 0.10;
        options.enableAutoSessionTracking = true;
        options.attachStacktrace = true;
        options.debug = false;
      },
      appRunner: () => runApp(const EcoFinwizeApp()),
    );
  } else {
    runApp(const EcoFinwizeApp());
  }
}

class EcoFinwizeApp extends StatelessWidget {
  const EcoFinwizeApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => AuthProvider()),
        ChangeNotifierProvider(create: (_) => ConnectivityProvider()..start()),
      ],
      child: _EcoFinwizeAppInner(),
    );
  }
}

class _EcoFinwizeAppInner extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: appConfig.appName,
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.light, // TODO: Add dark mode toggle
      home: const AuthGate(),
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(textScaler: const TextScaler.linear(1.0)),
          child: child ?? const SizedBox.shrink(),
        );
      },
      onGenerateRoute: (settings) {
        AppErrorHandler.setCurrentRoute(settings.name);
        return null; // Use default routing
      },
      // Custom error widget for uncaught errors
      errorBuilder: (context, errorDetails) => ErrorFallbackWidget(
        errorDetails: errorDetails,
        onRetry: () {
          // App will restart on next launch
        },
      ),
    );
  }
}

class AuthGate extends StatelessWidget {
  const AuthGate({super.key});

  @override
  Widget build(BuildContext context) {
    final auth = context.watch<AuthProvider>();
    if (auth.loading) return const Scaffold(body: Center(child: CircularProgressIndicator()));
    if (!auth.isLoggedIn) return const LandingScreen();
    return const MainShell();
  }
}

class MainShell extends StatefulWidget {
  const MainShell({super.key});

  @override
  State<MainShell> createState() => _MainShellState();
}

class _MainShellState extends State<MainShell> {
  int _currentIndex = 0;

  static const _screens = [
    AdvisorScreen(),           // Kemi (financial advisor)
    MentorScreen(),            // Chidi (business mentor)
    InvestmentScreen(),        // Musa (investment advisor)
    DashboardScreen(),         // Overview / Home
    LearningScreen(),          // Courses & articles
    BudgetScreen(),            // Finance capability
  ];

  static const _pageNames = [
    'advisor', 'mentor', 'investment', 'dashboard', 'learning', 'budget',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Column(
        children: [
          const OfflineBanner(),
          Expanded(
            child: IndexedStack(index: _currentIndex, children: _screens),
          ),
          AdBanner(pageContext: _pageNames[_currentIndex]),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (i) => setState(() => _currentIndex = i),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.forum_outlined), activeIcon: Icon(Icons.forum), label: 'Kemi'),
          BottomNavigationBarItem(icon: Icon(Icons.business_center_outlined), activeIcon: Icon(Icons.business_center), label: 'Chidi'),
          BottomNavigationBarItem(icon: Icon(Icons.trending_up_outlined), activeIcon: Icon(Icons.trending_up), label: 'Musa'),
          BottomNavigationBarItem(icon: Icon(Icons.dashboard_outlined), activeIcon: Icon(Icons.dashboard), label: 'Home'),
          BottomNavigationBarItem(icon: Icon(Icons.menu_book_outlined), activeIcon: Icon(Icons.menu_book), label: 'Learn'),
          BottomNavigationBarItem(icon: Icon(Icons.account_balance_wallet_outlined), activeIcon: Icon(Icons.account_balance_wallet), label: 'Finance'),
        ],
      ),
    );
  }
}