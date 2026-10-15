class Trade {
  
  final String account_id;
  final String trade_id;
  final String type;
  final String ticker;
  final double amount;
  final double shareCost;
  final double shares;
  final String description;
  final DateTime date;
  final String? imgURL;

  Trade({
    required this.account_id,
    required this.trade_id,
    required this.type,
    required this.ticker,
    required this.amount,
    required this.shareCost,
    required this.shares,
    required this.description,
    required this.date,
    this.imgURL,
  });

  Map<String, dynamic> toMap() => {
    'account_id': account_id,
    'trade_id': trade_id,
    'type': type,
    'ticker': ticker,
    'amount': amount,
    'shareCost': shareCost,
    'shares': shares,
    'description': description,
    'date': date.toIso8601String(),
    'imgURL': imgURL
  };

  factory Trade.fromMap(Map<String, dynamic> map) => Trade(
    account_id: map['account_id'],
    trade_id: map['trade_id'],
    type: map['type'],
    ticker: map['ticker'],
    amount: map['amount'],
    shareCost: map['shareCost'],
    shares: map['shares'],
    description: map['description'],
    date: DateTime.parse(map['date']),
    imgURL: map['imgURL']
  );

}