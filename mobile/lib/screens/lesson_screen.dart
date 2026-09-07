import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';

class LessonScreen extends StatefulWidget {
  final String courseId, lessonId;
  const LessonScreen({super.key, required this.courseId, required this.lessonId});

  @override
  State<LessonScreen> createState() => _LessonScreenState();
}

class _LessonScreenState extends State<LessonScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _lesson;
  final List<int> _answers = [];
  Map<String, dynamic>? _result;
  bool _submitting = false;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { _lesson = await _api.get('/courses/${widget.courseId}/lessons/${widget.lessonId}') as Map<String, dynamic>?; } catch (_) {}
    if (mounted) setState(() {});
  }

  Future<void> _submit() async {
    final quiz = (_lesson?['quiz'] as Map<String, dynamic>?);
    final questions = (quiz?['questions'] as List?) ?? [];
    if (_answers.length != questions.length) return;
    setState(() => _submitting = true);
    try {
      _result = await _api.post('/courses/${widget.courseId}/lessons/${widget.lessonId}/quiz',
        body: {'course_id': widget.courseId, 'lesson_id': widget.lessonId, 'answers': _answers}) as Map<String, dynamic>?;
    } catch (_) {}
    if (mounted) setState(() => _submitting = false);
  }

  Future<void> _complete() async {
    try { await _api.post('/courses/${widget.courseId}/lessons/${widget.lessonId}/complete'); } catch (_) {}
    if (mounted) Navigator.pop(context);
  }

  @override
  Widget build(BuildContext context) {
    final lesson = _lesson;
    if (lesson == null) return Scaffold(appBar: AppBar(title: const Text('Lesson')), body: const Center(child: CircularProgressIndicator()));
    final quiz = (lesson['quiz'] as Map<String, dynamic>?);
    final questions = (quiz?['questions'] as List?) ?? [];
    return Scaffold(
      appBar: AppBar(title: const Text('Lesson')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text(lesson['title'] ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          Text('${lesson['duration_minutes'] ?? 0} min read', style: const TextStyle(color: AppTheme.muted, fontSize: 12)),
          const SizedBox(height: 12),
          Text(lesson['content'] ?? '', style: const TextStyle(fontSize: 14, height: 1.5)),
        ]))),
        if (questions.isNotEmpty) ...[
          const SizedBox(height: 8),
          Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            const Text('Quiz', style: TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 8),
            ...List.generate(questions.length, (q) => _questionCard(q, questions[q])),
            const SizedBox(height: 8),
            if (_result == null)
              SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _submitting ? null : _submit,
                child: _submitting ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white)) : const Text('Submit Quiz')))
            else ...[
              Container(padding: const EdgeInsets.all(12), decoration: BoxDecoration(
                color: _result!['passed'] == true ? AppTheme.mintSoft : AppTheme.errorSoft, borderRadius: BorderRadius.circular(12)),
                child: Text('Score: ${_result!['score']}/${_result!['total']} (${(_result!['percentage'] as num?)?.toStringAsFixed(0)}%) - ${_result!['passed'] == true ? 'Passed' : 'Try again'}',
                  style: TextStyle(color: _result!['passed'] == true ? AppTheme.success : AppTheme.error, fontWeight: FontWeight.w600))),
              const SizedBox(height: 8),
              SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _complete, child: const Text('Mark Lesson Complete'))),
            ],
          ]))),
        ],
      ]),
    );
  }

  Widget _questionCard(int q, dynamic question) {
    final options = (question['options'] as List?) ?? [];
    return Padding(padding: const EdgeInsets.only(bottom: 12), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
      Text('${q + 1}. ${question['question'] ?? ''}', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
      const SizedBox(height: 4),
      ...List.generate(options.length, (o) => RadioListTile<int>(
        dense: true, contentPadding: EdgeInsets.zero, value: o, groupValue: _answers.length > q ? _answers[q] : null,
        title: Text('${options[o]}', style: const TextStyle(fontSize: 13)),
        onChanged: _result == null ? (v) {
          if (v != null) {
            setState(() { if (_answers.length > q) { _answers[q] = v; } else { _answers.add(v); } });
          }
        } : null,
      )),
    ]));
  }
}