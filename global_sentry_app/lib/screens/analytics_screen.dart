import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:fl_chart/fl_chart.dart';
import '../theme/app_theme.dart';
import '../models/alert.dart';

class AnalyticsScreen extends StatefulWidget {
  final SentryMode sentryMode;
  const AnalyticsScreen({super.key, required this.sentryMode});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildSectionHeader('📊 Threat Analytics', 'Live data visualization from aggregated sentry models'),
          const SizedBox(height: 16),
          _buildEpiChart(),
          const SizedBox(height: 16),
          _buildEcoBarChart(),
          const SizedBox(height: 16),
          _buildSupplyPieChart(),
          const SizedBox(height: 16),
          _buildAlertStatsGrid(),
          const SizedBox(height: 16),
          _buildSDGBadges(),
        ],
      ),
    );
  }

  Widget _buildSectionHeader(String title, String subtitle) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: GoogleFonts.spaceGrotesk(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 4),
        Text(
          subtitle,
          style: GoogleFonts.spaceGrotesk(
            fontSize: 13,
            color: AppTheme.textSecondary,
          ),
        ),
      ],
    );
  }

  Widget _buildEpiChart() {
    return _chartCard(
      title: '🩺 Epi-Sentry: R₀ Trajectory',
      subtitle: 'Estimated reproductive number over 12 months',
      color: AppTheme.epiColor,
      chart: LineChart(
        LineChartData(
          backgroundColor: Colors.transparent,
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            horizontalInterval: 0.5,
            getDrawingHorizontalLine: (value) => FlLine(
              color: AppTheme.borderColor.withOpacity(0.5),
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 0.5,
                reservedSize: 36,
                getTitlesWidget: (value, meta) => Text(
                  value.toStringAsFixed(1),
                  style: GoogleFonts.spaceGrotesk(
                    fontSize: 10,
                    color: AppTheme.textMuted,
                  ),
                ),
              ),
            ),
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                interval: 2,
                getTitlesWidget: (value, meta) {
                  const months = ['Jan', 'Mar', 'May', 'Jul', 'Sep', 'Nov'];
                  final index = (value ~/ 2).clamp(0, months.length - 1);
                  return Text(
                    months[index],
                    style: GoogleFonts.spaceGrotesk(fontSize: 10, color: AppTheme.textMuted),
                  );
                },
              ),
            ),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          minX: 0,
          maxX: 11,
          minY: 0.5,
          maxY: 3,
          lineBarsData: [
            LineChartBarData(
              spots: const [
                FlSpot(0, 1.2),
                FlSpot(1, 1.4),
                FlSpot(2, 1.1),
                FlSpot(3, 1.8),
                FlSpot(4, 2.3),
                FlSpot(5, 1.9),
                FlSpot(6, 1.5),
                FlSpot(7, 1.7),
                FlSpot(8, 2.1),
                FlSpot(9, 2.5),
                FlSpot(10, 2.2),
                FlSpot(11, 1.8),
              ],
              isCurved: true,
              color: AppTheme.epiColor,
              barWidth: 2.5,
              isStrokeCapRound: true,
              dotData: const FlDotData(show: false),
              belowBarData: BarAreaData(
                show: true,
                color: AppTheme.epiColor.withOpacity(0.1),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildEcoBarChart() {
    return _chartCard(
      title: '🌪️ Eco-Sentry: Climate Disaster Index',
      subtitle: 'Severity-weighted events count by category',
      color: AppTheme.ecoColor,
      chart: BarChart(
        BarChartData(
          backgroundColor: Colors.transparent,
          gridData: FlGridData(
            show: true,
            drawVerticalLine: false,
            getDrawingHorizontalLine: (v) => FlLine(
              color: AppTheme.borderColor.withOpacity(0.5),
              strokeWidth: 1,
            ),
          ),
          titlesData: FlTitlesData(
            bottomTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                getTitlesWidget: (value, meta) {
                  const labels = ['Cyclones', 'Seismic', 'Heat', 'Floods', 'Wildfire'];
                  if (value.toInt() >= 0 && value.toInt() < labels.length) {
                    return Padding(
                      padding: const EdgeInsets.only(top: 6),
                      child: Text(
                        labels[value.toInt()],
                        style: GoogleFonts.spaceGrotesk(
                          fontSize: 9,
                          color: AppTheme.textSecondary,
                        ),
                      ),
                    );
                  }
                  return const SizedBox();
                },
              ),
            ),
            leftTitles: AxisTitles(
              sideTitles: SideTitles(
                showTitles: true,
                reservedSize: 36,
                getTitlesWidget: (v, meta) => Text(
                  v.toInt().toString(),
                  style: GoogleFonts.spaceGrotesk(fontSize: 10, color: AppTheme.textMuted),
                ),
              ),
            ),
            rightTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
            topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          ),
          borderData: FlBorderData(show: false),
          barGroups: [
            _makeBar(0, 89, AppTheme.ecoColor),
            _makeBar(1, 47, AppTheme.ecoColor.withOpacity(0.8)),
            _makeBar(2, 120, AppTheme.warningYellow),
            _makeBar(3, 73, AppTheme.ecoColor.withOpacity(0.6)),
            _makeBar(4, 95, AppTheme.dangerRed),
          ],
        ),
      ),
    );
  }

  BarChartGroupData _makeBar(int x, double y, Color color) {
    return BarChartGroupData(
      x: x,
      barRods: [
        BarChartRodData(
          toY: y,
          color: color,
          width: 20,
          borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
        ),
      ],
    );
  }

  Widget _buildSupplyPieChart() {
    return _chartCard(
      title: '♻️ Supply-Sentry: Disruption Factors',
      subtitle: 'Percentage breakdown of active supply chain risks',
      color: AppTheme.supplyColor,
      chart: PieChart(
        PieChartData(
          sectionsSpace: 3,
          centerSpaceRadius: 50,
          sections: [
            PieChartSectionData(
              value: 35,
              title: 'Shipping\n35%',
              color: AppTheme.supplyColor,
              radius: 70,
              titleStyle: GoogleFonts.spaceGrotesk(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            PieChartSectionData(
              value: 25,
              title: 'Geopolitical\n25%',
              color: AppTheme.epiColor,
              radius: 70,
              titleStyle: GoogleFonts.spaceGrotesk(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
            PieChartSectionData(
              value: 20,
              title: 'Climate\n20%',
              color: AppTheme.ecoColor,
              radius: 70,
              titleStyle: GoogleFonts.spaceGrotesk(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppTheme.bgDeep,
              ),
            ),
            PieChartSectionData(
              value: 20,
              title: 'ESG\n20%',
              color: AppTheme.accentPurple,
              radius: 70,
              titleStyle: GoogleFonts.spaceGrotesk(
                fontSize: 10,
                fontWeight: FontWeight.w600,
                color: AppTheme.textPrimary,
              ),
            ),
          ],
        ),
      ),
      chartHeight: 220,
    );
  }

  Widget _buildAlertStatsGrid() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '📈 Global Alert Statistics',
          style: GoogleFonts.spaceGrotesk(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(child: _statTile('1,247', 'Total Threats', AppTheme.epiColor, Icons.warning_rounded)),
            const SizedBox(width: 10),
            Expanded(child: _statTile('94', 'Countries', AppTheme.ecoColor, Icons.public_rounded)),
          ],
        ),
        const SizedBox(height: 10),
        Row(
          children: [
            Expanded(child: _statTile('96%', 'Accuracy', AppTheme.supplyColor, Icons.verified_rounded)),
            const SizedBox(width: 10),
            Expanded(child: _statTile('99.7%', 'Uptime', AppTheme.accentPurple, Icons.speed_rounded)),
          ],
        ),
      ],
    );
  }

  Widget _statTile(String value, String label, Color color, IconData icon) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(height: 8),
          Text(
            value,
            style: GoogleFonts.orbitron(
              fontSize: 22,
              fontWeight: FontWeight.w900,
              color: color,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            label,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 12,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSDGBadges() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '🌐 UN SDG Alignment',
          style: GoogleFonts.spaceGrotesk(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        Wrap(
          spacing: 8,
          runSpacing: 8,
          children: [
            _sdgBadge('SDG 3', 'Good Health', AppTheme.epiColor),
            _sdgBadge('SDG 11', 'Sustainable Cities', AppTheme.ecoColor),
            _sdgBadge('SDG 12', 'Responsible Consumption', AppTheme.supplyColor),
            _sdgBadge('SDG 13', 'Climate Action', AppTheme.accentPurple),
          ],
        ),
      ],
    );
  }

  Widget _sdgBadge(String sdg, String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.4)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            sdg,
            style: GoogleFonts.orbitron(
              fontSize: 11,
              fontWeight: FontWeight.w700,
              color: color,
            ),
          ),
          Text(
            label,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 11,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _chartCard({
    required String title,
    required String subtitle,
    required Color color,
    required Widget chart,
    double chartHeight = 180,
  }) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.bgCard,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: color.withOpacity(0.3)),
        boxShadow: [
          BoxShadow(
            color: color.withOpacity(0.05),
            blurRadius: 20,
            spreadRadius: 0,
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            title,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 14,
              fontWeight: FontWeight.w700,
              color: AppTheme.textPrimary,
            ),
          ),
          const SizedBox(height: 2),
          Text(
            subtitle,
            style: GoogleFonts.spaceGrotesk(
              fontSize: 11,
              color: AppTheme.textSecondary,
            ),
          ),
          const SizedBox(height: 16),
          SizedBox(
            height: chartHeight,
            child: chart,
          ),
        ],
      ),
    );
  }
}
