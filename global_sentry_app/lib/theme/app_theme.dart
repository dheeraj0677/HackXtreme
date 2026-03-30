import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

class AppTheme {
  // --- Core Modern Light Colors ---
  static const Color bgDeep = Color(0xFFF8FAFC); // Main background (Very light Slate)
  static const Color bgCard = Color(0xFFFFFFFF); // Pure white cards
  static const Color bgCardLighter = Color(0xFFF1F5F9); // Lighter header highlights
  static const Color borderColor = Color(0xFFE2E8F0); // Subtle Slate border

  // --- Sentry-specific Colors (Adjusted for Light Theme) ---
  static const Color epiColor = Color(0xFF0369A1); // Sky blue focus
  static const Color epiGlow = Color(0x1A0369A1); // Subtle Sky Blue tint
  static const Color epiDark = Color(0xFF0C4A6E); 

  static const Color ecoColor = Color(0xFF059669); // Emerald Green focus
  static const Color ecoGlow = Color(0x1A059669); // Subtle Emerald tint
  static const Color ecoDark = Color(0xFF064E3B);

  static const Color supplyColor = Color(0xFFD97706); // Amber/Orange focus
  static const Color supplyGlow = Color(0x1AD97706); // Subtle Amber tint
  static const Color supplyDark = Color(0xFF78350F);

  static const Color accentPurple = Color(0xFF7C3AED); // Violet
  static const Color accentPurpleGlow = Color(0x1A7C3AED);

  // --- Typography ---
  static const Color textPrimary = Color(0xFF0F172A); // Deep Slate blue/black
  static const Color textSecondary = Color(0xFF334155); // Dark Slate blue
  static const Color textMuted = Color(0xFF64748B); // Medium Slate grey

  // --- Status Colors ---
  static const Color dangerRed = Color(0xFFDC2626);
  static const Color warningYellow = Color(0xFFCA8A04);
  static const Color successGreen = Color(0xFF059669);

  static ThemeData get lightTheme {
    return ThemeData(
      brightness: Brightness.light,
      scaffoldBackgroundColor: bgDeep,
      colorScheme: const ColorScheme.light(
        primary: epiColor,
        secondary: ecoColor,
        surface: bgCard,
        error: dangerRed,
        outline: borderColor,
      ),
      textTheme: GoogleFonts.spaceGroteskTextTheme(
        const TextTheme(
          displayLarge: TextStyle(color: textPrimary, fontWeight: FontWeight.w800),
          displayMedium: TextStyle(color: textPrimary, fontWeight: FontWeight.w800),
          displaySmall: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
          headlineLarge: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
          headlineMedium: TextStyle(color: textPrimary, fontWeight: FontWeight.w600),
          headlineSmall: TextStyle(color: textPrimary, fontWeight: FontWeight.w600),
          titleLarge: TextStyle(color: textPrimary, fontWeight: FontWeight.w700),
          titleMedium: TextStyle(color: textPrimary, fontWeight: FontWeight.w600),
          titleSmall: TextStyle(color: textSecondary, fontWeight: FontWeight.w600),
          bodyLarge: TextStyle(color: textPrimary),
          bodyMedium: TextStyle(color: textSecondary),
          bodySmall: TextStyle(color: textMuted),
        ),
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: bgCard,
        elevation: 0,
        centerTitle: false,
        titleTextStyle: GoogleFonts.orbitron(
          color: textPrimary,
          fontSize: 18,
          fontWeight: FontWeight.w900,
          letterSpacing: 1.5,
        ),
        iconTheme: const IconThemeData(color: textPrimary),
      ),
      cardTheme: CardTheme(
        color: bgCard,
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(16),
          side: const BorderSide(color: borderColor),
        ),
      ),
      useMaterial3: true,
    );
  }

  // Maintaining dark theme for future toggle support
  static ThemeData get darkTheme {
    return ThemeData(
      brightness: Brightness.dark,
      scaffoldBackgroundColor: const Color(0xFF040B14),
      // ... previous dark theme configuration ...
      useMaterial3: true,
    );
  }
}
