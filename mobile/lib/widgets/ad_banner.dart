import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../config/theme.dart';
import '../providers/auth_provider.dart';
import '../services/api_service.dart';
import 'package:url_launcher/url_launcher.dart';

class AdBanner extends StatefulWidget {
  final String pageContext;
  const AdBanner({super.key, required this.pageContext});

  @override
  State<AdBanner> createState() => _AdBannerState();
}

class _AdBannerState extends State<AdBanner> {
  Map<String, dynamic>? _ad;
  final _api = ApiService();

  @override
  void initState() {
    super.initState();
    _loadAd();
  }

  Future<void> _loadAd() async {
    if (context.read<AuthProvider>().plan != 'free') return;
    try {
      final data = await _api.get('/ads/${widget.pageContext}');
      if (data is List && data.isNotEmpty) {
        if (mounted) setState(() => _ad = data[0] as Map<String, dynamic>);
      }
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    if (context.watch<AuthProvider>().plan != 'free') return const SizedBox.shrink();

    if (_ad == null) {
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        child: InkWell(
          onTap: () => Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => const PricingScreen()),
          ),
          child: Container(
            padding: const EdgeInsets.all(10),
            decoration: BoxDecoration(
              border: Border.all(color: AppTheme.border),
              borderRadius: BorderRadius.circular(10),
              color: AppTheme.bg,
            ),
            child: const Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.workspace_premium, size: 14, color: AppTheme.primary),
                SizedBox(width: 6),
                Text('Upgrade to Pro for ad-free', style: TextStyle(fontSize: 12, color: AppTheme.softMuted)),
              ],
            ),
          ),
        ),
      );
    }

    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
      child: InkWell(
        onTap: () async {
          await _api.post('/ads/impression', body: {'campaign_id': _ad!['id']});
          final uri = Uri.tryParse(_ad!['target_url'] ?? '');
          if (uri != null) await launchUrl(uri, mode: LaunchMode.externalApplication);
        },
        child: Container(
          padding: const EdgeInsets.all(10),
          decoration: BoxDecoration(
            gradient: const LinearGradient(colors: [AppTheme.mintSoft, Colors.white]),
            borderRadius: BorderRadius.circular(10),
            border: Border.all(color: AppTheme.border),
          ),
          child: Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Container(width: 6, height: 6, decoration: const BoxDecoration(shape: BoxShape.circle, color: AppTheme.primary)),
                        const SizedBox(width: 4),
                        Text('Sponsored by ${_ad!['sponsor_name'] ?? ''}',
                          style: const TextStyle(fontSize: 10, color: AppTheme.softMuted)),
                      ],
                    ),
                    if (_ad!['image_url'] != null)
                      Padding(
                        padding: const EdgeInsets.only(top: 4),
                        child: Image.network(_ad!['image_url'], height: 30, fit: BoxFit.contain),
                      ),
                  ],
                ),
              ),
              const Icon(Icons.open_in_new, size: 14, color: AppTheme.border),
            ],
          ),
        ),
      ),
    );
  }
}

class PricingScreen extends StatefulWidget {
  const PricingScreen({super.key});

  @override
  State<PricingScreen> createState() => _PricingScreenState();
}

class _PricingScreenState extends State<PricingScreen> {
  final _api = ApiService();
  List<dynamic>? _plans;
  bool _upgrading = false;
  String? _message;

  @override
  void initState() {
    super.initState();
    _loadPlans();
  }

  Future<void> _loadPlans() async {
    try {
      final data = await _api.get('/subscriptions/plans');
      if (mounted) setState(() => _plans = data as List<dynamic>);
    } catch (_) {}
  }

  Future<void> _upgrade(String plan) async {
    setState(() { _upgrading = true; _message = null; });
    try {
      final data = await _api.post('/subscriptions/upgrade', body: {'plan': plan});
      final checkoutUrl = data['checkout_url'] as String?;
      if (checkoutUrl != null && checkoutUrl.isNotEmpty) {
        final uri = Uri.tryParse(checkoutUrl);
        if (uri != null) {
          await launchUrl(uri, mode: LaunchMode.externalApplication);
        }
        if (mounted) Navigator.pop(context);
        return;
      }
      setState(() => _message = data['message']);
      await Future.delayed(const Duration(seconds: 1));
      if (mounted) Navigator.pop(context);
    } catch (e) {
      setState(() => _message = 'Upgrade failed');
    } finally {
      setState(() => _upgrading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentPlan = context.watch<AuthProvider>().plan;

    return Scaffold(
      appBar: AppBar(title: const Text('Choose Your Plan')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text('Unlock more features as you grow', style: TextStyle(color: AppTheme.muted)),
          const SizedBox(height: 16),
          if (_message != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 12),
              decoration: BoxDecoration(
                color: AppTheme.mintSoft,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(_message!, style: const TextStyle(color: AppTheme.primary)),
            ),
          ...(_plans ?? []).map((plan) {
            final key = plan['key'] as String;
            final isCurrent = currentPlan == key;
            final price = plan['price_monthly'];
            final features = <String>[
              plan['ai_chats_per_month'] == null ? 'Unlimited chats' : '${plan['ai_chats_per_month']} chats/month',
              plan['max_savings_goals'] == null ? 'Unlimited savings goals' : '${plan['max_savings_goals']} savings goal',
              plan['max_invoices_per_month'] == null ? 'Unlimited invoices' : plan['max_invoices_per_month'] == 0 ? 'No invoices' : '${plan['max_invoices_per_month']} invoices/month',
              plan['ad_free'] == true ? 'Ad-free' : 'Ad-supported',
            ];

            return Card(
              margin: const EdgeInsets.only(bottom: 12),
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(12),
                side: isCurrent ? const BorderSide(color: AppTheme.primary, width: 2) : BorderSide.none,
              ),
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(
                          key == 'free' ? Icons.star : key == 'pro' ? Icons.workspace_premium : Icons.flash_on,
                          color: key == 'free' ? AppTheme.softMuted : AppTheme.primary,
                        ),
                        const SizedBox(width: 8),
                        Text(plan['name'], style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                        const Spacer(),
                        Text(price == null ? '—' : '₦$price', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 22)),
                        const Text('/mo', style: TextStyle(color: AppTheme.muted, fontSize: 12)),
                        if (isCurrent) ...[
                          const SizedBox(width: 8),
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                            decoration: BoxDecoration(
                              color: AppTheme.primary,
                              borderRadius: BorderRadius.circular(12),
                            ),
                            child: const Text('Current', style: TextStyle(color: Colors.white, fontSize: 10)),
                          ),
                        ],
                      ],
                    ),
                    const Divider(),
                    ...features.map((f) => Padding(
                      padding: const EdgeInsets.symmetric(vertical: 4),
                      child: Row(children: [
                        const Icon(Icons.check, size: 16, color: AppTheme.success),
                        const SizedBox(width: 8),
                        Text(f, style: const TextStyle(fontSize: 13)),
                      ]),
                    )),
                    const SizedBox(height: 12),
                    if (!isCurrent)
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: _upgrading ? null : () => _upgrade(key),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: key == 'free' ? AppTheme.bg : AppTheme.primary,
                            foregroundColor: key == 'free' ? AppTheme.muted : Colors.white,
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                          ),
                          child: Text(_upgrading ? 'Processing...' : 'Upgrade to ${plan['name']}'),
                        ),
                      ),
                  ],
                ),
              ),
            );
          }),
        ],
      ),
    );
  }
}
