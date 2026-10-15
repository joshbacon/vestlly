class Stock {
  
  final int stock_id;
  final String account_id;
  final String ticker;
  final String? price;
  final String? imgURL;
  final double score;
  final String action;
  final double? eps;
  final double? peg;
  final double? pts;
  final double? ptb;
  final double? dte;
  final double? meanstd;

  Stock({
    required this.stock_id,
    required this.account_id,
    required this.ticker,
    this.price,
    this.imgURL,
    required this.score,
    required this.action,
    this.eps,
    this.peg,
    this.pts,
    this.ptb,
    this.dte,
    this.meanstd
  });

  Map<String, dynamic> toMap() => {
    'stock_id': stock_id,
    'account_id': account_id,
    'ticker': ticker,
    'price': price,
    'imgURL': imgURL,
    'score': score,
    'action': action,
    'eps': eps,
    'peg': peg,
    'pts': pts,
    'ptb': ptb,
    'dte': dte,
    'meanstd': meanstd
  };

  factory Stock.fromMap(Map<String, dynamic> map) => Stock(
    stock_id: map['stock_id'],
    account_id: map['account_id'],
    ticker: map['ticker'],
    price: map['price'],
    imgURL: map['imgURL'],
    score: map['score'],
    action: map['action'],
    eps: map['eps'],
    peg: map['peg'],
    pts: map['pts'],
    ptb: map['ptb'],
    dte: map['dte'],
    meanstd: map['meanstd']
  );

}