import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import '../theme/app_theme.dart';

class PipelineScreen extends StatefulWidget {
  const PipelineScreen({super.key});

  @override
  State<PipelineScreen> createState() => _PipelineScreenState();
}

class _PipelineScreenState extends State<PipelineScreen> with TickerProviderStateMixin {
  int _activeStep = -1;
  bool _isRunning = false;
  late AnimationController _progressController;

  final List<_PipelineNode> _nodes = [
    _PipelineNode(icon: '📥', label: 'Ingest & Profiler', desc: 'Mode-aware noise filtering', color: AppTheme.epiColor),
    _PipelineNode(icon: '🗃️', label: 'Retriever (RAG)', desc: 'Qdrant historical search', color: AppTheme.accentPurple),
    _PipelineNode(icon: '⚡', label: 'Agent A — Triage', desc: 'Flash LLM threat filter', color: AppTheme.warningYellow),
    _PipelineNode(icon: '🧠', label: 'Agent B — Analyst', desc: 'Deep reasoning engine', color: AppTheme.ecoColor),
    _PipelineNode(icon: '🔍', label: 'Agent C — Validator', desc: 'Web fact-checking', color: AppTheme.ecoColor),
    _PipelineNode(icon: '💾', label: 'Archive (Qdrant)', desc: 'RAG memory storage', color: AppTheme.accentPurple),
  ];

  @override
  void initState() {
    super.initState();
    _progressController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
  }

  @override
  void dispose() {
    _progressController.dispose();
    super.dispose();
  }

  Future<void> _runPipeline() async {
    if (_isRunning) return;
    setState(() {
      _isRunning = true;
      _activeStep = -1;
    });

    for (int i = 0; i < _nodes.length; i++) {
      await Future.delayed(const Duration(milliseconds: 700));
      if (mounted) {
        setState(() => _activeStep = i);
        _progressController.forward(from: 0);
      }
    }

    await Future.delayed(const Duration(milliseconds: 800));
    if (mounted) {
      setState(() {
        _isRunning = false;
        _activeStep = _nodes.length; // All done
      });
    }
  }

