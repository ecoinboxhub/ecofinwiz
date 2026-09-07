// QA capture harness — renders every feature + sub-feature with mocked data,
// exercises interactions (chat, calculators, filters, plan generation, shell
// tab switching) and writes PNGs as golden files. Run with:
//   flutter test test/screenshots/qa_capture_test.dart --update-goldens
import 'dart:convert';
import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:provider/provider.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:finwize/config/theme.dart';
import 'package:finwize/providers/auth_provider.dart';
import 'package:finwize/providers/connectivity_provider.dart';
import 'package:finwize/services/api_service.dart';
import 'package:finwize/services/local_db.dart';
import 'package:finwize/widgets/ad_banner.dart';

import 'package:finwize/main.dart';
import 'package:finwize/screens/landing_screen.dart';
import 'package:finwize/screens/login_screen.dart';
import 'package:finwize/screens/register_screen.dart';
import 'package:finwize/screens/dashboard_screen.dart';
import 'package:finwize/screens/advisor_screen.dart';
import 'package:finwize/screens/mentor_screen.dart';
import 'package:finwize/screens/investment_screen.dart';
import 'package:finwize/screens/calculators_screen.dart';
import 'package:finwize/screens/markets_screen.dart';
import 'package:finwize/screens/budget_screen.dart';
import 'package:finwize/screens/transactions_screen.dart';
import 'package:finwize/screens/savings_screen.dart';
import 'package:finwize/screens/learning_screen.dart';
import 'package:finwize/screens/articles_screen.dart';
import 'package:finwize/screens/article_detail_screen.dart';
import 'package:finwize/screens/news_screen.dart';
import 'package:finwize/screens/news_detail_screen.dart';
import 'package:finwize/screens/forum_screen.dart';
import 'package:finwize/screens/forum_topic_detail_screen.dart';
import 'package:finwize/screens/courses_screen.dart';
import 'package:finwize/screens/course_detail_screen.dart';
import 'package:finwize/screens/lesson_screen.dart';
import 'package:finwize/screens/invoices_screen.dart';
import 'package:finwize/screens/business_tasks_screen.dart';
import 'package:finwize/screens/business_plan_screen.dart';
import 'package:finwize/screens/profile_screen.dart';
import 'package:finwize/screens/notifications_screen.dart';
import 'package:finwize/screens/admin_screen.dart';

Map<String, dynamic> _user() => {
      'id': 'u1', 'full_name': 'Adaeze Okafor', 'email': 'adaeze@finwize.app',
      'is_admin': true, 'is_active': true,
    };

const _allTxns = [
  {'id': 't1', 'description': 'Salary', 'category': 'Income', 'type': 'income', 'amount': 350000, 'date': '2026-08-14'},
  {'id': 't2', 'description': 'Groceries', 'category': 'Food', 'type': 'expense', 'amount': 42000, 'date': '2026-08-13'},
  {'id': 't3', 'description': 'Fuel', 'category': 'Transport', 'type': 'expense', 'amount': 18000, 'date': '2026-08-12'},
  {'id': 't4', 'description': 'Freelance gig', 'category': 'Income', 'type': 'income', 'amount': 85000, 'date': '2026-08-11'},
];

String _sse(List<Map<String, dynamic>> events) =>
    events.map((e) => 'data: ${jsonEncode(e)}\n\n').join();

