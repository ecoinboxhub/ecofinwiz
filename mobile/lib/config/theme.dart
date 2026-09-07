import 'package:flutter/material.dart';

class AppTheme {
  static const Color primary = Color(0xFF0E6F73);
  static const Color primaryDark = Color(0xFF094D53);
  static const Color mint = Color(0xFF5FD0B3);
  static const Color mintSoft = Color(0xFFE5F4EF);
  static const Color gold = Color(0xFFD9A441);
  static const Color goldSoft = Color(0xFFFBF0DC);
  static const Color ink = Color(0xFF123334);
  static const Color muted = Color(0xFF5E7371);
  static const Color softMuted = Color(0xFF93A7A3);
  static const Color textPrimary = ink;
  static const Color textSecondary = muted;
  static const Color bg = Color(0xFFF6F9F7);
  static const Color surface = Color(0xFFFFFFFF);
  static const Color border = Color(0xFFE3EBE7);
  static const Color success = Color(0xFF2F9E7F);
  static const Color error = Color(0xFFC65D5A);
  static const Color errorSoft = Color(0xFFFCEAE9);
  static const Color goldDark = Color(0xFF8A6A1F);
  static const Color primaryLight = Color(0xFF55B6A7);
  static const Color lightBackground = Color(0xFFF6F9F7);
  static const Color darkBackground = Color(0xFF0C1E20);
  static const Color lightCardBackground = Color(0xFFFFFFFF);
  static const Color darkCardBackground = Color(0xFF173032);

  static const double screenPadding = 20;
  static const double authPadding = 24;
  static const double gap8 = 8;
  static const double gap12 = 12;
  static const double gap16 = 16;
  static const double gap24 = 24;
  static const double cardRadius = 16;
  static const double inputRadius = 12;
  static const double buttonRadius = 12;
  static const double chipRadius = 12;
  static const double iconTileRadius = 14;
  static const double buttonHeight = 48;

  static ThemeData get lightTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.light,
      colorScheme: const ColorScheme.light(primary: primary, secondary: gold, tertiary: mint, error: error, surface: surface),
      scaffoldBackgroundColor: bg,
      appBarTheme: const AppBarTheme(backgroundColor: surface, foregroundColor: ink, elevation: 0, centerTitle: true,
        titleTextStyle: TextStyle(color: ink, fontSize: 18, fontWeight: FontWeight.bold)),
      cardTheme: CardTheme(color: surface, elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(cardRadius), side: const BorderSide(color: border)),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4)),
      inputDecorationTheme: InputDecorationTheme(filled: true, fillColor: surface,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: border)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: border)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: primary, width: 2)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14)),
      elevatedButtonTheme: ElevatedButtonThemeData(style: ElevatedButton.styleFrom(
        backgroundColor: primary, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(buttonHeight),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(buttonRadius)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600))),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: ink),
        headlineMedium: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: ink),
        titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: ink),
        titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: ink),
        bodyMedium: TextStyle(fontSize: 14, color: muted),
        bodySmall: TextStyle(fontSize: 12, color: softMuted)),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: surface, selectedItemColor: primary, unselectedItemColor: softMuted, type: BottomNavigationBarType.fixed, elevation: 8),
    );
  }

  static ThemeData get darkTheme {
    return ThemeData(
      useMaterial3: true,
      brightness: Brightness.dark,
      colorScheme: const ColorScheme.dark(primary: mint, secondary: gold, tertiary: mint, error: error, surface: darkCardBackground),
      scaffoldBackgroundColor: darkBackground,
      appBarTheme: const AppBarTheme(backgroundColor: darkCardBackground, foregroundColor: Colors.white, elevation: 0, centerTitle: true,
        titleTextStyle: TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
      cardTheme: CardTheme(color: darkCardBackground, elevation: 0,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(cardRadius), side: const BorderSide(color: Colors.white10)),
        margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 4)),
      inputDecorationTheme: InputDecorationTheme(filled: true, fillColor: darkCardBackground,
        border: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: Colors.white12)),
        enabledBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: Colors.white12)),
        focusedBorder: OutlineInputBorder(borderRadius: BorderRadius.circular(inputRadius), borderSide: const BorderSide(color: mint, width: 2)),
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14)),
      elevatedButtonTheme: ElevatedButtonThemeData(style: ElevatedButton.styleFrom(
        backgroundColor: primary, foregroundColor: Colors.white, minimumSize: const Size.fromHeight(buttonHeight),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(buttonRadius)),
        textStyle: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600))),
      textTheme: const TextTheme(
        headlineLarge: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: Colors.white),
        headlineMedium: TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: Colors.white),
        titleLarge: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white),
        titleMedium: TextStyle(fontSize: 16, fontWeight: FontWeight.w600, color: Colors.white),
        bodyMedium: TextStyle(fontSize: 14, color: Colors.white70),
        bodySmall: TextStyle(fontSize: 12, color: Colors.white54)),
      bottomNavigationBarTheme: const BottomNavigationBarThemeData(
        backgroundColor: darkCardBackground, selectedItemColor: mint, unselectedItemColor: Colors.white54, type: BottomNavigationBarType.fixed, elevation: 8),
    );
  }
}

class AppColors {
  static const List<Color> tealMintGradient = [Color(0xFF0E6F73), Color(0xFF5FD0B3)];
  static const List<Color> goldGradient = [Color(0xFFD9A441), Color(0xFFE8B84F)];
  static const List<Color> mintGradient = [Color(0xFF5FD0B3), Color(0xFF2F9E7F)];
}