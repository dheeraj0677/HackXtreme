import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';

class AlertDetailScreen extends StatefulWidget {
  final Alert alert;
  const AlertDetailScreen({super.key, required this.alert});

  @override
  State<AlertDetailScreen> createState() => _AlertDetailScreenState();
}

class _AlertDetailScreenState extends State<AlertDetailScreen>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _fadeAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 500),
    )..forward();
    _fadeAnim = CurvedAnimation(parent: _controller, curve: Curves.easeOut);
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

  String get _modeEmoji {
    switch (widget.alert.mode) {
      case SentryMode.epi:
        return '🩺';
      case SentryMode.eco:
        return '🌪️';
      case SentryMode.supply:
        return '♻️';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDeep,
      body: FadeTransition(
        opacity: _fadeAnim,
        child: CustomScrollView(
          slivers: [
            _buildSliverAppBar(context),
            SliverPadding(
              padding: const EdgeInsets.all(16),
              sliver: SliverList(
                delegate: SliverChildListDelegate([
                  _buildAlertMeta(),
                  const SizedBox(height: 16),
                  _buildConfidenceBar(),
                  const SizedBox(height: 16),
                  _buildDetailSection(),
                  const SizedBox(height: 16),
                  _buildTagsSection(),
                  const SizedBox(height: 16),
                  _buildPipelineStatus(),
                  const SizedBox(height: 32),
                ]),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSliverAppBar(BuildContext context) {
    return SliverAppBar(
      expandedHeight: 180,
      pinned: true,
      backgroundColor: AppTheme.bgCard,
      leading: IconButton(
        icon: Container(
          padding: const EdgeInsets.all(6),
          decoration: BoxDecoration(
            color: AppTheme.bgCardLighter,
            shape: BoxShape.circle,
            border: Border.all(color: AppTheme.borderColor),
          ),
          child: const Icon(Icons.arrow_back_ios_new_rounded, size: 16, color: AppTheme.textPrimary),
        ),
        onPressed: () => Navigator.pop(context),
      ),
      flexibleSpace: FlexibleSpaceBar(
        background: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [
                _severityColor.withOpacity(0.2),
                _modeColor.withOpacity(0.08),
                AppTheme.bgCard,
              ],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
            ),
          ),
          child: Stack(
            children: [
              // Grid pattern overlay
              CustomPaint(
                painter: _GridPainter(),
                size: Size.infinite,
              ),
              Padding(
                padding: const EdgeInsets.fromLTRB(16, 80, 16, 16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Row(
                      children: [
                        _badgePill(widget.alert.severityLabel, _severityColor),
                        const SizedBox(width: 8),
                        _badgePill('$_modeEmoji ${widget.alert.modeLabel}', _modeColor),
                      ],
                    ),
                    const SizedBox(height: 8),
                    Text(
                      widget.alert.title,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 18,
                        fontWeight: FontWeight.w800,
                        color: AppTheme.textPrimary,
                        height: 1.3,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
        title: Text(
          'Alert Detail',
          style: GoogleFonts.orbitron(
            fontSize: 14,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        titlePadding: const EdgeInsets.only(left: 56, bottom: 14),
      ),
    );
  }

  Widget _badgePill(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.5)),
      ),
      child: Text(
        label,
        style: GoogleFonts.orbitron(
          fontSize: 9,
          fontWeight: FontWeight.w700,
          color: color,
          letterSpacing: 0.8,
        ),
      ),
    );
  }

  Widget _buildAlertMeta() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        children: [
          _metaRow(Icons.location_on_rounded, 'Region', widget.alert.region, AppTheme.textSecondary),
          const Divider(color: AppTheme.borderColor, height: 20),
          _metaRow(Icons.schedule_rounded, 'Detected',
              DateFormat('MMM d, yyyy · HH:mm').format(widget.alert.timestamp), AppTheme.textSecondary),
          const Divider(color: AppTheme.borderColor, height: 20),
          _metaRow(Icons.fingerprint_rounded, 'Alert ID', widget.alert.id.toUpperCase(), _modeColor),
        ],
      ),
    );
  }

  Widget _metaRow(IconData icon, String label, String value, Color valueColor) {
    return Row(
      children: [
        Icon(icon, size: 16, color: AppTheme.textMuted),
        const SizedBox(width: 10),
        Text(
          label,
          style: GoogleFonts.spaceGrotesk(
            fontSize: 13,
            color: AppTheme.textMuted,
          ),
        ),
        const Spacer(),
        Text(
          value,
          style: GoogleFonts.spaceGrotesk(
            fontSize: 13,
            fontWeight: FontWeight.w600,
            color: valueColor,
          ),
        ),
      ],
    );
  }

  Widget _buildConfidenceBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: _modeColor.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(Icons.verified_rounded, size: 16, color: _modeColor),
              const SizedBox(width: 8),
              Text(
                'AI Confidence Score',
                style: GoogleFonts.spaceGrotesk(
                  fontSize: 13,
                  fontWeight: FontWeight.w600,
                  color: AppTheme.textPrimary,
                ),
              ),
              const Spacer(),
              Text(
                '${(widget.alert.confidence * 100).toInt()}%',
                style: GoogleFonts.orbitron(
                  fontSize: 18,
                  fontWeight: FontWeight.w900,
                  color: _modeColor,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          TweenAnimationBuilder<double>(
            tween: Tween(begin: 0, end: widget.alert.confidence),
            duration: const Duration(milliseconds: 1200),
            curve: Curves.easeOut,
            builder: (context, value, _) {
              return Stack(
                children: [
                  Container(
                    height: 8,
                    decoration: BoxDecoration(
                      color: AppTheme.bgCardLighter,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                  FractionallySizedBox(
                    widthFactor: value,
                    child: Container(
                      height: 8,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [_modeColor.withOpacity(0.6), _modeColor],
                        ),
                        borderRadius: BorderRadius.circular(4),
                        boxShadow: [
                          BoxShadow(
                            color: _modeColor.withOpacity(0.4),
                            blurRadius: 6,
                          ),
                        ],
                      ),
                    ),
                  ),
                ],
              );
            },
          ),
          const SizedBox(height: 8),
          Text(
            'Score based on multi-agent cross-validation and RAG memory similarity.',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 11,
              color: AppTheme.textMuted,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailSection() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('🧠', style: TextStyle(fontSize: 16)),
              const SizedBox(width: 8),
              Text(
                'AI Analysis Report',
                style: GoogleFonts.spaceGrotesk(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Container(height: 1, color: AppTheme.borderColor),
          const SizedBox(height: 12),
          Text(
            widget.alert.detail,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 13,
              color: AppTheme.textSecondary,
              height: 1.7,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTagsSection() {
    if (widget.alert.tags.isEmpty) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Intelligence Tags',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 13,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 10),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: widget.alert.tags.map((tag) {
              return Container(
                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _modeColor.withOpacity(0.08),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: _modeColor.withOpacity(0.3)),
                ),
                child: Text(
                  tag,
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 12,
                    color: _modeColor,
                    fontWeight: FontWeight.w600,
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineStatus() {
    final stages = [
      ('📥 Ingest', true, 'Noise filtered'),
      ('🗃️ RAG Retrieved', true, '7 matches found'),
      ('⚡ Triaged', true, 'Threat confirmed'),
      ('🧠 Analyzed', true, 'Report generated'),
      ('🔍 Validated', true, 'Sources verified'),
      ('💾 Archived', true, 'Stored in Qdrant'),
    ];

    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(14),
        border: Border.all(color: AppTheme.accentPurple.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              const Text('⚙️', style: TextStyle(fontSize: 16)),
              const SizedBox(width: 8),
              Text(
                'Pipeline Status',
                style: GoogleFonts.spaceGrotesk(
                  fontSize: 14,
                  fontWeight: FontWeight.w700,
                  color: AppTheme.textPrimary,
                ),
              ),
              const Spacer(),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                decoration: BoxDecoration(
                  color: AppTheme.ecoColor.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  'COMPLETE',
                  style: GoogleFonts.orbitron(
                    fontSize: 8,
                    color: AppTheme.ecoColor,
                    fontWeight: FontWeight.w700,
                    letterSpacing: 1,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 14),
          ...stages.map((stage) => Padding(
                padding: const EdgeInsets.only(bottom: 8),
                child: Row(
                  children: [
                    Icon(
                      stage.$2 ? Icons.check_circle_rounded : Icons.radio_button_unchecked_rounded,
                      size: 16,
                      color: stage.$2 ? AppTheme.ecoColor : AppTheme.textMuted,
                    ),
                    const SizedBox(width: 10),
                    Text(
                      stage.$1,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 13,
                        fontWeight: FontWeight.w600,
                        color: stage.$2 ? AppTheme.textPrimary : AppTheme.textMuted,
                      ),
                    ),
                    const Spacer(),
                    Text(
                      stage.$3,
                      style: GoogleFonts.spaceGrotesk(
                        fontSize: 11,
                        color: AppTheme.textMuted,
                      ),
                    ),
                  ],
                ),
              )),
        ],
      ),
    );
  }
}

class _GridPainter extends CustomPainter {
  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..color = Colors.white.withOpacity(0.03)
      ..strokeWidth = 1;

    const spacing = 30.0;
    for (double x = 0; x < size.width; x += spacing) {
      canvas.drawLine(Offset(x, 0), Offset(x, size.height), paint);
    }
    for (double y = 0; y < size.height; y += spacing) {
      canvas.drawLine(Offset(0, y), Offset(size.width, y), paint);
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => false;
}
