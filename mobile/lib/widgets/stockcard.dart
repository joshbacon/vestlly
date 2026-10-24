import 'package:flutter/material.dart';
import 'package:vestlly/models/stock.dart';
import 'package:vestlly/models/statemanager.dart';

class StockCard extends StatefulWidget {
  final Stock data;

  const StockCard(this.data, {Key? key}) : super(key: key);

  @override
  State<StockCard> createState() => _StockCardState();
}

class _StockCardState extends State<StockCard> {
  bool expanded = false;
  double ACTION_THRESHOLD = 0.2; // TODO: read this in from the sector-trained genomes
  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.hardEdge,
      child: InkWell(
        splashColor: Theme.of(context).colorScheme.primary,
        onTap: () { setState(() {expanded = !expanded;}); },
        child: Padding(
          padding: EdgeInsets.all(8.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.start,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(widget.data.ticker),
              Text(
                StateManager.currencyFormater.format(double.parse(widget.data.price!)),
                style: Theme.of(context).textTheme.titleSmall,
              ),
              Row(
                children: [
                  Spacer(),
                  Text(
                    widget.data.action,
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontSize: 14.0,
                      color: widget.data.score > ACTION_THRESHOLD ? Colors.lightGreen : widget.data.score < -ACTION_THRESHOLD ? Colors.red : Theme.of(context).colorScheme.primary
                    )
                  ),
                  SizedBox(width: 8.0),
                  Text(
                    widget.data.score.toStringAsFixed(2),
                    style: Theme.of(context).textTheme.titleSmall?.copyWith(
                      fontSize: 14.0,
                      color: widget.data.score > ACTION_THRESHOLD ? Colors.lightGreen : widget.data.score < -ACTION_THRESHOLD ? Colors.red : Theme.of(context).colorScheme.primary
                    )
                  ),
                  SizedBox(width: 8.0),
                ]
              ),
              Visibility(
                visible: expanded,
                child: Padding(
                  padding: EdgeInsets.symmetric(horizontal: 10.0),
                  child: Column(
                    children: [
                      Divider(
                        indent: 4,
                        endIndent: 4
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "EPS\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.eps}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "PEG\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.peg ?? '-'}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "P/S\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.pts}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "P/B\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.ptb}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "D/E\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.dte}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            "STD\t",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                          Text(
                            "${widget.data.meanstd}",
                            style: Theme.of(context).textTheme.titleSmall
                          ),
                        ]
                      ),
                      SizedBox(height: 8.0),
                    ]
                  )
                )
              )
            ]
          )
        )
      )
    );
  }
}