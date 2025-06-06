import 'package:flutter/material.dart';
import 'package:lecture_notes_generation_app/pages/navigation_page.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: "Flutter",
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: const NavigationPage(),
    );
  }
}