MockClient _mockClient({bool sponsoredAd = false}) {
  return MockClient((request) async {
    final path = request.url.path.replaceFirst('/api/v1', '');

    if (path.startsWith('/ai/')) {
      final reply = path.contains('mentor')
          ? 'Break down your goals into small wins and track them weekly.'
          : path.contains('investment')
              ? 'Diversify across a few low-cost ETFs and hold for the long run.'
              : 'Try a 50-30-20 split: needs, wants, savings.';
      return http.Response(
        _sse([
          {'event': 'started', 'conversation_id': 'c1'},
          {'event': 'token', 'token': reply},
          {'event': 'done', 'message_id': 'm1', 'conversation_id': 'c1'},
        ]),
        200,
        headers: {'content-type': 'text/event-stream'},
      );
    }

    if (path == '/calculators/mortgage') {
      return http.Response(jsonEncode({'monthly_payment': 658421, 'total_payment': 158021040, 'total_interest': 108021040, 'monthly_rate_pct': 0.83}), 200);
    }
    if (path == '/calculators/investment') {
      return http.Response(jsonEncode({'future_value': 310584, 'roi_pct': 210.58, 'cagr_pct': 8.14}), 200);
    }
    if (path == '/calculators/mutual-fund') {
      return http.Response(jsonEncode({'future_value': 6120034, 'total_invested': 2900000, 'growth_amount': 3220034, 'growth_pct': 111.0}), 200);
    }
    if (path == '/calculators/bond') {
      return http.Response(jsonEncode({'annual_coupon': 100000, 'current_yield_pct': 10.53, 'ytm_approx_pct': 11.84}), 200);
    }
    if (path == '/calculators/treasury-bill') {
      return http.Response(jsonEncode({'discount_yield_pct': 13.85, 'effective_yield_pct': 16.04, 'profit': 70000}), 200);
    }
    if (path == '/calculators/commercial-paper') {
      return http.Response(jsonEncode({'price': 980000, 'discount_yield_pct': 32.5, 'effective_yield_pct': 33.8, 'profit': 20000}), 200);
    }
    if (path == '/calculators/real-estate') {
      return http.Response(jsonEncode({'gross_rental_yield_pct': 8.0, 'net_rental_yield_pct': 6.0, 'net_annual_income': 3000000, 'cash_on_cash_roi_pct': 7.5}), 200);
    }
    if (path == '/calculators/compound-interest') {
      return http.Response(jsonEncode({'future_value': 14858240, 'total_contributions': 4600000, 'total_interest': 10258240}), 200);
    }
    if (path == '/business-plans/generate') {
      return http.Response(jsonEncode({
        'id': 'bp1', 'user_id': 'u1',
        'title': 'AgroFresh Logistics Business Plan',
        'content': {'executive_summary': 'A farm-to-market cold-chain delivery service reducing post-harvest losses for smallholder farmers in Nigeria.'},
        'status': 'completed', 'created_at': '2026-08-17', 'updated_at': '2026-08-17',
      }), 201);
    }

    if (request.url.pathSegments.isNotEmpty && request.url.pathSegments.first == 'ads') {
      if (sponsoredAd) {
        return http.Response(jsonEncode([{'id': 'ad1', 'sponsor_name': 'Zenith Bank', 'target_url': 'https://example.com', 'image_url': null}]), 200);
      }
      return http.Response(jsonEncode([]), 200);
    }

    if (path == '/users/me') return http.Response(jsonEncode(_user()), 200);
    if (path == '/subscriptions/my') {
      return http.Response(jsonEncode({
        'id': 's1', 'user_id': 'u1', 'plan': 'free', 'status': 'active',
        'provider': 'internal', 'provider_ref': null,
        'current_period_start': '2026-08-01T00:00:00Z', 'current_period_end': null,
        'auto_renew': false, 'created_at': '2026-08-01T00:00:00Z',
      }), 200);
    }
    if (path == '/users/me/progress') {
      return http.Response(jsonEncode({'lessons_completed': 12, 'badges': ['b1', 'b2', 'b3', 'b4', 'b5'], 'active_goals': 3}), 200);
    }
    if (path == '/users/me/notifications') {
      return http.Response(jsonEncode({
        'items': [
          {'id': 'n1', 'title': 'Budget alert', 'message': 'You spent 80% of your Food budget.', 'created_at': '2026-08-16', 'is_read': false},
          {'id': 'n2', 'title': 'Goal reached', 'message': 'Emergency fund goal is 50% funded.', 'created_at': '2026-08-15', 'is_read': true},
        ],
        'page': 1, 'per_page': 20,
      }), 200);
    }
    if (path == '/users/me/notifications/read-all') return http.Response('{}', 200);
    if (path == '/finance/budgets') {
      return http.Response(jsonEncode({'budgets': [
        {'id': 'b1', 'name': 'Food', 'category': 'Food', 'monthly_limit': 120000, 'spent': 96000, 'remaining': 24000},
        {'id': 'b2', 'name': 'Transport', 'category': 'Transport', 'monthly_limit': 60000, 'spent': 21000, 'remaining': 39000},
        {'id': 'b3', 'name': 'Rent', 'category': 'Housing', 'monthly_limit': 300000, 'spent': 300000, 'remaining': 0},
      ]}), 200);
    }
    if (path == '/finance/transactions') {
      final type = request.url.queryParameters['type'];
      final txns = type == null || type == 'all' ? _allTxns : _allTxns.where((t) => t['type'] == type).toList();
      return http.Response(jsonEncode({'transactions': txns}), 200);
    }
    if (path == '/finance/savings-goals') {
      return http.Response(jsonEncode({'goals': [
        {'id': 'g1', 'name': 'Emergency Fund', 'target_amount': 500000, 'current_amount': 250000},
        {'id': 'g2', 'name': 'New Laptop', 'target_amount': 800000, 'current_amount': 320000},
      ]}), 200);
    }
    if (path == '/intelligence/tips/daily') {
      return http.Response(jsonEncode({'tip': 'Set aside at least 20% of your income before spending it.'}), 200);
    }
    if (path == '/articles') {
      return http.Response(jsonEncode([
        {'id': 'a1', 'title': 'The 50-30-20 Budgeting Rule', 'summary': 'A simple way to split your income into needs, wants and savings.', 'content': 'body', 'author': 'Kemi', 'read_time_minutes': 5, 'tags': ['budget']},
        {'id': 'a2', 'title': 'Understanding Compound Interest', 'summary': 'Why time in the market beats timing the market.', 'content': 'body', 'author': 'Chidi', 'read_time_minutes': 4, 'tags': ['investing']},
        {'id': 'a3', 'title': 'Getting Your First Loan', 'summary': 'What lenders look for and how to qualify.', 'content': 'body', 'author': 'Musa', 'read_time_minutes': 6, 'tags': ['loans']},
      ]), 200);
    }
    if (path == '/articles/a1') {
      return http.Response(jsonEncode({'id': 'a1', 'title': 'The 50-30-20 Budgeting Rule', 'summary': 'A simple way to split your income into needs, wants and savings.', 'content': 'The 50-30-20 rule splits your after-tax income into three buckets: 50% for needs, 30% for wants and 20% for savings and debt repayment. It gives a simple framework to stay on track.', 'author': 'Kemi', 'read_time_minutes': 5, 'tags': ['budget', 'savings']}), 200);
    }
    if (path == '/news') {
      return http.Response(jsonEncode([
        {'id': 'nw1', 'title': 'CBN holds benchmark rate at 27.5%', 'summary': 'Inflation pressures ease as economy stabilises.', 'content': 'body', 'source': 'Finance Daily', 'category': 'financial', 'is_breaking': true},
        {'id': 'nw2', 'title': 'NGX All-Share Index crosses 150k', 'summary': 'Investors eye banking and telecom stocks.', 'content': 'body', 'source': 'Market Watch', 'category': 'business', 'is_breaking': false},
      ]), 200);
    }
    if (path == '/news/nw1') {
      return http.Response(jsonEncode({'id': 'nw1', 'title': 'CBN holds benchmark rate at 27.5%', 'summary': 'Inflation pressures ease as economy stabilises.', 'content': 'The central bank held its benchmark rate steady this week, citing easing inflation pressures and a more stable exchange rate environment.', 'source': 'Finance Daily', 'category': 'financial', 'is_breaking': true, 'source_url': 'https://example.com/news/nw1'}), 200);
    }
    if (path == '/forum/topics') {
      return http.Response(jsonEncode([
        {'id': 'f1', 'title': 'Best apps for budgeting in Nigeria?', 'content': 'Looking for recommendations...', 'reply_count': 14, 'is_pinned': true, 'is_locked': false},
        {'id': 'f2', 'title': 'Where to start investing with NGN 50k', 'content': 'Mutual funds or T-bills?', 'reply_count': 8, 'is_pinned': false, 'is_locked': false},
      ]), 200);
    }
    if (path == '/forum/topics/f1') {
      return http.Response(jsonEncode({'id': 'f1', 'title': 'Best apps for budgeting in Nigeria?', 'content': 'Looking for recommendations for simple budgeting apps that work with naira accounts.', 'author_name': 'Ada', 'reply_count': 14, 'is_pinned': true, 'is_locked': false, 'replies': [
        {'id': 'r1', 'content': 'I use the built-in tracking tools in this app plus a spreadsheet.', 'author_name': 'Chidi'},
        {'id': 'r2', 'content': 'Try the envelope method with a simple notebook.', 'author_name': 'Musa'},
      ]}), 200);
    }
    if (path == '/forum/topics/f1/replies') {
      return http.Response(jsonEncode({'id': 'r3', 'content': 'Thanks for the tips!', 'author_name': 'Ada'}), 200);
    }
    if (path == '/courses') {
      return http.Response(jsonEncode([
        {'id': 'c1', 'title': 'Budgeting Basics', 'description': 'Learn how to plan and track your spending.', 'difficulty': 'beginner', 'category': 'personalFinance', 'lesson_count': 5, 'duration_hours': 1.5, 'is_published': true},
        {'id': 'c2', 'title': 'Investment Fundamentals', 'description': 'Understand stocks, bonds and funds.', 'difficulty': 'intermediate', 'category': 'investing', 'lesson_count': 6, 'duration_hours': 2.0, 'is_published': true},
      ]), 200);
    }
    if (path == '/courses/c1') {
      return http.Response(jsonEncode({'id': 'c1', 'title': 'Budgeting Basics', 'description': 'Learn how to plan and track your spending.', 'difficulty': 'beginner', 'category': 'personalFinance', 'lesson_count': 5, 'duration_hours': 1.5, 'is_published': true, 'lessons': [
        {'id': 'l1', 'title': 'Why Budgeting Matters', 'content': 'A budget is your spending plan.', 'duration_minutes': 12, 'order': 1},
        {'id': 'l2', 'title': 'Building Your First Budget', 'content': 'Track income and fixed costs first.', 'duration_minutes': 15, 'order': 2},
      ]}), 200);
    }
    if (path == '/courses/c1/progress') {
      return http.Response(jsonEncode({'course_id': 'c1', 'course_title': 'Budgeting Basics', 'total_lessons': 5, 'completed_lessons': 1, 'percentage': 20.0, 'passed_quizzes': 1, 'total_quizzes': 5}), 200);
    }
    if (path == '/courses/c1/lessons/l1') {
      return http.Response(jsonEncode({'id': 'l1', 'course_id': 'c1', 'title': 'Why Budgeting Matters', 'content': 'A budget is your spending plan. It helps you control cash flow, prepare for the unexpected and reach your savings goals.', 'content_type': 'text', 'duration_minutes': 12, 'order': 1, 'quiz': {'questions': [
        {'id': 'q1', 'question': 'What does a budget help you control?', 'options': ['Cash flow', 'Weather', 'Traffic'], 'correct_answer': 0, 'explanation': 'A budget controls your cash flow.'},
        {'id': 'q2', 'question': 'Which of these is a budgeting method?', 'options': ['50-30-20', '5-10-5', '20-20-20'], 'correct_answer': 0, 'explanation': '50-30-20 is a popular method.'},
      ], 'passing_score': 70}}), 200);
    }
    if (path == '/courses/c1/lessons/l1/quiz') {
      return http.Response(jsonEncode({'score': 2, 'total': 2, 'percentage': 100.0, 'passed': true, 'correct_answers': [0, 0], 'explanations': ['A budget controls your cash flow.', '50-30-20 is a popular method.']}), 200);
    }
    if (path == '/courses/c1/lessons/l1/complete') {
      return http.Response(jsonEncode({'completed': true}), 200);
    }
    if (path == '/courses/c1/enroll') {
      return http.Response(jsonEncode({'enrolled': true}), 200);
    }
    if (path == '/invoices') {
      return http.Response(jsonEncode([
        {'id': 'i1', 'number': 'INV-001', 'client_name': 'Babs Ltd', 'total': 250000, 'currency': 'NGN', 'status': 'paid'},
        {'id': 'i2', 'number': 'INV-002', 'client_name': 'Ada Traders', 'total': 120000, 'currency': 'NGN', 'status': 'sent'},
      ]), 200);
    }
    if (path == '/tasks') {
      return http.Response(jsonEncode([
        {'id': 't1', 'title': 'Send proposal to client', 'priority': 'high', 'status': 'pending'},
        {'id': 't2', 'title': 'Update cash flow sheet', 'priority': 'medium', 'status': 'in_progress'},
      ]), 200);
    }
    if (path == '/admin/stats') {
      return http.Response(jsonEncode({'total_users': 2480, 'total_transactions': 15642}), 200);
    }
    if (path == '/admin/users') {
      return http.Response(jsonEncode({
        'items': [
          {'id': 'u1', 'full_name': 'Adaeze Okafor', 'email': 'adaeze@finwize.app', 'is_admin': true, 'is_active': true},
          {'id': 'u2', 'full_name': 'Chidi Obi', 'email': 'chidi@finwize.app', 'is_admin': false, 'is_active': true},
        ],
        'total': 2,
      }), 200);
    }
    if (path == '/markets/overview') {
      return http.Response(jsonEncode({
        'as_of': '2026-08-17T09:00:00Z',
        'disclaimer': 'Market data is indicative and for educational purposes only. It is not investment advice and may be delayed or incomplete. Past performance does not guarantee future results.',
        'regions': [
          {
            'region': 'africa',
            'name': 'African Exchanges',
            'indices': [
              {'symbol': 'NGXASI', 'name': 'NGX All-Share Index', 'country': 'Nigeria', 'currency': 'NGN', 'value': 152840.35, 'change': 875.12, 'change_pct': 0.58},
              {'symbol': 'GSE', 'name': 'GSE Composite Index', 'country': 'Ghana', 'currency': 'GHS', 'value': 4380.12, 'change': -18.44, 'change_pct': -0.42},
              {'symbol': 'NSE20', 'name': 'NSE 20 Share Index', 'country': 'Kenya', 'currency': 'KES', 'value': 2140.87, 'change': 12.36, 'change_pct': 0.58},
              {'symbol': 'JSE40', 'name': 'FTSE/JSE Top 40', 'country': 'South Africa', 'currency': 'ZAR', 'value': 78210.55, 'change': -420.33, 'change_pct': -0.53},
              {'symbol': 'EGX30', 'name': 'EGX 30 Index', 'country': 'Egypt', 'currency': 'EGP', 'value': 33240.12, 'change': 215.60, 'change_pct': 0.65},
              {'symbol': 'MASI', 'name': 'MASI Index', 'country': 'Morocco', 'currency': 'MAD', 'value': 14280.90, 'change': -32.10, 'change_pct': -0.22},
              {'symbol': 'BRVM', 'name': 'BRVM Composite', 'country': 'Ivory Coast', 'currency': 'XOF', 'value': 265.40, 'change': 0.85, 'change_pct': 0.32},
              {'symbol': 'DSE', 'name': 'DSE All-Share Index', 'country': 'Tanzania', 'currency': 'TZS', 'value': 2350.75, 'change': 8.40, 'change_pct': 0.36},
              {'symbol': 'USE', 'name': 'USE All-Share Index', 'country': 'Uganda', 'currency': 'UGX', 'value': 1040.25, 'change': 3.15, 'change_pct': 0.30},
              {'symbol': 'RSE', 'name': 'RSE Share Index', 'country': 'Rwanda', 'currency': 'RWF', 'value': 2480.60, 'change': 12.20, 'change_pct': 0.49},
              {'symbol': 'SEMDEX', 'name': 'SEMDEX Index', 'country': 'Mauritius', 'currency': 'MUR', 'value': 2250.85, 'change': -5.60, 'change_pct': -0.25},
              {'symbol': 'BSE', 'name': 'BSE Domestic Index', 'country': 'Botswana', 'currency': 'BWP', 'value': 12580.30, 'change': 45.20, 'change_pct': 0.36},
              {'symbol': 'ZSE', 'name': 'ZSE All-Share Index', 'country': 'Zimbabwe', 'currency': 'ZWL', 'value': 1840.55, 'change': -22.35, 'change_pct': -1.20},
              {'symbol': 'TUNINDEX', 'name': 'TUNINDEX', 'country': 'Tunisia', 'currency': 'TND', 'value': 9850.45, 'change': 10.80, 'change_pct': 0.11},
            ],
          },
          {
            'region': 'global',
            'name': 'Global Markets',
            'indices': [
              {'symbol': 'SPX', 'name': 'S&P 500', 'country': 'United States', 'currency': 'USD', 'value': 6254.30, 'change': 18.20, 'change_pct': 0.29},
              {'symbol': 'IXIC', 'name': 'NASDAQ Composite', 'country': 'United States', 'currency': 'USD', 'value': 20850.55, 'change': 95.40, 'change_pct': 0.46},
              {'symbol': 'DJI', 'name': 'Dow Jones Industrial', 'country': 'United States', 'currency': 'USD', 'value': 44520.85, 'change': -62.10, 'change_pct': -0.14},
              {'symbol': 'FTSE', 'name': 'FTSE 100', 'country': 'United Kingdom', 'currency': 'GBP', 'value': 8920.45, 'change': 12.35, 'change_pct': 0.14},
              {'symbol': 'N225', 'name': 'Nikkei 225', 'country': 'Japan', 'currency': 'JPY', 'value': 42250.60, 'change': -210.50, 'change_pct': -0.50},
              {'symbol': 'HSI', 'name': 'Hang Seng Index', 'country': 'Hong Kong (China)', 'currency': 'HKD', 'value': 24980.35, 'change': 88.20, 'change_pct': 0.35},
              {'symbol': 'SSE', 'name': 'Shanghai Composite', 'country': 'China', 'currency': 'CNY', 'value': 3820.15, 'change': -12.40, 'change_pct': -0.32},
              {'symbol': 'SENSEX', 'name': 'S&P BSE Sensex', 'country': 'India', 'currency': 'INR', 'value': 85540.25, 'change': 215.60, 'change_pct': 0.25},
              {'symbol': 'DAX', 'name': 'DAX 40', 'country': 'Germany', 'currency': 'EUR', 'value': 22540.80, 'change': 45.20, 'change_pct': 0.20},
              {'symbol': 'CAC', 'name': 'CAC 40', 'country': 'France', 'currency': 'EUR', 'value': 7860.55, 'change': -15.30, 'change_pct': -0.19},
            ],
          },
        ],
        'crypto': [
          {'symbol': 'BTC', 'name': 'Bitcoin', 'currency': 'USD', 'value': 104500.20, 'change': 1420.50, 'change_pct': 1.38},
          {'symbol': 'ETH', 'name': 'Ethereum', 'currency': 'USD', 'value': 3980.75, 'change': 52.30, 'change_pct': 1.33},
          {'symbol': 'SOL', 'name': 'Solana', 'currency': 'USD', 'value': 228.40, 'change': 4.10, 'change_pct': 1.83},
          {'symbol': 'BNB', 'name': 'BNB', 'currency': 'USD', 'value': 742.15, 'change': 6.80, 'change_pct': 0.92},
          {'symbol': 'XRP', 'name': 'XRP', 'currency': 'USD', 'value': 2.86, 'change': 0.04, 'change_pct': 1.42},
          {'symbol': 'DOGE', 'name': 'Dogecoin', 'currency': 'USD', 'value': 0.42, 'change': 0.01, 'change_pct': 2.44},
        ],
        'commodities': [
          {'symbol': 'XAU', 'name': 'Gold', 'currency': 'USD', 'unit': 'USD/troy oz', 'value': 3385.40, 'change': 12.60, 'change_pct': 0.37},
          {'symbol': 'XAG', 'name': 'Silver', 'currency': 'USD', 'unit': 'USD/troy oz', 'value': 41.85, 'change': 0.35, 'change_pct': 0.84},
          {'symbol': 'BRENT', 'name': 'Brent Crude Oil', 'currency': 'USD', 'unit': 'USD/bbl', 'value': 82.40, 'change': -0.60, 'change_pct': -0.72},
          {'symbol': 'WTI', 'name': 'WTI Crude Oil', 'currency': 'USD', 'unit': 'USD/bbl', 'value': 78.65, 'change': -0.45, 'change_pct': -0.57},
          {'symbol': 'NG', 'name': 'Natural Gas', 'currency': 'USD', 'unit': 'USD/MMBtu', 'value': 3.42, 'change': 0.08, 'change_pct': 2.40},
          {'symbol': 'COPPER', 'name': 'Copper', 'currency': 'USD', 'unit': 'USD/lb', 'value': 4.85, 'change': 0.04, 'change_pct': 0.83},
          {'symbol': 'COCOA', 'name': 'Cocoa', 'currency': 'USD', 'unit': 'USD/tonne', 'value': 10480.00, 'change': 220.00, 'change_pct': 2.14},
        ],
      }), 200);
    }
    if (path == '/subscriptions/plans') {
      return http.Response(jsonEncode([
        {'key': 'free', 'name': 'Free', 'price_monthly': 0, 'ai_chats_per_month': null, 'max_savings_goals': 3, 'max_invoices_per_month': 0, 'ad_free': false},
        {'key': 'pro', 'name': 'Pro', 'price_monthly': 4000, 'ai_chats_per_month': null, 'max_savings_goals': null, 'max_invoices_per_month': null, 'ad_free': true},
      ]), 200);
    }
    return http.Response(jsonEncode([]), 200);
  });
}

