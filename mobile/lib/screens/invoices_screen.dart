import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class InvoicesScreen extends StatefulWidget {
  const InvoicesScreen({super.key});

  @override
  State<InvoicesScreen> createState() => _InvoicesScreenState();
}

class _InvoicesScreenState extends State<InvoicesScreen> {
  final _api = ApiService();
  List<dynamic> _invoices = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/invoices'); setState(() => _invoices = (data as List?) ?? []); } catch (_) {}
  }

  String _number(dynamic inv) {
    final n = inv['number'] ?? inv['invoice_number'];
    if (n != null && n.toString().isNotEmpty) return n.toString();
    final id = inv['id']?.toString();
    return id != null && id.length >= 8 ? '#${id.substring(0, 8)}' : '#Invoice';
  }

  String _symbol(dynamic inv) => inv['currency'] == 'USD' ? '\$' : '₦';

  Color _statusColor(String s) => switch (s) { 'paid' => AppTheme.success, 'overdue' => AppTheme.error, 'sent' => AppTheme.primary, _ => AppTheme.gold };

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Invoices')),
      body: RefreshIndicator(onRefresh: _load, child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _invoices.length, itemBuilder: (_, i) {
        final inv = _invoices[i];
        return Card(child: ListTile(
          title: Text(inv['client_name'] ?? 'Invoice', style: const TextStyle(fontWeight: FontWeight.w600)),
          subtitle: Text(_number(inv)),
          trailing: Column(mainAxisAlignment: MainAxisAlignment.center, crossAxisAlignment: CrossAxisAlignment.end, children: [
            Text('${_symbol(inv)}${(inv['total'] ?? inv['total_amount'] ?? inv['amount'] ?? 0).toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15)),
            Chip(label: Text(inv['status'] ?? 'draft', style: const TextStyle(color: Colors.white, fontSize: 10)), backgroundColor: _statusColor(inv['status'] ?? ''), padding: EdgeInsets.zero, visualDensity: VisualDensity.compact, materialTapTargetSize: MaterialTapTargetSize.shrinkWrap, labelPadding: const EdgeInsets.symmetric(horizontal: 6, vertical: 0)),
          ]),
        ));
      })),
    );
  }
}
