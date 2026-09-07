import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'article_detail_screen.dart';

class ArticlesScreen extends StatefulWidget {
  const ArticlesScreen({super.key});

  @override
  State<ArticlesScreen> createState() => _ArticlesScreenState();
}

class _ArticlesScreenState extends State<ArticlesScreen> {
  final _api = ApiService();
  List<dynamic> _articles = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/articles'); setState(() => _articles = (data as List?) ?? []); } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Articles')),
      body: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _articles.length, itemBuilder: (_, i) {
        final a = _articles[i];
        return Card(child: ListTile(
          leading: Container(width: 40, height: 40, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.article, color: AppTheme.primary, size: 20)),
          title: Text(a['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
          subtitle: Text(a['summary'] ?? (a['content'] ?? '').toString(), maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
          trailing: const Icon(Icons.chevron_right),
          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => ArticleDetailScreen(articleId: a['id'] ?? ''))),
        ));
      }),
    );
  }
}
