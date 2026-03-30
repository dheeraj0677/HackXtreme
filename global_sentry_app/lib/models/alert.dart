// Alert severity levels
enum Severity { critical, high, medium, low }

// Sentry modes
enum SentryMode { epi, eco, supply }

class Alert {
  final String id;
  final String title;
  final String summary;
  final String region;
  final Severity severity;
  final SentryMode mode;
  final DateTime timestamp;
  final double confidence;
  final String detail;
  final List<String> tags;

  Alert({
    required this.id,
    required this.title,
    required this.summary,
    required this.region,
    required this.severity,
    required this.mode,
    required this.timestamp,
    required this.confidence,
    required this.detail,
    required this.tags,
  });

  String get severityLabel {
    switch (severity) {
      case Severity.critical:
        return 'CRITICAL';
      case Severity.high:
        return 'HIGH';
      case Severity.medium:
        return 'MEDIUM';
      case Severity.low:
        return 'LOW';
    }
  }

  String get modeLabel {
    switch (mode) {
      case SentryMode.epi:
        return 'EPI';
      case SentryMode.eco:
        return 'ECO';
      case SentryMode.supply:
        return 'SUPPLY';
    }
  }
}

class MockDataService {
  static List<Alert> getAlerts(SentryMode mode) {
    switch (mode) {
      case SentryMode.epi:
        return _epiAlerts;
      case SentryMode.eco:
        return _ecoAlerts;
      case SentryMode.supply:
        return _supplyAlerts;
    }
  }

  static final List<Alert> _epiAlerts = [
    Alert(
      id: 'epi-001',
      title: 'Novel Respiratory Cluster — Southeast Asia',
      summary: 'WHO confirms unusual respiratory illness cluster in 3 provinces. R₀ estimated at 1.8. Cross-border spread indicators detected.',
      region: 'Southeast Asia',
      severity: Severity.critical,
      mode: SentryMode.epi,
      timestamp: DateTime.now().subtract(const Duration(minutes: 12)),
      confidence: 0.94,
      detail: 'Epi-Sentry detected anomalous hospitalization spikes across 3 provinces in Thailand and Vietnam. ProMED analysis cross-referenced with historical H1N1 patterns. R₀ trajectory suggests exponential growth within 14 days without containment. RAG memory matched 87% similarity with 2009 early outbreak patterns. Immediate WHO notification recommended.',
      tags: ['WHO Alert', 'R₀ Elevated', 'Cross-border Risk'],
    ),
    Alert(
      id: 'epi-002',
      title: 'Cholera Resurgence — East Africa Horn',
      summary: 'Wastewater genomic surveillance indicates V. cholerae El Tor resurgence. 4 districts affected.',
      region: 'East Africa',
      severity: Severity.high,
      mode: SentryMode.epi,
      timestamp: DateTime.now().subtract(const Duration(hours: 2)),
      confidence: 0.88,
      detail: 'Genomic sequencing from wastewater samples across Kenya and Somalia border regions shows V. cholerae El Tor variant. Displacement camps at highest risk. Aid corridor disruption noted in supply-sentry data. Cross-mode convergence with Supply-Sentry flagged.',
      tags: ['Waterborne', 'Genomic Alert', 'Aid Risk'],
    ),
    Alert(
      id: 'epi-003',
      title: 'Antimicrobial Resistance Signal — South Asia',
      summary: 'Carbapenem-resistant Klebsiella surge detected in hospital networks across 5 metros.',
      region: 'South Asia',
      severity: Severity.high,
      mode: SentryMode.epi,
      timestamp: DateTime.now().subtract(const Duration(hours: 5)),
      confidence: 0.82,
      detail: 'Hospital network data aggregation reveals 340% surge in carbapenem-resistant Klebsiella pneumoniae over 30 days. ICU bed occupancy approaching 90% in Mumbai, Delhi, Dhaka. Last-resort antibiotic stockpile depletion risk flagged by Supply-Sentry.',
      tags: ['AMR', 'Hospital Network', 'ICU Strain'],
    ),
    Alert(
      id: 'epi-004',
      title: 'Dengue Fever Spike — Caribbean Basin',
      summary: 'Vector density models predict 3x seasonal dengue peak. Travel advisories recommended.',
      region: 'Caribbean',
      severity: Severity.medium,
      mode: SentryMode.epi,
      timestamp: DateTime.now().subtract(const Duration(hours: 9)),
      confidence: 0.76,
      detail: 'Satellite thermal imaging combined with rainfall pattern analysis indicates Aedes aegypti breeding surge across Dominican Republic and Haiti. Climate-driven vector expansion model predicts 68K additional cases in Q1. Eco-Sentry climate convergence flagged.',
      tags: ['Vector-borne', 'Seasonal', 'Climate-linked'],
    ),
  ];

