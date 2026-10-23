import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/models/holding.dart';
import 'package:vestlly/models/order.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/stock.dart';

// singleton class to manage the database
class DB {

  // This is the actual database filename that is saved in the docs directory.
  static final _databaseName = "vestlly.db";
  // Increment this version when you need to change the schema.
  static final _databaseVersion = 1;

  // Table and Column names
  final String accountTable = "accounts";
  final String accountID = "account_id";
  final String accountType = "type";
  final String accountName = "name";
  final String accountCash = "cash";
  final String accountValue = "value";
  final String accountInstitution = "institution";
  final String accountPerformance = "performance";
  final String accountContributions = "contributions";
  final String accountWithdrawals = "withdrawals";

  final String holdingTable = "holdings";
  final String holdingID = "holding_id";
  final String holdingTicker = "ticker";
  final String holdingAvgPrice = "averagePrice";
  final String holdingMarketPrice = "marketPrice";
  final String holdingShares = "shares";
  final String holdingImgURL = "imgURL";

  final String tradeTable = "trades";
  final String tradeID = "trade_id";
  final String tradeType = "type";
  final String tradeTicker = "ticker";
  final String tradeAmount = "amount";
  final String tradeShareCost = "shareCost";
  final String tradeShares = "shares";
  final String tradeDescription = "description";
  final String tradeDate = "date";
  final String tradeImgURL = "imgURL";

  final String orderTable = "orders";
  final String orderID = "order_id";
  final String orderType = "type";
  final String orderAction = "action";
  final String orderTicker = "ticker";
  final String orderDuration = "duration";
  final String orderPrice = "price";
  final String orderQty = "qty";
  final String orderExpiryDate = "expiry_date";
  final String orderImgURL = "img_url";

  final String stockTable = "stocks";
	final String stockID = "stock_id";
	final String stockAccount = "account_id";
	final String stockTicker = "ticker";
	final String stockPrice = "price";
  final String stockImg = "imgURL";
	final String stockScore = "score";
	final String stockAction = "action";
	final String stockEps = "eps";
	final String stockPeg = "peg";
	final String stockPts = "pts";
	final String stockPtb = "ptb";
	final String stockDte = "dte";
	final String stockMeanstd = "meanstd";

  static final DB _instance = DB._internal();
  static Database? _database;

  factory DB() => _instance;
  DB._internal();

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDatabase();
    return _database!;
  }

  Future<Database> _initDatabase() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, _databaseName);

    return await openDatabase(
      path,
      version: 1,
      onCreate: _onCreate,
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE $accountTable (
        $accountID TEXT PRIMARY KEY,
        $accountType TEXT NOT NULL,
        $accountName TEXT NOT NULL,
        $accountCash REAL NOT NULL,
        $accountValue REAL NOT NULL,
        $accountInstitution TEXT NOT NULL,
        $accountPerformance TEXT NOT NULL,
        $accountContributions TEXT NOT NULL,
        $accountWithdrawals TEXT NOT NULL
      )
    ''');
    await db.execute('''
      CREATE TABLE $holdingTable (
        $holdingID TEXT PRIMARY KEY,
        $accountID TEXT NOT NULL,
        $holdingTicker TEXT NOT NULL,
        $holdingAvgPrice REAL NOT NULL,
        $holdingMarketPrice REAL NOT NULL,
        $holdingShares REAL NOT NULL,
        $holdingImgURL TEXT
      )
    ''');
    await db.execute('''
      CREATE TABLE $tradeTable (
        $tradeID TEXT PRIMARY KEY,
        $accountID TEXT NOT NULL,
        $tradeType TEXT NOT NULL,
        $tradeTicker TEXT NOT NULL,
        $tradeAmount REAL NOT NULL,
        $tradeShareCost REAL NOT NULL,
        $tradeShares REAL NOT NULL,
        $tradeDescription TEXT NOT NULL,
        $tradeDate TEXT NOT NULL,
        $tradeImgURL TEXT
      )
    ''');
    await db.execute('''
      CREATE TABLE $orderTable (
        $orderID TEXT PRIMARY KEY,
        $accountID TEXT NOT NULL,
        $orderType TEXT NOT NULL,
        $orderAction TEXT NOT NULL,
        $orderTicker TEXT NOT NULL,
        $orderDuration TEXT NOT NULL,
        $orderPrice REAL NOT NULL,
        $orderQty REAL NOT NULL,
        $orderExpiryDate TEXT,
        $orderImgURL TEXT
      )
    ''');
    await db.execute('''
      CREATE TABLE $stockTable (
        $stockID INTEGER PRIMARY KEY,
        $stockAccount TEXT NOT NULL,
        $stockTicker TEXT NOT NULL,
        $stockPrice TEXT,
        $stockImg TEXT,
        $stockScore REAL NOT NULL,
        $stockAction TEXT NOT NULL,
        $stockEps REAL,
        $stockPeg REAL,
        $stockPts REAL,
        $stockPtb REAL,
        $stockDte REAL,
        $stockMeanstd REAL
      )
    ''');
  }
  
  Future<int> insertAccount(Account account) async {
    final db = await database;
    return await db.insert(accountTable, account.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }
  
  Future<int> insertHolding(Holding holding) async {
    final db = await database;
    return await db.insert(holdingTable, holding.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }
  
  Future<int> insertTrade(Trade trade) async {
    final db = await database;
    return await db.insert(tradeTable, trade.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }
  
  Future<int> insertOrder(Order order) async {
    final db = await database;
    return await db.insert(orderTable, order.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }
  
  Future<int> insertStock(Stock stock) async {
    final db = await database;
    return await db.insert(stockTable, stock.toMap(), conflictAlgorithm: ConflictAlgorithm.replace);
  }

  Future<List<Map<String, dynamic>>> getAccounts() async {
    final db = await database;
    final result = await db.query(accountTable, orderBy: 'account_id DESC');
    return result;
  }

  Future<List<Map<String, dynamic>>> getHoldings(String aid) async {
    final db = await database;
    final result = await db.query(holdingTable, where: '$accountID = ?', whereArgs: [aid]);
    return result.isNotEmpty ? result : [];
  }

  Future<List<Map<String, dynamic>>> getTrades(String aid) async {
    final db = await database;
    final result = await db.query(tradeTable, where: '$accountID = ?', whereArgs: [aid]);
    return result.isNotEmpty ? result : [];
  }

  Future<List<Map<String, dynamic>>> getOrders(String aid) async {
    final db = await database;
    final result = await db.query(orderTable, where: '$accountID = ?', whereArgs: [aid]);
    return result.isNotEmpty ? result : [];
  }

  Future<List<Map<String, dynamic>>> getStocks(String ordering, String account) async {
    final db = await database;
    final result = await db.query(stockTable, where: '$stockAccount = ?', whereArgs: [account], orderBy: ordering);
    return result.isNotEmpty ? result : [];
  }

  Future<void> clearTables() async {
    clearAccounts();
    clearHoldings();
    clearTrades();
    clearOrders();
  }

  Future<void> clearAccounts() async {
    final db = await database;
    await db.delete(accountTable);
  }

  Future<void> clearHoldings() async {
    final db = await database;
    await db.delete(holdingTable);
  }

  Future<void> clearTrades() async {
    final db = await database;
    await db.delete(tradeTable);
  }

  Future<void> clearOrders() async {
    final db = await database;
    await db.delete(orderTable);
  }

  Future<void> clearStocks() async {
    final db = await database;
    await db.delete(stockTable);
  }

}