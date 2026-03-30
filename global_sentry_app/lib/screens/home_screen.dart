import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';
import 'dashboard_screen.dart';
import 'analytics_screen.dart';
import 'pipeline_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with TickerProviderStateMixin {
  int _selectedIndex = 0;
  SentryMode _sentryMode = SentryMode.eco;
  late AnimationController _pulseController;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
  }

  @override
  void dispose() {
    _pulseController.dispose();
    super.dispose();
  }

  void _onSentryModeChanged(SentryMode mode) {
    setState(() {
      _sentryMode = mode;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.bgDeep,
      appBar: _buildAppBar(),
      body: Column(
        children: [
          _buildSentryModeSwitcher(),
          Expanded(
            child: IndexedStack(
              index: _selectedIndex,
              children: [
                DashboardScreen(sentryMode: _sentryMode),
                AnalyticsScreen(sentryMode: _sentryMode),
                PipelineScreen(),
              ],
            ),
          ),
        ],
      ),
      bottomNavigationBar: _buildBottomNav(),
    );
  }

  PreferredSizeWidget _buildAppBar() {
    return AppBar(
      backgroundColor: AppTheme.bgCard,
      elevation: 0,
      flexibleSpace: Container(
        decoration: const BoxDecoration(
          border: Border(
            bottom: BorderSide(color: AppTheme.borderColor, width: 1),
          ),
        ),
      ),
      title: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(4),
            decoration: BoxDecoration(
              color: AppTheme.bgCardLighter,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.borderColor),
            ),
            child: Image.asset(
              'assets/images/logo.png',
              width: 24,
              height: 24,
              fit: BoxFit.contain,
            ),
          ),
          const SizedBox(width: 10),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                'GlobalSentry',
                style: GoogleFonts.orbitron(
                  fontSize: 16,
                  fontWeight: FontWeight.w900,
                  color: AppTheme.textPrimary,
                  letterSpacing: 1.5,
                ),
              ),
              Text(
                'Intelligence Platform',
                style: GoogleFonts.spaceGrotesk(
                  fontSize: 10,
                  color: AppTheme.textSecondary,
                  letterSpacing: 0.8,
                ),
              ),
            ],
          ),
        ],
      ),
      actions: [
        AnimatedBuilder(
          animation: _pulseController,
          builder: (context, child) {
            return Padding(
              padding: const EdgeInsets.only(right: 16),
              child: Row(
                children: [
                  Container(
                    width: 8,
                    height: 8,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: AppTheme.ecoColor.withOpacity(
                        0.5 + 0.5 * _pulseController.value,
                      ),
                      boxShadow: [
                        BoxShadow(
                          color: AppTheme.ecoColor.withOpacity(0.5),
                          blurRadius: 8,
                          spreadRadius: 2,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(width: 6),
                  Text(
                    'LIVE',
                    style: GoogleFonts.orbitron(
                      fontSize: 10,
                      color: AppTheme.ecoColor,
                      fontWeight: FontWeight.w700,
                      letterSpacing: 1.5,
                    ),
                  ),
                ],
              ),
            );
          },
        ),
      ],
    );
  }

  Widget _buildSentryModeSwitcher() {
    return Container(
      width: double.infinity,
      decoration: const BoxDecoration(
        color: AppTheme.bgCard,
        border: Border(bottom: BorderSide(color: AppTheme.borderColor, width: 0.5)),
      ),
      child: SingleChildScrollView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
        physics: const BouncingScrollPhysics(),
        child: Row(
          children: [
            _sentryModeButton(SentryMode.epi, '🩺', 'Epi-Sentry', AppTheme.epiColor, AppTheme.epiGlow),
            const SizedBox(width: 10),
            _sentryModeButton(SentryMode.eco, '🌪️', 'Eco-Sentry', AppTheme.ecoColor, AppTheme.ecoGlow),
            const SizedBox(width: 10),
            _sentryModeButton(SentryMode.supply, '♻️', 'Supply-Sentry', AppTheme.supplyColor, AppTheme.supplyGlow),
            const SizedBox(width: 16),
            Container(width: 1, height: 20, color: AppTheme.borderColor),
            const SizedBox(width: 16),
            _buildSdgBadge(),
          ],
        ),
      ),
    );
  }

  Widget _buildSdgBadge() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.bgCardLighter,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppTheme.borderColor),
      ),
      child: Row(
        children: [
          const Icon(Icons.satellite_alt_rounded, size: 12, color: AppTheme.textMuted),
          const SizedBox(width: 6),
          Text(
            'SDG 3·11·12·13',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 10,
              color: AppTheme.textMuted,
              fontWeight: FontWeight.w600,
            ),
          ),
        ],
      ),
    );
  }

  Widget _sentryModeButton(SentryMode mode, String emoji, String label, Color color, Color glow) {
    final isActive = _sentryMode == mode;
    return GestureDetector(
      onTap: () => _onSentryModeChanged(mode),
      child: AnimatedContainer(
        duration: const Duration(milliseconds: 250),
        curve: Curves.easeOut,
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
        decoration: BoxDecoration(
          color: isActive ? glow : Colors.transparent,
          borderRadius: BorderRadius.circular(20),
          border: Border.all(
            color: isActive ? color : AppTheme.borderColor,
            width: 1.5,
          ),
          boxShadow: isActive
              ? [BoxShadow(color: color.withOpacity(0.15), blurRadius: 10, spreadRadius: 1)]
              : [],
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(emoji, style: const TextStyle(fontSize: 14)),
            const SizedBox(width: 6),
            Text(
              label,
              style: GoogleFonts.spaceGrotesk(
                fontSize: 12,
                fontWeight: isActive ? FontWeight.w700 : FontWeight.w500,
                color: isActive ? color : AppTheme.textSecondary,
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNav() {
    return Container(
      decoration: const BoxDecoration(
        color: AppTheme.bgCard,
        border: Border(
          top: BorderSide(color: AppTheme.borderColor, width: 1),
        ),
      ),
      child: BottomNavigationBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        selectedItemColor: AppTheme.epiColor,
        unselectedItemColor: AppTheme.textMuted,
        currentIndex: _selectedIndex,
        onTap: (i) => setState(() => _selectedIndex = i),
        type: BottomNavigationBarType.fixed,
        selectedLabelStyle: GoogleFonts.spaceGrotesk(
          fontSize: 11,
          fontWeight: FontWeight.w600,
        ),
        unselectedLabelStyle: GoogleFonts.spaceGrotesk(fontSize: 11),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_rounded),
            label: 'Dashboard',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics_rounded),
            label: 'Analytics',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.account_tree_rounded),
            label: 'Pipeline',
          ),
        ],
      ),
    );
  }
}
