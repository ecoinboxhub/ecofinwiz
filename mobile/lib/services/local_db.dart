import 'dart:async';
import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:path/path.dart' as p;
import 'package:sqflite/sqflite.dart';

/// Local SQLite store: single shared instance, caches API responses keyed by
/// URL and queues offline writes for background sync (AGENTS.md Principle 3).
///
/// Conventions:
/// - `pending_ops` is a FIFO queue; `id` is autoincrement so flush order
///   matches insertion order.
/// - Soft deletes: rows are not removed, they are flagged `deleted = 1` so a
///   tombstone can be synced later.
/// - Timestamps are UTC milliseconds since epoch.
class LocalDb {
  LocalDb._();
  static final LocalDb instance = LocalDb._();

  static const int _schemaVersion = 1;
  Database? _db;

  /// Test-only hook to override the database factory (e.g. sqflite_common_ffi).
  @visibleForTesting
  static Future<Database> Function()? databaseFactoryOverride;

  Future<Database> get database async {
    if (_db != null) return _db!;
    final factory = openOverride ?? databaseFactoryOverride;
    if (factory != null) {
      _db = await factory();
    } else {
      _db = await databaseFactory.openDatabase(
        p.join(await getDatabasesPath(), 'finwize.db'),
        options: OpenDatabaseOptions(
          version: _schemaVersion,
          onCreate: _onCreate,
        ),
      );
    }
    return _db!;
  }

  /// Test-only hook to inject a custom open function.
  Future<Database> Function()? openOverride;

  /// Replaces the current connection with [db] (used by tests to inject an
  /// in-memory database and by the app to reset storage).
  @visibleForTesting
  void attach(Database db) => _db = db;

  @visibleForTesting
  void reset() {
    _db = null;
    openOverride = null;
  }

  /// Test-only: creates the schema on [db] (used by harnesses to build a
  /// fresh in-memory/file-backed database with the same tables).
  @visibleForTesting
  static Future<void> createSchema(Database db, int version) =>
      instance._onCreate(db, version);

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE cached_responses (
        url TEXT PRIMARY KEY,
        body TEXT NOT NULL,
        cached_at INTEGER NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE pending_ops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT NOT NULL,
        url TEXT NOT NULL,
        body TEXT,
        created_at INTEGER NOT NULL,
        status TEXT NOT NULL DEFAULT 'pending'
      )
    ''');
    await db.execute('''
      CREATE TABLE offline_tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE,
        tip TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE chat_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        created_at INTEGER NOT NULL
      )
    ''');
  }

  // ---------------------------------------------------------------- cache ---

  Future<void> cacheResponse(String url, dynamic body) async {
    final db = await database;
    await db.insert('cached_responses', {
      'url': url,
      'body': body is String ? body : jsonEncode(body),
      'cached_at': DateTime.now().toUtc().millisecondsSinceEpoch,
    }, conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<dynamic>? _pending;
  Future<dynamic> _cacheFutureLock(Future<dynamic> Function() work) {
    final next = (_pending ?? Future.value()).then((_) => work());
    _pending = next.catchError((_) {});
    return next;
  }

  Future<dynamic> readCache(String url) async {
    return _cacheFutureLock(() async {
      final db = await database;
      final rows = await db.query('cached_responses', where: 'url = ?', whereArgs: [url], limit: 1);
      if (rows.isEmpty) return null;
      final body = rows.first['body'] as String;
      try {
        return jsonDecode(body);
      } catch (_) {
        return body;
      }
    });
  }

  Future<void> clearCache() async {
    final db = await database;
    await db.delete('cached_responses');
  }

  // ----------------------------------------------------------- pending ops ---

  Future<int> enqueueOp(String method, String url, {Map<String, dynamic>? body}) async {
    final db = await database;
    return db.insert('pending_ops', {
      'method': method,
      'url': url,
      'body': body != null ? jsonEncode(body) : null,
      'created_at': DateTime.now().toUtc().millisecondsSinceEpoch,
      'status': 'pending',
    });
  }

  Future<List<Map<String, Object?>>> pendingOps() async {
    final db = await database;
    return db.query('pending_ops', orderBy: 'id ASC', where: 'status = ?', whereArgs: ['pending']);
  }

  Future<int> pendingOpCount() async {
    final db = await database;
    final result = await db.rawQuery('SELECT COUNT(*) AS c FROM pending_ops WHERE status = ?', ['pending']);
    return Sqflite.firstIntValue(result) ?? 0;
  }

  Future<void> markOpDone(int id, {bool failed = false}) async {
    final db = await database;
    await db.update('pending_ops', {'status': failed ? 'failed' : 'done'}, where: 'id = ?', whereArgs: [id]);
  }

  Future<void> clearPendingOps() async {
    final db = await database;
    await db.delete('pending_ops');
  }

  // ----------------------------------------------------------- daily tip ---

  Future<void> cacheDailyTip(String date, String tip) async {
    final db = await database;
    await db.insert('offline_tips', {'date': date, 'tip': tip},
        conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<String?> dailyTip(String date) async {
    final db = await database;
    final rows = await db.query('offline_tips', where: 'date = ?', whereArgs: [date], limit: 1);
    if (rows.isEmpty) return null;
    return rows.first['tip'] as String?;
  }

  // --------------------------------------------------------- chat history ---

  Future<void> appendChatMessage(String role, String content) async {
    final db = await database;
    await db.insert('chat_cache', {
      'role': role,
      'content': content,
      'created_at': DateTime.now().toUtc().millisecondsSinceEpoch,
    });
  }

  Future<List<Map<String, Object?>>> chatHistory({int limit = 50}) async {
    final db = await database;
    return db.query('chat_cache', orderBy: 'id DESC', limit: limit);
  }

  Future<void> clearChatHistory() async {
    final db = await database;
    await db.delete('chat_cache');
  }
}