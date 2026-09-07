import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../config/theme.dart';
import '../providers/connectivity_provider.dart';

/// Subtle banner shown when the device is offline. Uses the existing muted
/// palette so it never distracts from the content (AGENTS.md Principle 3).
class OfflineBanner extends StatelessWidget {
  const OfflineBanner({super.key});

  @override
  Widget build(BuildContext context) {
    final online = context.select<ConnectivityProvider, bool>((p) => p.isOnline);
    if (online) return const SizedBox.shrink();
    return const Material(
      color: AppTheme.goldSoft,
      child: SafeArea(
        top: false,
        child: Padding(
          padding: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
          child: Row(
            children: [
              Icon(Icons.cloud_off_outlined, size: 16, color: AppTheme.goldDark),
              SizedBox(width: 8),
              Expanded(
                child: Text(
                  'You are offline - showing saved data',
                  style: TextStyle(fontSize: 12, color: AppTheme.goldDark, fontWeight: FontWeight.w600),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}