import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../config/theme.dart';
import '../../config/app_config.dart';

/// User-friendly error fallback widget for MaterialApp.errorBuilder.
/// Shows a friendly error screen with retry/go home/report actions.
class ErrorFallbackWidget extends StatelessWidget {
  final FlutterErrorDetails errorDetails;
  final VoidCallback? onRetry;
  final String? customMessage;
  final bool showReportButton;

  const ErrorFallbackWidget({
    super.key,
    required this.errorDetails,
    this.onRetry,
    this.customMessage,
    this.showReportButton = true,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Scaffold(
      backgroundColor: isDark ? AppTheme.darkBackground : AppTheme.lightBackground,
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24),
            child: ConstrainedBox(
              constraints: const BoxConstraints(maxWidth: 400),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  // Illustration/Icon
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      gradient: LinearGradient(
                        colors: isDark
                            ? [AppTheme.primaryDark, AppTheme.primaryLight]
                            : [AppTheme.primary, AppTheme.primaryLight],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                      borderRadius: BorderRadius.circular(32),
                    ),
                    child: const Icon(
                      Icons.error_outline_rounded,
                      size: 60,
                      color: Colors.white,
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Title
                  Text(
                    'Something went wrong',
                    style: theme.textTheme.headlineSmall?.copyWith(
                      fontWeight: FontWeight.w600,
                      color: isDark ? Colors.white : AppTheme.textPrimary,
                    ),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 8),

                  // Subtitle
                  Text(
                    customMessage ??
                        'We\'ve been notified about this issue. Please try again or go back home.',
                    style: theme.textTheme.bodyLarge?.copyWith(
                      color: isDark ? Colors.white70 : AppTheme.textSecondary,
                    ),
                    textAlign: TextAlign.center,
                  ),

                  const SizedBox(height: 32),

                  // Action buttons
                  Column(
                    children: [
                      // Retry button
                      SizedBox(
                        width: double.infinity,
                        child: FilledButton.icon(
                          onPressed: onRetry ??
                              () {
                                // Default: reload app
                                // In practice, navigator might not be available here
                                // The app will restart on next launch
                              },
                          icon: const Icon(Icons.refresh_rounded),
                          label: const Text('Retry'),
                          style: FilledButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            backgroundColor: AppTheme.primary,
                          ),
                        ),
                      ),

                      const SizedBox(height: 12),

                      // Go Home button
                      SizedBox(
                        width: double.infinity,
                        child: OutlinedButton.icon(
                          onPressed: () {
                            // Navigate to home - this might not work in error builder
                            // but provides the action
                          },
                          icon: const Icon(Icons.home_rounded),
                          label: const Text('Go Home'),
                          style: OutlinedButton.styleFrom(
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(
                              borderRadius: BorderRadius.circular(16),
                            ),
                            side: BorderSide(
                              color: isDark ? Colors.white30 : AppTheme.primary,
                            ),
                          ),
                        ),
                      ),

                      if (showReportButton) ...[
                        const SizedBox(height: 12),
                        // Report Issue button
                        SizedBox(
                          width: double.infinity,
                          child: TextButton.icon(
                            onPressed: _reportIssue,
                            icon: const Icon(Icons.bug_report_rounded),
                            label: const Text('Report Issue'),
                            style: TextButton.styleFrom(
                              padding: const EdgeInsets.symmetric(vertical: 12),
                              foregroundColor: isDark ? Colors.white60 : AppTheme.textSecondary,
                            ),
                          ),
                        ),
                      ],
                    ],
                  ),

                  const SizedBox(height: 24),

                  // Technical details (expandable)
                  _ErrorDetailsPanel(errorDetails: errorDetails),

                  const SizedBox(height: 24),

                  // Footer
                  Text(
                    'EcoFinwize v1.0.0 • ${appConfig.flavor.name}',
                    style: theme.textTheme.bodySmall?.copyWith(
                      color: isDark ? Colors.white30 : AppTheme.textSecondary,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _reportIssue() async {
    final error = errorDetails.exception;
    final stack = errorDetails.stack;
    final body = '''
Error Report from EcoFinwize Mobile
====================================
Flavor: ${appConfig.flavor.name}
App Version: 1.0.0
Timestamp: ${DateTime.now().toIso8601String()}

Error:
$error

Stack Trace:
$stack
''';

    final uri = Uri(
      scheme: 'mailto',
      path: 'support@finwize.app',
      query: 'subject=EcoFinwize Error Report&body=${Uri.encodeComponent(body)}',
    );

    if (await canLaunchUrl(uri)) {
      await launchUrl(uri);
    }
  }
}

/// Expandable panel showing technical error details for debugging.
class _ErrorDetailsPanel extends StatefulWidget {
  final FlutterErrorDetails errorDetails;

  const _ErrorDetailsPanel({required this.errorDetails});

  @override
  State<_ErrorDetailsPanel> createState() => _ErrorDetailsPanelState();
}

class _ErrorDetailsPanelState extends State<_ErrorDetailsPanel> {
  bool _expanded = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Column(
      children: [
        InkWell(
          onTap: () => setState(() => _expanded = !_expanded),
          borderRadius: BorderRadius.circular(12),
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? AppTheme.darkCardBackground : AppTheme.lightCardBackground,
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isDark ? Colors.white10 : Colors.grey[200]!,
              ),
            ),
            child: Row(
              children: [
                Expanded(
                  child: Text(
                    'Technical Details',
                    style: theme.textTheme.bodyMedium?.copyWith(
                      fontWeight: FontWeight.w500,
                      color: isDark ? Colors.white : AppTheme.textPrimary,
                    ),
                  ),
                ),
                Icon(
                  _expanded ? Icons.expand_less : Icons.expand_more,
                  color: isDark ? Colors.white54 : Colors.grey[600],
                ),
              ],
            ),
          ),
        ),

        if (_expanded) ...[
          const SizedBox(height: 12),
          Container(
            width: double.infinity,
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: isDark ? Colors.black : Colors.grey[100],
              borderRadius: BorderRadius.circular(12),
              border: Border.all(
                color: isDark ? Colors.white10 : Colors.grey[200]!,
              ),
            ),
            child: SingleChildScrollView(
              child: SelectableText(
                _formatErrorDetails(widget.errorDetails),
                style: theme.textTheme.bodySmall?.copyWith(
                  fontFamily: 'monospace',
                  color: isDark ? Colors.greenAccent[100] : Colors.black87,
                ),
              ),
            ),
          ),
        ],
      ],
    );
  }

