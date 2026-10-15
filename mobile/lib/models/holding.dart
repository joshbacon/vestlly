class Holding {
  
  final String account_id;
  final String holding_id;
  final String ticker;
  final double avgPrice;
  final double marketPrice;
  final double shares;
  final String? imgURL;

  Holding({
    required this.account_id,
    required this.holding_id,
    required this.ticker,
    required this.avgPrice,
    required this.marketPrice,
    required this.shares,
    this.imgURL,
  });

  Map<String, dynamic> toMap() => {
    'account_id': account_id,
    'holding_id': holding_id,
    'ticker': ticker,
    'averagePrice': avgPrice,
    'marketPrice': marketPrice,
    'shares': shares,
    'imgURL': imgURL
  };

  factory Holding.fromMap(Map<String, dynamic> map) => Holding(
    account_id: map['account_id'],
    holding_id: map['holding_id'],
    ticker: map['ticker'],
    avgPrice: map['averagePrice'],
    marketPrice: map['marketPrice'],
    shares: map['shares'],
    imgURL: map['imgURL']
  );

}