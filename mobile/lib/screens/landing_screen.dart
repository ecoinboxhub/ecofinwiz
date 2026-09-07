import 'package:flutter/material.dart';
import '../config/theme.dart';
import 'login_screen.dart';
import 'register_screen.dart';

class LandingScreen extends StatelessWidget {
  const LandingScreen({super.key});

  void _showHowItWorks(BuildContext context) {
    showDialog<void>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('How EcoFinwize helps'),
        content: const Text(
          'Get personal finance guidance from Kemi, business help from Chidi and investing tips from Musa. Track budgets, savings and goals, learn from short courses, and plan your business - all in one app.',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(dialogContext), child: const Text('Got it')),
          FilledButton(
            onPressed: () {
              Navigator.pop(dialogContext);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen()));
            },
            child: const Text('Get Started'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(child: SingleChildScrollView(padding: const EdgeInsets.all(24), child: Column(children: [
        Row(children: [
          Container(width: 40, height: 40, decoration: const BoxDecoration(gradient: LinearGradient(colors: AppColors.tealMintGradient), borderRadius: BorderRadius.all(Radius.circular(10))),
            child: const Center(child: Text('F', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 20)))),
          const SizedBox(width: 8),
          const Expanded(child: Text('EcoFinwize', overflow: TextOverflow.ellipsis, maxLines: 1, style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.ink))),
          TextButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const LoginScreen())), child: const Text('Log In')),
          const SizedBox(width: 8),
          ElevatedButton(
            style: ElevatedButton.styleFrom(minimumSize: const Size(0, 48), padding: const EdgeInsets.symmetric(horizontal: 14)),
            onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen())),
            child: const Text('Get Started'),
          ),
        ]),
        const SizedBox(height: 60),
        Container(padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6), decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(20)),
          child: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.handshake_outlined, size: 16, color: AppTheme.primary), SizedBox(width: 4), Text('Financial guidance you can trust', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w500, color: AppTheme.primary))])),
        const SizedBox(height: 24),
        Text.rich(TextSpan(text: 'Your ', style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: AppTheme.ink),
          children: [TextSpan(text: 'Financial Future\n', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, foreground: Paint()..shader = const LinearGradient(colors: [AppTheme.primary, AppTheme.mint, AppTheme.gold]).createShader(const Rect.fromLTWH(0, 0, 300, 100)))),
            const TextSpan(text: 'Built for your financial future', style: TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: AppTheme.ink))]), textAlign: TextAlign.center),
        const SizedBox(height: 16),
        const Text('EcoFinwize helps African youths, SMEs, freelancers, and students take control of their finances with guidance you can trust.', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.muted)),
        const SizedBox(height: 32),
        SizedBox(width: double.infinity, child: ElevatedButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const RegisterScreen())), child: const Text('Start Free'))),
        const SizedBox(height: 12),
        SizedBox(width: double.infinity, child: OutlinedButton(onPressed: () => _showHowItWorks(context),
          style: OutlinedButton.styleFrom(minimumSize: const Size(double.infinity, 48), shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12))), child: const Text('See How It Works'))),
      ]))),
    );
  }
}