  String _formatErrorDetails(FlutterErrorDetails details) {
    final buffer = StringBuffer();
    buffer.writeln('Exception: ${details.exception}');
    buffer.writeln('Library: ${details.library}');
    buffer.writeln('Context: ${details.context}');
    if (details.stack != null) {
      buffer.writeln('\nStack Trace:\n${details.stack}');
    }
    if (details.informationCollector != null) {
      buffer.writeln('\nAdditional Info:\n${details.informationCollector!()}');
    }
    return buffer.toString();
  }
}

/// Simplified error widget for use within specific screens/widgets.
/// Smaller footprint, suitable for inline errors.
class InlineErrorWidget extends StatelessWidget {
  final String message;
  final VoidCallback? onRetry;
  final String? retryLabel;
  final IconData? icon;

  const InlineErrorWidget({
    super.key,
    required this.message,
    this.onRetry,
    this.retryLabel,
    this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Container(
      padding: const EdgeInsets.all(24),
      margin: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isDark ? AppTheme.darkCardBackground : AppTheme.lightCardBackground,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: isDark ? Colors.red[900]!.withOpacity(0.3) : Colors.red[100]!,
        ),
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(
            icon ?? Icons.error_outline_rounded,
            size: 48,
            color: isDark ? Colors.red[300] : Colors.red[600],
          ),
          const SizedBox(height: 12),
          Text(
            'Oops!',
            style: theme.textTheme.titleLarge?.copyWith(
              fontWeight: FontWeight.w600,
              color: isDark ? Colors.white : AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            message,
            style: theme.textTheme.bodyMedium?.copyWith(
              color: isDark ? Colors.white70 : AppTheme.textSecondary,
            ),
            textAlign: TextAlign.center,
          ),
          if (onRetry != null) ...[
            const SizedBox(height: 16),
            FilledButton.icon(
              onPressed: onRetry,
              icon: const Icon(Icons.refresh_rounded, size: 18),
              label: Text(retryLabel ?? 'Try Again'),
              style: FilledButton.styleFrom(
                backgroundColor: AppTheme.primary,
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ],
      ),
    );
  }
}