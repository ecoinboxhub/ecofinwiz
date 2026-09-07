import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class AdminScreen extends StatefulWidget {
  const AdminScreen({super.key});

  @override
  State<AdminScreen> createState() => _AdminScreenState();
}

class _AdminScreenState extends State<AdminScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _stats;
  List<dynamic> _users = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    Map<String, dynamic>? stats;
    List<dynamic> users = [];
    try {
      final s = await _api.get('/admin/stats');
      if (s is Map) stats = s.cast<String, dynamic>();
    } catch (_) {}
    try {
      final u = await _api.get('/admin/users');
      if (u is List) {
        users = u;
      } else if (u is Map) {
        users = u['items'] as List? ?? [];
      }
    } catch (_) {}
    setState(() { _stats = stats; _users = users; });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Admin Dashboard')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        if (_stats != null) ...[
          Row(children: [
            Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('${_stats!['total_users'] ?? 0}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.primary)), const Text('Users', style: TextStyle(fontSize: 12))])))),
            const SizedBox(width: 8),
            Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [Text('${_stats!['total_transactions'] ?? 0}', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppTheme.gold)), const Text('Transactions', style: TextStyle(fontSize: 12))])))),
          ]),
          const SizedBox(height: 16),
        ],
        const Text('Users', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        ..._users.take(20).map((u) => ListTile(
          leading: CircleAvatar(backgroundColor: AppTheme.mintSoft, child: Text(u['full_name']?.toString().substring(0, 1) ?? 'U', style: const TextStyle(color: AppTheme.primary, fontWeight: FontWeight.bold))),
          title: Text(u['full_name'] ?? '', style: const TextStyle(fontWeight: FontWeight.w500, fontSize: 14)),
          subtitle: Text(u['email'] ?? '', style: const TextStyle(fontSize: 12)),
          trailing: Row(mainAxisSize: MainAxisSize.min, children: [
            if (u['is_admin'] == true) const Chip(label: Text('Admin', style: TextStyle(color: Colors.white, fontSize: 10)), backgroundColor: AppTheme.primary, padding: EdgeInsets.zero, materialTapTargetSize: MaterialTapTargetSize.shrinkWrap),
            const SizedBox(width: 4),
            if (u['is_active'] == true) const Chip(label: Text('Active', style: TextStyle(color: Colors.white, fontSize: 10)), backgroundColor: AppTheme.success, padding: EdgeInsets.zero, materialTapTargetSize: MaterialTapTargetSize.shrinkWrap),
          ]),
        )),
      ]),
    );
  }
}
