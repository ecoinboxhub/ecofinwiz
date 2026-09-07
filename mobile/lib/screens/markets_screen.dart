import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class MarketsScreen extends StatefulWidget {
  const MarketsScreen({super.key});

  @override
  State<MarketsScreen> createState() => _MarketsScreenState();
}

class _MarketsScreenState extends State<MarketsScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _data;
  String _category = 'africa';
  bool _loading = true;

  static const _categories = [
    {'key': 'africa', 'label': 'Africa'},
    {'key': 'global', 'label': 'Global'},
    {'key': 'crypto', 'label': 'Crypto'},
    {'key': 'commodities', 'label': 'Commodities'},
  ];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _loading = true);
    try {
      final res = await _api.get('/markets/overview');
      setState(() => _data = res is Map<String, dynamic> ? res : <String, dynamic>{});
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Unable to load market data. Check your connection.')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  List<Map<String, dynamic>> _visibleItems() {
    final data = _data ?? {};
    if (_category == 'crypto') {
      return (data['crypto'] as List? ?? []).cast<Map<String, dynamic>>();
    }
    if (_category == 'commodities') {
      return (data['commodities'] as List? ?? []).cast<Map<String, dynamic>>();
    }
    final regions = (data['regions'] as List? ?? []).cast<Map<String, dynamic>>();
    final match = regions.where((r) => r['region'] == _category).toList();
    if (match.isEmpty) return [];
    return (match.first['indices'] as List? ?? []).cast<Map<String, dynamic>>();
  }

  String _subtitle(Map<String, dynamic> item) {
    if (_category == 'crypto') return (item['name'] ?? '').toString();
    if (_category == 'commodities') return (item['unit'] ?? '').toString();
    return '${item['country'] ?? ''}';
  }

  IconData _categoryIcon() {
    switch (_category) {
      case 'global':
        return Icons.public;
      case 'crypto':
        return Icons.currency_bitcoin;
      case 'commodities':
        return Icons.local_gas_station;
      default:
        return Icons.landscape;
    }
  }

  @override
  Widget build(BuildContext context) {
    final disclaimer = (_data?['disclaimer'] ?? '') as String;
    return Scaffold(
      appBar: AppBar(title: const Text('World Markets')),
      body: RefreshIndicator(
        onRefresh: _load,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                gradient: const LinearGradient(colors: AppColors.goldGradient),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Row(children: [
                const Icon(Icons.show_chart, color: Colors.white, size: 28),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                    const Text('World Markets', style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.bold)),
                    Text(
                      'Indices, crypto and commodities at a glance',
                      style: TextStyle(color: Colors.white.withOpacity(0.9), fontSize: 12),
                    ),
                  ]),
                ),
              ]),
            ),
            const SizedBox(height: 16),
            SizedBox(
              height: 44,
              child: ListView.separated(
                scrollDirection: Axis.horizontal,
                itemCount: _categories.length,
                separatorBuilder: (_, __) => const SizedBox(width: 8),
                itemBuilder: (context, i) {
                  final c = _categories[i];
                  final selected = c['key'] == _category;
                  return GestureDetector(
                    onTap: () => setState(() => _category = c['key']!),
                    child: Container(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      alignment: Alignment.center,
                      decoration: BoxDecoration(
                        color: selected ? AppTheme.primary : Colors.white,
                        borderRadius: BorderRadius.circular(12),
                        border: Border.all(color: selected ? AppTheme.primary : AppTheme.border),
                      ),
                      child: Text(
                        c['label']!,
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.w600,
                          color: selected ? Colors.white : AppTheme.muted,
                        ),
                      ),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            if (_loading)
              const Padding(padding: EdgeInsets.symmetric(vertical: 60), child: Center(child: CircularProgressIndicator()))
            else if (_visibleItems().isEmpty)
              const Padding(padding: EdgeInsets.symmetric(vertical: 60), child: Center(child: Text('No market data available', style: TextStyle(color: AppTheme.softMuted))))
            else ...[
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                decoration: BoxDecoration(color: AppTheme.bg, borderRadius: BorderRadius.circular(10)),
                child: Row(children: [
                  Icon(_categoryIcon(), size: 16, color: AppTheme.ink),
                  const SizedBox(width: 6),
                  Text(
                    _categories.firstWhere((c) => c['key'] == _category)['label']!,
                    style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppTheme.ink),
                  ),
                ]),
              ),
              const SizedBox(height: 12),
              Card(
                child: Padding(
                  padding: const EdgeInsets.symmetric(vertical: 4),
                  child: Column(
                    children: [
                      for (final item in _visibleItems())
                        _MarketRow(
                          symbol: (item['symbol'] ?? '').toString(),
                          name: (item['name'] ?? '').toString(),
                          subtitle: _subtitle(item),
                          currency: (item['currency'] ?? 'USD').toString(),
                          value: (item['value'] ?? 0) as num,
                          change: (item['change'] ?? 0) as num,
                          changePct: (item['change_pct'] ?? 0) as num,
                          isCrypto: _category == 'crypto',
                        ),
                    ],
                  ),
                ),
              ),
            ],
            if (disclaimer.isNotEmpty) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(color: AppTheme.goldSoft, borderRadius: BorderRadius.circular(10)),
                child: Text(
                  disclaimer,
                  style: const TextStyle(fontSize: 11, color: AppTheme.goldDark, height: 1.4),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _MarketRow extends StatelessWidget {
  final String symbol;
  final String name;
  final String subtitle;
  final String currency;
  final num value;
  final num change;
  final num changePct;
  final bool isCrypto;

  const _MarketRow({
    required this.symbol,
    required this.name,
    required this.subtitle,
    required this.currency,
    required this.value,
    required this.change,
    required this.changePct,
    required this.isCrypto,
  });

  String _fmt(num n) {
    final s = n >= 1000 ? n.toStringAsFixed(2).replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',') : n.toStringAsFixed(2);
    if (s.endsWith('.00')) return n.toStringAsFixed(0).replaceAllMapped(RegExp(r'\B(?=(\d{3})+(?!\d))'), (m) => ',');
    return s;
  }

  @override
  Widget build(BuildContext context) {
    final up = changePct >= 0;
    final color = up ? AppTheme.success : AppTheme.error;
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 40,
            height: 40,
            alignment: Alignment.center,
            decoration: BoxDecoration(color: up ? AppTheme.mintSoft : AppTheme.errorSoft, borderRadius: BorderRadius.circular(10)),
            child: Icon(isCrypto ? Icons.currency_bitcoin : Icons.trending_up, size: 20, color: color),
          ),
          const SizedBox(width: 12),
          Expanded(
            child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
              Text(symbol, key: Key('market_row_$symbol'), style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.ink)),
              Text('$name · $subtitle', style: const TextStyle(fontSize: 11, color: AppTheme.softMuted), maxLines: 1, overflow: TextOverflow.ellipsis),
            ]),
          ),
          const SizedBox(width: 8),
          Column(crossAxisAlignment: CrossAxisAlignment.end, children: [
            Text('$currency ${_fmt(value)}', style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.ink)),
            Text('${up ? '+' : ''}${_fmt(change)} (${up ? '+' : ''}${changePct.toStringAsFixed(2)}%)',
                style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: color)),
          ]),
        ],
      ),
    );
  }
}