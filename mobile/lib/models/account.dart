class Account {

  final String account_id;
  final String type;
  final String name;
  final double cash;
  final double value;
  final String institution;
  final List<double> performance;
  final List<double> contributions;
  final List<double> withdrawals;

  Account({
    required this.account_id,
    required this.type,
    required this.name,
    required this.cash,
    required this.value,
    required this.institution,
    required this.performance,
    required this.contributions,
    required this.withdrawals,
  });

  Map<String, dynamic> toMap() => {
    'account_id': account_id,
    'type': type,
    'name': name,
    'cash': cash,
    'value': value,
    'institution': institution,
    'performance': performance.join(","),
    'contributions': contributions.join(","),
    'withdrawals': withdrawals.join(",")
  };

  factory Account.fromMap(Map<String, dynamic> map) {
    List<double> perf = List<double>.from(map['performance'].split(",").map((p) => double.parse(p)).toList());
    List<double> contrib = List<double>.from(map['contributions'].split(",").map((p) => double.parse(p)).toList());
    List<double> withdrawals = List<double>.from(map['withdrawals'].split(",").map((p) => double.parse(p)).toList());
    return Account(
      account_id: map['account_id'],
      type: map['type'],
      name: map['name'],
      cash: map['cash'],
      value: map['value'],
      institution: map['institution'],
      performance: perf,
      contributions: contrib,
      withdrawals: withdrawals
    );
  }

}