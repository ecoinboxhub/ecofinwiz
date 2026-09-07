import 'package:flutter/material.dart';
import '../config/theme.dart';
import '../services/api_service.dart';
import 'course_detail_screen.dart';

class CoursesScreen extends StatefulWidget {
  const CoursesScreen({super.key});

  @override
  State<CoursesScreen> createState() => _CoursesScreenState();
}

class _CoursesScreenState extends State<CoursesScreen> {
  final _api = ApiService();
  List<dynamic> _courses = [];

  @override
  void initState() { super.initState(); _load(); }

  Future<void> _load() async {
    try { final data = await _api.get('/courses'); setState(() => _courses = (data as List?) ?? []); } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Courses')),
      body: RefreshIndicator(onRefresh: _load, child: ListView.builder(padding: const EdgeInsets.all(16), itemCount: _courses.length, itemBuilder: (_, i) {
        final c = _courses[i];
        return Card(child: ListTile(
          leading: Container(width: 44, height: 44, decoration: BoxDecoration(color: AppTheme.mintSoft, borderRadius: BorderRadius.circular(12)), child: const Icon(Icons.school, color: AppTheme.primary, size: 22)),
          title: Text(c['title'] ?? '', style: const TextStyle(fontWeight: FontWeight.w600, fontSize: 14)),
          subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
            Text(c['description'] ?? '', maxLines: 2, overflow: TextOverflow.ellipsis, style: const TextStyle(fontSize: 12)),
            const SizedBox(height: 4),
            Row(children: [
              Text(c['difficulty'] ?? '', style: const TextStyle(color: AppTheme.primary, fontSize: 11, fontWeight: FontWeight.w600)),
              const SizedBox(width: 8),
              Text('${c['lesson_count'] ?? 0} lessons', style: const TextStyle(fontSize: 11)),
              const SizedBox(width: 8),
              Text('${c['duration_hours'] ?? 0}h', style: const TextStyle(fontSize: 11)),
            ]),
          ]),
          isThreeLine: true,
          trailing: const Icon(Icons.chevron_right),
          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => CourseDetailScreen(courseId: c['id'] ?? ''))),
        ));
      })),
    );
  }
}