import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'invoices_screen.dart';

class BusinessTasksScreen extends StatefulWidget {
  const BusinessTasksScreen({super.key});

  @override
  State<BusinessTasksScreen> createState() => _BusinessTasksScreenState();
}

class _BusinessTasksScreenState extends State<BusinessTasksScreen> {
  final _api = ApiService();
  List<dynamic> _tasks = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/tasks'); setState(() => _tasks = (data as List?) ?? []); } catch (_) {}
  }

  Future<void> _toggleTask(dynamic task) async {
    final taskId = task?['id'];
    if (taskId == null) return;
    final next = task['status'] == 'completed' ? 'in_progress' : 'completed';
    try {
      await _api.patch('/tasks/$taskId', body: {'status': next});
      setState(() {
        final idx = _tasks.indexWhere((x) => x is Map && x['id'] == taskId);
        if (idx != -1 && _tasks[idx] is Map) {
          _tasks[idx] = <String, dynamic>{...(_tasks[idx] as Map<String, dynamic>), 'status': next};
        }
      });
    } catch (_) {
      _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Business Tools')),
      body: RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
        Row(children: [
          Expanded(child: Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [const Icon(Icons.assignment, color: AppTheme.gold, size: 32), const SizedBox(height: 4), Text('${_tasks.length} Tasks', style: const TextStyle(fontWeight: FontWeight.w600))])))),
          const SizedBox(width: 12),
          Expanded(child: GestureDetector(onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const InvoicesScreen())), child: const Card(child: Padding(padding: EdgeInsets.all(16), child: Column(children: [Icon(Icons.receipt, color: AppTheme.primary, size: 32), SizedBox(height: 4), Text('Invoices', style: TextStyle(fontWeight: FontWeight.w600))]))))),
        ]),
        const SizedBox(height: 16),
        ..._tasks.map((t) => Card(child: CheckboxListTile(
          value: t['status'] == 'completed', onChanged: (_) => _toggleTask(t),
          title: Text(t['title'] ?? '', style: TextStyle(fontWeight: FontWeight.w500, decoration: t['status'] == 'completed' ? TextDecoration.lineThrough : null)),
          secondary: Icon(t['priority'] == 'high' ? Icons.flag : Icons.flag_outlined, color: t['priority'] == 'high' ? AppTheme.error : t['priority'] == 'medium' ? AppTheme.gold : AppTheme.primary),
        ))),
      ])),
    );
  }
}
