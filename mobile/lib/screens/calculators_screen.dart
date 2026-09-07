import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class _CalculatorDef {
  final String key;
  final String name;
  final IconData icon;
  final String endpoint;
  final List<_FieldDef> fields;

  const _CalculatorDef({
    required this.key,
    required this.name,
    required this.icon,
    required this.endpoint,
    required this.fields,
  });
}

class _FieldDef {
  final String key;
  final String label;
  final TextInputType keyboard;
  final String? hint;

  const _FieldDef({
    required this.key,
    required this.label,
    required this.keyboard,
    this.hint,
  });
}

const _calculators = [
  _CalculatorDef(
    key: 'mortgage', name: 'Mortgage', icon: Icons.home_work_outlined,
    endpoint: '/calculators/mortgage',
    fields: [
      _FieldDef(key: 'principal', label: 'Loan amount', keyboard: TextInputType.number),
      _FieldDef(key: 'annual_rate_pct', label: 'Annual interest rate (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'term_years', label: 'Term (years)', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'investment', name: 'Stock / Investment', icon: Icons.show_chart,
    endpoint: '/calculators/investment',
    fields: [
      _FieldDef(key: 'principal', label: 'Initial investment', keyboard: TextInputType.number),
      _FieldDef(key: 'annual_rate_pct', label: 'Expected annual return (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'years', label: 'Years held', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'mutual_fund', name: 'Mutual Fund', icon: Icons.savings_outlined,
    endpoint: '/calculators/mutual-fund',
    fields: [
      _FieldDef(key: 'initial_lump_sum', label: 'Lump sum', keyboard: TextInputType.number, hint: '0'),
      _FieldDef(key: 'monthly_contribution', label: 'Monthly contribution (SIP)', keyboard: TextInputType.number, hint: '0'),
      _FieldDef(key: 'annual_rate_pct', label: 'Annual return (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'years', label: 'Years', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'bond', name: 'Bond Yield', icon: Icons.account_balance_outlined,
    endpoint: '/calculators/bond',
    fields: [
      _FieldDef(key: 'face_value', label: 'Face value', keyboard: TextInputType.number),
      _FieldDef(key: 'coupon_rate_pct', label: 'Coupon rate (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'price', label: 'Market price', keyboard: TextInputType.number),
      _FieldDef(key: 'years_to_maturity', label: 'Years to maturity', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'treasury_bill', name: 'Treasury Bill', icon: Icons.receipt_outlined,
    endpoint: '/calculators/treasury-bill',
    fields: [
      _FieldDef(key: 'face_value', label: 'Face value', keyboard: TextInputType.number),
      _FieldDef(key: 'price', label: 'Purchase price', keyboard: TextInputType.number),
      _FieldDef(key: 'days', label: 'Tenor (91 / 182 / 364)', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'commercial_paper', name: 'Commercial Paper', icon: Icons.description_outlined,
    endpoint: '/calculators/commercial-paper',
    fields: [
      _FieldDef(key: 'face_value', label: 'Face value', keyboard: TextInputType.number),
      _FieldDef(key: 'discount_rate_pct', label: 'Discount rate (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'days', label: 'Tenor (days)', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'real_estate', name: 'Real Estate', icon: Icons.house_outlined,
    endpoint: '/calculators/real-estate',
    fields: [
      _FieldDef(key: 'property_value', label: 'Property value', keyboard: TextInputType.number),
      _FieldDef(key: 'annual_rent', label: 'Annual rent', keyboard: TextInputType.number),
      _FieldDef(key: 'annual_expenses', label: 'Annual expenses', keyboard: TextInputType.number, hint: '0'),
      _FieldDef(key: 'down_payment', label: 'Down payment', keyboard: TextInputType.number),
    ],
  ),
  _CalculatorDef(
    key: 'compound_interest', name: 'Goal Projection', icon: Icons.trending_up,
    endpoint: '/calculators/compound-interest',
    fields: [
      _FieldDef(key: 'principal', label: 'Starting amount', keyboard: TextInputType.number, hint: '0'),
      _FieldDef(key: 'monthly_contribution', label: 'Monthly contribution', keyboard: TextInputType.number),
      _FieldDef(key: 'annual_rate_pct', label: 'Annual return (%)', keyboard: TextInputType.numberWithOptions(decimal: true)),
      _FieldDef(key: 'years', label: 'Years', keyboard: TextInputType.number),
    ],
  ),
];

class CalculatorsScreen extends StatefulWidget {
  const CalculatorsScreen({super.key});

  @override
  State<CalculatorsScreen> createState() => _CalculatorsScreenState();
}

class _CalculatorsScreenState extends State<CalculatorsScreen> {
  final _api = ApiService();
  final _controllers = <String, TextEditingController>{};
  _CalculatorDef _active = _calculators.first;
  Map<String, dynamic>? _result;
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _initControllers();
  }

  void _initControllers() {
    for (final c in _calculators) {
      for (final f in c.fields) {
        _controllers[f.key] ??= TextEditingController();
      }
    }
  }

  void _switch(_CalculatorDef calc) {
    setState(() {
      _active = calc;
      _result = null;
    });
  }

  String _fmt(num? n) {
    if (n == null) return '-';
    final s = n.toStringAsFixed(2);
    if (s.endsWith('.00')) return n.toStringAsFixed(0);
    return s;
  }

  bool _isMoney(String key) {
    return RegExp(r'payment|total|interest|value|coupon|income|profit|price|principal|investment|invested|contributions|growth_amount').hasMatch(key);
  }

  Future<void> _calculate() async {
    final body = <String, dynamic>{};
    for (final f in _active.fields) {
      final raw = _controllers[f.key]!.text.trim();
      if (raw.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Please fill ${f.label.toLowerCase()}')));
        return;
      }
      body[f.key] = double.tryParse(raw) ?? 0;
    }
    setState(() => _loading = true);
    try {
      final res = await _api.post(_active.endpoint, body: body);
      setState(() => _result = res);
    } catch (_) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('Calculation failed. Check your inputs.')));
      }
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Calculators')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          SizedBox(
            height: 44,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: _calculators.length,
              separatorBuilder: (_, __) => const SizedBox(width: 8),
              itemBuilder: (context, i) {
                final c = _calculators[i];
                final selected = c.key == _active.key;
                return GestureDetector(
                  onTap: () => _switch(c),
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 14),
                    alignment: Alignment.center,
                    decoration: BoxDecoration(
                      color: selected ? AppTheme.primary : Colors.white,
                      borderRadius: BorderRadius.circular(12),
                      border: Border.all(color: selected ? AppTheme.primary : AppTheme.border),
                    ),
                    child: Text(
                      c.name,
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
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(children: [
                    Icon(_active.icon, color: AppTheme.primary, size: 20),
                    const SizedBox(width: 8),
                    Text(_active.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.ink)),
                  ]),
                  const SizedBox(height: 16),
                  for (final f in _active.fields) ...[
                    Text(f.label, style: const TextStyle(fontSize: 12, color: AppTheme.muted)),
                    const SizedBox(height: 4),
                    TextField(
                      controller: _controllers[f.key],
                      keyboardType: f.keyboard,
                      decoration: InputDecoration(
                        hintText: f.hint,
                        isDense: true,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
                      ),
                    ),
                    const SizedBox(height: 12),
                  ],
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton(
                      onPressed: _loading ? null : _calculate,
                      style: ElevatedButton.styleFrom(backgroundColor: AppTheme.primary, foregroundColor: Colors.white),
                      child: Text(_loading ? 'Calculating...' : 'Calculate'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (_result != null) ...[
            const SizedBox(height: 16),
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Results', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.ink)),
                    const SizedBox(height: 8),
                    for (final e in _result!.entries)
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 6),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(e.key.replaceAll('_', ' '), style: const TextStyle(fontSize: 13, color: AppTheme.muted)),
                            Text(
                              '${_isMoney(e.key) ? '₦' : ''}${_fmt((e.value as num?) ?? 0)}${_isMoney(e.key) ? '' : '%'}',
                              style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppTheme.ink),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }

  @override
  void dispose() {
    for (final c in _controllers.values) {
      c.dispose();
    }
    super.dispose();
  }
}