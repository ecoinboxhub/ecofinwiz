import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class ArticleDetailScreen extends StatefulWidget {
  final String articleId;
  const ArticleDetailScreen({super.key, required this.articleId});

  @override
  State<ArticleDetailScreen> createState() => _ArticleDetailScreenState();
}

class _ArticleDetailScreenState extends State<ArticleDetailScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _article;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { _article = await _api.get('/articles/${widget.articleId}') as Map<String, dynamic>?; } catch (_) {}
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final a = _article;
    return Scaffold(
      appBar: AppBar(title: const Text('Article')),
      body: a == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Text(a['title'] ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, height: 1.3)),
                const SizedBox(height: 8),
                Row(children: [
                  Text(a['author'] ?? '', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primary)),
                  const SizedBox(width: 8),
                  Text('${a['read_time_minutes'] ?? 0} min read', style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
                ]),
                const SizedBox(height: 8),
                if ((a['tags'] as List?)?.isNotEmpty == true)
                  Wrap(spacing: 8, children: (a['tags'] as List).map((t) => Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                    decoration: BoxDecoration(color: AppTheme.goldSoft, borderRadius: BorderRadius.circular(20)),
                    child: Text('$t', style: const TextStyle(color: AppTheme.goldDark, fontSize: 11, fontWeight: FontWeight.w600)))).toList()),
                const SizedBox(height: 12),
                Text(a['content'] ?? '', style: const TextStyle(fontSize: 14, height: 1.6)),
              ]))),
            ])),
    );
  }
}