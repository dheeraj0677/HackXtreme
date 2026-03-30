import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';

class StatsHeader extends StatelessWidget {
  final SentryMode sentryMode;
  final Color modeColor;

  const StatsHeader({
    super.key,
    required this.sentryMode,
    required this.modeColor,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      margin: const EdgeInsets.all(16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            modeColor.withOpacity(0.12),
            modeColor.withOpacity(0.03),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: modeColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          _statItem(_getAlertCount(), 'Alerts', modeColor),
          _divider(),
          _statItem(_getRegionCount(), 'Regions', modeColor),
          _divider(),
          _statItem(_getAccuracy(), 'AI Conf.', modeColor),
          _divider(),
          _statItem(_getCritical(), 'Critical', AppTheme.dangerRed),
        ],
      ),
    );
  }

  String _getAlertCount() {
    switch (sentryMode) {
      case SentryMode.epi:
        return '312';
      case SentryMode.eco:
        return '489';
      case SentryMode.supply:
        return '198';
    }
  }

  String _getRegionCount() {
    switch (sentryMode) {
      case SentryMode.epi:
        return '47';
      case SentryMode.eco:
        return '63';
      case SentryMode.supply:
        return '38';
    }
  }

  String _getAccuracy() {
    switch (sentryMode) {
      case SentryMode.epi:
        return '94%';
      case SentryMode.eco:
        return '97%';
      case SentryMode.supply:
        return '89%';
    }
  }

  String _getCritical() {
    switch (sentryMode) {
      case SentryMode.epi:
        return '12';
      case SentryMode.eco:
        return '23';
      case SentryMode.supply:
        return '8';
    }
  }

  Widget _statItem(String value, String label, Color color) {
    return Expanded(
      child: Column(
        children: [
          Text(
            value,
            style: GoogleFonts.orbitron(
              fontSize: 18,
              fontWeight: FontWeight.w900,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 10,
              color: AppTheme.textSecondary,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }

  Widget _divider() {
    return Container(
      width: 1,
      height: 36,
      color: AppTheme.borderColor,
      margin: const EdgeInsets.symmetric(horizontal: 4),
    );
  }
}
