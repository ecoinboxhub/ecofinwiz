import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'lesson_screen.dart';

class CourseDetailScreen extends StatefulWidget {
  final String courseId;
  const CourseDetailScreen({super.key, required this.courseId});

  @override
  State<CourseDetailScreen> createState() => _CourseDetailScreenState();
}

class _CourseDetailScreenState extends State<CourseDetailScreen> {
  final _api = ApiService();
  Map<String, dynamic>? _course;
  Map<String, dynamic>? _progress;

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { _course = await _api.get('/courses/${widget.courseId}') as Map<String, dynamic>?; } catch (_) {}
    try { _progress = await _api.get('/courses/${widget.courseId}/progress') as Map<String, dynamic>?; } catch (_) {}
    if (mounted) setState(() {});
  }

  Future<void> _enroll() async {
    try { await _api.post('/courses/${widget.courseId}/enroll'); } catch (_) {}
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    final course = _course;
    return Scaffold(
      appBar: AppBar(title: const Text('Course')),
      body: course == null
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(onRefresh: _load, child: ListView(padding: const EdgeInsets.all(16), children: [
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                Row(children: [
                  Container(width: 48, height: 48, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(12)), child: const Icon(Icons.school, color: AppTheme.primary, size: 24)),
                  const SizedBox(width: 12),
                  Expanded(child: Text(course['title'] ?? '', style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold))),
                ]),
                const SizedBox(height: 12),
                Text(course['description'] ?? '', style: const TextStyle(fontSize: 13)),
                const SizedBox(height: 12),
                Wrap(spacing: 8, runSpacing: 8, children: [
                  _chip(course['difficulty'] ?? '', AppTheme.primary),
                  _chip('${course['lesson_count'] ?? 0} lessons', AppTheme.gold),
                  _chip('${course['duration_hours'] ?? 0} hours', AppTheme.mint),
                ]),
                if (_progress != null) ...[
                  const SizedBox(height: 16),
                  LinearProgressIndicator(value: ((_progress!['percentage'] as num?) ?? 0) / 100, color: AppTheme.primary, backgroundColor: AppTheme.border),
                  const SizedBox(height: 4),
                  Text('${_progress!['completed_lessons'] ?? 0}/${_progress!['total_lessons'] ?? 0} lessons completed', style: const TextStyle(fontSize: 12)),
                ],
              ]))),
              const SizedBox(height: 8),
              Card(child: Padding(padding: const EdgeInsets.all(16), child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
                const Text('Lessons', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                ...((course['lessons'] as List?) ?? []).map((l) => ListTile(
                  contentPadding: EdgeInsets.zero,
                  leading: Container(width: 36, height: 36, decoration: BoxDecoration(color: AppTheme.goldSoft, borderRadius: BorderRadius.circular(10)), child: const Icon(Icons.play_arrow, color: AppTheme.gold, size: 20)),
                  title: Text(l['title'] ?? '', style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
                  subtitle: Text('${l['duration_minutes'] ?? 0} min', style: const TextStyle(fontSize: 12)),
                  trailing: const Icon(Icons.chevron_right),
                  onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => LessonScreen(courseId: widget.courseId, lessonId: l['id'] ?? ''))),
                )),
                if (((course['lessons'] as List?) ?? []).isEmpty)
                  const Padding(padding: EdgeInsets.symmetric(vertical: 8), child: Text('No lessons yet', style: TextStyle(color: AppTheme.muted))),
              ]))),
              const SizedBox(height: 8),
              if ((_progress?['completed_lessons'] ?? 0) == 0)
                SizedBox(width: double.infinity, child: ElevatedButton(onPressed: _enroll, child: const Text('Enroll in this course'))),
            ])),
    );
  }

  Widget _chip(String text, Color color) {
    return Container(padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4), decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(20)),
      child: Text(text, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w600)));
  }
}