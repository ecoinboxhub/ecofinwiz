import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import '../widgets/ad_banner.dart';
import 'notifications_screen.dart';
import 'admin_screen.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _stats;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/users/me/progress').catchError((_) => <String, dynamic>{}); setState(() => _stats = data as Map<String, dynamic>?); } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final auth = context.read<AuthProvider>();
    final user = auth.user;
    final plan = auth.plan;
    final lessonsCompleted = _stats?['lessons_completed'] ?? 0;
    final badges = _stats?['badges'] is List ? (_stats?['badges'] as List).length : (_stats?['badges'] ?? 0);
    final activeGoals = _stats?['active_goals'] ?? 0;
    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        Center(child: Column(children: [
          CircleAvatar(radius: 40, backgroundColor: AppTheme.mintSoft, child: Text(user?['full_name']?.toString().substring(0, 1).toUpperCase() ?? 'U', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppTheme.primary))),
          const SizedBox(height: 12),
          Text(user?['full_name'] ?? 'User', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
          Text(user?['email'] ?? '', style: const TextStyle(color: AppTheme.muted)),
          Row(mainAxisAlignment: MainAxisAlignment.center, children: [
            if (user?['is_admin'] == true)
              const Padding(
                padding: EdgeInsets.only(right: 4),
                child: Chip(label: Text('Admin', style: TextStyle(color: Colors.white, fontSize: 12)), backgroundColor: AppTheme.primary, padding: EdgeInsets.zero),
              ),
            GestureDetector(
              onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PricingScreen())),
              child: Chip(
                label: Row(mainAxisSize: MainAxisSize.min, children: [
                  Icon(plan == 'free' ? Icons.star : Icons.workspace_premium, size: 12, color: Colors.white),
                  const SizedBox(width: 4),
                  Text(plan == 'free' ? 'Free Plan' : plan == 'pro' ? 'Pro Plan' : 'Business Plan',
                    style: const TextStyle(color: Colors.white, fontSize: 12)),
                ]),
                backgroundColor: plan == 'free' ? AppTheme.softMuted : AppTheme.primary,
                padding: EdgeInsets.zero,
              ),
            ),
          ]),
        ])),
        const SizedBox(height: 24),
        Row(children: [
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('$lessonsCompleted', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.primary)), const Text('Lessons', style: TextStyle(fontSize: 12, color: AppTheme.muted))])))),
          const SizedBox(width: 8),
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('$badges', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.gold)), const Text('Badges', style: TextStyle(fontSize: 12, color: AppTheme.muted))])))),
          const SizedBox(width: 8),
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('$activeGoals', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.mint)), const Text('Goals', style: TextStyle(fontSize: 12, color: AppTheme.muted))])))),
        ]),
        const SizedBox(height: 16),
        ListTile(leading: const Icon(Icons.workspace_premium, color: AppTheme.primary), title: const Text('Upgrade Plan', style: TextStyle(color: AppTheme.primary)), trailing: const Icon(Icons.chevron_right), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const PricingScreen()))),
        ListTile(leading: const Icon(Icons.notifications_outlined), title: const Text('Notifications'), trailing: const Icon(Icons.chevron_right), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NotificationsScreen()))),
        if (user?['is_admin'] == true) ListTile(leading: const Icon(Icons.admin_panel_settings, color: AppTheme.primary), title: const Text('Admin Dashboard', style: TextStyle(color: AppTheme.primary)), trailing: const Icon(Icons.chevron_right), onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminScreen()))),
        const Divider(),
        ListTile(leading: const Icon(Icons.logout, color: AppTheme.error), title: const Text('Sign Out', style: TextStyle(color: AppTheme.error)), onTap: () { auth.logout(); Navigator.popUntil(context, (route) => route.isFirst); }),
      ]),
    );
  }
}
