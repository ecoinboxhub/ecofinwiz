import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class ForumTopicDetailScreen extends StatefulWidget {
  final String topicId;
  const ForumTopicDetailScreen({super.key, required this.topicId});

  @override
  State<ForumTopicDetailScreen> createState() => _ForumTopicDetailScreenState();
}

class _ForumTopicDetailScreenState extends State<ForumTopicDetailScreen> {
  final _api = ApiService();
  final _replyController = TextEditingController();
  Map<String, dynamic>? _topic;
  bool _sending = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { _topic = await _api.get('/forum/topics/${widget.topicId}') as Map<String, dynamic>?; } catch (_) {}
    if (mounted) setState(() {});
  }

  Future<void> _sendReply() async {
    final text = _replyController.text.trim();
    if (text.isEmpty) return;
    setState(() => _sending = true);
    try { await _api.post('/forum/topics/${widget.topicId}/replies', body: {'content': text}); _replyController.clear(); } catch (_) {}
    if (mounted) setState(() => _sending = false);
    await _load();
  }

  @override
  void dispose() { _replyController.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    final t = _topic;
    return Scaffold(
      appBar: AppBar(title: const Text('Topic')),
      body: t == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  Expanded(child: Text(t['title'] ?? '', style: const TextStyle(fontSize: 17, fontWeight: FontWeight.bold))),
                  if (t['is_pinned'] == true) const Icon(Icons.push_pin, size: 16, color: AppTheme.primary),
                ]),
                const SizedBox(height: 6),
                Text(t['content'] ?? '', style: const TextStyle(fontSize: 14)),
                const SizedBox(height: 8),
                Row(children: [
                  Text(t['author_name'] ?? 'Anonymous', style: const TextStyle(fontSize: 12, color: AppTheme.primary, fontWeight: FontWeight.w600)),
                  const SizedBox(width: 8),
                  Text('${t['reply_count'] ?? 0} replies', style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
                ]),
              ]))),
              const SizedBox(height: 8),
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Replies', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...((t['replies'] as List?) ?? []).map((r) => Padding(padding: const EdgeInsets.only(bottom: 12), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                  Text(r['content'] ?? '', style: const TextStyle(fontSize: 13)),
                  const SizedBox(height: 2),
                  Text(r['author_name'] ?? 'Anonymous', style: const TextStyle(fontSize: 11, color: AppTheme.softMuted)),
                ]))),
                if (((t['replies'] as List?) ?? []).isEmpty)
                  const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Text('No replies yet', style: TextStyle(color: AppTheme.muted))),
              ]))),
              const SizedBox(height: 8),
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(children: [
                TextField(controller: _replyController, minLines: 2, maxLines: 4, decoration: const InputDecoration(labelText: 'Write a reply')),
                const SizedBox(height: 8),
                SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _sending ? null : _sendReply,
                  child: _sending ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Post Reply'))),
              ]))),
            ])),
    );
  }
}