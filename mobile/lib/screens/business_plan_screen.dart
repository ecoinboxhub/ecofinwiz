import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class BusinessPlanScreen extends StatefulWidget {
  const BusinessPlanScreen({super.key});

  @override
  State<BusinessPlanScreen> createState() => _BusinessPlanScreenState();
}

class _BusinessPlanScreenState extends State<BusinessPlanScreen> {
  final _api = ApiService();
  final _nameController = TextEditingController();
  final _industryController = TextEditingController();
  final _descriptionController = TextEditingController();
  Map<String, dynamic>? _plan;
  bool _loading = false;

  Future<void> _generate() async {
    final name = _nameController.text.trim();
    final industry = _industryController.text.trim();
    final description = _descriptionController.text.trim();
    if (name.isEmpty || industry.isEmpty || description.isEmpty) return;
    setState(() => _loading = true);
    try {
      final data = await _api.post('/business-plans/generate', body: {
        'business_name': name,
        'industry': industry,
        'description': description,
        'target_market': '',
        'revenue_model': '',
      });
      setState(() => _plan = data is Map ? data.cast<String, dynamic>() : null);
    } catch (_) {}
    setState(() => _loading = false);
  }

  String? get _summary {
    final content = _plan?['content'];
    if (content is Map) return content['executive_summary'] as String?;
    return _plan?['executive_summary'] as String?;
  }

  @override
  void dispose() {
    _nameController.dispose();
    _industryController.dispose();
    _descriptionController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Business Plan Generator')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Card(child: Padding(padding: EdgeInsets.all(16), child: Column(children: [Icon(Icons.description_outlined, color: AppTheme.gold, size: 40), SizedBox(height: 8), Text('Describe your business and get a detailed plan ready for your bank', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.muted))]))),
        const SizedBox(height: 16),
        TextField(controller: _nameController, decoration: const InputDecoration(labelText: 'Business name', hintText: 'e.g. AgroFresh Logistics', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        TextField(controller: _industryController, decoration: const InputDecoration(labelText: 'Industry', hintText: 'e.g. Logistics', border: OutlineInputBorder())),
        const SizedBox(height: 12),
        TextField(controller: _descriptionController, decoration: const InputDecoration(labelText: 'Describe your business idea', hintText: 'What does your business do?', border: OutlineInputBorder()), maxLines: 4),
        const SizedBox(height: 16),
        ElevatedButton(onPressed: _generate, child: _loading ? const CircularProgressIndicator(color: Colors.white) : const Text('Generate Plan')),
        if (_plan != null) ...[
          const SizedBox(height: 16),
          Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(_plan!['title'] ?? _plan!['business_name'] ?? _plan!['name'] ?? 'Business Plan', style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            if (_summary != null) Text(_summary!, style: const TextStyle(color: AppTheme.muted)),
          ]))),
        ],
      ]),
    );
  }
}