Future<void> _loadFonts() async {
  const fontDir = 'C:/src/flutter/bin/cache/artifacts/material_fonts';
  final loader = FontLoader('Roboto');
  for (final name in ['roboto-regular.ttf', 'roboto-medium.ttf', 'roboto-bold.ttf']) {
    final bytes = await File('$fontDir/$name').readAsBytes();
    loader.addFont(Future.value(ByteData.view(bytes.buffer)));
  }
  await loader.load();
}

Future<void> _pump(WidgetTester tester, Widget home) async {
  tester.view.physicalSize = const Size(824, 1784);
  tester.view.devicePixelRatio = 2.0;
  addTearDown(tester.view.reset);
  await tester.pumpWidget(
    MultiProvider(
      providers: [
        ChangeNotifierProvider<AuthProvider>(create: (_) => AuthProvider()),
        ChangeNotifierProvider<ConnectivityProvider>(create: (_) => ConnectivityProvider()),
      ],
      child: MaterialApp(theme: AppTheme.lightTheme, home: home),
    ),
  );
  await tester.pumpAndSettle();
  tester.takeException();
}

Future<void> _shot(WidgetTester tester, String name) async {
  await expectLater(find.byType(MaterialApp), matchesGoldenFile('goldens/qa/$name.png'));
  tester.takeException();
}

