class Order {
  
  final String account_id;
  final String order_id;
  final String type;
  final String action;
  final String ticker;
  final String duration;
  final double price;
  final double quantity;
  final DateTime? expiryDate;
  final String? imgURL;

  Order({
    required this.account_id,
    required this.order_id,
    required this.type,
    required this.action,
    required this.ticker,
    required this.duration,
    required this.price,
    required this.quantity,
    this.expiryDate,
    this.imgURL,
  });

  Map<String, dynamic> toMap() => {
    'account_id': account_id,
    'order_id': order_id,
    'type': type,
    'action': action,
    'ticker': ticker,
    'duration': duration,
    'price': price,
    'qty': quantity,
    'expiry_date': expiryDate?.toIso8601String(),
    'img_url': imgURL
  };

  factory Order.fromMap(Map<String, dynamic> map) => Order(
    account_id: map['account_id'],
    order_id: map['order_id'],
    type: map['type'],
    action: map['action'],
    ticker: map['ticker'],
    duration: map['duration'],
    price: map['price'],
    quantity: map['qty'],
    expiryDate: map['expiry_date'] != null ? DateTime.parse(map['expiry_date']) : null,
    imgURL: map['img_url']
  );

}