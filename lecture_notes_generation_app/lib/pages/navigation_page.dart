import 'package:flutter/material.dart';
import 'package:lecture_notes_generation_app/pages/generation_page.dart';
import 'package:lecture_notes_generation_app/pages/my_saved_page.dart';

class NavigationPage extends StatefulWidget {
  const NavigationPage({super.key});

  @override
  State<NavigationPage> createState() => _HomePageState();
}

class _HomePageState extends State<NavigationPage> {
  int _savedpageKey = 0;
  int _selectedIndex = 0;

  // Change _pages from a list to a getter method that returns a new list each time
  List<Widget> get _pages => [
        const GenerationPage(),
        MySavedPage(key: ValueKey(_savedpageKey)), // Use a key to force rebuild
      ];

  void _onItemTapped(int index) {
    if (index == 1) {
      setState(() {
        _savedpageKey++;
      });
    }
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("Notes Generation App"),
        backgroundColor: Colors.grey.shade300,
      ),
      backgroundColor: Colors.grey.shade300,
      body: IndexedStack(
        index: _selectedIndex,
        children: _pages, // Now use _pages getter, no parentheses
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
        items: [
          BottomNavigationBarItem(
            icon: _selectedIndex == 0
                ? Container(
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: const EdgeInsets.all(10),
                    child: const Icon(Icons.menu_book),
                  )
                : const Icon(Icons.menu_book),
            label: "Generate Notes",
          ),
          BottomNavigationBarItem(
            icon: _selectedIndex == 1
                ? Container(
                    decoration: BoxDecoration(
                      color: Colors.grey.shade300,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    padding: const EdgeInsets.all(10),
                    child: const Icon(Icons.save_alt),
                  )
                : const Icon(Icons.save_alt),
            label: "Saved Notes",
          ),
        ],
      ),
    );
  }
}
