import 'package:flutter/material.dart';
import 'package:vestlly/models/holding.dart';
import 'package:vestlly/models/statemanager.dart';

class HoldingCard extends StatefulWidget {
  final Holding data;

  const HoldingCard(this.data, {Key? key}) : super(key: key);

  @override
  State<HoldingCard> createState() => _HoldingCardState();
}

class _HoldingCardState extends State<HoldingCard> {

  @override
  Widget build(BuildContext context) {
    return Card(
      clipBehavior: Clip.hardEdge,
      child: Padding(
        padding: EdgeInsets.fromLTRB(8.0, 8.0, 12.0, 8.0),
        child: Column(
          children: [
            Row(
              children: [
                ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Image.network(
                    widget.data.imgURL ?? 'https://external-content.duckduckgo.com/iu/?u=https%3A%2F%2Fwww.pngmart.com%2Ffiles%2F23%2FCrypto-PNG-Image.png&f=1&nofb=1&ipt=8fc0100eec0abe957ad72e1ca66babd9ed1c56a9eb830feed2509d3bb8da486d',
                    width: 48.0, height: 48.0,
                  ),
                ),
                SizedBox(width: 10.0),
                Text(widget.data.ticker),
                Spacer(),
                Text(
                  StateManager.currencyFormater.format(widget.data.marketPrice*widget.data.shares),
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: widget.data.marketPrice > widget.data.avgPrice ? Colors.lightGreen : Colors.red,
                  ),
                ),
              ]
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Text(
                      "book value",
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                      ),
                    ),
                    SizedBox(width: 10.0),
                    Text(
                      StateManager.currencyFormater.format(widget.data.avgPrice * widget.data.shares),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ]
                ),
                Row(
                  mainAxisAlignment: MainAxisAlignment.end,
                  children: [
                    Text(
                      "shares",
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                        color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                      ),
                    ),
                    SizedBox(width: 10.0),
                    Text(
                      widget.data.shares.toString(),
                      style: Theme.of(context).textTheme.bodyMedium,
                    ),
                  ]
                ),
                Text(
                  "${StateManager.currencyFormater.format((widget.data.marketPrice-widget.data.avgPrice)*widget.data.shares)} (${StateManager.percentFormater(widget.data.marketPrice/widget.data.avgPrice-1)})",
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: widget.data.marketPrice > widget.data.avgPrice ? Colors.lightGreen : Colors.red,
                  ),
                ),
              ]
            ),
          ],
        ),
      ),
    );
  }
}