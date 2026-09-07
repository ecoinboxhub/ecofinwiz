import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class NotificationsScreen extends StatefulWidget {
  const NotificationsScreen({super.key});

  @override
  State<NotificationsScreen> createState() => _NotificationsScreenState();
}

class _NotificationsScreenState extends State<NotificationsScreen> {
  final _api = ApiService();
  List<dynamic> _notifications = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final data = await _api.get('/users/me/notifications');
      setState(() => _notifications = data is List ? data : (data is Map ? (data['items'] as List? ?? []) : []));
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Notifications'), actions: [
        TextButton(onPressed: () async { await _api.post('/users/me/notifications/read-all'); _load(); }, child: const Text('Mark All Read')),
      ]),
      body: RefreshIndicator(onRefresh: _load, child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _notifications.length, itemBuilder: (_, i) {
        final n = _notifications[i];
        final isRead = n['is_read'] == true;
        return Card(child: ListTile(
          leading: Container(width: 40, height: 40, decoration: BoxDecoration(color: isRead ? AppTheme.border : AppTheme.mintSoft, borderRadius: BorderRadius.circular(10)),
            child: Icon(Icons.notifications, color: isRead ? AppTheme.softMuted : AppTheme.primary, size: 20)),
          title: Text(n['message'] ?? n['title'] ?? '', style: TextStyle(fontWeight: isRead ? FontWeight.normal : FontWeight.w600, fontSize: 14)),
          subtitle: n['created_at'] != null ? Text(n['created_at'].toString().substring(0, 10), style: const TextStyle(fontSize: 11)) : null,
        ));
      })),
    );
  }
}