  static final List<Alert> _ecoAlerts = [
    Alert(
      id: 'eco-001',
      title: 'Category 5 Cyclone — Bay of Bengal',
      summary: 'NOAA confirms rapidly intensifying cyclone. Landfall predicted: Odisha coast in 68 hours. 2.1M at risk.',
      region: 'Bay of Bengal',
      severity: Severity.critical,
      mode: SentryMode.eco,
      timestamp: DateTime.now().subtract(const Duration(minutes: 4)),
      confidence: 0.97,
      detail: 'Eco-Sentry detected rapid intensification from Cat-2 to Cat-5 in 18 hours — a rare intensification event cross-referenced with historical records. Sea surface temperature anomaly: +2.4°C above seasonal baseline. Storm surge modeling predicts 6-8m inundation across 140km coastline. Mandatory evacuation of 2.1M residents required within 48 hours. Historical RAG match: 2013 Cyclone Phailin pattern.',
      tags: ['NOAA Alert', 'Cat-5', 'Storm Surge', 'Evacuation'],
    ),
    Alert(
      id: 'eco-002',
      title: 'Seismic Swarm — Cascadia Subduction Zone',
      summary: 'Unusual M3.2–M4.1 seismic swarm detected. Slow slip event indicators suggest elevated Cascadia mega-thrust risk.',
      region: 'Pacific Northwest, USA',
      severity: Severity.critical,
      mode: SentryMode.eco,
      timestamp: DateTime.now().subtract(const Duration(minutes: 45)),
      confidence: 0.79,
      detail: 'USGS realtime feed flagged 47 micro-earthquakes in 6-hour window along Cascadia subduction zone. GPS strain gauge data indicates 12mm of plate deflection — consistent with SSE (Slow Slip Event) precursor patterns. Historical RAG: 2001 Cascadia SSE preceded by similar swarm. Probability of M7+ event elevated to 12% over next 72 hours.',
      tags: ['USGS Alert', 'Seismic Swarm', 'Mega-Thrust Risk'],
    ),
    Alert(
      id: 'eco-003',
      title: 'Extreme Heat Dome — Central Europe',
      summary: 'Unprecedented heat dome forming. 7-day forecast: 47°C peak in Spain/France. Wildfire cascade risk HIGH.',
      region: 'Western Europe',
      severity: Severity.high,
      mode: SentryMode.eco,
      timestamp: DateTime.now().subtract(const Duration(hours: 1)),
      confidence: 0.91,
      detail: 'Atmospheric blocking pattern producing heat dome not seen in Central Europe since 2003. Copernicus satellite data confirms drought conditions across 340,000 km². Wildfire risk model: 89% probability of multi-front wildfire event within 5 days. Power grid stress models show 23% surplus demand over generation capacity.',
      tags: ['Heat Dome', 'Wildfire Risk', 'Grid Stress'],
    ),
    Alert(
      id: 'eco-004',
      title: 'Amazon Deforestation Surge — Brazil',
      summary: 'MODIS satellite data: 340% above-average deforestation rate in Pará state. Carbon sink disruption projected.',
      region: 'Brazil',
      severity: Severity.high,
      mode: SentryMode.eco,
      timestamp: DateTime.now().subtract(const Duration(hours: 3)),
      confidence: 0.88,
      detail: 'MODIS forest-change analysis shows 48,000 hectares cleared in 30-day rolling window — unprecedented for dry season. Fires set deliberately based on hotspot clustering patterns. Impact: 8.2 MtCO₂ equivalent released. Regional rainfall pattern disruption modeled to affect 3 agricultural zones. Supply-Sentry cross-flag: Brazilian soy/coffee supply chains at risk.',
      tags: ['MODIS Satellite', 'Deforestation', 'Carbon Risk'],
    ),
  ];