  void _resetPipeline() {
    setState(() {
      _activeStep = -1;
      _isRunning = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildHeader(),
          const SizedBox(height: 20),
          _buildPipelineNodes(),
          const SizedBox(height: 24),
          _buildRunButton(),
          const SizedBox(height: 24),
          _buildArchitectureInfo(),
        ],
      ),
    );
  }

  Widget _buildHeader() {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: LinearGradient(
          colors: [
            AppTheme.accentPurple.withOpacity(0.15),
            AppTheme.epiColor.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.accentPurple.withOpacity(0.3)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Text(
                '🤖',
                style: const TextStyle(fontSize: 28),
              ),
              const SizedBox(width: 10),
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'AI Agent Pipeline',
                    style: GoogleFonts.orbitron(
                      fontSize: 16,
                      fontWeight: FontWeight.w700,
                      color: AppTheme.textPrimary,
                    ),
                  ),
                  Text(
                    'LangGraph Architecture',
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 12,
                      color: AppTheme.accentPurple,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            'Six specialized nodes working in sequence to triage, analyze, verify, and archive every threat signal with RAG-powered memory.',
            style: GoogleFonts.spaceGrotesk(
              fontSize: 13,
              color: AppTheme.textSecondary,
              height: 1.5,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPipelineNodes() {
    return Column(
      children: List.generate(_nodes.length, (index) {
        final node = _nodes[index];
        final isActive = _activeStep == index;
        final isCompleted = _activeStep > index;

        return Column(
          children: [
            AnimatedContainer(
              duration: const Duration(milliseconds: 400),
              curve: Curves.easeOut,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isActive
                    ? node.color.withOpacity(0.08)
                    : isCompleted
                        ? AppTheme.bgCardLighter
                        : AppTheme.bgCard,
                borderRadius: BorderRadius.circular(14),
                border: Border.all(
                  color: isActive
                      ? node.color
                      : isCompleted
                          ? node.color.withOpacity(0.4)
                          : AppTheme.borderColor,
                  width: isActive ? 1.5 : 1,
                ),
                boxShadow: isActive
                    ? [BoxShadow(color: node.color.withOpacity(0.2), blurRadius: 16)]
                    : [],
              ),
              child: Row(
                children: [
                  // Step number
                  Container(
                    width: 32,
                    height: 32,
                    decoration: BoxDecoration(
                      shape: BoxShape.circle,
                      color: isCompleted
                          ? node.color
                          : isActive
                              ? node.color.withOpacity(0.2)
                              : AppTheme.borderColor,
                    ),
                    child: Center(
                      child: isCompleted
                          ? const Icon(Icons.check_rounded, size: 16, color: Colors.black)
                          : isActive
                              ? SizedBox(
                                  width: 16,
                                  height: 16,
                                  child: CircularProgressIndicator(
                                    color: node.color,
                                    strokeWidth: 2,
                                  ),
                                )
                              : Text(
                                  '${index + 1}',
                                  style: GoogleFonts.orbitron(
                                    fontSize: 12,
                                    color: AppTheme.textMuted,
                                    fontWeight: FontWeight.w700,
                                  ),
                                ),
                    ),
                  ),
                  const SizedBox(width: 14),
                  // Icon
                  Text(node.icon, style: const TextStyle(fontSize: 22)),
                  const SizedBox(width: 12),
                  // Labels
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          node.label,
                          style: GoogleFonts.spaceGrotesk(
                            fontSize: 14,
                            fontWeight: FontWeight.w700,
                            color: isActive || isCompleted ? AppTheme.textPrimary : AppTheme.textSecondary,
                          ),
                        ),
                        Text(
                          node.desc,
                          style: GoogleFonts.spaceGrotesk(
                            fontSize: 12,
                            color: AppTheme.textMuted,
                          ),
                        ),
                      ],
                    ),
                  ),
                  // Status badge
                  if (isActive)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: node.color.withOpacity(0.2),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: node.color.withOpacity(0.6)),
                      ),
                      child: Text(
                        'RUNNING',
                        style: GoogleFonts.orbitron(
                          fontSize: 8,
                          color: node.color,
                          fontWeight: FontWeight.w700,
                          letterSpacing: 1,
                        ),
                      ),
                    )
                  else if (isCompleted)
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                      decoration: BoxDecoration(
                        color: AppTheme.ecoColor.withOpacity(0.15),
                        borderRadius: BorderRadius.circular(8),
                      ),
                      child: Text(
                        'DONE',
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
            ),
            if (index < _nodes.length - 1)
              Padding(
                padding: const EdgeInsets.symmetric(vertical: 6),
                child: Row(
                  children: [
                    const SizedBox(width: 54),
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 400),
                      width: 2,
                      height: 20,
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: isCompleted || (isActive && index < _activeStep)
                              ? [_nodes[index].color, _nodes[index + 1].color]
                              : [AppTheme.borderColor, AppTheme.borderColor],
                          begin: Alignment.topCenter,
                          end: Alignment.bottomCenter,
                        ),
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                  ],
                ),
              ),
          ],
        );
      }),
    );
  }

  Widget _buildRunButton() {
    final isComplete = _activeStep >= _nodes.length;

    return Center(
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          GestureDetector(
            onTap: _isRunning ? null : _runPipeline,
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 250),
              padding: const EdgeInsets.symmetric(horizontal: 28, vertical: 14),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: _isRunning
                      ? [AppTheme.borderColor, AppTheme.borderColor]
                      : isComplete
                          ? [AppTheme.ecoColor, AppTheme.ecoColor.withOpacity(0.7)]
                          : [AppTheme.accentPurple, AppTheme.epiColor],
                ),
                borderRadius: BorderRadius.circular(30),
                boxShadow: _isRunning
                    ? []
                    : [
                        BoxShadow(
                          color: (isComplete ? AppTheme.ecoColor : AppTheme.accentPurple).withOpacity(0.4),
                          blurRadius: 20,
                          offset: const Offset(0, 6),
                        ),
                      ],
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    _isRunning
                        ? Icons.hourglass_top_rounded
                        : isComplete
                            ? Icons.check_circle_rounded
                            : Icons.play_arrow_rounded,
                    color: Colors.white,
                    size: 20,
                  ),
                  const SizedBox(width: 8),
                  Text(
                    _isRunning
                        ? 'Running Pipeline...'
                        : isComplete
                            ? 'Pipeline Complete!'
                            : 'Run Pipeline Demo',
                    style: GoogleFonts.spaceGrotesk(
                      fontSize: 15,
                      fontWeight: FontWeight.w700,
                      color: Colors.white,
                    ),
                  ),
                ],
              ),
            ),
          ),
          if (isComplete) ...[
            const SizedBox(width: 12),
            GestureDetector(
              onTap: _resetPipeline,
              child: Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.bgCard,
                  shape: BoxShape.circle,
                  border: Border.all(color: AppTheme.borderColor),
                ),
                child: const Icon(Icons.refresh_rounded, color: AppTheme.textSecondary, size: 20),
              ),
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildArchitectureInfo() {
    final items = [
      ('LangGraph', 'Multi-agent workflow orchestration with stateful nodes', AppTheme.accentPurple),
      ('Qdrant', 'Vector database for RAG historical memory', AppTheme.epiColor),
      ('Flash LLM', 'Low-latency model for rapid triage decisions', AppTheme.warningYellow),
      ('Gemini Pro', 'Deep reasoning for full threat analysis reports', AppTheme.ecoColor),
    ];

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '⚙️ Stack Architecture',
          style: GoogleFonts.spaceGrotesk(
            fontSize: 16,
            fontWeight: FontWeight.w700,
            color: AppTheme.textPrimary,
          ),
        ),
        const SizedBox(height: 12),
        ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 10),
              child: Container(
                padding: const EdgeInsets.all(14),
                decoration: BoxDecoration(
                  color: AppTheme.bgCard,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: item.$3.withOpacity(0.25)),
                ),
                child: Row(
                  children: [
                    Container(
                      width: 4,
                      height: 40,
                      decoration: BoxDecoration(
                        color: item.$3,
                        borderRadius: BorderRadius.circular(2),
                      ),
                    ),
                    const SizedBox(width: 12),
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          item.$1,
                          style: GoogleFonts.orbitron(
                            fontSize: 13,
                            fontWeight: FontWeight.w700,
                            color: item.$3,
                          ),
                        ),
                        const SizedBox(height: 2),
                        SizedBox(
                          width: MediaQuery.of(context).size.width - 100,
                          child: Text(
                            item.$2,
                            style: GoogleFonts.spaceGrotesk(
                              fontSize: 12,
                              color: AppTheme.textSecondary,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            )),
      ],
    );
  }
}

class _PipelineNode {
  final String icon;
  final String label;
  final String desc;
  final Color color;

  const _PipelineNode({
    required this.icon,
    required this.label,
    required this.desc,
    required this.color,
  });
}