Future<void> _sendChat(WidgetTester tester, String message) async {
  await tester.enterText(find.byType(TextField), message);
  await tester.tap(find.byIcon(Icons.send));
  await tester.pump();
  await tester.pump(const Duration(milliseconds: 100));
  await tester.pumpAndSettle();
  tester.takeException();
}

Future<void> _switchCalculator(WidgetTester tester, String chipName) async {
  final horizontal = find.descendant(of: find.byType(CalculatorsScreen), matching: find.byType(Scrollable)).at(1);
  await tester.scrollUntilVisible(find.text(chipName), 80, scrollable: horizontal);
  await tester.pumpAndSettle();
  await tester.tap(find.text(chipName));
  await tester.pumpAndSettle();
  tester.takeException();
}

Future<void> _fillAndCalculate(WidgetTester tester, List<String> values) async {
  final fields = find.byType(TextField);
  for (var i = 0; i < values.length; i++) {
    await tester.enterText(fields.at(i), values[i]);
  }
  await tester.tap(find.text('Calculate'));
  await tester.pumpAndSettle();
  tester.takeException();
}

Future<void> _switchNewsCategory(WidgetTester tester, String label) async {
  final horizontal = find.descendant(of: find.byType(NewsScreen), matching: find.byType(Scrollable)).at(0);
  await tester.scrollUntilVisible(find.widgetWithText(ChoiceChip, label), 40, scrollable: horizontal);
  await tester.pumpAndSettle();
  await tester.tap(find.widgetWithText(ChoiceChip, label));
  await tester.pumpAndSettle();
  tester.takeException();
}

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();

  setUp(() {
    SharedPreferences.setMockInitialValues({});
    ApiService.debugClient = _mockClient();
    LocalDb.instance.reset();
    LocalDb.instance.openOverride = () async {
      final db = await databaseFactoryFfiNoIsolate.openDatabase(
        inMemoryDatabasePath,
        options: OpenDatabaseOptions(version: 1, onCreate: LocalDb.createSchema),
      );
      return db;
    };
  });

  tearDown(() => ApiService.debugClient = null);

  setUpAll(() async => _loadFonts());

  testWidgets('01 auth landing', (tester) async {
    await _pump(tester, const LandingScreen());
    await _shot(tester, '01_auth_landing');
  });

  testWidgets('02 auth login', (tester) async {
    await _pump(tester, const LoginScreen());
    await _shot(tester, '02_auth_login');
  });

  testWidgets('03 auth register', (tester) async {
    await _pump(tester, const RegisterScreen());
    await _shot(tester, '03_auth_register');
  });

  testWidgets('04 advisor empty', (tester) async {
    await _pump(tester, const AdvisorScreen());
    await _shot(tester, '04_advisor_empty');
  });

  testWidgets('05 advisor conversation', (tester) async {
    await _pump(tester, const AdvisorScreen());
    await _sendChat(tester, 'How do I start budgeting?');
    await _shot(tester, '05_advisor_conversation');
  });

  testWidgets('06 mentor empty', (tester) async {
    await _pump(tester, const MentorScreen());
    await _shot(tester, '06_mentor_empty');
  });

  testWidgets('07 mentor conversation', (tester) async {
    await _pump(tester, const MentorScreen());
    await _sendChat(tester, 'How do I start a business?');
    await _shot(tester, '07_mentor_conversation');
  });

  testWidgets('08 investment empty', (tester) async {
    await _pump(tester, const InvestmentScreen());
    await _shot(tester, '08_investment_empty');
  });

  testWidgets('09 investment conversation', (tester) async {
    await _pump(tester, const InvestmentScreen());
    await _sendChat(tester, 'Best stocks to buy now?');
    await _shot(tester, '09_investment_conversation');
  });

  testWidgets('10 home dashboard', (tester) async {
    await _pump(tester, const DashboardScreen());
    await _shot(tester, '10_home_dashboard');
  });

  testWidgets('11 learning hub', (tester) async {
    await _pump(tester, const LearningScreen());
    await _shot(tester, '11_learning_hub');
  });

  testWidgets('12 learning articles', (tester) async {
    await _pump(tester, const ArticlesScreen());
    await _shot(tester, '12_learning_articles');
  });

  testWidgets('13 learning news', (tester) async {
    await _pump(tester, const NewsScreen());
    await _shot(tester, '13_learning_news');
  });

  testWidgets('14 learning forum', (tester) async {
    await _pump(tester, const ForumScreen());
    await _shot(tester, '14_learning_forum');
  });

  testWidgets('15 finance budget', (tester) async {
    await _pump(tester, const BudgetScreen());
    await _shot(tester, '15_finance_budget');
  });

  testWidgets('16 finance transactions all', (tester) async {
    await _pump(tester, const TransactionsScreen());
    await _shot(tester, '16_finance_transactions_all');
  });

  testWidgets('17 finance transactions income', (tester) async {
    await _pump(tester, const TransactionsScreen());
    await tester.tap(find.widgetWithText(ChoiceChip, 'Income'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '17_finance_transactions_income');
  });

  testWidgets('18 finance transactions expense', (tester) async {
    await _pump(tester, const TransactionsScreen());
    await tester.tap(find.widgetWithText(ChoiceChip, 'Expense'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '18_finance_transactions_expense');
  });

  testWidgets('19 finance savings', (tester) async {
    await _pump(tester, const SavingsScreen());
    await _shot(tester, '19_finance_savings');
  });

  testWidgets('20 calculator mortgage', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _shot(tester, '20_calc_mortgage');
  });

  testWidgets('21 calculator investment', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Stock / Investment');
    await _shot(tester, '21_calc_investment');
  });

  testWidgets('22 calculator mutual fund', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Mutual Fund');
    await _shot(tester, '22_calc_mutual_fund');
  });

  testWidgets('23 calculator bond', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Bond Yield');
    await _shot(tester, '23_calc_bond');
  });

  testWidgets('24 calculator treasury bill', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Treasury Bill');
    await _shot(tester, '24_calc_treasury_bill');
  });

  testWidgets('25 calculator commercial paper', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Commercial Paper');
    await _shot(tester, '25_calc_commercial_paper');
  });

  testWidgets('26 calculator real estate', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Real Estate');
    await _shot(tester, '26_calc_real_estate');
  });

  testWidgets('27 calculator goal projection', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Goal Projection');
    await _shot(tester, '27_calc_goal_projection');
  });

  testWidgets('28 calculator mortgage result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _fillAndCalculate(tester, ['50000000', '15', '20']);
    await _shot(tester, '28_calc_mortgage_result');
  });

  testWidgets('29 business tasks', (tester) async {
    await _pump(tester, const BusinessTasksScreen());
    await _shot(tester, '29_business_tasks');
  });

  testWidgets('30 business invoices', (tester) async {
    await _pump(tester, const InvoicesScreen());
    await _shot(tester, '30_business_invoices');
  });

  testWidgets('31 business plan generator', (tester) async {
    await _pump(tester, const BusinessPlanScreen());
    await _shot(tester, '31_business_plan');
  });

  testWidgets('32 business plan generated', (tester) async {
    await _pump(tester, const BusinessPlanScreen());
    await tester.enterText(find.byType(TextField).at(0), 'AgroFresh Logistics');
    await tester.enterText(find.byType(TextField).at(1), 'Logistics');
    await tester.enterText(find.byType(TextField).at(2), 'Farm-to-market cold chain logistics');
    await tester.tap(find.text('Generate Plan'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '32_business_plan_generated');
  });

  testWidgets('33 profile', (tester) async {
    await _pump(tester, const ProfileScreen());
    await _shot(tester, '33_profile');
  });

  testWidgets('34 notifications', (tester) async {
    await _pump(tester, const NotificationsScreen());
    await _shot(tester, '34_notifications');
  });

  testWidgets('35 pricing', (tester) async {
    await _pump(tester, const PricingScreen());
    await _shot(tester, '35_pricing');
  });

  testWidgets('36 admin dashboard', (tester) async {
    await _pump(tester, const AdminScreen());
    await _shot(tester, '36_admin_dashboard');
  });

  testWidgets('37 shell advisor tab', (tester) async {
    await _pump(tester, const MainShell());
    await _shot(tester, '37_shell_advisor');
  });

  testWidgets('38 shell home tab', (tester) async {
    await _pump(tester, const MainShell());
    await tester.tap(find.text('Home'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '38_shell_home');
  });

  testWidgets('39 shell finance tab + sponsored ad', (tester) async {
    ApiService.debugClient = _mockClient(sponsoredAd: true);
    await _pump(tester, const MainShell());
    await tester.tap(find.text('Finance'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '39_shell_finance_sponsored_ad');
  });

  testWidgets('40 markets africa', (tester) async {
    await _pump(tester, const MarketsScreen());
    await _shot(tester, '40_markets_africa');
  });

  testWidgets('41 markets global', (tester) async {
    await _pump(tester, const MarketsScreen());
    await tester.tap(find.text('Global'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '41_markets_global');
  });

  testWidgets('42 markets crypto', (tester) async {
    await _pump(tester, const MarketsScreen());
    await tester.tap(find.text('Crypto'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '42_markets_crypto');
  });

  testWidgets('43 markets commodities', (tester) async {
    await _pump(tester, const MarketsScreen());
    await tester.tap(find.text('Commodities'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '43_markets_commodities');
  });

  testWidgets('44 dashboard quick action markets', (tester) async {
    await _pump(tester, const DashboardScreen());
    await _shot(tester, '44_dashboard_markets_chip');
  });

  testWidgets('45 news financial category', (tester) async {
    await _pump(tester, const NewsScreen());
    await _switchNewsCategory(tester, 'Financial');
    await _shot(tester, '45_news_financial');
  });

  testWidgets('46 news business category', (tester) async {
    await _pump(tester, const NewsScreen());
    await _switchNewsCategory(tester, 'Business');
    await _shot(tester, '46_news_business');
  });

  testWidgets('47 news economy category', (tester) async {
    await _pump(tester, const NewsScreen());
    await _switchNewsCategory(tester, 'Economy');
    await _shot(tester, '47_news_economy');
  });

  testWidgets('48 news startups category', (tester) async {
    await _pump(tester, const NewsScreen());
    await _switchNewsCategory(tester, 'Startups');
    await _shot(tester, '48_news_startups');
  });

  testWidgets('49 calculator investment result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Stock / Investment');
    await _fillAndCalculate(tester, ['2000000', '12', '10']);
    await _shot(tester, '49_calc_investment_result');
  });

  testWidgets('50 calculator mutual fund result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Mutual Fund');
    await _fillAndCalculate(tester, ['500000', '100000', '15', '10']);
    await _shot(tester, '50_calc_mutual_fund_result');
  });

  testWidgets('51 calculator bond result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Bond Yield');
    await _fillAndCalculate(tester, ['1000000', '10', '950000', '5']);
    await _shot(tester, '51_calc_bond_result');
  });

  testWidgets('52 calculator treasury bill result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Treasury Bill');
    await _fillAndCalculate(tester, ['1000000', '860000', '364']);
    await _shot(tester, '52_calc_treasury_bill_result');
  });

  testWidgets('53 calculator commercial paper result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Commercial Paper');
    await _fillAndCalculate(tester, ['1000000', '20', '90']);
    await _shot(tester, '53_calc_commercial_paper_result');
  });

  testWidgets('54 calculator real estate result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Real Estate');
    await _fillAndCalculate(tester, ['50000000', '6000000', '3000000', '10000000']);
    await _shot(tester, '54_calc_real_estate_result');
  });

  testWidgets('55 calculator goal projection result', (tester) async {
    await _pump(tester, const CalculatorsScreen());
    await _switchCalculator(tester, 'Goal Projection');
    await _fillAndCalculate(tester, ['200000', '50000', '12', '15']);
    await _shot(tester, '55_calc_goal_projection_result');
  });

  testWidgets('56 shell mentor tab', (tester) async {
    await _pump(tester, const MainShell());
    await tester.tap(find.text('Chidi'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '56_shell_mentor');
  });

  testWidgets('57 shell investment tab', (tester) async {
    await _pump(tester, const MainShell());
    await tester.tap(find.text('Musa'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '57_shell_investment');
  });

  testWidgets('58 shell learn tab', (tester) async {
    await _pump(tester, const MainShell());
    await tester.tap(find.text('Learn'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '58_shell_learn');
  });

  testWidgets('59 dashboard quick action transactions', (tester) async {
    await _pump(tester, const DashboardScreen());
    await tester.tap(find.byKey(const Key('quick_action_transactions')));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '59_dashboard_transactions');
  });

  testWidgets('60 dashboard quick action savings', (tester) async {
    await _pump(tester, const DashboardScreen());
    await tester.tap(find.byKey(const Key('quick_action_savings')));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '60_dashboard_savings');
  });

  testWidgets('61 dashboard quick action kemi', (tester) async {
    await _pump(tester, const DashboardScreen());
    await tester.tap(find.byKey(const Key('quick_action_kemi')));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '61_dashboard_kemi');
  });

  testWidgets('62 dashboard quick action calculators', (tester) async {
    await _pump(tester, const DashboardScreen());
    await tester.tap(find.byKey(const Key('quick_action_calculators')));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '62_dashboard_calculators');
  });

  testWidgets('63 learning courses', (tester) async {
    await _pump(tester, const CoursesScreen());
    await _shot(tester, '63_learning_courses');
  });

  testWidgets('64 course detail', (tester) async {
    await _pump(tester, const CourseDetailScreen(courseId: 'c1'));
    await _shot(tester, '64_course_detail');
  });

  testWidgets('65 lesson with quiz', (tester) async {
    await _pump(tester, const LessonScreen(courseId: 'c1', lessonId: 'l1'));
    await _shot(tester, '65_lesson_quiz');
  });

  testWidgets('66 lesson quiz result', (tester) async {
    await _pump(tester, const LessonScreen(courseId: 'c1', lessonId: 'l1'));
    await tester.tap(find.widgetWithText(RadioListTile<int>, 'Cash flow'));
    await tester.tap(find.widgetWithText(RadioListTile<int>, '50-30-20'));
    await tester.pumpAndSettle();
    await tester.tap(find.text('Submit Quiz'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '66_lesson_quiz_result');
  });

  testWidgets('67 article detail', (tester) async {
    await _pump(tester, const ArticleDetailScreen(articleId: 'a1'));
    await _shot(tester, '67_article_detail');
  });

  testWidgets('68 news detail', (tester) async {
    await _pump(tester, const NewsDetailScreen(newsId: 'nw1'));
    await _shot(tester, '68_news_detail');
  });

  testWidgets('69 forum topic detail', (tester) async {
    await _pump(tester, const ForumTopicDetailScreen(topicId: 'f1'));
    await _shot(tester, '69_forum_topic_detail');
  });

  testWidgets('70 learning hub to courses', (tester) async {
    await _pump(tester, const LearningScreen());
    await tester.tap(find.text('Courses & Lessons'));
    await tester.pumpAndSettle();
    tester.takeException();
    await _shot(tester, '70_learning_nav_courses');
  });
}
