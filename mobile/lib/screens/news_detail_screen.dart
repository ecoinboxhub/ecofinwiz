import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class NewsDetailScreen extends StatefulWidget {
  final String newsId;
  const NewsDetailScreen({super.key, required this.newsId});

  @override
  State<NewsDetailScreen> createState() => _NewsDetailScreenState();
}

class _NewsDetailScreenState extends State<NewsDetailScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _news;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { _news = await _api.get('/news/${widget.newsId}') as Map<String, dynamic>?; } catch (_) {}
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    final n = _news;
    return Scaffold(
      appBar: AppBar(title: const Text('News')),
      body: n == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                if (n['is_breaking'] == true) ...[
                  Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: AppTheme.errorSoft, borderRadius: BorderRadius.circular(20)),
                    child: const Text('Breaking', style: TextStyle(color: AppTheme.error, fontSize: 11, fontWeight: FontWeight.w600))),
                  const SizedBox(height: 8),
                ],
                Text(n['title'] ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, height: 1.3)),
                const SizedBox(height: 8),
                Row(children: [
                  Text(n['source'] ?? '', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppTheme.primary)),
                  const SizedBox(width: 8),
                  Text(n['category'] ?? '', style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
                ]),
                const SizedBox(height: 12),
                Text(n['content'] ?? '', style: const TextStyle(fontSize: 14, height: 1.6)),
                if (n['source_url'] != null) ...[
                  const SizedBox(height: 12),
                  Text(n['source_url'].toString(), style: const TextStyle(fontSize: 12, color: AppTheme.primary, decoration: TextDecoration.underline)),
                ],
              ]))),
            ])),
    );
  }
}