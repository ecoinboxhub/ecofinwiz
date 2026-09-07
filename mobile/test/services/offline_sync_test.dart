import 'package:flutter_test/flutter_test.dart';
import 'package:http/http.dart' as http;
import 'package:http/testing.dart';
import 'package:path/path.dart' as p;
import 'package:shared_preferences/shared_preferences.dart';
import 'package:sqflite_common_ffi/sqflite_ffi.dart';

import 'package:finwize/services/api_service.dart';
import 'package:finwize/services/local_db.dart';
import 'package:finwize/services/sync_service.dart';

void main() {
  TestWidgetsFlutterBinding.ensureInitialized();
  sqfliteFfiInit();

  final dbFactory = databaseFactoryFfiNoIsolate;
  String? dbDir;
  var dbCounter = 0;
  Database? currentDb;

  Future<String> getDbDir() async => dbDir ??= await dbFactory.getDatabasesPath();

  Future<void> createSchema(Database db, int version) async {
    await db.execute('''
      CREATE TABLE cached_responses (
        url TEXT PRIMARY KEY, body TEXT NOT NULL, cached_at INTEGER NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE pending_ops (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        method TEXT NOT NULL, url TEXT NOT NULL, body TEXT,
        created_at INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'pending'
      )
    ''');
    await db.execute('''
      CREATE TABLE offline_tips (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL UNIQUE, tip TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE chat_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT NOT NULL, content TEXT NOT NULL, created_at INTEGER NOT NULL
      )
    ''');
  }

  setUp(() async {
    SharedPreferences.setMockInitialValues({});
    await currentDb?.close();
    final dbPath = p.join(await getDbDir(), 'finwize_test_${dbCounter++}.db');
    if (await dbFactory.databaseExists(dbPath)) await dbFactory.deleteDatabase(dbPath);
    currentDb = await dbFactory.openDatabase(
      dbPath,
      options: OpenDatabaseOptions(version: 1, onCreate: createSchema),
    );
    LocalDb.instance.attach(currentDb!);
    ApiService.debugClient = null;
  });

  tearDown(() async {
    await currentDb?.close();
    currentDb = null;
    LocalDb.instance.reset();
    ApiService.debugClient = null;
  });

  group('LocalDb cache', () {
    test('caches and reads back a JSON response', () async {
      await LocalDb.instance.cacheResponse('/finance/budgets', {'budgets': [1, 2]});
      final cached = await LocalDb.instance.readCache('/finance/budgets');
      expect(cached, {'budgets': [1, 2]});
    });

    test('readCache returns null for missing key', () async {
      expect(await LocalDb.instance.readCache('/nope'), isNull);
    });

    test('overwrites cache on repeat write', () async {
      await LocalDb.instance.cacheResponse('/tip', {'tip': 'old'});
      await LocalDb.instance.cacheResponse('/tip', {'tip': 'new'});
      expect(await LocalDb.instance.readCache('/tip'), {'tip': 'new'});
    });

    test('daily tip caches and reads by date', () async {
      await LocalDb.instance.cacheDailyTip('2026-08-17', 'Save 20% first.');
      expect(await LocalDb.instance.dailyTip('2026-08-17'), 'Save 20% first.');
      expect(await LocalDb.instance.dailyTip('2026-08-16'), isNull);
    });

    test('chat history appends in order', () async {
      await LocalDb.instance.appendChatMessage('user', 'Hi');
      await LocalDb.instance.appendChatMessage('assistant', 'Hello');
      final history = await LocalDb.instance.chatHistory();
      expect(history.length, 2);
      expect(history.last['role'], 'user');
    });
  });

  group('LocalDb pending ops queue', () {
    test('enqueue and FIFO order', () async {
      await LocalDb.instance.enqueueOp('POST', '/a', body: {'x': 1});
      await LocalDb.instance.enqueueOp('PUT', '/b', body: {'y': 2});
      await LocalDb.instance.enqueueOp('DELETE', '/c');
      final ops = await LocalDb.instance.pendingOps();
      expect(ops.length, 3);
      expect(ops[0]['url'], '/a');
      expect(ops[1]['url'], '/b');
      expect(ops[2]['url'], '/c');
      expect(await LocalDb.instance.pendingOpCount(), 3);
    });

    test('markOpDone removes from pending', () async {
      final id = await LocalDb.instance.enqueueOp('POST', '/a');
      await LocalDb.instance.markOpDone(id);
      expect(await LocalDb.instance.pendingOpCount(), 0);
    });
  });

  group('ApiService offline methods', () {
    test('getOffline returns live response and caches it', () async {
      var calls = 0;
      ApiService.debugClient = MockClient((request) async {
        calls++;
        return http.Response('{"transactions":["t1"]}', 200);
      });
      final data = await ApiService().getOffline('/finance/transactions');
      expect(data, {'transactions': ['t1']});
      expect(await LocalDb.instance.readCache('/finance/transactions?'), {'transactions': ['t1']});
      expect(calls, 1);
    });

    test('getOffline falls back to cache when network fails', () async {
      await LocalDb.instance.cacheResponse('/finance/budgets?', {'budgets': ['cached']});
      ApiService.debugClient = MockClient((request) async {
        throw http.ClientException('offline');
      });
      final data = await ApiService().getOffline('/finance/budgets');
      expect(data, {'budgets': ['cached']});
    });

    test('getOffline returns null with no cache and no network', () async {
      ApiService.debugClient = MockClient((request) async {
        throw http.ClientException('offline');
      });
      expect(await ApiService().getOffline('/unknown'), isNull);
    });

    test('postOffline queues op when network fails', () async {
      ApiService.debugClient = MockClient((request) async {
        throw http.ClientException('offline');
      });
      final result = await ApiService().postOffline('/finance/transactions', body: {'amount': 100});
      expect(result, true);
      expect(await LocalDb.instance.pendingOpCount(), 1);
      final ops = await LocalDb.instance.pendingOps();
      expect(ops.first['url'], '/finance/transactions');
    });
  });

  group('SyncService flush', () {
    test('does nothing when unreachable', () async {
      SyncService.instance.skipReachabilityProbe = false;
      SyncService.instance.reachabilityProbe = () async => false;
      await LocalDb.instance.enqueueOp('POST', '/finance/transactions', body: {'amount': 5});
      await SyncService.instance.flush();
      expect(await LocalDb.instance.pendingOpCount(), 1);
      SyncService.instance.reachabilityProbe = null;
    });

    test('replays queued ops in FIFO order when reachable', () async {
      final replayed = <String>[];
      ApiService.debugClient = MockClient((request) async {
        replayed.add('${request.method} ${request.url.path}');
        return http.Response('{}', 200);
      });
      SyncService.instance.skipReachabilityProbe = true;
      await LocalDb.instance.enqueueOp('POST', '/finance/transactions', body: {'amount': 5});
      await LocalDb.instance.enqueueOp('DELETE', '/finance/budgets');
      await SyncService.instance.flush();
      expect(replayed, ['POST /api/v1/finance/transactions', 'DELETE /api/v1/finance/budgets']);
      expect(await LocalDb.instance.pendingOpCount(), 0);
      SyncService.instance.skipReachabilityProbe = false;
    });

    test('stops on server error and keeps op pending', () async {
      ApiService.debugClient = MockClient((request) async {
        if (request.url.path.endsWith('/fail')) return http.Response('server error', 500);
        return http.Response('{}', 200);
      });
      SyncService.instance.skipReachabilityProbe = true;
      await LocalDb.instance.enqueueOp('POST', '/fail', body: {'x': 1});
      await LocalDb.instance.enqueueOp('POST', '/ok', body: {'y': 2});
      await SyncService.instance.flush();
      expect(await LocalDb.instance.pendingOpCount(), 2);
      SyncService.instance.skipReachabilityProbe = false;
    });

    test('drops op on permanent client error', () async {
      ApiService.debugClient = MockClient((request) async {
        return http.Response('{"detail":"bad request"}', 400);
      });
      SyncService.instance.skipReachabilityProbe = true;
      await LocalDb.instance.enqueueOp('POST', '/finance/transactions', body: {'amount': -5});
      await SyncService.instance.flush();
      expect(await LocalDb.instance.pendingOpCount(), 0);
      SyncService.instance.skipReachabilityProbe = false;
    });
  });
}