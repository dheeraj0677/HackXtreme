import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';

class AlertCard extends StatefulWidget {
  final Alert alert;
  final VoidCallback onTap;
  final Duration animationDelay;

  const AlertCard({
    super.key,
    required this.alert,
    required this.onTap,
    this.animationDelay = Duration.zero,
  });

  @override
  State<AlertCard> createState() => _AlertCardState();
}

class _AlertCardState extends State<AlertCard> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnim;
  late Animation<Offset> _slideAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    );
    _fadeAnim = Tween<double>(begin: 0, end: 1).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeOut),
    );
    _slideAnim = Tween<Offset>(
      begin: const Offset(0, 0.15),
      end: Offset.zero,
    ).animate(CurvedAnimation(parent: _controller, curve: Curves.easeOut));

    Future.delayed(widget.animationDelay, () {
      if (mounted) _controller.forward();
    });
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Color get _severityColor {
    switch (widget.alert.severity) {
      case Severity.critical:
        return AppTheme.dangerRed;
      case Severity.high:
        return AppTheme.warningYellow;
      case Severity.medium:
        return AppTheme.epiColor;
      case Severity.low:
        return AppTheme.ecoColor;
    }
  }

  Color get _modeColor {
    switch (widget.alert.mode) {
      case SentryMode.epi:
        return AppTheme.epiColor;
      case SentryMode.eco:
        return AppTheme.ecoColor;
      case SentryMode.supply:
        return AppTheme.supplyColor;
    }
  }

  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inMinutes < 60) return '${diff.inMinutes}m ago';
    if (diff.inHours < 24) return '${diff.inHours}h ago';
    return DateFormat('MMM d').format(dt);
  }

  @override
  Widget build(BuildContext context) {
    return FadeTransition(
      opacity: _fadeAnim,
      child: SlideTransition(
        position: _slideAnim,
        child: GestureDetector(
          onTap: widget.onTap,
          child: Container(
            margin: const EdgeInsets.only(bottom: 12),
            decoration: BoxDecoration(
              color: AppTheme.bgCard,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(
                color: _severityColor == AppTheme.dangerRed
                    ? _severityColor.withOpacity(0.5)
                    : AppTheme.borderColor,
                width: widget.alert.severity == Severity.critical ? 1.5 : 1,
              ),
              boxShadow: widget.alert.severity == Severity.critical
                  ? [BoxShadow(color: AppTheme.dangerRed.withOpacity(0.1), blurRadius: 16)]
                  : [],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Top bar with severity color
                Container(
                  height: 3,
                  decoration: BoxDecoration(
                    color: _severityColor,
                    borderRadius: const BorderRadius.vertical(top: Radius.circular(16)),
                  ),
                ),
                Padding(
                  padding: const EdgeInsets.all(14),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      // Header Row
                      Row(
                        children: [
                          _severityBadge(),
                          const SizedBox(width: 6),
                          _modeBadge(),
                          const Spacer(),
                          Row(
                            children: [
                              Icon(Icons.schedule_rounded, size: 11, color: AppTheme.textMuted),
                              const SizedBox(width: 3),
                              Text(
                                _formatTime(widget.alert.timestamp),
                                style: GoogleFonts.spaceGrotesk(
                                  fontSize: 11,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                      const SizedBox(height: 10),
                      // Title
                      Text(
                        widget.alert.title,
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 15,
                          fontWeight: FontWeight.w700,
                          color: AppTheme.textPrimary,
                          height: 1.3,
                        ),
                      ),
                      const SizedBox(height: 6),
                      // Summary
                      Text(
                        widget.alert.summary,
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 12,
                          color: AppTheme.textSecondary,
                          height: 1.5,
                        ),
                        maxLines: 3,
                        overflow: TextOverflow.ellipsis,
                      ),
                      const SizedBox(height: 12),
                      // Footer Row
                      Row(
                        children: [
                          // Region
                          Row(
                            children: [
                              const Icon(Icons.location_on_rounded, size: 12, color: AppTheme.textMuted),
                              const SizedBox(width: 3),
                              Text(
                                widget.alert.region,
                                style: GoogleFonts.spaceGrotesk(
                                  fontSize: 11,
                                  color: AppTheme.textMuted,
                                ),
                              ),
                            ],
                          ),
                          const Spacer(),
                          // Confidence
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                            decoration: BoxDecoration(
                              color: _modeColor.withOpacity(0.1),
                              borderRadius: BorderRadius.circular(8),
                            ),
                            child: Row(
                              children: [
                                Icon(Icons.verified_rounded, size: 10, color: _modeColor),
                                const SizedBox(width: 3),
                                Text(
                                  '${(widget.alert.confidence * 100).toInt()}% conf.',
                                  style: GoogleFonts.spaceGrotesk(
                                    fontSize: 10,
                                    color: _modeColor,
                                    fontWeight: FontWeight.w600,
                                  ),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(width: 6),
                          Icon(Icons.arrow_forward_ios_rounded, size: 12, color: AppTheme.textMuted),
                        ],
                      ),
                      if (widget.alert.tags.isNotEmpty) ...[
                        const SizedBox(height: 10),
                        Wrap(
                          spacing: 6,
                          runSpacing: 4,
                          children: widget.alert.tags.map((tag) => _tag(tag)).toList(),
                        ),
                      ],
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _severityBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: _severityColor.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: _severityColor.withOpacity(0.5)),
      ),
      child: Text(
        widget.alert.severityLabel,
        style: GoogleFonts.orbitron(
          fontSize: 8,
          fontWeight: FontWeight.w700,
          color: _severityColor,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  Widget _modeBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
      decoration: BoxDecoration(
        color: _modeColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(
        widget.alert.modeLabel,
        style: GoogleFonts.orbitron(
          fontSize: 8,
          fontWeight: FontWeight.w700,
          color: _modeColor,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  Widget _tag(String tag) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 2),
      decoration: BoxDecoration(
        color: AppTheme.bgCardLighter,
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Text(
        tag,
        style: GoogleFonts.spaceGrotesk(
          fontSize: 10,
          color: AppTheme.textSecondary,
          fontWeight: FontWeight.w500,
        ),
      ),
    );
  }
}
