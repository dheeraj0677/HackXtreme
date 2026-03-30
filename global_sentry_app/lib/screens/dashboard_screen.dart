import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';
import '../widgets/alert_card.dart';
import '../widgets/stats_header.dart';
import 'alert_detail_screen.dart';

class DashboardScreen extends StatefulWidget {
  final SentryMode sentryMode;
  const DashboardScreen({super.key, required this.sentryMode});

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> with AutomaticKeepAliveClientMixin {
  late List<Alert> _alerts;
  bool _isLoading = true;

  @override
  bool get wantKeepAlive => true;

  @override
  void initState() {
    super.initState();
    _loadAlerts();
  }

  @override
  void didUpdateWidget(covariant DashboardScreen oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (oldWidget.sentryMode != widget.sentryMode) {
      setState(() => _isLoading = true);
      Future.delayed(const Duration(milliseconds: 600), () {
        if (mounted) {
          setState(() {
            _alerts = MockDataService.getAlerts(widget.sentryMode);
            _isLoading = false;
          });
        }
      });
    }
  }

  void _loadAlerts() {
    Future.delayed(const Duration(milliseconds: 800), () {
      if (mounted) {
        setState(() {
          _alerts = MockDataService.getAlerts(widget.sentryMode);
          _isLoading = false;
        });
      }
    });
  }

  Color get _modeColor {
    switch (widget.sentryMode) {
      case SentryMode.epi:
        return AppTheme.epiColor;
      case SentryMode.eco:
        return AppTheme.ecoColor;
      case SentryMode.supply:
        return AppTheme.supplyColor;
    }
  }

  String get _modeTitle {
    switch (widget.sentryMode) {
      case SentryMode.epi:
        return '🩺 Epi-Sentry Feed';
      case SentryMode.eco:
        return '🌪️ Eco-Sentry Feed';
      case SentryMode.supply:
        return '♻️ Supply-Sentry Feed';
    }
  }

  @override
  Widget build(BuildContext context) {
    super.build(context);
    return Container(
      color: AppTheme.bgDeep,
      child: Column(
        children: [
          StatsHeader(
            sentryMode: widget.sentryMode,
            modeColor: _modeColor,
          ),
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: [
                Text(
                  _modeTitle,
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 15,
                    fontWeight: FontWeight.w700,
                    color: AppTheme.textPrimary,
                  ),
                ),
                const Spacer(),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                  decoration: BoxDecoration(
                    color: _modeColor.withOpacity(0.15),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(color: _modeColor.withOpacity(0.4)),
                  ),
                  child: Text(
                    'LIVE',
                    style: GoogleFonts.orbitron(
                      fontSize: 9,
                      color: _modeColor,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.5,
                    ),
                  ),
                ),
              ],
            ),
          ),
          Expanded(
            child: _isLoading
                ? _buildLoadingState()
                : _buildAlertList(),
          ),
        ],
      ),
    );
  }

  Widget _buildLoadingState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          SizedBox(
            width: 48,
            height: 48,
            child: CircularProgressIndicator(
              color: _modeColor,
              strokeWidth: 2,
            ),
          ),
          const SizedBox(height: 16),
          Text(
            'Fetching intelligence...',
            style: GoogleFonts.spaceGrotesk(
              color: AppTheme.textSecondary,
              fontSize: 14,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildAlertList() {
    return AnimatedSwitcher(
      duration: const Duration(milliseconds: 400),
      child: ListView.builder(
        key: ValueKey(widget.sentryMode),
        padding: const EdgeInsets.only(left: 16, right: 16, bottom: 16),
        itemCount: _alerts.length,
        itemBuilder: (context, index) {
          return AlertCard(
            alert: _alerts[index],
            animationDelay: Duration(milliseconds: index * 120),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(
                  builder: (_) => AlertDetailScreen(alert: _alerts[index]),
                ),
              );
            },
          );
        },
      ),
    );
  }
}
