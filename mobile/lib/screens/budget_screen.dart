import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class BudgetScreen extends StatefulWidget {
  const BudgetScreen({super.key});

  @override
  State<BudgetScreen> createState() => _BudgetScreenState();
}

class _BudgetScreenState extends State<BudgetScreen> {
  final _api = ApiService();
  List<dynamic> _budgets = [];
  bool _loading = true;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await _api.getOffline('/finance/budgets');
      setState(() { _budgets = data is List ? data : (data?['budgets'] ?? []); _loading = false; });
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    final totalBudget = _budgets.fold<double>(0, (s, b) => s + ((b['monthly_limit'] ?? b['amount']) ?? 0).toDouble());
    final totalSpent = _budgets.fold<double>(0, (s, b) => s + (b['spent'] ?? 0).toDouble());
    return Scaffold(
      appBar: AppBar(title: const Text('Budgets')),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Total Budget', style: TextStyle(color: AppTheme.muted)),
                const SizedBox(height: 4),
                Text('₦${totalBudget.toStringAsFixed(0)}', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppTheme.ink)),
                const SizedBox(height: 8),
                ClipRRect(borderRadius: BorderRadius.circular(4), child: LinearProgressIndicator(value: totalBudget > 0 ? (totalSpent / totalBudget).clamp(0, 1) : 0,
                  backgroundColor: AppTheme.border, valueColor: AlwaysStoppedAnimation(totalSpent > totalBudget * 0.9 ? AppTheme.error : AppTheme.primary), minHeight: 8)),
                const SizedBox(height: 4),
                Text('₦${totalSpent.toStringAsFixed(0)} spent of ₦${totalBudget.toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
              ]))),
              const SizedBox(height: 8),
              ..._budgets.map((b) {
                final limit = ((b['monthly_limit'] ?? b['amount']) ?? 0);
                final pct = limit > 0 ? ((b['spent'] ?? 0) / limit).clamp(0, 1) : 0.0;
                return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Row(children: [
                    Container(width: 40, height: 40, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.pie_chart, color: AppTheme.primary, size: 20)),
                    const SizedBox(width: 12),
                    Expanded(child: Text(b['category'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600))),
                  ]),
                  const SizedBox(height: 8),
                  ClipRRect(borderRadius: BorderRadius.circular(4), child: LinearProgressIndicator(value: pct, backgroundColor: AppTheme.border, valueColor: AlwaysStoppedAnimation(pct > 0.9 ? AppTheme.error : AppTheme.primary), minHeight: 6)),
                  const SizedBox(height: 4),
                  Text('₦${(b['spent'] ?? 0).toStringAsFixed(0)} / ₦${limit.toStringAsFixed(0)}', style: const TextStyle(fontSize: 11, color: AppTheme.muted)),
                ])));
              }),
            ])),
    );
  }
}
