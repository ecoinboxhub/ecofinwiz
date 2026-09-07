import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import '../services/local_db.dart';
import '../widgets/voice_button.dart';

class AdvisorScreen extends StatefulWidget {
  const AdvisorScreen({super.key});

  @override
  State<AdvisorScreen> createState() => _AdvisorScreenState();
}

class _AdvisorScreenState extends State<AdvisorScreen> {
  static const String _channel = 'advisor';
  final _api = ApiService();
  final _local = LocalDb.instance;
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<Map<String, String>> _messages = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    try {
      final history = await _local.chatHistory();
      final rows = history.where((row) => (row['role'] as String? ?? '').startsWith('${_channel}_')).toList().reversed.toList();
      if (rows.isEmpty) return;
      setState(() {
        _messages.addAll(rows.map((row) => {
          'role': (row['role'] as String).replaceFirst('${_channel}_', ''),
          'content': row['content'] as String? ?? '',
        }));
      });
    } catch (_) {
      // Chat still works when local history is unavailable.
    }
  }

  Future<void> _persist(String userText, String assistantText) async {
    try {
      await _local.appendChatMessage('${_channel}_user', userText);
      await _local.appendChatMessage('${_channel}_assistant', assistantText);
    } catch (_) {}
  }

  Future<void> _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;
    setState(() {
      _messages.add({'role': 'user', 'content': text});
      _messages.add({'role': 'assistant', 'content': ''});
      _loading = true;
    });
    _controller.clear();
    String streaming = '';
    try {
      await _api.stream('/ai/advisor/chat', body: {'message': text}, onEvent: (event) {
        switch (event['event']) {
          case 'token':
            streaming += (event['token'] ?? '') as String;
            setState(() => _messages[_messages.length - 1] = {'role': 'assistant', 'content': streaming});
          case 'done':
            break;
          case 'error':
            setState(() => _messages[_messages.length - 1] = {'role': 'assistant', 'content': event['message'] ?? 'Service temporarily unavailable. Please try again.'});
          default:
            break;
        }
      });
      if (_messages.isNotEmpty && _messages.last['content']?.isEmpty == true) {
        setState(() => _messages[_messages.length - 1] = {'role': 'assistant', 'content': 'No response'});
      }
    } catch (_) {
      setState(() => _messages[_messages.length - 1] = {'role': 'assistant', 'content': 'Sorry, I couldn\'t process that.'});
    }
    await _persist(text, _messages.last['content'] ?? '');
    setState(() => _loading = false);
    WidgetsBinding.instance.addPostFrameCallback((_) => _scrollController.jumpTo(_scrollController.position.maxScrollExtent));
  }

  @override
  void dispose() { _controller.dispose(); _scrollController.dispose(); super.dispose(); }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Row(mainAxisSize: MainAxisSize.min, children: [Icon(Icons.forum, color: AppTheme.primary, size: 20), SizedBox(width: 6), Text('Kemi')]),
        actions: [IconButton(onPressed: () => setState(() => _messages.clear()), icon: const Icon(Icons.refresh))]),
      body: Column(children: [
        Expanded(child: _messages.isEmpty
          ? Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [
              Container(width: 64, height: 64, decoration: const BoxDecoration(shape: BoxShape.circle, color: AppTheme.mintSoft),
                child: const Icon(Icons.waving_hand, size: 32, color: AppTheme.primary)), const SizedBox(height: 16),
              const Text("Hi! I'm Kemi", style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppTheme.ink)),
              const SizedBox(height: 8), const Text('Your personal finance coach.', style: TextStyle(color: AppTheme.muted)),
              const SizedBox(height: 16),
              ...['How do I start budgeting?', "What's the best way to save?", 'Explain compound interest'].map((q) => Padding(padding: const EdgeInsets.only(bottom: 8), child: ActionChip(label: Text(q, style: const TextStyle(fontSize: 12)), onPressed: () { _controller.text = q; _send(); }))),
            ]))
          : ListView.builder(controller: _scrollController, padding: const EdgeInsets.all(16), itemCount: _messages.length + (_loading ? 1 : 0), itemBuilder: (_, i) {
              if (i == _messages.length) return const Padding(padding: EdgeInsets.all(16), child: Center(child: CircularProgressIndicator()));
              final m = _messages[i]; final isUser = m['role'] == 'user';
              return Align(alignment: isUser ? Alignment.centerRight : Alignment.centerLeft, child: Container(
                margin: const EdgeInsets.only(bottom: 8), padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                decoration: BoxDecoration(color: isUser ? AppTheme.primary : AppTheme.border, borderRadius: BorderRadius.only(
                  topLeft: const Radius.circular(16), topRight: const Radius.circular(16), bottomLeft: isUser ? const Radius.circular(16) : Radius.zero, bottomRight: isUser ? Radius.zero : const Radius.circular(16))),
                constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
                child: Row(mainAxisSize: MainAxisSize.min, children: [
                  Flexible(child: Text(m['content'] ?? '', style: TextStyle(color: isUser ? Colors.white : AppTheme.ink, fontSize: 14))),
                  if (!isUser) ...[const SizedBox(width: 6), VoiceButton(speakText: m['content'], size: 16, color: AppTheme.primary)],
                ]),
              ));
            })),
        Container(padding: const EdgeInsets.all(16), decoration: const BoxDecoration(color: Colors.white, border: Border(top: BorderSide(color: AppTheme.border))), child: Row(children: [
          Expanded(child: TextField(key: const Key('chat_input'), controller: _controller, decoration: const InputDecoration(hintText: 'Ask Kemi...', isDense: true), onSubmitted: (_) => _send())),
          const SizedBox(width: 8),
          VoiceButton(onTranscript: (t) { _controller.text = t; }, color: AppTheme.primary),
          const SizedBox(width: 4),
          IconButton.filled(onPressed: _send, icon: const Icon(Icons.send, color: Colors.white), style: IconButton.styleFrom(backgroundColor: AppTheme.primary)),
        ])),
      ]),
    );
  }
}
