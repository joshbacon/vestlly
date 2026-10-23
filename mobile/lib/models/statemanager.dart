import 'package:http/http.dart' as http;
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'dart:convert';
import 'package:vestlly/models/db.dart';
import 'package:vestlly/models/account.dart';
import 'package:vestlly/models/holding.dart';
import 'package:vestlly/models/order.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/tradepair.dart';
import 'package:vestlly/models/stock.dart';
import 'package:intl/intl.dart';
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';

class StateManager extends ChangeNotifier {

  final DB database = DB();

  DateTime lastUpdated = DateTime.now();
  double totalValue = 0.0;
  double totalContrib = 0.0;
  double totalWithdrawal = 0.0;

  static var currencyFormater = new NumberFormat.currency(locale: "en_US", symbol: "\$");
  static String percentFormater(double percent) => (percent*100).toStringAsFixed(percent.truncateToDouble() == percent ? 0 : 2) + "%";

  StateManager() {
    loadLocal();
    fetchStockData();
    fetchSTData();
  }

  Future<void> loadLocal() async {
    final prefs = await SharedPreferences.getInstance();
    String? temp = prefs.getString('lastUpdated');
    if (temp != null) lastUpdated = DateTime.parse(temp);
    totalValue = prefs.getDouble('totalValue') ?? 0.0;
    totalContrib = prefs.getDouble('totalContrib') ?? 0.0;
    totalWithdrawal = prefs.getDouble('totalWithdrawal') ?? 0.0;
    notifyListeners();
  }

  Future<List<Map<String,dynamic>>> getTradePairs(account_id) async {
    var trades = await database.getTrades(account_id);
    List<Map<String,dynamic>> formatted = [];
    int n = 0;
    while (n < trades.length) {
      if (trades[n]['type'] == 'CONTRIBUTION' || trades[n]['type'] == 'WITHDRAWAL') {
        formatted.add({"type": "TRANSFER", "trade": Trade.fromMap(trades[n])});
      } else if (trades[n]['type'] == "SELL") {
        // create a card for each sale, loop ahead to find the entry
        var entry = null;
        for (var i=n+1; i < trades.length; i++) {
          if (trades[i]['ticker'] == trades[n]['ticker'] && trades[i]['type'] == "BUY") {
            entry = {...trades[i]};
            entry['shares'] = trades[n]['shares'];
            entry['amount'] = entry['shares'] * entry['shareCost'];
            break;
          }
        }
        formatted.add({
          "type": "TRADE",
          "trade": TradePair(
            entry: Trade.fromMap(entry),
            exit: Trade.fromMap(trades[n])
          )
        });
      }
      n++;
    }
    return formatted;
  }

  Future<int> fetchStockData() async {
    var response;
    try {
      const path = String.fromEnvironment('STOCK_DATA_ENDPOINT');
      response = await http.get(
        Uri.parse(path)
      ).timeout(const Duration(seconds: 20));
    } on TimeoutException {
      notifyListeners();
      return 110;
    }
    if (response.statusCode != 200) {
      notifyListeners();
      return response.statusCode;
    }

    List<dynamic> data = json.decode(response.body);
    for (final stock in data) {
      database.insertStock(Stock(
        stock_id: stock["sid"],
        account_id: stock["account"],
        ticker: stock["ticker"],
        price: stock["price"],
        imgURL: stock["img"],
        score: double.parse(stock["score"]),
        action: stock["action"],
        eps: stock["eps"] != null ? double.parse(stock["eps"]) : null,
        peg: stock["peg"] != null ? double.parse(stock["peg"]) : null,
        pts: stock["pts"] != null ? double.parse(stock["pts"]) : null,
        ptb: stock["ptb"] != null ? double.parse(stock["ptb"]) : null,
        dte: stock["dte"] != null ? double.parse(stock["dte"]) : null,
        meanstd: stock["meanstd"] != null ? double.parse(stock["meanstd"]) : null,
      ));
    }
    return response.statusCode;
  }

