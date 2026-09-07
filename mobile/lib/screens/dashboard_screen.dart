import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../providers/connectivity_provider.dart';
import '../services/api_service.dart';
import 'transactions_screen.dart';
import 'savings_screen.dart';
import 'advisor_screen.dart';
import 'notifications_screen.dart';
import 'profile_screen.dart';
import 'calculators_screen.dart';
import 'markets_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _data;
  bool _offline = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    final online = context.read<ConnectivityProvider>().isOnline;
    try {
      final budgetsRes = await _api.getOffline('/finance/budgets');
      await _api.getOffline('/finance/transactions?limit=5');
      final savingsRes = await _api.getOffline('/finance/savings-goals');
      final tip = await _api.getOffline('/intelligence/tips/daily');
      final bRaw = budgetsRes is Map ? (budgetsRes['budgets'] ?? budgetsRes['data']) : budgetsRes;
      final budgetList = bRaw is List ? bRaw : <dynamic>[];
      final totalBudget = budgetList.fold<double>(0, (s, b) => s + ((b['monthly_limit'] ?? b['amount'] ?? b['total_budget']) ?? 0).toDouble());
      final totalSpent = budgetList.fold<double>(0, (s, b) => s + (b['spent'] ?? 0).toDouble());
      final sRaw = savingsRes is Map ? (savingsRes['goals'] ?? savingsRes['data']) : savingsRes;
      final savingsList = sRaw is List ? sRaw : <dynamic>[];
      final totalGoal = savingsList.fold<double>(0, (s, g) => s + (g['target_amount'] ?? 0).toDouble());
      final totalSaved = savingsList.fold<double>(0, (s, g) => s + (g['current_amount'] ?? 0).toDouble());
      final budget = <String, dynamic>{'total_budget': totalBudget, 'total_spent': totalSpent, 'remaining': totalBudget - totalSpent, 'budget_count': budgetList.length};
      final savings = <String, dynamic>{'total_goal': totalGoal, 'total_saved': totalSaved, 'goal_count': savingsList.length};
      if (mounted) setState(() { _data = {'budget': budget, 'savings': savings, 'tip': tip is Map ? tip : {}}; _offline = !online; });
    } catch (_) {
      if (mounted) setState(() => _offline = !online);
    }
  }

  @override
  Widget build(BuildContext context) {
    final name = context.watch<AuthProvider>().user?['full_name']?.toString().split(' ').first ?? 'User';
    final budget = _data?['budget'] as Map<String, dynamic>? ?? {};
    final savings = _data?['savings'] as Map<String, dynamic>? ?? {};
    final tip = _data?['tip'] as Map<String, dynamic>? ?? {};
    final totalBudget = (budget['total_budget'] ?? 0).toDouble();
    final totalSpent = (budget['total_spent'] ?? 0).toDouble();
    final totalGoal = (savings['total_goal'] ?? 0).toDouble();
    final totalSaved = (savings['total_saved'] ?? 0).toDouble();
    final hasData = ((budget['budget_count'] ?? 0) as num) > 0 || ((savings['goal_count'] ?? 0) as num) > 0;

    return Scaffold(
      appBar: AppBar(title: Text('Hi, $name!'), actions: [
        IconButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NotificationsScreen())), icon: const Icon(Icons.notifications_outlined)),
        IconButton(onPressed: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ProfileScreen())), icon: const Icon(Icons.person_outline)),
      ]),
      body: RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
        if (tip['tip'] != null)
          Container(padding: const EdgeInsets.all(16), margin: const EdgeInsets.only(bottom: 16), decoration: BoxDecoration(gradient: const LinearGradient(colors: AppColors.tealMintGradient), borderRadius: BorderRadius.circular(16)),
            child: Row(children: [const Icon(Icons.lightbulb_outline, color: Colors.white, size: 20), const SizedBox(width: 8), Expanded(child: Text(tip['tip'] ?? '', style: const TextStyle(color: Colors.white, fontSize: 13)))])),
        Row(children: [
          Expanded(child: _SummaryCard(title: 'Budget', amount: totalBudget - totalSpent, total: totalBudget, color: AppTheme.primary)),
          const SizedBox(width: 12),
          Expanded(child: _SummaryCard(title: 'Savings', amount: totalSaved, total: totalGoal, color: AppTheme.gold)),
        ]),
        if (_offline && !hasData) ...[
          const SizedBox(height: 16),
          Container(padding: const EdgeInsets.all(16), decoration: const BoxDecoration(color: AppTheme.goldSoft, borderRadius: BorderRadius.all(Radius.circular(16))),
            child: const Row(children: [
              Icon(Icons.cloud_off_outlined, size: 20, color: AppTheme.goldDark),
              SizedBox(width: 10),
              Expanded(child: Text("You're offline and there's no saved data yet - reconnect to see your finances.", style: TextStyle(fontSize: 13, color: AppTheme.goldDark, height: 1.4))),
            ])),
        ],
        const SizedBox(height: 24),
        const Text('Quick Actions', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.ink)),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: _ActionChip(key: const Key('quick_action_transactions'), icon: Icons.compare_arrows, label: 'Transactions', color: AppTheme.primary, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const TransactionsScreen())))),
          const SizedBox(width: 8),
          Expanded(child: _ActionChip(key: const Key('quick_action_savings'), icon: Icons.savings, label: 'Savings', color: AppTheme.gold, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const SavingsScreen())))),
          const SizedBox(width: 8),
          Expanded(child: _ActionChip(key: const Key('quick_action_kemi'), icon: Icons.forum_outlined, label: 'Kemi', color: AppTheme.mint, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const AdvisorScreen())))),
        ]),
        const SizedBox(height: 12),
        Row(children: [
          Expanded(child: _ActionChip(key: const Key('quick_action_calculators'), icon: Icons.calculate_outlined, label: 'Calculators', color: AppTheme.primary, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CalculatorsScreen())))),
          const SizedBox(width: 8),
          Expanded(child: _ActionChip(key: const Key('quick_action_markets'), icon: Icons.show_chart, label: 'Markets', color: AppTheme.gold, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const MarketsScreen())))),
        ]),
      ])),
    );
  }
}

class _SummaryCard extends StatelessWidget {
  final String title; final double amount, total; final Color color;
  const _SummaryCard({required this.title, required this.amount, required this.total, required this.color});

  @override
  Widget build(BuildContext context) {
    final pct = total > 0 ? amount / total : 0.0;
    return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text(title, style: const TextStyle(color: AppTheme.muted, fontSize: 12)),
      const SizedBox(height: 4),
      Text('₦${amount.toStringAsFixed(0)}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.ink)),
      Text('of ₦${total.toStringAsFixed(0)}', style: const TextStyle(fontSize: 11, color: AppTheme.softMuted)),
      const SizedBox(height: 8),
      ClipRRect(borderRadius: BorderRadius.circular(4), child: LinearProgressIndicator(value: pct.clamp(0, 1), backgroundColor: AppTheme.border, valueColor: AlwaysStoppedAnimation(color), minHeight: 6)),
    ])));
  }
}

class _ActionChip extends StatelessWidget {
  final IconData icon; final String label; final Color color; final VoidCallback onTap;
  const _ActionChip({super.key, required this.icon, required this.label, required this.color, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return GestureDetector(onTap: onTap, child: Container(
      padding: const EdgeInsets.symmetric(vertical: 16), decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)),
      child: Column(children: [Icon(icon, color: color, size: 24), const SizedBox(height: 4), Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w500))]),
    ));
  }
}
