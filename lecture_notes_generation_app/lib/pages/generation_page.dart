import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:youtube_player_flutter/youtube_player_flutter.dart';
import 'package:shared_preferences/shared_preferences.dart';

class GenerationPage extends StatefulWidget {
  const GenerationPage({super.key});

  @override
  State<GenerationPage> createState() => _GenerationPageState();
}

class _GenerationPageState extends State<GenerationPage> {
  final TextEditingController _urlController = TextEditingController();
  YoutubePlayerController? _youtubeController;
  bool _isLoading = false;
  bool _showPlayer = false;
  String notes = '';
  String questions = '';
  String _selectedTab = 'Notes';

  Future<void> _getNotesAndQuestions() async {
    final url = _urlController.text.trim();
    final videoId = YoutubePlayer.convertUrlToId(url);

    if (videoId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid YouTube URL')),
      );
      return;
    }

    setState(() {
      _showPlayer = true;
      _isLoading = true;
      notes = '';
      questions = '';
    });

    _youtubeController?.dispose();
    _youtubeController = YoutubePlayerController(
      initialVideoId: videoId,
      flags: const YoutubePlayerFlags(
        autoPlay: false,
        loop: false,
        mute: false,
        enableCaption: true,
      ),
    );

    try {
      final response = await http.post(
        Uri.parse("https://4f80-152-58-186-224.ngrok-free.app/process"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"url": url}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          notes = (data['notes'] as List<dynamic>).join('\n\n');
          questions = (data['questions'] as List<dynamic>).join('\n\n');
        });
      } else {
        throw Exception("Failed to fetch data from server.");
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${e.toString()}')),
      );
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _saveContent() async {
    final prefs = await SharedPreferences.getInstance();
    final List<String> currentSaved = prefs.getStringList('saved_items') ?? [];
    final combined = 'Notes:\n$notes\n\nQuestions:\n$questions';
    currentSaved.add(combined);
    await prefs.setStringList('saved_items', currentSaved);

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Notes saved successfully!')),
    );
  }

  @override
  void dispose() {
    _youtubeController?.dispose();
    _urlController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: IntrinsicHeight(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  children: [
                    AnimatedContainer(
                      duration: const Duration(milliseconds: 500),
                      height: 200,
                      decoration: BoxDecoration(
                        color: _showPlayer ? Colors.transparent : Colors.black,
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: _showPlayer && _youtubeController != null
                          ? YoutubePlayer(
                              controller: _youtubeController!,
                              showVideoProgressIndicator: true,
                            )
                          : const Center(
                              child: Text(
                                'Video Preview',
                                style: TextStyle(color: Colors.white),
                              ),
                            ),
                    ),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        Expanded(
                          child: TextField(
                            controller: _urlController,
                            decoration: const InputDecoration(
                              border: OutlineInputBorder(),
                              labelText: 'Enter YouTube URL',
                            ),
                          ),
                        ),
                        const SizedBox(width: 10),
                        ElevatedButton(
                          onPressed: _isLoading ? null : _getNotesAndQuestions,
                          child: const Text("Get Notes"),
                        ),
                      ],
                    ),
                    const SizedBox(height: 20),
                    Container(
                      height: 2,
                      width: double.infinity,
                      color: Colors.grey.shade600,
                    ),
                    const SizedBox(height: 20),
                    if (_isLoading)
                      Column(
                        children: const [
                          CircularProgressIndicator(),
                          SizedBox(height: 10),
                          Text("Generating notes and questions..."),
                        ],
                      )
                    else if (notes.isNotEmpty || questions.isNotEmpty)
                      Expanded(
                        child: Column(
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                ToggleButtons(
                                  isSelected: [
                                    _selectedTab == 'Notes',
                                    _selectedTab == 'Questions'
                                  ],
                                  onPressed: (index) {
                                    setState(() {
                                      _selectedTab =
                                          index == 0 ? 'Notes' : 'Questions';
                                    });
                                  },
                                  children: const [
                                    Padding(
                                      padding:
                                          EdgeInsets.symmetric(horizontal: 16),
                                      child: Text('Notes'),
                                    ),
                                    Padding(
                                      padding:
                                          EdgeInsets.symmetric(horizontal: 16),
                                      child: Text('Questions'),
                                    ),
                                  ],
                                ),
                                ElevatedButton.icon(
                                  onPressed: _saveContent,
                                  icon: const Icon(Icons.save_alt),
                                  label: const Text("Save"),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Expanded(
                              child: SingleChildScrollView(
                                child: Text(
                                  _selectedTab == 'Notes' ? notes : questions,
                                  style: const TextStyle(fontSize: 16),
                                ),
                              ),
                            ),
                          ],
                        ),
                      ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
