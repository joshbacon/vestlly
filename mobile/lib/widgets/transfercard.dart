import 'package:flutter/material.dart';
import 'package:vestlly/models/trade.dart';
import 'package:vestlly/models/statemanager.dart';

class TransferCard extends StatefulWidget {
  final Trade data;

  const TransferCard(this.data, {Key? key}) : super(key: key);

  @override
  State<TransferCard> createState() => _TransferCardState();
}

class _TransferCardState extends State<TransferCard> {
  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.hardEdge,
      child: Padding(
        padding: EdgeInsets.fromLTRB(8.0, 8.0, 20.0, 8.0),
        child: Row(
          children: [
            Image.network(
              'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.pngmart.com%2Ffiles%2F23%2FCrypto-PNG-Image.png&f=1&nofb=1&ipt=8fc0100eec0abe957ad72e1ca66babd9ed1c56a9eb830feed2509d3bb8da486d',
              width: 48.0, height: 48.0,
            ),
            SizedBox(width: 8.0),
            Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  widget.data.ticker,
                  style: Theme.of(context).textTheme.bodyMedium
                ),
                Text(
                  "${widget.data.date.year}-${widget.data.date.month}-${widget.data.date.day} ${widget.data.date.hour}:${(widget.data.date.minute < 10 ? "0" : "")}${widget.data.date.minute}",
                  style: Theme.of(context).textTheme.bodySmall
                ),
              ]
            ),
            Spacer(),
            Text(
              StateManager.currencyFormater.format(widget.data.amount),
              style: Theme.of(context).textTheme.titleMedium?.copyWith(
                color: Theme.of(context).colorScheme.primary,
              ),
            ),
          ]
        ),
      )
    );
  }
}