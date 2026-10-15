import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:vestlly/models/statemanager.dart';
import 'package:vestlly/pages/homepage.dart';

void main() {
  runApp(
    ChangeNotifierProvider(
      create: (_) => StateManager(),
      child: MainApp(),
    ),
  );
}

// TODO:
// - make widgets dynamic
// - connect to server (also need to make the server)
// -- need both data querying and transaction initiations
// - finish the portfolio page
// - start adding automation customizations and toggling
// -- start with mean reversion
// -- focus on universal(or portfolio level) automation atrributes, eg. which stocks are included, what (if anything) happens with cash account


class MainApp extends StatelessWidget {
  MainApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: "vestlly",
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(
          brightness: Brightness.dark,
          seedColor: Colors.blueGrey,
          // seedColor: Colors.deepPurple,
          // seedColor: Colors.lightGreen,
        ),
        fontFamily: "Inter",
        textTheme: const TextTheme(
          titleLarge: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            fontWeight: FontWeight.bold,
            fontSize: 28,
          ),
          titleMedium: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            fontWeight: FontWeight.bold,
            fontSize: 18,
          ),
          titleSmall: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            fontWeight: FontWeight.bold,
            fontSize: 12,
          ),
          bodyMedium: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            fontSize: 16,
          ),
          bodySmall: TextStyle(
            fontFamily: "Inter",
            decoration: TextDecoration.none,
            fontSize: 12,
          ),
        ),
      ),
      home: HomePage(),
    );
  }
}