import 'package:flutter/material.dart';
import 'screens/home_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const GlobalSentryApp());
}

class GlobalSentryApp extends StatelessWidget {
  const GlobalSentryApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'GlobalSentry',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      home: const HomeScreen(),
    );
  }
}
