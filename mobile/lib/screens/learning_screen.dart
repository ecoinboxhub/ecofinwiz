import 'package:flutter/material.dart';
import '../config/theme.dart';
import 'articles_screen.dart';
import 'courses_screen.dart';
import 'forum_screen.dart';
import 'news_screen.dart';

class LearningScreen extends StatelessWidget {
  const LearningScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Learning Hub')),
      body: ListView(padding: const EdgeInsets.all(16), children: [
        const Card(child: ListTile(leading: Icon(Icons.menu_book_outlined, color: AppTheme.primary),
          title: Text('Your Progress', style: TextStyle(fontWeight: FontWeight.bold)), subtitle: Text('Continue where you left off'))),
        const SizedBox(height: 16),
        _SectionCard(icon: Icons.school, label: 'Courses & Lessons', desc: 'Financial literacy with quizzes', color: AppTheme.primary, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const CoursesScreen()))),
        const SizedBox(height: 8),
        _SectionCard(icon: Icons.article, label: 'Articles & Blog', desc: 'Investment and financial articles', color: AppTheme.gold, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ArticlesScreen()))),
        const SizedBox(height: 8),
        _SectionCard(icon: Icons.assignment, label: 'Financial News', desc: 'Latest business and economy news', color: AppTheme.mint, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const NewsScreen()))),
        const SizedBox(height: 8),
        _SectionCard(icon: Icons.forum, label: 'Community Forum', desc: 'Discuss and ask questions', color: AppTheme.primary, onTap: () => Navigator.push(context, MaterialPageRoute(builder: (_) => const ForumScreen()))),
      ]),
    );
  }
}

class _SectionCard extends StatelessWidget {
  final IconData icon; final String label, desc; final Color color; final VoidCallback? onTap;
  const _SectionCard({required this.icon, required this.label, required this.desc, required this.color, this.onTap});

  @override
  Widget build(BuildContext context) {
    return Card(child: ListTile(
      onTap: onTap,
      leading: Container(width: 48, height: 48, decoration: BoxDecoration(color: color.withOpacity(0.1), borderRadius: BorderRadius.circular(12)), child: Icon(icon, color: color)),
      title: Text(label, style: const TextStyle(fontWeight: FontWeight.w600)),
      subtitle: Text(desc, style: const TextStyle(fontSize: 12)),
      trailing: const Icon(Icons.chevron_right),
    ));
  }
}