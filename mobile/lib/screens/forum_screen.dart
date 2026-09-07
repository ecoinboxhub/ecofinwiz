import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'forum_topic_detail_screen.dart';

class ForumScreen extends StatefulWidget {
  const ForumScreen({super.key});

  @override
  State<ForumScreen> createState() => _ForumScreenState();
}

class _ForumScreenState extends State<ForumScreen> {
  final _api = ApiService();
  List<dynamic> _topics = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/forum/topics'); setState(() => _topics = (data as List?) ?? []); } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Forum')),
      body: RefreshIndicator(onRefresh: _load, child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _topics.length, itemBuilder: (_, i) {
        final t = _topics[i];
        return Card(child: ListTile(
          leading: Container(width: 40, height: 40, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.forum, color: AppTheme.primary, size: 20)),
          title: Row(children: [
            if (t['is_pinned'] == true) const Icon(Icons.push_pin, size: 14, color: AppTheme.primary),
            if (t['is_locked'] == true) const Icon(Icons.lock, size: 14, color: AppTheme.softMuted),
            const SizedBox(width: 4),
            Expanded(child: Text(t['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14))),
          ]),
          subtitle: Text(t['content'] ?? '', maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
          trailing: Text('${t['reply_count'] ?? 0}', style: const TextStyle(color: AppTheme.muted)),
          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ForumTopicDetailScreen(topicId: t['id'].toString()))),
        ));
      })),
    );
  }
}
