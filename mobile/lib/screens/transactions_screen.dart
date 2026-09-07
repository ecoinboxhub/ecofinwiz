import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class TransactionsScreen extends StatefulWidget {
  const TransactionsScreen({super.key});

  @override
  State<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends State<TransactionsScreen> {
  final _api = ApiService();
  List<dynamic> _txns = [];
  bool _loading = true;
  String _filter = 'all';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final params = <String, String>{'limit': '50'};
      if (_filter != 'all') params['type'] = _filter;
      final data = await _api.getOffline('/finance/transactions', params: params);
      setState(() { _txns = data is List ? data : (data?['transactions'] ?? []); _loading = false; });
    } catch (_) { setState(() => _loading = false); }
  }

  @override
  Widget build(BuildContext context) {
    final income = _txns.fold<double>(0, (s, t) => s + (t['type'] == 'income' ? (t['amount'] ?? 0).toDouble() : 0));
    final expense = _txns.fold<double>(0, (s, t) => s + (t['type'] == 'expense' ? (t['amount'] ?? 0).toDouble() : 0));
    return Scaffold(
      appBar: AppBar(title: const Text('Transactions')),
      body: _loading ? const Center(child: CircularProgressIndicator()) : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
        Row(children: [
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [const Text('Income', style: TextStyle(color: AppTheme.success, fontSize: 12)), Text('+₦${income.toStringAsFixed(0)}', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.success))])))),
          const SizedBox(width: 12),
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [const Text('Expenses', style: TextStyle(color: AppTheme.error, fontSize: 12)), Text('-₦${expense.toStringAsFixed(0)}', style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppTheme.error))])))),
        ]),
        const SizedBox(height: 16),
        SingleChildScrollView(scrollDirection: Axis.horizontal, child: Row(children: ['all', 'income', 'expense'].map((f) => Padding(padding: const EdgeInsets.only(right: 8), child: ChoiceChip(label: Text(f[0].toUpperCase() + f.substring(1)), selected: _filter == f, onSelected: (_) => setState(() { _filter = f; _load(); })))).toList())),
        const SizedBox(height: 8),
        ..._txns.map((t) => Card(child: ListTile(
          leading: CircleAvatar(backgroundColor: t['type'] == 'income' ? AppTheme.mintSoft : AppTheme.errorSoft, child: Icon(t['type'] == 'income' ? Icons.arrow_upward : Icons.arrow_downward, color: t['type'] == 'income' ? AppTheme.success : AppTheme.error, size: 20)),
          title: Text(t['description'] ?? t['category'] ?? t['category_name'] ?? 'Transaction', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w500)),
          subtitle: Text('${t['category'] ?? t['category_name'] ?? ''}  \u2022  ${t['date'] ?? t['created_at'] ?? ''}', style: const TextStyle(fontSize: 11)),
          trailing: Text('${t['type'] == 'income' ? '+' : '-'}₦${(t['amount'] ?? 0).toStringAsFixed(0)}', style: TextStyle(fontWeight: FontWeight.bold, color: t['type'] == 'income' ? AppTheme.success : AppTheme.error)),
        ))),
      ])),
    );
  }
}
