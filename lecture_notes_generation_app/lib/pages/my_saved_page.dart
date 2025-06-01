import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class MySavedPage extends StatefulWidget {
  const MySavedPage({super.key});

  @override
  State<MySavedPage> createState() => _MySavedPageState();
}

class _MySavedPageState extends State<MySavedPage> {
  List<String> savedItems = [];

  @override
  void initState() {
    super.initState();
    _loadSavedItems();
  }

  Future<void> _loadSavedItems() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      savedItems = prefs.getStringList('saved_items') ?? [];
    });
  }

  Future<void> _deleteItem(int index) async {
    final prefs = await SharedPreferences.getInstance();
    savedItems.removeAt(index);
    await prefs.setStringList('saved_items', savedItems);
    setState(() {});
  }

  Future<void> _deleteAll() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('saved_items');
    setState(() {
      savedItems.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        children: [
          if (savedItems.isNotEmpty)
            Align(
              alignment: Alignment.centerRight,
              child: TextButton.icon(
                onPressed: () {
                  showDialog(
                    context: context,
                    builder: (_) => AlertDialog(
                      title: const Text("Delete All Notes"),
                      content: const Text(
                          "Are you sure you want to delete all saved notes?"),
                      actions: [
                        TextButton(
                          onPressed: () => Navigator.pop(context),
                          child: const Text("Cancel"),
                        ),
                        TextButton(
                          onPressed: () {
                            _deleteAll();
                            Navigator.pop(context);
                          },
                          child: const Text("Delete All",
                              style: TextStyle(color: Colors.red)),
                        ),
                      ],
                    ),
                  );
                },
                icon: const Icon(Icons.delete_forever, color: Colors.red),
                label: const Text("Delete All",
                    style: TextStyle(color: Colors.red)),
              ),
            ),
          Expanded(
            child: savedItems.isEmpty
                ? const Center(child: Text("No saved notes yet."))
                : ListView.builder(
                    itemCount: savedItems.length,
                    itemBuilder: (context, index) {
                      final item = savedItems[index];
                      final preview = item.split('\n').take(3).join('\n');

                      return ExpansionTile(
                        title: Text("Saved Note #${index + 1}",
                            style:
                                const TextStyle(fontWeight: FontWeight.bold)),
                        subtitle: Text(preview),
                        children: [
                          Padding(
                            padding: const EdgeInsets.symmetric(
                                horizontal: 16.0, vertical: 8),
                            child: Text(item),
                          ),
                          TextButton.icon(
                            onPressed: () => _deleteItem(index),
                            icon: const Icon(Icons.delete, color: Colors.red),
                            label: const Text("Delete",
                                style: TextStyle(color: Colors.red)),
                          )
                        ],
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }
}
