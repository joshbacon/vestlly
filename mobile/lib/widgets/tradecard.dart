import 'package:flutter/material.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/tradepair.dart';
import 'package:vestlly/models/statemanager.dart';

class TradeCard extends StatefulWidget {
  final TradePair data;

  const TradeCard(this.data, {Key? key}) : super(key: key);

  @override
  State<TradeCard> createState() => _TradeCardState();
}

class _TradeCardState extends State<TradeCard> {
  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.hardEdge,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: EdgeInsets.fromLTRB(8.0, 8.0, 20.0, 8.0),
            child: Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Image.network(
                    widget.data.exit.imgURL ?? 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.pngmart.com%2Ffiles%2F23%2FCrypto-PNG-Image.png&f=1&nofb=1&ipt=8fc0100eec0abe957ad72e1ca66babd9ed1c56a9eb830feed2509d3bb8da486d',
                    width: 48.0, height: 48.0,
                  ),
                ),
                SizedBox(width: 10.0),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      widget.data.exit.ticker,
                      style: Theme.of(context).textTheme.bodyMedium
                    ),
                    // Text(
                    //   "${widget.data.date.year}-${widget.data.date.month}-${widget.data.date.day} ${widget.data.date.hour}:${(widget.data.date.minute < 10 ? "0" : "")}${widget.data.date.minute}",
                    //   style: Theme.of(context).textTheme.bodySmall
                    // ),
                  ]
                ),
                Spacer(),
                Center(
                  child: Text(
                    StateManager.currencyFormater.format(widget.data.exit.amount + widget.data.entry.amount),
                    style: Theme.of(context).textTheme.titleMedium?.copyWith(
                      color: widget.data.exit.amount + widget.data.entry.amount >= 0 ? Colors.lightGreen : Colors.pink,
                    ),
                  ),
                ),
              ]
            ),
          ),
          Container(
            color: Theme.of(context).colorScheme.surfaceDim,
            child: Padding(
              padding: EdgeInsets.symmetric(vertical: 8.0),
              child: IntrinsicHeight(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("Entry:"),
                        Text(
                          StateManager.currencyFormater.format(widget.data.entry.amount),
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        // Text(widget.data.description, style: TextStyle(color: Colors.grey)),
                        Text("${(widget.data.entry.shares*-1).toStringAsFixed(2)} shares", style: TextStyle(color: Colors.grey)),
                        Text("@ \$${widget.data.entry.shareCost.toStringAsFixed(2)}", style: TextStyle(color: Colors.grey)),
                        SizedBox(height: 5.0),
                        Text(
                          "${widget.data.entry.date.year}-${widget.data.entry.date.month}-${widget.data.entry.date.day} ${widget.data.entry.date.hour}:${(widget.data.entry.date.minute < 10 ? "0" : "")}${widget.data.entry.date.minute}",
                          style: Theme.of(context).textTheme.bodySmall
                        ),
                      ]
                    ),
                    VerticalDivider(
                      width: 20,
                      thickness: 1,
                      indent: 1,
                      endIndent: 1,
                      color: Theme.of(context).colorScheme.primary,
                    ),
                    Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text("Exit:"),
                        Text(
                          StateManager.currencyFormater.format(widget.data.exit.amount),
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            color: Theme.of(context).colorScheme.primary,
                          ),
                        ),
                        Text("${(widget.data.exit.shares*-1).toStringAsFixed(2)} shares", style: TextStyle(color: Colors.grey)),
                        Text("@ \$${widget.data.exit.shareCost.toStringAsFixed(2)}", style: TextStyle(color: Colors.grey)),
                        SizedBox(height: 5.0),
                        Text(
                          "${widget.data.exit.date.year}-${widget.data.exit.date.month}-${widget.data.exit.date.day} ${widget.data.exit.date.hour}:${(widget.data.exit.date.minute < 10 ? "0" : "")}${widget.data.exit.date.minute}",
                          style: Theme.of(context).textTheme.bodySmall
                        ),
                      ]
                    ),
                  ]
                ),
              ),
            ),
          ),
        ]
      ),
    );
  }
}