import 'package:vestlly/models/trade.dart';

class TradePair {

  final Trade entry;
  final Trade exit;

  TradePair({
    required this.entry,
    required this.exit,
  });

  Map<String,Trade> toMap() => {
    "entry": entry,
    "exit": exit
  };

  factory TradePair.fromMap(Map<String,Trade> map) => TradePair(
    entry: map["entry"]!,
    exit: map["exit"]!
  );

}