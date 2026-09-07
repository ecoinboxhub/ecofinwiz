import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class SavingsScreen extends StatefulWidget {
  const SavingsScreen({super.key});

  @override
  State<SavingsScreen> createState() => _SavingsScreenState();
}

class _SavingsScreenState extends State<SavingsScreen> {
  final _api = ApiService();
  List<dynamic> _goals = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await _api.getOffline('/finance/savings-goals');
      setState(() => _goals = data is List ? data : (data?['goals'] ?? []));
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Savings Goals')),
      body: RefreshIndicator(onRefresh: _load, child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _goals.length, itemBuilder: (_, i) {
        final g = _goals[i];
        final pct = (g['target_amount'] ?? 0) > 0 ? ((g['current_amount'] ?? 0) / (g['target_amount'] ?? 1)).clamp(0, 1) : 0.0;
        return Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Row(children: [
            Container(width: 40, height: 40, decoration: BoxDecoration(color: AppTheme.goldSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.savings, color: AppTheme.gold, size: 20)),
            const SizedBox(width: 12),
            Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(g['name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600)),
            ])),
          ]),
          const SizedBox(height: 12),
          ClipRRect(borderRadius: BorderRadius.circular(4), child: LinearProgressIndicator(value: pct, backgroundColor: AppTheme.border, valueColor: const AlwaysStoppedAnimation(AppTheme.gold), minHeight: 8)),
          const SizedBox(height: 4),
          Row(mainAxisAlignment: MainAxisAlignment.spaceBetween, children: [
            Text('₦${(g['current_amount'] ?? 0).toStringAsFixed(0)} saved', style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
            Text('₦${(g['target_amount'] ?? 0).toStringAsFixed(0)}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
          ]),
        ])));
      })),
    );
  }
}