  Future<int> fetchSTData() async {
    var response;
    print("~~~~~~~~~~~~~~~~~THIS IS WHERE YOU WANT TO BE LOOKING AT~~~~~~~~~~~~~~~~");
    try {
      const path = String.fromEnvironment('ACCOUNT_DATA_ENDPOINT');
      response = await http.get(
        Uri.parse(path)
      ).timeout(const Duration(seconds: 20));
    } on TimeoutException {
      notifyListeners();
      return 110;
    }
    if (response.statusCode != 200) {
      notifyListeners();
      return response.statusCode;
    }

    // Clear out old data to fill in the new
    await database.clearTables();

    Map<String, dynamic> data = json.decode(response.body);

    double updatedTotal = 0.0;
    double updatedContrib = 0.0;
    double updatedWithdrawal = 0.0;

    double tempTotal;
    double cash;
    for (final account in data['accounts']) {
      tempTotal = account['cash']['amount'].toDouble();
      cash = tempTotal;
      // print(account);
      for (final h in account['holdings']) {
        database.insertHolding(Holding(
          account_id: account['id'],
          holding_id: h['symbol']['id'],
          ticker: h['symbol']['symbol']['symbol'],
          avgPrice: h['average_purchase_price'],
          marketPrice: h['price'],
          shares: h['units'],
          imgURL: h['symbol']['symbol']['logo_url'],
        ));
        cash -= h['units'] * h['price'];
      }
      if (account['orders'].length > 0) {
        for (final o in account['orders']) {
          database.insertOrder(Order(
            account_id: account['id'],
            order_id: o['brokerage_order_id'],
            type: o['order_type'],
            action: o['action'],
            ticker: o['universal_symbol']['symbol'],
            duration: o['time_in_force'],
            price: double.parse(o['limit_price']),
            quantity: double.parse(o['open_quantity']),
            expiryDate: o['expiry_date'],
            imgURL: o['universal_symbol']['logo_url'],
          ));
        }
      }
      if (account['transactions'].length > 0) {
        for (final t in account['transactions']) {
          database.insertTrade(Trade(
            account_id: account['id'],
            trade_id: t['id'],
            type: t['type'],
            ticker: t['type'] == 'CONTRIBUTION' ? 'Deposit' : t['type'] == 'WITHDRAWAL' ? 'Withdrawal' : t['symbol']['symbol'],
            amount: t['amount'].toDouble(),
            shareCost: t['price'].toDouble(),
            shares: t['units'].toDouble(),
            description: t['description'],
            date: DateTime.parse(t['trade_date']),
            imgURL: t['type'] == 'CONTRIBUTION' || t['type'] == 'WITHDRAWAL' ? null : t['symbol']['logo_url'],
          ));
        }
      }
      List<double> perf = account['performance'].map<double>((e) => double.parse(e.toString())).toList();
      if (perf.isEmpty) {
        perf = [0.0];
      }
      List<double> contribs = account['contributions'].map<double>((e) => double.parse(e.toString())).toList();
      if (contribs.isEmpty) {
        contribs = [0.0];
      }
      List<double> witds = account['withdrawals'].map<double>((e) => double.parse(e.toString())).toList();
      if (witds.isEmpty) {
        witds = [0.0];
      }
      database.insertAccount(Account(
        account_id: account['id'],
        type: account['type'],
        name: account['name'].substring(account['institution'].length+1),
        cash: cash,
        value: tempTotal,
        institution: account['institution'],
        performance: perf,
        contributions: contribs,
        withdrawals: witds
      ));
      updatedTotal += tempTotal;
      updatedContrib += contribs.last;
      updatedWithdrawal += witds.last;
    }
    final prefs = await SharedPreferences.getInstance();
    totalValue = updatedTotal;
    totalContrib = updatedContrib;
    totalWithdrawal = updatedWithdrawal;
    lastUpdated = DateTime.now();
    await prefs.setString('lastUpdated', DateTime.now().toIso8601String());
    await prefs.setDouble('totalValue', totalValue);
    await prefs.setDouble('totalContrib', totalContrib);
    await prefs.setDouble('totalWithdrawal', totalWithdrawal);
    notifyListeners();
    return data['status'];
  }

}