  static final List<Alert> _supplyAlerts = [
    Alert(
      id: 'sup-001',
      title: 'Taiwan Strait Shipping Lane Disruption',
      summary: 'Military exercises create 72-hour closure of critical semiconductor shipping corridor. \$8.4B daily trade at risk.',
      region: 'Taiwan Strait',
      severity: Severity.critical,
      mode: SentryMode.supply,
      timestamp: DateTime.now().subtract(const Duration(minutes: 22)),
      confidence: 0.93,
      detail: 'AIS vessel tracking shows 340 container ships diverted from Taiwan Strait over 24 hours. Semiconductor fab output affected: TSMC, Samsung Giheung facilities on heightened alert. Electronic component stockpile models indicate 60-day buffer before automotive OEM production halts. Medical device supply chain also flagged — 23 critical device categories vulnerable.',
      tags: ['Semiconductor', 'Shipping Closure', 'Trade Risk'],
    ),
    Alert(
      id: 'sup-002',
      title: 'Rare Earth Supply Shock — DRC Cobalt',
      summary: 'Artisanal mining suspension affecting 34% of global cobalt supply. EV battery manufacturers on 90-day alert.',
      region: 'Democratic Republic of Congo',
      severity: Severity.high,
      mode: SentryMode.supply,
      timestamp: DateTime.now().subtract(const Duration(hours: 1, minutes: 30)),
      confidence: 0.86,
      detail: 'Government-mandated safety audit of Katanga Province mines creates sudden cobalt supply gap. ESG analysis of major mining companies shows 6 in material misrepresentation of safety standards — whistleblower signals processed by Supply-Sentry RAG pipeline. LME cobalt price spiked 28% in 48 hours. Battery manufacturer inventory: median 87 days of buffer.',
      tags: ['Cobalt', 'EV Supply', 'ESG Risk', 'Whistleblower'],
    ),
    Alert(
      id: 'sup-003',
      title: 'Black Sea Grain Corridor — Export Block',
      summary: 'Port infrastructure damage prevents wheat and corn exports. 67 nations food-import dependent on affected routes.',
      region: 'Black Sea Region',
      severity: Severity.high,
      mode: SentryMode.supply,
      timestamp: DateTime.now().subtract(const Duration(hours: 4)),
      confidence: 0.89,
      detail: 'Satellite imagery confirms damage to 3 major grain terminal facilities. Ukrainian wheat export capacity reduced 58%. FAO vulnerability index flags 67 food-import dependent nations. Cross-mode convergence with Epi-Sentry: malnutrition risk cascade in Sub-Saharan Africa projected. 4-month buffer before critical food security threshold breached.',
      tags: ['Food Security', 'Grain Export', 'FAO Alert'],
    ),
    Alert(
      id: 'sup-004',
      title: 'Solar Panel Supply Chain — Polysilicon Shortage',
      summary: 'Energy transition at risk: Xinjiang polysilicon production curtailed 40%. 6-month renewable energy project delays projected.',
      region: 'Global / China',
      severity: Severity.medium,
      mode: SentryMode.supply,
      timestamp: DateTime.now().subtract(const Duration(hours: 7)),
      confidence: 0.77,
      detail: 'Trade compliance analysis reveals 78% of solar panel manufacturers sourcing polysilicon from flagged Xinjiang facilities. New US/EU import restrictions create immediate 40% supply shock. Solar project pipeline analysis: 124 GW of projects delayed globally. Grid decarbonization targets miss by 2.3 years on current trajectory.',
      tags: ['Solar', 'Polysilicon', 'Trade Compliance', 'ESG'],
    ),
  ];
}
