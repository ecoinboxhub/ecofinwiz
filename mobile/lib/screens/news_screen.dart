import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'news_detail_screen.dart';

class NewsScreen extends StatefulWidget {
  const NewsScreen({super.key});

  @override
  State<NewsScreen> createState() => _NewsScreenState();
}

class _NewsScreenState extends State<NewsScreen> {
  final _api = ApiService();
  List<dynamic> _news = [];
  String _category = 'all';

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try {
      final params = _category != 'all' ? {'category': _category} : null;
      final data = await _api.get('/news', params: params); setState(() => _news = (data as List?) ?? []);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    const cats = ['all', 'financial', 'business', 'economy', 'startups'];
    return Scaffold(
      appBar: AppBar(title: const Text('Financial News')),
      body: Column(children: [
        SizedBox(height: 48, child: ListView(scrollDirection: Axis.horizontal, padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8), children: cats.map((c) => Padding(padding: const EdgeInsets.only(right: 8), child: ChoiceChip(label: Text(c[0].toUpperCase() + c.substring(1)), selected: _category == c, onSelected: (_) => setState(() { _category = c; _load(); })))).toList())),
        Expanded(child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _news.length, itemBuilder: (_, i) {
          final n = _news[i];
          return Card(child: ListTile(
            leading: Container(width: 40, height: 40, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.newspaper, color: AppTheme.mint, size: 20)),
            title: Text(n['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
            subtitle: Text(n['summary'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
            trailing: n['is_breaking'] == true ? const Icon(Icons.trending_up, color: AppTheme.error, size: 18) : const Icon(Icons.chevron_right),
            onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => NewsDetailScreen(newsId: n['id'] ?? ''))),
          ));
        })),
      ]),
    );
  }
}
